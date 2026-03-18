from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ai_service import distill_brief, generate_insights
from models import ArtifactEvent, BriefSection, Dossier, IntakeSeed, SourceTrace, get_db, serialize_preferences

router = APIRouter()


class PlanRequest(BaseModel):
    query: str
    preferences: str = ""


class InsightsRequest(BaseModel):
    selection: str
    context: str


class SaveDossierRequest(BaseModel):
    title: str
    query: str
    preferences: str = ""
    status: str = Field(default="saved")


@router.get("/seeds")
@router.get("/seeds")
def get_seeds(db: Session = Depends(get_db)):
    seeds = db.query(IntakeSeed).order_by(IntakeSeed.id.asc()).all()
    return {
        "items": [
            {
                "id": s.id,
                "title": s.title,
                "raw_notes": s.raw_notes,
                "domain": s.domain,
            }
            for s in seeds
        ]
    }


@router.post("/plan")
@router.post("/plan")
async def plan(payload: PlanRequest, db: Session = Depends(get_db)):
    result = await distill_brief(payload.query, payload.preferences)
    return {
        "summary": result.get("summary", ""),
        "items": result.get("items", []),
        "score": result.get("score", 0.0),
        "sections": result.get("sections", {}),
        "traces": result.get("traces", {}),
        "note": result.get("note", ""),
    }


@router.post("/insights")
@router.post("/insights")
async def insights(payload: InsightsRequest, db: Session = Depends(get_db)):
    result = await generate_insights(payload.selection, payload.context)
    return {
        "insights": result.get("insights", []),
        "next_actions": result.get("next_actions", []),
        "highlights": result.get("highlights", []),
        "note": result.get("note", ""),
    }


@router.post("/dossiers/save")
@router.post("/dossiers/save")
async def save_dossier(payload: SaveDossierRequest, db: Session = Depends(get_db)):
    distilled = await distill_brief(payload.query, payload.preferences)
    sections = distilled.get("sections", {})
    traces = distilled.get("traces", {})

    dossier = Dossier(
        title=payload.title,
        raw_input=payload.query,
        preferences_json=serialize_preferences(payload.preferences),
        problem=str(sections.get("problem", "")),
        target_users=str(sections.get("target_users", "")),
        solution=str(sections.get("solution", "")),
        workflow_outline=str(sections.get("workflow", "")),
        status=payload.status,
        readiness_score=float(distilled.get("score", 0.0)),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(dossier)
    db.flush()

    section_map = {
        "problem": "Problem",
        "target_users": "Target Users",
        "solution": "Solution",
        "key_features": "Key Features",
        "workflow": "Workflow Outline",
        "constraints": "Constraints",
    }

    for key, title in section_map.items():
        content = str(sections.get(key, ""))
        completeness = 0.95 if content else 0.25
        sec = BriefSection(
            dossier_id=dossier.id,
            section_key=key,
            section_title=title,
            content=content,
            completeness=completeness,
        )
        db.add(sec)
        db.flush()

        trace_items = traces.get(key, []) if isinstance(traces, dict) else []
        if isinstance(trace_items, list):
            for t in trace_items[:6]:
                db.add(
                    SourceTrace(
                        section_id=sec.id,
                        source_text=str(t),
                        rationale=f"Linked from {key} section generation",
                        confidence=0.74,
                    )
                )

    db.add(
        ArtifactEvent(
            dossier_id=dossier.id,
            status=payload.status,
            note="Dossier saved from studio distillation flow",
            metadata_json={"readiness_score": float(distilled.get("score", 0.0))},
        )
    )

    db.commit()
    db.refresh(dossier)

    return {
        "id": dossier.id,
        "title": dossier.title,
        "status": dossier.status,
        "score": dossier.readiness_score,
        "saved_at": dossier.created_at.isoformat(),
    }


@router.get("/dossiers")
@router.get("/dossiers")
def list_dossiers(limit: Optional[int] = 20, db: Session = Depends(get_db)):
    rows = db.query(Dossier).order_by(Dossier.created_at.desc()).limit(max(1, min(limit or 20, 50))).all()
    items = []
    for d in rows:
        items.append(
            {
                "id": d.id,
                "title": d.title,
                "status": d.status,
                "score": d.readiness_score,
                "created_at": d.created_at.isoformat() if d.created_at else None,
                "updated_at": d.updated_at.isoformat() if d.updated_at else None,
            }
        )
    return {"items": items}
