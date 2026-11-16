from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class RegistrationForm(UserCreationForm):
    """
    Registration form for AmbagLedger (F-01).
    Validates required fields, unique email (BR-01), role choice (BR-02),
    optional contact number, and matching password confirmation.
    """

    full_name = forms.CharField(
        max_length=100,
        required=True,
        label='Full Name',
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., Juan Dela Cruz',
            'class': 'form-control',
        }),
    )
    email = forms.EmailField(
        max_length=100,
        required=True,
        label='Institutional Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'e.g., juan.delacruz@cit.edu',
            'class': 'form-control',
        }),
    )
    contact_number = forms.CharField(
        max_length=20,
        required=False,
        label='Contact Number (Optional)',
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., 09171234567',
            'class': 'form-control',
        }),
    )
    role = forms.ChoiceField(
        choices=CustomUser.Role.choices,
        initial=CustomUser.Role.MEMBER,
        required=True,
        label='Account Role',
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('full_name', 'email', 'contact_number', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Password'
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Create a strong password',
            'class': 'form-control',
        })
        self.fields['password2'].label = 'Confirm Password'
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Re-enter your password',
            'class': 'form-control',
        })

    def clean_email(self):
        """Enforces BR-01: case-insensitive email uniqueness."""
        email = self.cleaned_data.get('email', '').strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email address already exists.')
        return email

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if not full_name:
            raise forms.ValidationError('Full name is required.')
        return full_name

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number', '').strip()
        return contact_number or None


class LoginForm(forms.Form):
    """
    Credential login form for AmbagLedger (F-01).
    Authenticates users via email and password.
    """

    email = forms.EmailField(
        max_length=100,
        required=True,
        label='Institutional Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'e.g., juan.delacruz@cit.edu',
            'class': 'form-control',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        required=True,
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'form-control',
        }),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            normalized_email = email.strip().lower()
            self.user_cache = authenticate(
                self.request,
                email=normalized_email,
                password=password,
            )
            if self.user_cache is None:
                raise forms.ValidationError('Invalid email address or password.')
            if not self.user_cache.is_active:
                raise forms.ValidationError('This account is inactive.')

        return cleaned_data

    def get_user(self):
        return self.user_cache


class ProfileUpdateForm(forms.ModelForm):
    """
    Allows authenticated users to update only their own profile details.
    Enforces unique email across all other users (BR-01).
    """

    full_name = forms.CharField(
        max_length=100,
        required=True,
        label='Full Name',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your full name',
            'class': 'form-control',
        }),
    )
    email = forms.EmailField(
        max_length=100,
        required=True,
        label='Institutional Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your institutional email',
            'class': 'form-control',
        }),
    )
    contact_number = forms.CharField(
        max_length=20,
        required=False,
        label='Contact Number (Optional)',
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., 09171234567',
            'class': 'form-control',
        }),
    )

    class Meta:
        model = CustomUser
        fields = ('full_name', 'email', 'contact_number')

    def clean_email(self):
        """Enforces BR-01 while allowing the current user to retain their existing email."""
        email = self.cleaned_data.get('email', '').strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Another account is already registered with this email address.')
        return email

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if not full_name:
            raise forms.ValidationError('Full name is required.')
        return full_name

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number', '').strip()
        return contact_number or None