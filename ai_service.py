import json
import os
import re
from typing import Any

import httpx

DO_INFERENCE_URL = "https://inference.do-ai.run/v1/chat/completions"
DEFAULT_MODEL = os.getenv("DO_INFERENCE_MODEL", "anthropic-claude-4.6-sonnet")


def _extract_json(text: str) -> str:
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def _coerce_unstructured_payload(raw_text: str) -> dict[str, object]:
    compact = raw_text.strip()
    normalized = compact.replace("\n", ",")
    tags = [part.strip(" -•\t") for part in normalized.split(",") if part.strip(" -•\t")]
    if not tags:
        tags = ["guided plan", "saved output", "shareable insight"]
    headline = tags[0].title()
    items = []
    for index, tag in enumerate(tags[:3], start=1):
        items.append({
            "title": f"Stage {index}: {tag.title()}",
            "detail": f"Use {tag} to move the request toward a demo-ready outcome.",
            "score": min(96, 80 + index * 4),
        })
    highlights = [tag.title() for tag in tags[:3]]
    return {
        "note": "Model returned plain text instead of JSON",
        "raw": compact,
        "text": compact,
        "summary": compact or f"{headline} fallback is ready for review.",
        "tags": tags[:6],
        "items": items,
        "score": 88,
        "insights": [f"Lead with {headline} on the first screen.", "Keep one clear action visible throughout the flow."],
        "next_actions": ["Review the generated plan.", "Save the strongest output for the demo finale."],
        "highlights": highlights,
    }

