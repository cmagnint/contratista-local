from django.db import models

from .admin import (
    Holding,
    Sociedad,
)

from .personal import (
    PersonalTrabajadores,
    Supervisores,
)

from .contratos import (
    ContratoTrabajador,
)

class RegistroCharlaSupervisor(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    sociedad = models.ForeignKey(Sociedad, on_delete=models.SET_NULL, null=True, blank=True)
    supervisor = models.ForeignKey(Supervisores, on_delete=models.SET_NULL, null=True, blank=True)
    contrato = models.ForeignKey(ContratoTrabajador, on_delete=models.CASCADE)

    class Meta:
        db_table = 'registro_charla'