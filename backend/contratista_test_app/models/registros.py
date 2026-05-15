from django.db import models

from .admin import Holding, Sociedad
from .personal import Supervisores
from .contratos import ContratoTrabajador


class RegistroCharlaSupervisor(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    sociedad = models.ForeignKey(Sociedad, on_delete=models.SET_NULL, null=True, blank=True)
    supervisor = models.ForeignKey(Supervisores, on_delete=models.SET_NULL, null=True, blank=True)
    contrato = models.ForeignKey(ContratoTrabajador, on_delete=models.CASCADE)

    class Meta:
        db_table = 'registro_charla'
        constraints = [
            models.UniqueConstraint(fields=['contrato'], name='uniq_registro_charla_contrato')
        ]

    def __str__(self):
        trabajador = None
        if self.contrato_id and getattr(self.contrato, 'trabajador', None):
            trabajador = f'{self.contrato.trabajador.nombres} {self.contrato.trabajador.apellidos or ""}'.strip()
        supervisor = 'Sin supervisor'
        if self.supervisor_id and self.supervisor.usuario_id:
            supervisor = self.supervisor.usuario.rut
        return f'Charla contrato {self.contrato_id} - {trabajador or "Sin trabajador"} - {supervisor}'