def _normalize_inference_payload(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        return _coerce_unstructured_payload(str(payload))
    normalized = dict(payload)
    summary = str(normalized.get("summary") or normalized.get("note") or "AI-generated plan ready")
    raw_items = normalized.get("items")
    items: list[dict[str, object]] = []
    if isinstance(raw_items, list):
        for index, entry in enumerate(raw_items[:3], start=1):
            if isinstance(entry, dict):
                title = str(entry.get("title") or f"Stage {index}")
                detail = str(entry.get("detail") or entry.get("description") or title)
                score = float(entry.get("score") or min(96, 80 + index * 4))
            else:
                label = str(entry).strip() or f"Stage {index}"
                title = f"Stage {index}: {label.title()}"
                detail = f"Use {label} to move the request toward a demo-ready outcome."
                score = float(min(96, 80 + index * 4))
            items.append({"title": title, "detail": detail, "score": score})
    if not items:
        items = _coerce_unstructured_payload(summary).get("items", [])
    raw_insights = normalized.get("insights")
    if isinstance(raw_insights, list):
        insights = [str(entry) for entry in raw_insights if str(entry).strip()]
    elif isinstance(raw_insights, str) and raw_insights.strip():
        insights = [raw_insights.strip()]
    else:
        insights = []
    next_actions = normalized.get("next_actions")
    if isinstance(next_actions, list):
        next_actions = [str(entry) for entry in next_actions if str(entry).strip()]
    else:
        next_actions = []
    highlights = normalized.get("highlights")
    if isinstance(highlights, list):
        highlights = [str(entry) for entry in highlights if str(entry).strip()]
    else:
        highlights = []
    if not insights and not next_actions and not highlights:
        fallback = _coerce_unstructured_payload(summary)
        insights = fallback.get("insights", [])
        next_actions = fallback.get("next_actions", [])
        highlights = fallback.get("highlights", [])
    return {
        **normalized,
        "summary": summary,
        "items": items,
        "score": float(normalized.get("score") or 88),
        "insights": insights,
        "next_actions": next_actions,
        "highlights": highlights,
    }


async def _call_inference(messages: list[dict[str, str]], max_tokens: int = 512) -> dict[str, Any]:
    key = os.getenv("GRADIENT_MODEL_ACCESS_KEY") or os.getenv("DIGITALOCEAN_INFERENCE_KEY")
    if not key:
        return {
            "note": "AI is temporarily unavailable (missing inference key). Returning fallback output.",
            "fallback": True,
        }

    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "max_completion_tokens": max(256, max_tokens),
        "response_format": {"type": "json_object"},
    }

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(DO_INFERENCE_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                return {
                    "note": "AI returned no choices; using fallback output.",
                    "fallback": True,
                }
            content = choices[0].get("message", {}).get("content", "")
            extracted = _extract_json(content)
            parsed = json.loads(extracted)
            if isinstance(parsed, dict):
                return parsed
            return {
                "note": "AI response was not a JSON object; using fallback output.",
                "fallback": True,
            }
    except Exception as exc:
        return {
            "note": f"AI is temporarily unavailable ({str(exc)}). Returning fallback output.",
            "fallback": True,
        }


async def distill_brief(query: str, preferences: str) -> dict[str, Any]:
    prompt = {
        "role": "system",
        "content": (
            "You are a product-planning distillation engine. Return strict JSON object with fields: "
            "summary (string), items (array of strings), score (number), sections (object with keys "
            "problem,target_users,solution,key_features,workflow,constraints), traces (object where each "
            "section key maps to array of source snippets)."
        ),
    }
    user = {
        "role": "user",
        "content": json.dumps({"query": query, "preferences": preferences}),
    }
    ai = await _call_inference([prompt, user], max_tokens=512)
    if ai.get("fallback"):
        return {
            "summary": "Draft brief generated with fallback logic while AI service is temporarily unavailable.",
            "items": [
                "Clarify target users from source notes",
                "Define one-pass distillation workflow",
                "Prepare dossier card with status stamps",
            ],
            "score": 0.62,
            "sections": {
                "problem": "Planning starts from messy notes and lacks structure.",
                "target_users": "Students and early builders exploring product planning.",
                "solution": "A studio that turns rough notes into a traceable brief and reusable dossier.",
                "key_features": "One-pass brief distillation, source trace links, artifact shelf with status labels.",
                "workflow": "Intake -> Distill -> Review -> Save",
                "constraints": preferences or "No constraints provided.",
            },
            "traces": {
                "problem": [query[:180]],
                "target_users": ["People exploring product planning from incomplete context"],
                "solution": ["structured product planning workflow with visible outputs"],
                "key_features": ["source-to-section trace view", "saved dossiers"],
                "workflow": ["Intake, Distill, Review, Save"],
                "constraints": [preferences or "general scope"],
            },
            "note": ai.get("note", "AI fallback used."),
        }

    return {
        "summary": ai.get("summary", "Structured brief generated."),
        "items": ai.get("items", []),
        "score": float(ai.get("score", 0.7)),
        "sections": ai.get("sections", {}),
        "traces": ai.get("traces", {}),
        "note": ai.get("note", "AI distillation completed."),
    }


async def generate_insights(selection: str, context: str) -> dict[str, Any]:
    prompt = {
        "role": "system",
        "content": (
            "You are a planning reviewer. Return strict JSON object with: insights (array of strings), "
            "next_actions (array of strings), highlights (array of strings). Keep outputs specific and actionable."
        ),
    }
    user = {"role": "user", "content": json.dumps({"selection": selection, "context": context})}
    ai = await _call_inference([prompt, user], max_tokens=512)
    if ai.get("fallback"):
        return {
            "insights": [
                "Your selected section is clear but could add measurable success criteria.",
                "Trace confidence improves when source phrases are short and explicit.",
            ],
            "next_actions": [
                "Refine feature priorities into must/should/could groups.",
                "Add one reviewer-oriented risk note for credibility.",
            ],
            "highlights": [selection[:140], context[:140]],
            "note": ai.get("note", "AI fallback used."),
        }

    return {
        "insights": ai.get("insights", []),
        "next_actions": ai.get("next_actions", []),
        "highlights": ai.get("highlights", []),
        "note": ai.get("note", "AI insights generated."),
    }
