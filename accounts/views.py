from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .decorators import member_required, treasurer_required
from .forms import LoginForm, RegistrationForm


def register_view(request):
    """Handles new user registration for AmbagLedger (F-01)."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f'Account created successfully for {user.full_name} ({user.get_role_display()}). Please log in.'
            )
            return redirect('accounts:login')
        else:
            messages.error(request, 'Registration failed. Please correct the errors highlighted below.')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Authenticates registered users and routes them to their role-based dashboard (F-01)."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    next_url = request.GET.get('next') or request.POST.get('next') or ''

    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.full_name}!')

            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Login failed. Please check your credentials and try again.')
    else:
        form = LoginForm(request=request)

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


@require_POST
@login_required
def logout_view(request):
    """Terminates the active user session and redirects to the login page (F-01)."""
    logout(request)
    messages.info(request, 'You have been logged out securely.')
    return redirect('accounts:login')


@login_required
def dashboard_redirect_view(request):
    """Dispatches authenticated users to the dashboard matching their role (F-01)."""
    if request.user.is_treasurer:
        return redirect('accounts:treasurer_dashboard')
    if request.user.is_member:
        return redirect('accounts:member_dashboard')
    return render(request, '403.html', status=403)


@treasurer_required
def treasurer_dashboard_view(request):
    """Administrative dashboard for Class Treasurers / Finance Officers (F-01)."""
    return render(request, 'accounts/treasurer_dashboard.html')


@member_required
def member_dashboard_view(request):
    """Read-only transparency dashboard for Class Members / Enrolled Students (F-01, F-09)."""
    return render(request, 'accounts/member_dashboard.html')