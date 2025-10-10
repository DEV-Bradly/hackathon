import json
from datetime import datetime
from typing import Any, Dict, List

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt

from .auth import firebase_login_required
from landdeg_backend.firebase_config import get_firestore_client


def health(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok", "time": datetime.utcnow().isoformat() + "Z"})


@firebase_login_required
def current_user(request: HttpRequest) -> JsonResponse:
    user = getattr(request, "firebase_user", {})
    return JsonResponse({"user": {"uid": user.get("uid"), "email": user.get("email")}})


@csrf_exempt
@firebase_login_required
def analyze_land_issue(request: HttpRequest) -> JsonResponse:
    """Analyze land degradation context and return an AI-driven plan.

    Request JSON:
    {
      "location": "lat,lon or name",
      "observations": "free text",
      "goals": ["soil health", "reforestation"],
      "data": {"ndvi": 0.42, "rainfall": 10.3}
    }

    This demo returns a deterministic, explainable plan without calling paid LLMs.
    You can swap the body of `generate_action_plan` with OpenAI/Claude later.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    location = payload.get("location") or "unspecified location"
    observations = payload.get("observations") or ""
    goals: List[str] = payload.get("goals") or []
    data: Dict[str, Any] = payload.get("data") or {}

    plan = generate_action_plan(location=location, goals=goals, observations=observations, data=data)

    # Persist a record in Firestore for the user
    user = getattr(request, "firebase_user", {})
    uid = user.get("uid") or "anonymous"
    db = get_firestore_client()
    doc_ref = db.collection("analyses").document()
    doc_ref.set({
        "uid": uid,
        "location": location,
        "observations": observations,
        "goals": goals,
        "data": data,
        "plan": plan,
        "createdAt": datetime.utcnow(),
    })

    return JsonResponse({"plan": plan, "id": doc_ref.id})


def generate_action_plan(location: str, goals: List[str], observations: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Very simple rules-based generator to emulate AI output.

    Replace with a call to your preferred LLM provider or a custom model.
    """
    ndvi = data.get("ndvi")
    rainfall = data.get("rainfall")

    diagnostics: List[str] = []
    if ndvi is not None:
        if ndvi < 0.2:
            diagnostics.append("Severe vegetation stress detected (NDVI < 0.2)")
        elif ndvi < 0.4:
            diagnostics.append("Moderate vegetation stress (NDVI 0.2–0.4)")
        else:
            diagnostics.append("Healthy vegetation cover (NDVI >= 0.4)")
    if rainfall is not None:
        if rainfall < 20:
            diagnostics.append("Low rainfall; consider drought-resilient crops and mulching")
        elif rainfall > 200:
            diagnostics.append("High rainfall; plan for erosion control and drainage")

    prioritized_goals = goals or ["soil health", "sustainable agriculture", "reforestation"]

    actions: List[str] = []
    if "soil health" in prioritized_goals:
        actions += [
            "Conduct soil organic matter test; target >3%",
            "Apply compost and biochar to improve structure",
            "Adopt minimal tillage and cover crops",
        ]
    if "sustainable agriculture" in prioritized_goals:
        actions += [
            "Introduce crop rotation with legumes",
            "Implement drip irrigation to reduce water loss",
            "Deploy integrated pest management",
        ]
    if "reforestation" in prioritized_goals:
        actions += [
            "Identify native species for assisted natural regeneration",
            "Establish contour hedgerows to reduce erosion",
            "Plan community-led tree nursery",
        ]

    if ndvi is not None and ndvi < 0.2:
        actions.append("Prioritize erosion barriers and ground cover within 4 weeks")
    if rainfall is not None and rainfall < 20:
        actions.append("Schedule rainwater harvesting and soil mulching before next dry spell")

    return {
        "location": location,
        "observations": observations,
        "diagnostics": diagnostics,
        "goals": prioritized_goals,
        "actions": actions,
        "kpis": [
            "NDVI +0.1 within 6 months",
            "Soil organic matter +0.5% within 12 months",
            "Survival rate of new trees >80%",
        ],
    }


@firebase_login_required
def projects(request: HttpRequest) -> JsonResponse:
    """List previous analyses for the authenticated user from Firestore."""
    user = getattr(request, "firebase_user", {})
    uid = user.get("uid")
    if not uid:
        return JsonResponse({"items": []})

    db = get_firestore_client()
    q = db.collection("analyses").where("uid", "==", uid).order_by("createdAt", direction=firestore.Query.DESCENDING)  # type: ignore[name-defined]
    items = []
    for doc in q.stream():
        d = doc.to_dict()
        d["id"] = doc.id
        # Convert timestamps to ISO strings for JSON
        if "createdAt" in d and hasattr(d["createdAt"], "isoformat"):
            d["createdAt"] = d["createdAt"].isoformat()
        items.append(d)

    return JsonResponse({"items": items})


@firebase_login_required
def agromet_snapshot(request: HttpRequest) -> JsonResponse:
    """Return a mock agro-meteorological snapshot.

    Swap this to call real APIs (e.g., Copernicus, NASA POWER, Open-Meteo).
    """
    data = {
        "temperatureC": 26.4,
        "rainfallMm": 12.8,
        "soilMoisture": 0.21,
        "ndvi": 0.36,
    }
    return JsonResponse({"agromet": data})
