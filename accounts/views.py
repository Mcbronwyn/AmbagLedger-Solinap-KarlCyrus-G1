from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .forms import LoginForm, RegistrationForm


def register_view(request):
    """Handles new user registration for AmbagLedger (F-01)."""
    if request.user.is_authenticated:
        return redirect('home')

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
    """Authenticates registered users and starts an authenticated session (F-01)."""
    if request.user.is_authenticated:
        return redirect('home')

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

            return redirect('home')
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
def home_view(request):
    """
    Protected landing route verifying @login_required protection.
    In Task 4, this will dispatch users to their role-specific dashboard.
    """
    return render(request, 'base.html')