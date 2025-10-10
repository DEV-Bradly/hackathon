import functools
from typing import Callable, Optional
from django.http import JsonResponse, HttpRequest
from landdeg_backend.firebase_config import verify_id_token


def firebase_login_required(view_func: Callable):
    """Decorator that enforces Firebase ID token authentication.

    Expects the client to send an Authorization header: "Bearer <ID_TOKEN>".
    On success, attaches `request.firebase_user` dict with uid and claims.
    """

    @functools.wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        auth_header: Optional[str] = request.headers.get("Authorization")
        if not auth_header or not auth_header.lower().startswith("bearer "):
            return JsonResponse({"error": "Missing Authorization Bearer token"}, status=401)
        id_token = auth_header.split(" ", 1)[1].strip()
        try:
            decoded = verify_id_token(id_token)
        except Exception as exc:  # noqa: BLE001 broad but OK for boundary
            return JsonResponse({"error": "Invalid token", "detail": str(exc)}, status=401)

        request.firebase_user = decoded  # type: ignore[attr-defined]
        return view_func(request, *args, **kwargs)

    return _wrapped
