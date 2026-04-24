from django.db import models
from .sii import CuentaOrigen
from .personal import PersonalTrabajadores
from ..utils import validate_image_format
from .auth import Usuarios
from .admin import (
    Holding,
    Sociedad,
)


class EmpresasTransporte(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    rut = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    comuna = models.CharField(max_length=255, blank=True, null=True)
    metodo_pago = models.CharField(max_length=50, blank=True, null=True)
    banco = models.ForeignKey('Banco', on_delete=models.SET_NULL, blank=True, null=True)
    tipo_cuenta = models.CharField(max_length=50, blank=True, null=True)
    numero_cuenta = models.CharField(max_length=50, blank=True, null=True)
    emite_factura = models.BooleanField(default=False, null=True)
    alias = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'empresas_transporte'


class VehiculosTransporte(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    empresa = models.ForeignKey(EmpresasTransporte, on_delete=models.CASCADE)
    ppu = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    year = models.IntegerField()
    color = models.CharField(max_length=100)
    num_pasajeros = models.IntegerField()
    marca = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'vehiculos_transporte'


class DocumentosVehiculo(models.Model):
    TIPOS_DOCUMENTO = [
        ('documentos_varios', 'Documentos Varios'),
    ]

    vehiculo = models.ForeignKey(VehiculosTransporte, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=50, choices=TIPOS_DOCUMENTO, default='documentos_varios')
    documentos_rutas = models.JSONField(default=list, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documentos_vehiculo'

    def __str__(self):
        return f"{self.vehiculo.ppu} - {self.tipo}"


class ChoferesTransporte(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    empresa = models.ForeignKey(EmpresasTransporte, on_delete=models.CASCADE)
    vehiculo = models.ForeignKey(VehiculosTransporte, on_delete=models.SET_NULL, null=True)
    nombre = models.CharField(max_length=255)
    rut = models.CharField(max_length=255, unique=True)
    licencia = models.CharField(max_length=20)

    class Meta:
        db_table = 'choferes'


class DocumentosChofer(models.Model):
    TIPOS_IMAGEN = [
        ('foto_licencia_frontal', 'Licencia Frontal'),
        ('foto_licencia_trasera', 'Licencia Trasera'),
        ('foto_cedula_frontal', 'Carnet Frontal'),
        ('foto_cedula_trasera', 'Carnet Trasero'),
    ]
    TIPOS_DOCUMENTO = [
        ('documentos_varios', 'Documentos Varios'),
    ]
    TIPO_CHOICES = TIPOS_IMAGEN + TIPOS_DOCUMENTO

    chofer = models.ForeignKey(ChoferesTransporte, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    imagen = models.ImageField(
        upload_to='transporte/archivos_choferes/imagenes/',
        null=True,
        blank=True,
        validators=[validate_image_format]
    )
    documentos_rutas = models.JSONField(default=list, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documentos_chofer'

    def __str__(self):
        return f"{self.chofer.nombre} - {self.tipo}"


class TrabajadorTransporteHistorial(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.CASCADE, related_name='historial_transporte')
    transportista = models.ForeignKey(EmpresasTransporte, on_delete=models.SET_NULL, null=True, blank=True)
    vehiculo = models.ForeignKey(VehiculosTransporte, on_delete=models.SET_NULL, null=True, blank=True)
    chofer = models.ForeignKey(ChoferesTransporte, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'trabajador_transporte_historial'
        indexes = [
            models.Index(fields=['trabajador', 'fecha_inicio', 'fecha_fin']),
            models.Index(fields=['transportista', 'fecha_inicio']),
        ]


class Tramos(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE, null=True)
    origen = models.TextField()
    destino = models.TextField()
    comentario = models.TextField()
    TIPO_CHOICES = [
        ('PASAJERO', 'Pasajero'),
        ('VIAJE', 'Viaje')
    ]
    unidad_pago = models.CharField(max_length=10, choices=TIPO_CHOICES, null=True, blank=True)

    class Meta:
        db_table = 'tramos_transportista'


class FolioTransportista(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    folio_comercial = models.ForeignKey('FolioComercial', on_delete=models.SET_NULL, null=True, blank=True)
    valor_cancelacion = models.IntegerField(null=True)
    tramo = models.ForeignKey(Tramos, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'folios_transportes'


class PagoTransportista(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    sociedad = models.ForeignKey(Sociedad, on_delete=models.CASCADE)
    transportista = models.ForeignKey(EmpresasTransporte, on_delete=models.CASCADE)
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField()
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=20, choices=[
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia')
    ])
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    cuenta_origen = models.ForeignKey(CuentaOrigen, on_delete=models.SET_NULL, null=True)
    usuario_registra = models.ForeignKey(Usuarios, on_delete=models.SET_NULL, null=True)
    total_personas = models.IntegerField(help_text="Total de personas transportadas en el período")
    total_dias = models.IntegerField(help_text="Total de días con servicio en el período")
    valor_por_unidad = models.DecimalField(max_digits=10, decimal_places=2,
                                           help_text="Valor por persona o por viaje según corresponda")
    tipo_pago = models.CharField(max_length=10, choices=[
        ('PASAJERO', 'Por Pasajero'),
        ('VIAJE', 'Por Viaje')
    ])

    class Meta:
        db_table = 'pagos_transportista'

    def __str__(self):
        return f"Pago a {self.transportista.nombre} - {self.fecha_desde} a {self.fecha_hasta}"


class DetallePagoTransportista(models.Model):
    id = models.AutoField(primary_key=True)
    pago = models.ForeignKey(PagoTransportista, on_delete=models.CASCADE, related_name='detalles')
    fecha = models.DateField()
    cantidad_personas = models.IntegerField()
    monto_dia = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'detalle_pagos_transportista'

    def __str__(self):
        return f"Detalle pago {self.pago.id} - {self.fecha}"