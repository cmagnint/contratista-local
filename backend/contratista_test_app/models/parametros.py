from django.db import models
from django.forms import ValidationError
from django.utils import timezone
import pytz
from django.conf import settings
import os
from ..utils import generate_token, generate_token_link_apk, validate_image_format
from .admin import (
    Holding,
    Perfiles,
    Sociedad,
)
from django.contrib.postgres.fields import ArrayField


def hora_santiago():
    return timezone.now().astimezone(pytz.timezone('America/Santiago'))


class UnidadControl(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    cantidad = models.IntegerField()
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'unidad_control'


class Labores(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    unidad_control = models.ForeignKey(UnidadControl, on_delete=models.SET_NULL, null=True)
    nombre = models.CharField(max_length=255)
    especie = models.CharField(max_length=255)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'labores'


class Horarios(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    sociedad = models.ForeignKey(Sociedad, null=True, blank=True, on_delete=models.CASCADE)
    nombre = models.CharField(null=True, blank=True, max_length=100)

    lunes_inicio = models.TimeField(null=True, blank=True)
    lunes_fin = models.TimeField(null=True, blank=True)
    lunes_colacion = models.BooleanField(default=False)
    lunes_minutos_colacion = models.IntegerField(default=0)

    martes_inicio = models.TimeField(null=True, blank=True)
    martes_fin = models.TimeField(null=True, blank=True)
    martes_colacion = models.BooleanField(default=False)
    martes_minutos_colacion = models.IntegerField(default=0)

    miercoles_inicio = models.TimeField(null=True, blank=True)
    miercoles_fin = models.TimeField(null=True, blank=True)
    miercoles_colacion = models.BooleanField(default=False)
    miercoles_minutos_colacion = models.IntegerField(default=0)

    jueves_inicio = models.TimeField(null=True, blank=True)
    jueves_fin = models.TimeField(null=True, blank=True)
    jueves_colacion = models.BooleanField(default=False)
    jueves_minutos_colacion = models.IntegerField(default=0)

    viernes_inicio = models.TimeField(null=True, blank=True)
    viernes_fin = models.TimeField(null=True, blank=True)
    viernes_colacion = models.BooleanField(default=False)
    viernes_minutos_colacion = models.IntegerField(default=0)

    sabado_inicio = models.TimeField(null=True, blank=True)
    sabado_fin = models.TimeField(null=True, blank=True)
    sabado_colacion = models.BooleanField(default=False)
    sabado_minutos_colacion = models.IntegerField(default=0)

    domingo_inicio = models.TimeField(null=True, blank=True)
    domingo_fin = models.TimeField(null=True, blank=True)
    domingo_colacion = models.BooleanField(default=False)
    domingo_minutos_colacion = models.IntegerField(default=0)

    class Meta:
        db_table = 'horarios'

    def get_horas_dia(self, fecha):
        dias = {
            0: 'lunes', 1: 'martes', 2: 'miercoles',
            3: 'jueves', 4: 'viernes', 5: 'sabado', 6: 'domingo',
        }
        dia = dias.get(fecha.weekday())
        inicio = getattr(self, f'{dia}_inicio', None)
        fin = getattr(self, f'{dia}_fin', None)

        if not inicio or not fin:
            return 0.0

        from datetime import datetime
        dt_inicio = datetime.combine(fecha, inicio)
        dt_fin = datetime.combine(fecha, fin)
        diferencia = (dt_fin - dt_inicio).total_seconds() / 3600

        if getattr(self, f'{dia}_colacion', False):
            minutos_colacion = getattr(self, f'{dia}_minutos_colacion', 0)
            diferencia -= minutos_colacion / 60

        return max(diferencia, 0.0)


class CasasTrabajadores(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    nombre = models.TextField()
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'casas'


class Region(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=255)

    class Meta:
        db_table = 'regiones'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Comuna(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=255)
    region = models.ForeignKey('Region', on_delete=models.CASCADE, related_name='comunas')

    class Meta:
        db_table = 'comunas'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class CodigoQR(models.Model):
    id = models.AutoField(primary_key=True)
    trabajador = models.ForeignKey('PersonalTrabajadores', on_delete=models.CASCADE)
    codigo_qr = models.TextField()

    class Meta:
        db_table = 'asociacion_codigo_qr'


class Haberes(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    imponible = models.BooleanField(default=False)
    orden = models.IntegerField(default=0)
    TIPO_VALOR_CHOICES = [
        ('CANTIDAD', 'Cantidad'),
        ('MONTO', 'Monto Fijo')
    ]
    tipo_valor = models.CharField(max_length=10, choices=TIPO_VALOR_CHOICES, default='MONTO')
    cuenta_contable_1 = models.CharField(max_length=50, blank=True, null=True)
    cuenta_contable_2 = models.CharField(max_length=50, blank=True, null=True)
    ubicacion_liquidacion = models.CharField(max_length=50, blank=True, null=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'haberes'
        unique_together = [['holding', 'nombre']]

    def __str__(self):
        return f"{self.id} - {self.nombre}"


class Descuentos(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    orden = models.IntegerField(default=0)
    cuota = models.BooleanField(blank=True, null=True)
    cuenta_contable = models.CharField(max_length=50, blank=True, null=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'descuentos'
        unique_together = [['holding', 'nombre']]

    def __str__(self):
        return f"{self.id} - {self.nombre}"


class EnlaceAutoRegistro(models.Model):
    id = models.AutoField(primary_key=True)
    token = models.CharField(max_length=16, default=generate_token, unique=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    perfil = models.ForeignKey(Perfiles, on_delete=models.CASCADE)
    usuario_creador = models.ForeignKey('Usuarios', on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    ruts_permitidos = ArrayField(models.TextField(), blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'enlaces_auto_registro'

    def is_valid(self):
        ahora = timezone.now()
        return self.activo and ahora <= self.fecha_expiracion

    def tiempo_restante(self):
        if not self.is_valid():
            return 0
        diferencia = self.fecha_expiracion - timezone.now()
        return max(0, diferencia.total_seconds() / 3600)

    def is_rut_allowed(self, rut):
        if not self.ruts_permitidos:
            return True
        return rut in self.ruts_permitidos

    def get_full_url(self):
        base_url = "http://localhost:4200/arl"
        return f"{base_url}/{self.token}/{self.id}"


class APKLink(models.Model):
    APK_NAME = 'contratista_testing.apk'
    APK_FOLDER = 'apk'

    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey('Holding', on_delete=models.CASCADE)
    token = models.CharField(
        max_length=32,
        default=generate_token_link_apk,
        unique=True,
        help_text="Token único para acceder al enlace de descarga"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    activo = models.BooleanField(default=True)
    usuario_creador = models.ForeignKey(
        'Usuarios',
        on_delete=models.SET_NULL,
        null=True,
        help_text="Usuario que creó el enlace de descarga"
    )

    class Meta:
        db_table = 'apk_links'
        verbose_name = 'Enlace APK'
        verbose_name_plural = 'Enlaces APK'

    @classmethod
    def get_apk_path(cls):
        return os.path.join(settings.BASE_DIR, cls.APK_FOLDER, cls.APK_NAME)

    def is_valid(self):
        if not self.activo or timezone.now() >= self.fecha_expiracion:
            return False
        return os.path.exists(self.get_apk_path())

    def tiempo_restante(self):
        if not self.is_valid():
            return 0
        diferencia = self.fecha_expiracion - timezone.now()
        return max(0, diferencia.total_seconds() / 3600)

    def get_full_url(self):
        base_url = "http://localhost:4200/apk-link"
        return f"{base_url}/{self.token}/{self.id}"

    def save(self, *args, **kwargs):
        if self.activo:
            if not os.path.exists(self.get_apk_path()):
                raise ValidationError(
                    f"El archivo APK no existe en la ruta: {self.get_apk_path()}"
                )
            APKLink.objects.filter(
                holding=self.holding,
                activo=True
            ).exclude(id=self.id).update(activo=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Enlace APK para {self.holding} - {'Activo' if self.activo else 'Inactivo'}"

class ElementoSeguridad(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    elemento = models.TextField()
    cantidad = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'elemento_seguridad'
        unique_together = [['holding', 'elemento']]