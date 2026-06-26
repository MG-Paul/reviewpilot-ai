from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Dict, Any
from pydantic import BaseModel, UUID4
from datetime import datetime

from app.core.database import get_db
from app.models.models import Project, Reference

router = APIRouter(prefix="/projects", tags=["Projects"])

# Pydantic schemas
class ProjectCreate(BaseModel):
    title: str
    description: str | None = None
    protocol_picos: Dict[str, Any] | None = None
    screening_criteria: str | None = None
    is_living_review: bool = False
    living_review_frequency: str = "monthly"
    living_review_query: str | None = None

class ProjectResponse(BaseModel):
    id: UUID4
    title: str
    description: str | None
    is_living_review: bool
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project_in: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """
    Creates a new Systematic Review Project.
    """
    project = Project(
        title=project_in.title,
        description=project_in.description,
        protocol_picos=project_in.protocol_picos,
        screening_criteria=project_in.screening_criteria,
        is_living_review=project_in.is_living_review,
        living_review_frequency=project_in.living_review_frequency,
        living_review_query=project_in.living_review_query
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

@router.get("", response_model=List[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    """
    Retrieves all projects.
    """
    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    return result.scalars().all()

@router.get("/{project_id}/prisma", response_model=Dict[str, int])
async def get_prisma_flow(project_id: UUID4, db: AsyncSession = Depends(get_db)):
    """
    Calculates dynamic node counts for the PRISMA Flow Diagram based on database states.
    """
    # Count references in different status states
    result = await db.execute(
        select(Reference.status, func.count(Reference.id))
        .where(Reference.project_id == project_id)
        .group_by(Reference.status)
    )
    counts = dict(result.all())
    
    # Calculate PRISMA flows
    unscreened = counts.get("unscreened", 0)
    duplicates = counts.get("duplicate", 0)
    screened_ta = counts.get("screening_title_abstract", 0)
    screened_ft = counts.get("screening_full_text", 0)
    included = counts.get("included", 0)
    excluded = counts.get("excluded", 0)
    
    total_imported = unscreened + duplicates + screened_ta + screened_ft + included + excluded
    
    return {
        "records_identified": total_imported,
        "duplicates_removed": duplicates,
        "records_screened": screened_ta + screened_ft + included + excluded + unscreened,
        "records_excluded_screening": excluded, # excluded during title/abstract or full text
        "full_text_sought_reports": screened_ft + included + excluded,
        "full_text_assessed_eligibility": included + excluded,
        "studies_included": included
    }
