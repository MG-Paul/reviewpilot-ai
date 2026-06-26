from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, Table, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid

from app.core.database import Base

# Association table for Project Members (RBAC)
project_members = Table(
    'project_members',
    Base.metadata,
    Column('project_id', UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', String, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role', String, nullable=False, default='reviewer') # owner, admin, reviewer, screener
)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True) # Clerk ID
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    projects = relationship("Project", secondary=project_members, back_populates="members")

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    protocol_picos = Column(JSONB, nullable=True) # PICOS parameters structure
    screening_criteria = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_living_review = Column(Boolean, default=False, nullable=False)
    living_review_frequency = Column(String, default="monthly", nullable=False)
    living_review_query = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    members = relationship("User", secondary=project_members, back_populates="projects")
    references = relationship("Reference", back_populates="project", cascade="all, delete-orphan")
    schemas = relationship("ExtractionSchema", back_populates="project", cascade="all, delete-orphan")
    analyses = relationship("RAnalysis", back_populates="project", cascade="all, delete-orphan")

class Reference(Base):
    __tablename__ = "references"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    abstract = Column(Text, nullable=True)
    authors = Column(ARRAY(String), nullable=True)
    journal = Column(String(255), nullable=True)
    year = Column(Integer, nullable=True)
    doi = Column(String(100), nullable=True)
    volume = Column(String(50), nullable=True)
    issue = Column(String(50), nullable=True)
    pages = Column(String(50), nullable=True)
    import_source = Column(String(100), nullable=True) # RIS, BibTeX, Zotero, PubMed
    raw_metadata = Column(JSONB, nullable=True)
    
    # 1536 dimension vector for OpenAI embeddings used by pgvector
    semantic_embedding = Column(Vector(1536), nullable=True)
    
    # unscreened, screening_title_abstract, screening_full_text, included, excluded, duplicate
    status = Column(String(50), default="unscreened", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="references")
    pdf = relationship("PDF", uselist=False, back_populates="reference", cascade="all, delete-orphan")
    extractions = relationship("ExtractedData", back_populates="reference", cascade="all, delete-orphan")
    rob_assessments = relationship("RiskOfBias", back_populates="reference", cascade="all, delete-orphan")

class ReferenceDuplicate(Base):
    __tablename__ = "reference_duplicates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    reference_id_primary = Column(UUID(as_uuid=True), ForeignKey("references.id", ondelete="CASCADE"), nullable=False)
    reference_id_duplicate = Column(UUID(as_uuid=True), ForeignKey("references.id", ondelete="CASCADE"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    duplicate_type = Column(String(50), nullable=False) # exact, semantic, companion
    status = Column(String(50), default="pending", nullable=False) # pending, resolved_duplicate, resolved_separate
    resolved_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)

class PDF(Base):
    __tablename__ = "pdfs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_id = Column(UUID(as_uuid=True), ForeignKey("references.id", ondelete="CASCADE"), nullable=False, unique=True)
    s3_key = Column(String(512), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    parsed_markdown = Column(Text, nullable=True)
    layout_json = Column(JSONB, nullable=True)
    ocr_status = Column(String(50), default="pending", nullable=False) # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    reference = relationship("Reference", back_populates="pdf")

class ExtractionSchema(Base):
    __tablename__ = "extraction_schemas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, default=1, nullable=False)
    fields = Column(JSONB, nullable=False) # [{name, type, description, picos}]
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="schemas")

class ExtractedData(Base):
    __tablename__ = "extracted_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_id = Column(UUID(as_uuid=True), ForeignKey("references.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(100), nullable=False)
    value = Column(Text, nullable=True)
    extracted_by = Column(String(50), nullable=False) # ai_agent, user
    confidence_score = Column(Float, nullable=True)
    provenance = Column(JSONB, nullable=True) # [{page, bounding_box, text}]
    status = Column(String(50), default="draft", nullable=False) # draft, verified, conflict
    verified_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    reference = relationship("Reference", back_populates="extractions")

class RiskOfBias(Base):
    __tablename__ = "risk_of_bias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_id = Column(UUID(as_uuid=True), ForeignKey("references.id", ondelete="CASCADE"), nullable=False)
    tool_name = Column(String(50), nullable=False) # RoB2, ROBINS-I
    domain_name = Column(String(100), nullable=False) # randomization_process, deviations, missing_data, etc.
    judgment = Column(String(50), nullable=False) # low, high, some_concerns
    justification = Column(Text, nullable=False)
    evidence_quotes = Column(JSONB, nullable=True) # [{page, text}]
    assessed_by = Column(String(50), nullable=False) # ai_agent, user
    status = Column(String(50), default="draft", nullable=False) # draft, verified, conflict
    verified_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    reference = relationship("Reference", back_populates="rob_assessments")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    reference_id = Column(UUID(as_uuid=True), ForeignKey("references.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_type = Column(String(50), nullable=False) # reference, extracted_field, rob_domain
    target_field = Column(String(100), nullable=True)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False) # import_references, screening_decision, edit_extraction, etc.
    details = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class RAnalysis(Base):
    __tablename__ = "r_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    analysis_type = Column(String(100), nullable=False) # meta_analysis, subgroup, meta_regression
    r_code = Column(Text, nullable=False)
    output_json = Column(JSONB, nullable=True)
    forest_plot_s3_key = Column(String(512), nullable=True)
    funnel_plot_s3_key = Column(String(512), nullable=True)
    created_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="analyses")
