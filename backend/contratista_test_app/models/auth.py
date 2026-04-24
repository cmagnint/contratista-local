from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from .admin import (
    Holding,
    Sociedad,
    Perfiles,
)


class CustomUserManager(BaseUserManager):
    def create_user(self, rut, email=None, password=None, **extra_fields):
        if not rut:
            raise ValueError('El usuario es obligatorio')
        if email:
            email = self.normalize_email(email)
            extra_fields.setdefault('email', email)
        rut = self.model(rut=rut, **extra_fields)
        rut.set_password(password)
        rut.save(using=self._db)
        return rut

    def create_superuser(self, rut, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(rut, email, password, **extra_fields)


class Developer(models.Model):
    id = models.AutoField(primary_key=True)
    version_movil = models.TextField()

    class Meta:
        db_table = 'developer'


class Usuarios(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE, null=True, blank=True)
    empresas_asignadas = models.ManyToManyField(Sociedad, blank=True)
    persona = models.ForeignKey('PersonalTrabajadores', on_delete=models.CASCADE, null=True, blank=True)
    rut = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    codigo = models.CharField(max_length=50, blank=True, null=True)
    codigo_expiracion = models.DateTimeField(blank=True, null=True)
    perfil = models.ForeignKey(Perfiles, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'rut'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'usuarios'