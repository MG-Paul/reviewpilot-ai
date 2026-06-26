from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any
from pydantic import BaseModel, UUID4
import uuid

from app.core.database import get_db
from app.models.models import Reference, ReferenceDuplicate, Project
from app.services.import_parser import parse_bibliography_file
from app.services.deduplication import check_duplicates_for_reference, get_embedding

router = APIRouter(prefix="", tags=["References"])

# Pydantic Schemas
class ReferenceResponse(BaseModel):
    id: UUID4
    title: str
    authors: List[str] | None
    journal: str | None
    year: int | None
    doi: str | None
    status: str

    class Config:
        from_attributes = True

class DuplicateResponse(BaseModel):
    id: UUID4
    primary: ReferenceResponse
    duplicate: ReferenceResponse
    similarity_score: float
    duplicate_type: str

@router.post("/projects/{project_id}/imports", status_code=status.HTTP_201_CREATED)
async def import_references(
    project_id: UUID4, 
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db)
):
    """
    Uploads and parses a RIS or BibTeX file. Stores references and runs background duplicate checking.
    """
    # Verify project exists
    project_res = await db.execute(select(Project).where(Project.id == project_id))
    if not project_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    content = await file.read()
    content_str = content.decode("utf-8", errors="ignore")
    
    try:
        parsed_refs = parse_bibliography_file(file.filename, content_str)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    created_references = []
    
    for ref_data in parsed_refs:
        # Generate semantic embedding of Title + Abstract
        text_to_embed = f"{ref_data.get('title', '')} {ref_data.get('abstract', '')}"
        embedding = await get_embedding(text_to_embed)
        
        reference = Reference(
            project_id=project_id,
            title=ref_data.get("title", "Untitled Reference"),
            abstract=ref_data.get("abstract"),
            authors=ref_data.get("authors"),
            journal=ref_data.get("journal"),
            year=ref_data.get("year"),
            doi=ref_data.get("doi"),
            volume=ref_data.get("volume"),
            issue=ref_data.get("issue"),
            pages=ref_data.get("pages"),
            import_source=ref_data.get("import_source"),
            raw_metadata=ref_data.get("raw_metadata"),
            semantic_embedding=embedding,
            status="unscreened"
        )
        db.add(reference)
        # Flush to generate ID for deduplication checks
        await db.flush()
        
        # Check duplicate relationship with existing records in this project
        await check_duplicates_for_reference(db, reference, project_id)
        created_references.append(reference)
        
    await db.commit()
    return {"message": f"Successfully imported {len(created_references)} references"}

@router.get("/projects/{project_id}/duplicates", response_model=List[Dict[str, Any]])
async def list_project_duplicates(project_id: UUID4, db: AsyncSession = Depends(get_db)):
    """
    Fetches pending duplicates for a project side-by-side.
    """
    result = await db.execute(
        select(ReferenceDuplicate).where(
            ReferenceDuplicate.project_id == project_id,
            ReferenceDuplicate.status == "pending"
        )
    )
    duplicates = result.scalars().all()
    
    response = []
    for dup in duplicates:
        # Fetch actual references
        primary_res = await db.execute(select(Reference).where(Reference.id == dup.reference_id_primary))
        duplicate_res = await db.execute(select(Reference).where(Reference.id == dup.reference_id_duplicate))
        primary = primary_res.scalar_one_or_none()
        duplicate = duplicate_res.scalar_one_or_none()
        
        if primary and duplicate:
            response.append({
                "duplicate_id": dup.id,
                "similarity_score": dup.similarity_score,
                "type": dup.duplicate_type,
                "primary": {
                    "id": primary.id,
                    "title": primary.title,
                    "authors": primary.authors,
                    "abstract": primary.abstract,
                    "year": primary.year,
                    "doi": primary.doi,
                    "journal": primary.journal
                },
                "duplicate": {
                    "id": duplicate.id,
                    "title": duplicate.title,
                    "authors": duplicate.authors,
                    "abstract": duplicate.abstract,
                    "year": duplicate.year,
                    "doi": duplicate.doi,
                    "journal": duplicate.journal
                }
            })
    return response

@router.post("/duplicates/resolve")
async def resolve_duplicate(
    duplicate_id: UUID4, 
    action: str, # 'merge' or 'separate'
    db: AsyncSession = Depends(get_db)
):
    """
    Resolves a flagged duplicate. If 'merge', updates duplicate status to 'duplicate' (hidden).
    """
    dup_res = await db.execute(select(ReferenceDuplicate).where(ReferenceDuplicate.id == duplicate_id))
    dup = dup_res.scalar_one_or_none()
    if not dup:
        raise HTTPException(status_code=404, detail="Duplicate record not found")
        
    if action == "merge":
        dup.status = "resolved_duplicate"
        # Update target reference status to duplicate
        target_ref_res = await db.execute(select(Reference).where(Reference.id == dup.reference_id_duplicate))
        target_ref = target_ref_res.scalar_one_or_none()
        if target_ref:
            target_ref.status = "duplicate"
    else:
        dup.status = "resolved_separate"
        
    await db.commit()
    return {"message": "Duplicate resolved successfully"}
