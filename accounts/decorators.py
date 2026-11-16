from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def treasurer_required(view_func):
    """
    Restricts view access strictly to authenticated users with role == 'TREASURER' (BR-02).
    Blocks MEMBER users with an HTTP 403 Forbidden response.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_treasurer:
            return render(
                request,
                '403.html',
                {'required_role': 'Treasurer'},
                status=403,
            )
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def member_required(view_func):
    """
    Restricts view access strictly to authenticated users with role == 'MEMBER' (BR-02).
    Blocks TREASURER users from opening member-only views with HTTP 403 Forbidden.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_member:
            return render(
                request,
                '403.html',
                {'required_role': 'Member'},
                status=403,
            )
        return view_func(request, *args, **kwargs)

    return _wrapped_view