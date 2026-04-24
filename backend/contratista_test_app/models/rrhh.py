from django.db import models
from .admin import (
    Holding,
)


class SaludTrabajadores(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    codigo = models.IntegerField(null=True)
    nombre = models.CharField(max_length=255)
    porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=7.0,
        help_text="Porcentaje de descuento salud (7% para la mayoría, puede variar)"
    )

    class Meta:
        db_table = 'salud'
        unique_together = [['holding', 'codigo']]

    def __str__(self):
        return f"{self.codigo:02d} - {self.nombre}"


class AFPTrabajadores(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    codigo = models.IntegerField(null=True)
    nombre = models.CharField(max_length=255)
    porcentaje_cotizacion_individual = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.0,
        help_text="% Cotización Individual del trabajador"
    )
    comision_afp = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.58,
        help_text="Comisión AFP %"
    )
    porcentaje_cargo_empleador = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.1,
        help_text="% Cargo Empleador"
    )
    porcentaje_seguro_social = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.9,
        help_text="% Seguro Social"
    )

    class Meta:
        db_table = 'afp'
        unique_together = [['holding', 'codigo']]

    def __str__(self):
        return f"{self.codigo:02d} - {self.nombre}"


class IpsRegimen(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=10)
    glosa = models.CharField(max_length=255)

    class Meta:
        db_table = 'ips_regimenes'

    def __str__(self):
        return f"{self.codigo} - {self.glosa}"


class ProformaTransportista(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey('Holding', on_delete=models.CASCADE)
    sociedad = models.ForeignKey('Sociedad', on_delete=models.CASCADE, null=True)
    transportista = models.ForeignKey('EmpresasTransporte', on_delete=models.CASCADE)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    fecha_inicio_periodo = models.DateField(null=True)
    fecha_fin_periodo = models.DateField(null=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('EMITIDO', 'Emitido'),
            ('FACTURADO', 'Facturado')
        ],
        default='EMITIDO'
    )
    documento_pdf = models.FileField(upload_to='proformas/', null=True, blank=True)
    tramo = models.CharField(max_length=200, null=True)
    tipo_servicio = models.CharField(max_length=20, null=True)
    cantidad_personas = models.IntegerField(null=True)
    valor_pago_transportista = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    factura_fecha = models.DateField(null=True, blank=True)
    factura_numero = models.CharField(max_length=50, null=True, blank=True)
    factura_rut = models.CharField(max_length=20, null=True, blank=True)
    factura_monto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'proformas_transportista'


class DiasTrabajadosAprobados(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    trabajador = models.ForeignKey('PersonalTrabajadores', on_delete=models.CASCADE)
    mes = models.IntegerField()
    year = models.IntegerField()
    usuario_aprueba = models.ForeignKey('Usuarios', on_delete=models.SET_NULL, null=True, related_name='aprobaciones_dias')
    fecha_aprobacion = models.DateTimeField(auto_now_add=True)
    dias_por_cliente = models.JSONField(help_text="Formato: {cliente_id: dias_trabajados}")
    reducciones_aplicadas = models.JSONField(null=True, blank=True,
        help_text="Formato: {cliente_id: {porcentaje: X, diasOriginales: Y}}")
    dias_totales = models.IntegerField()
    modificado_por = models.ForeignKey('Usuarios', on_delete=models.SET_NULL, null=True, related_name='modificaciones_dias_trabajados')
    ultima_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dias_trabajados_aprobados'
        unique_together = [['trabajador', 'mes', 'year']]

    def __str__(self):
        return f"{self.trabajador.nombres} - {self.mes}/{self.year}"


class LicenciaMedica(models.Model):
    trabajador = models.ForeignKey('PersonalTrabajadores', on_delete=models.CASCADE, related_name='licencias')
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_totales = models.IntegerField()
    tipo_licencia = models.CharField(max_length=100, default='COMUN')
    numero_licencia = models.CharField(max_length=50, blank=True, null=True)
    documento = models.FileField(upload_to='licencias/', null=True, blank=True)

    class Meta:
        db_table = 'licencias_medicas'


class Vacaciones(models.Model):
    trabajador = models.ForeignKey('PersonalTrabajadores', on_delete=models.CASCADE, related_name='vacaciones')
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_habiles = models.IntegerField()
    tipo = models.CharField(max_length=50, choices=[
        ('LEGAL', 'Feriado Legal'),
        ('PROGRESIVO', 'Feriado Progresivo'),
        ('COLECTIVO', 'Feriado Colectivo')
    ])

    class Meta:
        db_table = 'vacaciones'


class MesCerrado(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    mes = models.IntegerField()
    year = models.IntegerField()
    fecha_cierre = models.DateTimeField(auto_now_add=True)
    usuario_cierre = models.ForeignKey('Usuarios', on_delete=models.SET_NULL, null=True, related_name='meses_cerrados')
    motivo = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'meses_cerrados'
        unique_together = [['holding', 'mes', 'year']]

    def __str__(self):
        return f"Mes {self.mes}/{self.year} - Holding {self.holding.nombre}"


class TipoImpuestoRenta(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=10)
    glosa = models.CharField(max_length=255)

    class Meta:
        db_table = 'tipos_impuesto_renta'


class TipoJornada(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=10)
    glosa = models.CharField(max_length=255)

    class Meta:
        db_table = 'tipos_jornada'

    def __str__(self):
        return f"{self.codigo} - {self.glosa}"


class TipoDiscapacidad(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=5)
    glosa = models.CharField(max_length=255)

    class Meta:
        db_table = 'estados_discapacidad'

    def __str__(self):
        return f"{self.codigo} - {self.glosa}"


class CCAF(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=255)

    class Meta:
        db_table = 'ccaf'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Mutualidad(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=255)

    class Meta:
        db_table = 'mutualidades'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"