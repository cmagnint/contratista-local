from django.db import models
from .parametros import Horarios, Labores
from .transporte import EmpresasTransporte, VehiculosTransporte

from .clientes import (
    Clientes,
    CamposClientes,
)
from .admin import Holding


class FolioComercial(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Clientes, on_delete=models.SET_NULL, null=True)
    fundos = models.ManyToManyField(CamposClientes, blank=True)
    labores = models.ManyToManyField(Labores, through='FolioComercialLabor', blank=True)
    transportistas = models.ManyToManyField(EmpresasTransporte, related_name='transportistas_folio', blank=True)
    vehiculos = models.ManyToManyField(VehiculosTransporte, related_name='vehiculos_folio', blank=True)
    horarios = models.ManyToManyField(Horarios, related_name='folios', blank=True)
    fecha_inicio_contrato = models.DateField()
    fecha_termino_contrato = models.DateField()
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'folio_comercial'

class FolioComercialLabor(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE) 
    folio = models.ForeignKey(FolioComercial, on_delete=models.CASCADE)
    labor = models.ForeignKey(Labores, on_delete=models.CASCADE)
    valor_pago_trabajador = models.IntegerField()
    valor_facturacion = models.IntegerField()
    
    class Meta:
        db_table = 'fc_labor_pago'

class HistorialCambioFolio(models.Model):
    """
    Tracks the history of changes to a folio's payment value
    """
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    folio = models.ForeignKey(FolioComercial, on_delete=models.CASCADE)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    valor_anterior = models.IntegerField()
    valor_nuevo = models.IntegerField()
    version = models.IntegerField()  # Tracks the change sequence
    fecha_inicio_validez = models.DateField()
    fecha_fin_validez = models.DateField()
    
    class Meta:
        db_table = 'historial_cambios_folio'
