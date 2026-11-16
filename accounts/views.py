from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import RegistrationForm


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
                f'Account created successfully for {user.full_name} ({user.get_role_display()}). You can now log in.'
            )
            return redirect('home')
        else:
            messages.error(request, 'Registration failed. Please correct the errors highlighted below.')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})