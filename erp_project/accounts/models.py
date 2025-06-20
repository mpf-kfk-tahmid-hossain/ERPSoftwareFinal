from django.db import models
from django.contrib.auth.models import AbstractUser


class Permission(models.Model):
    """Simple permission identified by codename."""

    codename = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.codename

class Company(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    permissions = models.ManyToManyField(Permission, through='RolePermission', blank=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'role', 'company')


class AuditLog(models.Model):
    """Record significant user actions for auditing."""

    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actor_logs')
    target_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='target_logs', null=True, blank=True
    )
    request_type = models.CharField(max_length=10, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        rt = f"[{self.request_type}]" if self.request_type else ""
        return f"{self.actor} {self.action} {rt} {self.target_user or ''}".strip()


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('role', 'permission')
