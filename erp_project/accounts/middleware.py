import json
from .utils import log_action

class AuditLogMiddleware:
    """Log every authenticated request with JSON details."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            details = {
                "method": request.method,
                "path": request.path,
                "GET": request.GET.dict(),
                "POST": {
                    k: v for k, v in request.POST.items()
                    if k.lower() not in [
                        "password",
                        "password1",
                        "password2",
                        "current_password",
                        "csrfmiddlewaretoken",
                    ]
                },
            }
            log_action(user, "request", details=details)
        return response
