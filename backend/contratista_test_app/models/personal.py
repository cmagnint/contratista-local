from django.db import models
from .admin import (
    Holding,
    Sociedad,
    AreasAdministracion,
    CargosAdministracion,
)


class PersonalTrabajadores(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    sociedad = models.ForeignKey(Sociedad, on_delete=models.SET_NULL, null=True, blank=True)
    area = models.ForeignKey(AreasAdministracion, on_delete=models.SET_NULL, null=True, blank=True)
    cargo = models.ForeignKey(CargosAdministracion, on_delete=models.SET_NULL, null=True, blank=True)
    nombres = models.CharField(max_length=255)
    apellidos = models.TextField(null=True, blank=True)
    rut = models.TextField(null=True, blank=True, unique=True)
    dni = models.TextField(null=True, blank=True)
    nic = models.TextField(null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    afp = models.ForeignKey('AFPTrabajadores', on_delete=models.SET_NULL, null=True, blank=True)
    salud = models.ForeignKey('SaludTrabajadores', on_delete=models.SET_NULL, null=True, blank=True)
    banco = models.ForeignKey('Banco', on_delete=models.SET_NULL, null=True, blank=True)
    metodo_pago = models.TextField(null=True, blank=True)
    tipo_cuenta_bancaria = models.TextField(null=True, blank=True)
    numero_cuenta = models.IntegerField(null=True, blank=True)
    nacionalidad = models.CharField(max_length=255, blank=True, null=True)
    estado_civil = models.CharField(max_length=255, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    sexo = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=255, blank=True, null=True)
    correo = models.CharField(max_length=255, blank=True, null=True)

    carnet_front_image = models.ImageField(upload_to='carnets/', default='carnets/dni.jpg', null=True, blank=True)
    carnet_back_image = models.ImageField(upload_to='carnets/', default='carnets/dni.jpg', null=True, blank=True)
    firma = models.ImageField(upload_to='firmas/', null=True, blank=True)
    huella_digital = models.ImageField(upload_to='huellas/', null=True, blank=True)

    fecha_ingreso = models.DateField(null=True, blank=True)
    estado = models.BooleanField(default=True, null=True, blank=True)

    sueldo_base = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    pensionado_vejez = models.BooleanField(default=False)
    ips_regimen = models.ForeignKey('IpsRegimen', on_delete=models.SET_NULL, null=True, blank=True)
    afiliado_afc = models.BooleanField(default=True, verbose_name="Afiliado a AFC")
    cargas_familiares_legales = models.IntegerField(default=0)
    cargas_familiares_maternales = models.BooleanField(default=False)
    cargas_familiares_invalidez = models.IntegerField(default=0)
    subsidio_trabajador_joven = models.BooleanField(default=False)
    colacion = models.IntegerField(null=True, blank=True)
    movilizacion = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'personal'


class Supervisores(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    usuario = models.ForeignKey('Usuarios', on_delete=models.CASCADE, null=True)
    trabajadores = models.ManyToManyField(PersonalTrabajadores, related_name='supervisor_directo', blank=True)
    firma = models.ImageField(upload_to='supervisores/firmas/', null=True, blank=True)
    huella = models.ImageField(upload_to='supervisores/huellas/', null=True, blank=True)
    class Meta:
        db_table = 'supervisores'

    def __str__(self):
        return f"Supervisor: {self.usuario.rut if self.usuario else 'Sin usuario'}"


class TrabajadorHaber(models.Model):
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.CASCADE, related_name='haberes_asignados')
    haber = models.ForeignKey('Haberes', on_delete=models.CASCADE, related_name='asignaciones')
    valor = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'trabajador_haber'
        unique_together = [['trabajador', 'haber']]


class TrabajadorDescuento(models.Model):
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.CASCADE, related_name='descuentos_asignados')
    descuento = models.ForeignKey('Descuentos', on_delete=models.CASCADE, related_name='asignaciones')
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    num_cuotas = models.IntegerField(default=1)
    cuota_actual = models.IntegerField(default=1)
    valor_cuota = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'trabajador_descuento'
        unique_together = [['trabajador', 'descuento']]

    def __str__(self):
        return f"{self.trabajador.nombres} - {self.descuento.nombre}"