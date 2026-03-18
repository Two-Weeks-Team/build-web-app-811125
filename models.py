import json
import os
from datetime import datetime, timezone
from typing import Generator

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker


def _normalize_database_url(raw_url: str) -> str:
    if raw_url.startswith("postgresql+asyncpg://"):
        return raw_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg://", 1)
    return raw_url


DATABASE_URL = _normalize_database_url(
    os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db"))
)

_engine_kwargs = {"future": True}
if DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
elif "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
    _engine_kwargs["connect_args"] = {"sslmode": "require"}

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class IntakeSeed(Base):
    __tablename__ = "bw_intake_seeds"

    id = Integer = Integer
    id = Integer().with_variant(Integer, "sqlite")

    id = Integer


class IntakeSeed(Base):
    __tablename__ = "bw_intake_seeds"

    id = Integer

    from sqlalchemy.orm import Mapped, mapped_column

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    raw_notes: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False, default="product-planning")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Dossier(Base):
    __tablename__ = "bw_dossiers"

    from sqlalchemy.orm import Mapped, mapped_column

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)
    preferences_json: Mapped[str] = mapped_column(Text, nullable=False, default="")

    problem: Mapped[str] = mapped_column(Text, nullable=False, default="")
    target_users: Mapped[str] = mapped_column(Text, nullable=False, default="")
    solution: Mapped[str] = mapped_column(Text, nullable=False, default="")
    workflow_outline: Mapped[str] = mapped_column(Text, nullable=False, default="")

    status: Mapped[str] = mapped_column(String(30), nullable=False, default="distilled")
    readiness_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    sections = relationship("BriefSection", back_populates="dossier", cascade="all, delete-orphan")


class BriefSection(Base):
    __tablename__ = "bw_brief_sections"

    from sqlalchemy.orm import Mapped, mapped_column

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dossier_id: Mapped[int] = mapped_column(Integer, ForeignKey("bw_dossiers.id", ondelete="CASCADE"), nullable=False, index=True)
    section_key: Mapped[str] = mapped_column(String(80), nullable=False)
    section_title: Mapped[str] = mapped_column(String(120), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    completeness: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    trace_spans = relationship("SourceTrace", back_populates="section", cascade="all, delete-orphan")
    dossier = relationship("Dossier", back_populates="sections")


class SourceTrace(Base):
    __tablename__ = "bw_source_traces"

    from sqlalchemy.orm import Mapped, mapped_column

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    section_id: Mapped[int] = mapped_column(Integer, ForeignKey("bw_brief_sections.id", ondelete="CASCADE"), nullable=False, index=True)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False, default="")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    section = relationship("BriefSection", back_populates="trace_spans")


class ArtifactEvent(Base):
    __tablename__ = "bw_artifact_events"

    from sqlalchemy.orm import Mapped, mapped_column

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dossier_id: Mapped[int] = mapped_column(Integer, ForeignKey("bw_dossiers.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def serialize_preferences(preferences: str) -> str:
    if not preferences:
        return ""
    return preferences.strip()


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        if db.query(IntakeSeed).count() == 0:
            seeds = [
                IntakeSeed(
                    title="Campus TaskMate",
                    raw_notes="Campus TaskMate: a student assignment planning app built from scattered supervisor notes. Need deadline tracking, milestone suggestions, and an academic review-ready brief.",
                    domain="education-productivity",
                ),
                IntakeSeed(
                    title="FocusFlow",
                    raw_notes="FocusFlow: a lightweight productivity tool for turning voice memos into weekly action plans. Target overloaded students and solo builders.",
                    domain="productivity",
                ),
                IntakeSeed(
                    title="LabSync Planner",
                    raw_notes="LabSync Planner: final-year project concept for coordinating team milestones and submissions with shared ownership and traceable rationale.",
                    domain="academic-collaboration",
                ),
            ]
            db.add_all(seeds)
            db.commit()

        if db.query(Dossier).count() == 0:
            dossier = Dossier(
                title="PitchDraft Foundry Brief",
                raw_input="PitchDraft converts founder idea dumps into structured product briefs for early validation.",
                preferences_json="focus: final-year project framing; scope: mvp; audience: students",
                problem="Ideas are captured as messy fragments and fail to become submission-ready plans.",
                target_users="Final-year students and early-stage builders with incomplete context.",
                solution="A planning studio that distills rough notes into traceable brief sections and reusable dossiers.",
                workflow_outline="Intake -> Distill -> Review -> Save",
                status="saved",
                readiness_score=0.86,
            )
            db.add(dossier)
            db.flush()

            section = BriefSection(
                dossier_id=dossier.id,
                section_key="target_users",
                section_title="Target Users",
                content="Final-year students and early-stage builders with incomplete context.",
                completeness=0.9,
            )
            db.add(section)
            db.flush()

            trace = SourceTrace(
                section_id=section.id,
                source_text="founder idea dumps into structured product briefs",
                rationale="Indicates user segment needing structure from raw notes.",
                confidence=0.82,
            )
            db.add(trace)

            db.add(
                ArtifactEvent(
                    dossier_id=dossier.id,
                    status="saved",
                    note="Seed dossier available on first load",
                    metadata_json={"source": "system_seed"},
                )
            )
            db.commit()
    finally:
        db.close()
