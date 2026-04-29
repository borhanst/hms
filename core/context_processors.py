from .permissions import get_sidebar_sections


def sidebar(request):
    if not request.user.is_authenticated:
        return {"sidebar_sections": []}
    return {"sidebar_sections": get_sidebar_sections(request.user)}
