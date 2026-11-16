from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class CustomUserManager(BaseUserManager):
    """Custom manager for AmbagLedger users authenticating via email."""

    def create_user(self, email, full_name, password=None, role='MEMBER', contact_number=None, **extra_fields):
        if not email:
            raise ValueError('An institutional email address is required.')
        if not full_name:
            raise ValueError('Full name is required.')

        normalized_email = self.normalize_email(email)
        user = self.model(
            email=normalized_email,
            full_name=full_name.strip(),
            role=role,
            contact_number=contact_number.strip() if contact_number else None,
            **extra_fields,
        )
        # Cryptographically hashes the raw password before saving
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', CustomUser.Role.TREASURER)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(
            email=email,
            full_name=full_name,
            password=password,
            **extra_fields,
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Maps to the 'users' entity in AmbagLedger Data Dictionary (Section 4.4).
    Supports TREASURER (administrative ledger control) and MEMBER (read-only access).
    """

    class Role(models.TextChoices):
        TREASURER = 'TREASURER', 'Treasurer'
        MEMBER = 'MEMBER', 'Member'

    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Required by Django's authentication and admin framework
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        constraints = [
            # Enforces BR-02 directly in PostgreSQL
            models.CheckConstraint(
                condition=models.Q(role__in=['TREASURER', 'MEMBER']),
                name='users_role_check',
            ),
        ]

    def __str__(self):
        return f'{self.full_name} ({self.email}) - {self.role}'

    @property
    def is_treasurer(self):
        return self.role == self.Role.TREASURER

    @property
    def is_member(self):
        return self.role == self.Role.MEMBER