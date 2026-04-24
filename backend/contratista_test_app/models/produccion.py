from django.utils import timezone
from django.db import models
from .parametros import CasasTrabajadores, Labores, UnidadControl
from .auth import Usuarios
from .admin import (
    Holding,
    Sociedad,
)
from .personal import (
    PersonalTrabajadores,
    Supervisores,
)


class RegistroIngreso(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    movimiento_cartola = models.ForeignKey('CartolaMovimiento', on_delete=models.CASCADE)
    factura_venta = models.ForeignKey('FacturaVentaSIIDistribuida', on_delete=models.CASCADE)
    monto_distribuido = models.DecimalField(max_digits=15, decimal_places=2)
    porcentaje_neto = models.DecimalField(max_digits=5, decimal_places=2)
    porcentaje_iva = models.DecimalField(max_digits=5, decimal_places=2)
    monto_neto_cubierto = models.DecimalField(max_digits=15, decimal_places=2)
    monto_iva_cubierto = models.DecimalField(max_digits=15, decimal_places=2)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    usuario_registro = models.ForeignKey(Usuarios, on_delete=models.PROTECT)

    class Meta:
        db_table = 'registro_ingreso'

    def __str__(self):
        return f"Ingreso ${self.monto_distribuido} - Factura {self.factura_venta.numero}"

    def save(self, *args, **kwargs):
        self.monto_neto_cubierto = (self.monto_distribuido * self.porcentaje_neto) / 100
        self.monto_iva_cubierto = (self.monto_distribuido * self.porcentaje_iva) / 100
        super().save(*args, **kwargs)


class RegistroEgreso(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    movimiento_cartola = models.ForeignKey('CartolaMovimiento', on_delete=models.CASCADE)
    factura_compra = models.ForeignKey('FacturaCompraSIIDistribuida', on_delete=models.CASCADE)
    monto_distribuido = models.DecimalField(max_digits=15, decimal_places=2)
    porcentaje_neto = models.DecimalField(max_digits=5, decimal_places=2)
    porcentaje_iva = models.DecimalField(max_digits=5, decimal_places=2)
    monto_neto_cubierto = models.DecimalField(max_digits=15, decimal_places=2)
    monto_iva_cubierto = models.DecimalField(max_digits=15, decimal_places=2)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    usuario_registro = models.ForeignKey(Usuarios, on_delete=models.PROTECT)

    class Meta:
        db_table = 'registro_egreso'

    def __str__(self):
        return f"Egreso ${self.monto_distribuido} - Factura {self.factura_compra.folio}"

    def save(self, *args, **kwargs):
        self.monto_neto_cubierto = (self.monto_distribuido * self.porcentaje_neto) / 100
        self.monto_iva_cubierto = (self.monto_distribuido * self.porcentaje_iva) / 100
        super().save(*args, **kwargs)


class RegistroAsistencia(models.Model):
    ESTADO_CHOICES = [
        ('A', 'Asistente'),
        ('F', 'Falta'),
        ('PN', 'Permiso No Pagado'),
        ('PR', 'Permiso Remunerado'),
    ]

    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.CASCADE, related_name='registros_asistencia')
    supervisor = models.ForeignKey(Supervisores, on_delete=models.SET_NULL, null=True, related_name='asistencias_registradas')
    fecha_asistencia = models.DateField()
    estado = models.CharField(max_length=2, choices=ESTADO_CHOICES, default='A')
    horas_registradas = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    modificado_por = models.ForeignKey(Usuarios, on_delete=models.SET_NULL, null=True, related_name='asistencias_modificadas')
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'registro_asistencia'
        unique_together = [['trabajador', 'fecha_asistencia', 'estado']]
        indexes = [
            models.Index(fields=['trabajador', 'fecha_asistencia']),
            models.Index(fields=['holding', 'fecha_asistencia']),
        ]

    def __str__(self):
        return f"{self.trabajador.nombres} - {self.fecha_asistencia} - {self.estado}"


class RegistroManoObraPersona(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    sociedad = models.ForeignKey(Sociedad, on_delete=models.SET_NULL, null=True, blank=True)
    supervisor = models.ForeignKey(Supervisores, on_delete=models.SET_NULL, null=True, related_name='registros_mano_obra')
    fecha_ingreso = models.DateField(default=timezone.localdate)
    folio = models.ForeignKey('FolioComercial', on_delete=models.SET_NULL, null=True, blank=True)
    labor = models.ForeignKey(Labores, on_delete=models.SET_NULL, null=True, blank=True)
    unidad_control = models.ForeignKey(UnidadControl, on_delete=models.SET_NULL, null=True, blank=True)
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.SET_NULL, null=True, related_name='registros_mano_obra')
    produccion = models.DecimalField(max_digits=10, decimal_places=2)
    horas = models.DecimalField(max_digits=5, decimal_places=2)
    

    class Meta:
        db_table = 'registro_mano_obra_persona'
        indexes = [
            models.Index(fields=['trabajador', 'fecha_ingreso']),
            models.Index(fields=['holding', 'fecha_ingreso']),
        ]


class SupervisorTrabajadorHistorial(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(Supervisores, on_delete=models.CASCADE, related_name='historial_asignaciones')
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.CASCADE, related_name='historial_supervisores')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'supervisor_trabajador_historial'
        indexes = [
            models.Index(fields=['trabajador', 'fecha_inicio', 'fecha_fin']),
            models.Index(fields=['supervisor', 'fecha_inicio']),
        ]

    def __str__(self):
        return f"{self.supervisor} → {self.trabajador} ({self.fecha_inicio} / {self.fecha_fin or 'vigente'})"


class RegistroCasaTrabajador(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.CASCADE, related_name='historial_casas')
    casa = models.ForeignKey(CasasTrabajadores, on_delete=models.SET_NULL, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'registro_casa_trabajador'
        indexes = [
            models.Index(fields=['trabajador', 'fecha_inicio', 'fecha_fin']),
        ]

    def __str__(self):
        return f"{self.trabajador.nombres} → {self.casa.nombre if self.casa else 'Sin casa'} ({self.fecha_inicio} / {self.fecha_fin or 'vigente'})"

class ProduccionTrabajador(models.Model):
    ESTADO_PROFORMA_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EMITIDO', 'Emitido'),
        ('CONFIRMADO', 'Confirmado')
    ]

    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    sociedad = models.ForeignKey(Sociedad, on_delete=models.SET_NULL, null=True, blank=True)
    usuario_ingresa = models.ForeignKey(Usuarios, on_delete=models.SET_NULL, null=True, blank=True)
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.SET_NULL, null=True, blank=True)
    labor = models.ForeignKey(Labores, on_delete=models.SET_NULL, null=True, blank=True)
    unidad_control = models.ForeignKey(UnidadControl, on_delete=models.SET_NULL, null=True, blank=True)
    folio = models.ForeignKey('FolioComercial', on_delete=models.SET_NULL, null=True, blank=True)
    hora_fecha_ingreso_produccion = models.DateTimeField(null=True, blank=True)
    peso_neto = models.FloatField(null=True, blank=True)
    peso_bruto = models.FloatField(null=True, blank=True)
    unidades_control = models.IntegerField(null=True, blank=True)
    pagado = models.BooleanField(default=False)
    proforma = models.CharField(
        max_length=20,
        choices=ESTADO_PROFORMA_CHOICES,
        default='PENDIENTE'
    )

    class Meta:
        db_table = 'produccion'

    def calcular_monto_a_pagar(self) -> float:
        if self.folio and self.folio.valor_pago_trabajador:
            if self.peso_neto and self.peso_neto > 0:
                return float(self.peso_neto * self.folio.valor_pago_trabajador)
            elif self.unidades_control:
                return float(self.unidades_control * self.folio.valor_pago_trabajador)
        return 0.0

    def __str__(self):
        return f"Producción {self.id} - {self.trabajador.nombres if self.trabajador else 'Sin trabajador'}"