from django.db import models
from .clientes import CamposClientes, Clientes
from .comercial import FolioComercial
from .rrhh import (
    TipoDiscapacidad, TipoImpuestoRenta, TipoJornada
)
from .parametros import (
    Horarios,
    Labores,
    Region,
    Comuna,
)
from .admin import Holding
from .personal import PersonalTrabajadores

class ContratoVariables(models.Model):
    TIPO_CHOICES = [
        ('CHILENO', 'Contrato Chileno'),
        ('EXTRANJERO', 'Contrato Extranjero'),
    ]
    
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255, help_text="Nombre del formato de contrato")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='CHILENO')
    archivo_pdf = models.FileField(upload_to='contracts/formats') 
    variables = models.JSONField(help_text="JSON con todas las variables y sus posiciones")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True, help_text="Indica si este formato está activo")
    
    class Meta:
        db_table = 'documentos_variables'
        
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
        
    def get_file_name(self):
        """Genera el nombre de archivo estandarizado"""
        slug_nombre = self.nombre.lower().replace(' ', '_')
        return f"{slug_nombre}.pdf"

class CausalFiniquito(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=10)
    glosa = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'causales_finiquito'
        
    def __str__(self):
        return f"{self.codigo} - {self.glosa}"

class ContratoTrabajador(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de firma'),
        ('FIRMADO', 'Firmado'),
        ('TERMINADO', 'Terminado'),
        ('ANULADO', 'Anulado')
    ]
    
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.CASCADE, related_name='contratos')
    documento = models.ForeignKey(ContratoVariables, on_delete=models.SET_NULL, null=True)
    # Fechas del contrato
    fecha_inicio_contrato = models.DateField()
    fecha_termino_contrato = models.DateField(null=True, blank=True)
    # Causal de finiquito
    causal_finiquito = models.ForeignKey(CausalFiniquito, on_delete=models.SET_NULL, null=True, blank=True)
    # Región de prestación de servicios
    region_prestacion_servicios = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    comuna_prestacion_servicios = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, blank=True)
    # Tipo de impuesto a la renta
    tipo_impuesto_renta = models.ForeignKey(TipoImpuestoRenta, on_delete=models.SET_NULL, null=True, blank=True)
    # Tipo de jornada (cod 1107)
    tipo_jornada = models.ForeignKey(TipoJornada, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de jornada")
    # Persona con discapacidad/pensionado por invalidez (cod 1108)
    tipo_discapacidad = models.ForeignKey(TipoDiscapacidad, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Persona con discapacidad/pensionado por invalidez")
    # Campos relacionados
    labor = models.ForeignKey(Labores, on_delete=models.SET_NULL, null=True, blank=True)
    folio_comercial = models.ForeignKey(FolioComercial, on_delete=models.SET_NULL, null=True, blank=True)
    horario = models.ForeignKey(
        Horarios, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Horario asignado",
    )
    fundo = models.ForeignKey(CamposClientes, on_delete=models.SET_NULL, null=True, blank=True)
    cliente = models.ForeignKey(Clientes, on_delete=models.SET_NULL, null=True, blank=True)
    contrato_generado = models.BooleanField(default=False)
    class Meta:
        db_table = 'contratos_trabajadores'


class FirmaOrganizacion(models.Model):
    TIPO_CHOICES = [
        ('firma', 'Firma'),
        ('huella', 'Huella'),
    ]
    
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE, related_name='firmas_organizacion')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='firmas_organizacion/')
    
    class Meta:
        db_table = 'firmas_organizacion'
        unique_together = [['holding', 'tipo', 'nombre']]

class ContratoHorarioSnapshot(models.Model):
    contrato = models.OneToOneField(ContratoTrabajador, on_delete=models.CASCADE, related_name='horario_snapshot')
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.CASCADE, related_name='horario_snapshots')
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE, related_name='horario_snapshots')
    datos = models.JSONField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contrato_horario'


class HoraExtraordinaria(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.CASCADE)
    fecha = models.DateField()  # Fecha en que se realizaron las horas extras
    cantidad_horas = models.DecimalField(max_digits=5, decimal_places=2)  # Permite fracciones de hora
    fecha_ingreso = models.DateTimeField(auto_now_add=True)  # Registro automático
    
    class Meta:
        db_table = 'horas_extraordinarias'
        indexes = [
            models.Index(fields=['trabajador', 'fecha']),  # Optimiza consultas por trabajador y fecha
        ]

class Parametro(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    formato = models.ForeignKey(
        ContratoVariables,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='parametros'
    )

    class Meta:
        db_table = 'parametros_contrato'

    def __str__(self):
        return self.nombre


class ContratoAsociadoTrabajador(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    trabajador = models.ForeignKey(
        PersonalTrabajadores,
        on_delete=models.CASCADE,
        related_name='contratos_asociados'
    )
    parametro = models.ForeignKey(
        Parametro,
        on_delete=models.CASCADE,
        related_name='contratos_asociados'
    )
    archivo_pdf = models.FileField(upload_to='contratos_asociados/')
    orden = models.PositiveIntegerField()
    fecha_subida = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    class Meta:
        db_table = 'contratos_asociados_trabajador'
        ordering = ['orden']
        unique_together = [['trabajador', 'parametro', 'orden']]

    def __str__(self):
        return f"{self.trabajador} → {self.parametro.nombre} (orden {self.orden})"

