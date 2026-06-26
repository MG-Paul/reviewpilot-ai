import re
from typing import List, Dict, Any, Tuple
import numpy as np
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Reference, ReferenceDuplicate
from app.core.config import settings

def normalize_title(title: str) -> str:
    """
    Cleans and normalizes a title for robust fuzzy matching.
    """
    if not title:
        return ""
    # Lowercase, remove punctuation, strip whitespaces
    title = title.lower()
    title = re.sub(r"[^\w\s]", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title

def levenshtein_similarity(s1: str, s2: str) -> float:
    """
    Computes Levenshtein similarity score between 0 and 1.
    """
    s1_norm = normalize_title(s1)
    s2_norm = normalize_title(s2)
    
    if not s1_norm and not s2_norm:
        return 1.0
    if not s1_norm or not s2_norm:
        return 0.0
        
    if len(s1_norm) < len(s2_norm):
        s1_norm, s2_norm = s2_norm, s1_norm
        
    distances = range(len(s2_norm) + 1)
    for i, c1 in enumerate(s1_norm):
        distances_ = [i+1]
        for j, c2 in enumerate(s2_norm):
            if c1 == c2:
                distances_.append(distances[j])
            else:
                distances_.append(1 + min((distances[j], distances[j + 1], distances_[-1])))
        distances = distances_
        
    lev_dist = distances[-1]
    max_len = max(len(s1_norm), len(s2_norm))
    return 1.0 - (lev_dist / max_len)

async def generate_mock_embedding(text: str) -> List[float]:
    """
    Generates a deterministic mock embedding vector of 1536 dimensions
    if OpenAI keys are missing. Based on hashing characters.
    """
    # Deterministic seed from text
    seed = sum(ord(c) * (i + 1) for i, c in enumerate(text[:100]))
    np.random.seed(seed % 999999)
    vector = np.random.randn(1536)
    # L2 normalize
    norm = np.linalg.norm(vector)
    vector = vector / norm if norm > 0 else vector
    return vector.tolist()

async def get_embedding(text: str) -> List[float]:
    """
    Fetches the 1536-dim OpenAI embedding for a text.
    Falls back to mock embeddings if API key is not present.
    """
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key":
        return await generate_mock_embedding(text)
    
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "text-embedding-3-small",
                    "input": text[:8000] # Trim to prevent context issues
                },
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()["data"][0]["embedding"]
            else:
                return await generate_mock_embedding(text)
    except Exception:
        return await generate_mock_embedding(text)

async def check_duplicates_for_reference(
    db: AsyncSession, 
    ref: Reference, 
    project_id: str
) -> List[Dict[str, Any]]:
    """
    Scans existing database references in a project to flag duplicates.
    Saves flagged connections inside the database.
    """
    # Fetch all active references in this project
    result = await db.execute(
        select(Reference).where(
            Reference.project_id == project_id,
            Reference.id != ref.id,
            Reference.status != "duplicate"
        )
    )
    existing_refs = result.scalars().all()
    duplicates_found = []
    
    for exist in existing_refs:
        similarity = 0.0
        dup_type = ""
        
        # 1. Exact DOI check
        if ref.doi and exist.doi and ref.doi.strip().lower() == exist.doi.strip().lower():
            similarity = 1.0
            dup_type = "exact"
            
        # 2. Fuzzy Title similarity
        if not dup_type:
            title_sim = levenshtein_similarity(ref.title, exist.title)
            if title_sim >= 0.88:
                similarity = title_sim
                dup_type = "semantic"
                
        # 3. Vector embedding check
        if not dup_type and ref.semantic_embedding is not None and exist.semantic_embedding is not None:
            # Cosine similarity since pgvector embeddings are L2 normalized
            v1 = np.array(ref.semantic_embedding)
            v2 = np.array(exist.semantic_embedding)
            cos_sim = float(np.dot(v1, v2))
            if cos_sim >= 0.92:
                similarity = cos_sim
                dup_type = "semantic"

        # If similarity meets threshold, store duplicate relationship
        if dup_type:
            dup_record = ReferenceDuplicate(
                project_id=project_id,
                reference_id_primary=exist.id, # Keep existing reference as primary
                reference_id_duplicate=ref.id,
                similarity_score=similarity,
                duplicate_type=dup_type,
                status="pending"
            )
            db.add(dup_record)
            duplicates_found.append({
                "primary_id": exist.id,
                "duplicate_id": ref.id,
                "similarity_score": similarity,
                "type": dup_type
            })
            
    await db.commit()
    return duplicates_found
