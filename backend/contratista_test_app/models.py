from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.forms import ValidationError
from django.utils import timezone
import pytz
import os
from .utils import generate_token, generate_token_link_apk
from decimal import Decimal 

def hora_santiago():
    return timezone.now().astimezone(pytz.timezone('America/Santiago'))

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

class Holding(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)
    estado = models.BooleanField(default=True)
    class Meta:
        db_table = 'holding'

class Sociedad(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    rol_sociedad = models.CharField(max_length=255, unique=True)
    nombre = models.CharField(max_length=255)
    nombre_representante = models.CharField()
    rut_representante =  models.CharField(max_length=255, unique=True)
    comuna = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=255)
    calle = models.CharField(max_length=255)
    # CCAF (cód 1110)
    ccaf = models.ForeignKey('CCAF', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Caja de Compensación")
    # Org. Administrador Ley 16.744 (cód 1152)
    mutualidad = models.ForeignKey('Mutualidad', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Organismo administrador Ley 16.744")
    estado = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'sociedad'
        unique_together = (('holding','id'),)

class ModulosWeb(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'modulos_web'
        unique_together = ['holding', 'nombre']  # Añadir esta restricción

    def __str__(self):
        return f"{self.nombre} - {self.holding}"

class SubModulosWeb(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    modulo = models.ForeignKey(ModulosWeb, on_delete=models.CASCADE, related_name='submodulos')
    nombre = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'submodulos_web'
        unique_together = ['modulo', 'nombre', 'holding']  # Añadir 'holding' aquí

    def __str__(self):
        return f"{self.nombre} - {self.modulo}"

class ModulosMovil(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'modulos_movil'
        unique_together = ['holding', 'nombre']  # Añadir esta restricción

    def __str__(self):
        return f"{self.nombre} - {self.holding}"

class SubModulosMovil(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    modulo = models.ForeignKey(ModulosMovil, on_delete=models.CASCADE, related_name='submodulos')
    nombre = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'submodulos_movil'
        unique_together = ['modulo', 'nombre', 'holding']  # Añadir 'holding' aquí

    def __str__(self):
        return f"{self.nombre} - {self.modulo}"

class Perfiles(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE,null=True, blank=True)
    nombre_perfil = models.CharField(max_length=100)
    TIPO_CHOICES = [
        ('WEB', 'Web'),
        ('MOVIL', 'Móvil'),
        ('AMBOS', 'Ambos')
    ]
    tipo = models.CharField(max_length=5, choices=TIPO_CHOICES, null=True, blank=True)
    modulos_web = models.ManyToManyField(ModulosWeb, blank=True)
    submodulos_web = models.ManyToManyField(SubModulosWeb, blank=True)
    modulos_movil = models.ManyToManyField(ModulosMovil, blank=True)
    submodulos_movil = models.ManyToManyField(SubModulosMovil, blank=True)
    estado = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'perfiles'

class CasasTrabajadores(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    nombre = models.TextField()
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'casas'

class Clientes(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    rut =  models.CharField(max_length=255, unique=True)
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    giro = models.CharField(max_length=255)
    rut_rep_legal = models.CharField(max_length=255,null=True, blank=True)
    nombre_rep_legal = models.CharField(max_length=255,null=True, blank=True)
    direccion_rep_legal = models.CharField(max_length=255,null=True, blank=True)
  
    class Meta:
        db_table = 'clientes'

class CamposClientes(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE, null=True, blank=True)
    cliente = models.ForeignKey(Clientes, related_name='campos_clientes', on_delete=models.CASCADE)
    nombre_campo = models.CharField(max_length=255)
    direccion_campo = models.CharField(max_length=255)
    comuna_campo = models.CharField(max_length=255)

    class Meta:
        db_table = 'campos_clientes'
 
class AreasCliente(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)

    class Meta:
        db_table = 'areas_clientes'

class CargosCliente(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    area = models.ForeignKey(AreasCliente, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)

    class Meta:
        db_table = 'cargos_clientes'

class ContactosClientes(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Clientes,on_delete=models.CASCADE)
    campo_cliente = models.ForeignKey(CamposClientes,on_delete=models.SET_NULL, null=True, blank=True)
    area_cliente =  models.ForeignKey(AreasCliente, on_delete=models.SET_NULL, null=True, blank=True)
    cargo_cliente = models.ForeignKey(CargosCliente, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_contacto = models.CharField(max_length=255)
    rut_contacto = models.CharField(max_length=255, unique=True)
    telefono = models.IntegerField()
    correo = models.EmailField(unique=True)
    
    class Meta:
        db_table = 'contactos_clientes'

class Areas(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)

    class Meta:
        db_table = 'areas'

class Cargos(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    area = models.ForeignKey(Areas, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)

    class Meta:
        db_table = 'cargos'

class AreasAdministracion(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)

    class Meta:
        db_table = 'areas_administracion'

class CargosAdministracion(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    area = models.ForeignKey(AreasAdministracion, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)

    class Meta:
        db_table = 'cargos_admnistracion'

class EmpresasTransporte(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    rut = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    folio_transportista = models.ForeignKey('FolioTransportista', on_delete=models.SET_NULL, blank=True, null=True)

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

    class Meta:
        db_table = 'vehiculos_transporte'
    
class ChoferesTransporte(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    empresa = models.ForeignKey(EmpresasTransporte, on_delete=models.CASCADE)
    vehiculo = models.ForeignKey(VehiculosTransporte, on_delete=models.SET_NULL, null=True)
    nombre = models.CharField(max_length=255)
    rut =  models.CharField(max_length=255, unique=True)
    licencia = models.CharField(max_length=20)

    class Meta:
        db_table = 'choferes'

class SaludTrabajadores(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    codigo = models.IntegerField(blank=True, null=True)
    nombre = models.CharField(max_length=255)
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, default=7.0)
    
    class Meta:
        db_table = 'salud'

class AFPTrabajadores(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    codigo = models.IntegerField(blank=True, null=True)
    nombre = models.CharField(max_length=255)
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    
    class Meta:
        db_table = 'afp'

class IpsRegimen(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=10)
    glosa = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'ips_regimenes'
        
    def __str__(self):
        return f"{self.codigo} - {self.glosa}"

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

class FolioComercial(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Clientes, on_delete=models.SET_NULL, null=True)
    fundos = models.ManyToManyField(CamposClientes , blank=True)
    labores = models.ManyToManyField(Labores, blank=True)
    transportistas = models.ManyToManyField(EmpresasTransporte, related_name='transportistas_folio', blank=True)
    vehiculos = models.ManyToManyField(VehiculosTransporte, related_name='vehiculos_folio', blank=True)
    fecha_inicio_contrato = models.DateField()
    fecha_termino_contrato = models.DateField()
    valor_pago_trabajador = models.IntegerField()
    valor_facturacion = models.IntegerField()
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'folio_comercial'

class Haberes(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    imponible = models.BooleanField(default=False)
    orden = models.IntegerField(default=0)  # Orden en la liquidación
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

class Banco(models.Model):
    id = models.AutoField(primary_key=True)
    codigo_sbif = models.CharField(max_length=3, unique=True)
    nombre = models.TextField()
    
    class Meta:
        db_table = 'banco'
        ordering = ['codigo_sbif']
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo_sbif})"
    
class PersonalTrabajadores(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    sociedad = models.ForeignKey(Sociedad, on_delete=models.SET_NULL, null=True, blank=True)
    fundo = models.ForeignKey(CamposClientes, on_delete=models.SET_NULL, null=True, blank=True)
    area = models.ForeignKey(AreasAdministracion, on_delete=models.SET_NULL, null=True, blank=True)
    cargo = models.ForeignKey(CargosAdministracion, on_delete=models.SET_NULL, null=True, blank=True)
    afp = models.ForeignKey(AFPTrabajadores, on_delete=models.SET_NULL, null=True, blank=True)
    salud = models.ForeignKey(SaludTrabajadores, on_delete=models.SET_NULL, null=True, blank=True)
    banco = models.ForeignKey(Banco, on_delete=models.SET_NULL, null=True, blank=True)  # New field
    casa = models.ForeignKey(CasasTrabajadores, on_delete=models.SET_NULL, null=True, blank=True)
    transportista = models.ForeignKey(EmpresasTransporte, on_delete=models.SET_NULL, null=True)
    vehiculo = models.ForeignKey(VehiculosTransporte, on_delete=models.SET_NULL, null=True)
    nombres = models.CharField(max_length=255)
    apellidos = models.TextField(null=True, blank=True)
    rut = models.TextField(null=True, blank=True)
    dni = models.TextField(null=True, blank=True)
    nic = models.TextField(null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    fecha_finiquito = models.DateField(null=True, blank=True)
    estado = models.BooleanField(default=True, null=True, blank=True)
    metodo_pago = models.TextField(null=True, blank=True)
    tipo_cuenta_bancaria = models.TextField(null=True, blank=True)
    numero_cuenta = models.IntegerField(null=True, blank=True)
    nacionalidad = models.CharField(max_length=255, blank=True, null=True)
    sexo = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=255, blank=True, null=True)
    correo = models.CharField(max_length=255, blank=True, null=True)
    carnet_front_image = models.ImageField(upload_to='carnets/', default='carnets/dni.jpg', null=True, blank=True)
    carnet_back_image = models.ImageField(upload_to='carnets/', default='carnets/dni.jpg', null=True, blank=True)
    firma = models.ImageField(upload_to='firmas/', null=True, blank=True)
    estado_civil = models.CharField(max_length=255, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    sueldo_base = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    pensionado_vejez = models.BooleanField(default=False)
    ips_regimen = models.ForeignKey(IpsRegimen, on_delete=models.SET_NULL, null=True, blank=True)
    # AFC (cód 1151)
    afiliado_afc = models.BooleanField(default=True, verbose_name="Afiliado a AFC")
    cargas_familiares_legales = models.IntegerField(default=0)
    cargas_familiares_maternales = models.BooleanField(default=False)
    cargas_familiares_invalidez = models.IntegerField(default=0)
    subsidio_trabajador_joven = models.BooleanField(default=False)
    colacion = models.IntegerField(null=True, blank=True)
    movilizacion = models.IntegerField(null=True, blank=True)
    
    
    class Meta:
        db_table = 'personal'
 
class Usuarios(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE, null=True, blank=True)
    empresas_asignadas = models.ManyToManyField(Sociedad, blank=True)
    persona = models.ForeignKey(PersonalTrabajadores, on_delete=models.CASCADE, null=True, blank=True)
    rut =  models.CharField(max_length=255, unique=True)
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

class Supervisores(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True)
    trabajadores = models.ManyToManyField(PersonalTrabajadores, related_name='supervisor_directo', blank=True)
    
    class Meta:
        db_table = 'supervisores'
        
    def __str__(self):
        return f"Supervisor: {self.usuario.rut if self.usuario else 'Sin usuario'}"

class JefesDeCuadrilla(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(Supervisores, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True)
    trabajadores = models.ManyToManyField(PersonalTrabajadores, related_name='jefe_cuadrilla', blank=True)

    class Meta:
        db_table = 'jefes_cuadrilla'
        
    def __str__(self):
        return f"Jefe de Cuadrilla: {self.usuario.rut if self.usuario else 'Sin usuario'}"

class Horarios(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    jornada = models.FloatField()

    class Meta:
        db_table = 'horarios'

class CodigoQR(models.Model):
    id = models.AutoField(primary_key=True)
    trabajador = models.ForeignKey(PersonalTrabajadores,on_delete=models.CASCADE)
    codigo_qr = models.TextField()

    class Meta:
        db_table = 'asociacion_codigo_qr'

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
    folio = models.ForeignKey(FolioComercial, on_delete=models.SET_NULL, null=True, blank=True)
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
        """
        Calcula el monto a pagar para esta producción basado en el peso neto
        o las unidades de control.
        
        Returns:
            float: El monto a pagar calculado
        """
        if self.folio and self.folio.valor_pago_trabajador:
            if self.peso_neto and self.peso_neto > 0:
                return float(self.peso_neto * self.folio.valor_pago_trabajador)
            elif self.unidades_control:
                return float(self.unidades_control * self.folio.valor_pago_trabajador)
        return 0.0

    def __str__(self):
        return f"Producción {self.id} - {self.trabajador.nombres if self.trabajador else 'Sin trabajador'}"
    
class Cuadrillas(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    id = models.IntegerField(primary_key=True)
    jefe_cuadrilla = models.ForeignKey(JefesDeCuadrilla, on_delete=models.CASCADE, null=True, blank=True)
    trabajadores = models.ManyToManyField(PersonalTrabajadores)
    
    class Meta:
        db_table = 'cuadrillas'

class EnlaceAutoRegistro(models.Model):
    id = models.AutoField(primary_key=True)
    token = models.CharField(max_length=16, default=generate_token, unique=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    perfil = models.ForeignKey(Perfiles, on_delete=models.CASCADE)
    usuario_creador = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    ruts_permitidos = ArrayField(models.TextField(), blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'enlaces_auto_registro'

    def is_valid(self):
        """Verifica si el enlace está activo y no ha expirado"""
        ahora = timezone.now()
        return self.activo and ahora <= self.fecha_expiracion

    def tiempo_restante(self):
        """Retorna el tiempo restante en horas"""
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
    
    """
    Modelo para manejar el enlace de descarga de la APK.
    Solo debe existir un enlace activo por holding en cualquier momento.
    El archivo APK tiene una ubicación fija en el sistema de archivos.
    """
    # Definición de la ruta fija del archivo APK
    APK_NAME = 'contratista_testing.apk'
    APK_FOLDER = 'apk'
    
    # Campos del modelo
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey('Holding', on_delete=models.CASCADE)
    token = models.CharField(
        max_length=32, 
        default=generate_token_link_apk, 
        unique=True,
        help_text="Token único para acceder al enlace de descarga"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se creó el enlace"
    )
    fecha_expiracion = models.DateTimeField(
        help_text="Fecha y hora en que expirará el enlace"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el enlace está activo y puede ser usado"
    )
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
        """
        Retorna la ruta completa del archivo APK.
        Este método de clase permite obtener la ruta desde cualquier parte del código
        sin necesidad de instanciar el modelo.
        
        Returns:
            str: Ruta completa al archivo APK
        """
        return os.path.join(settings.BASE_DIR, cls.APK_FOLDER, cls.APK_NAME)

    def is_valid(self):
        """
        Verifica si el enlace está activo y no ha expirado.
        También comprueba que el archivo APK existe en el sistema.
        
        Returns:
            bool: True si el enlace es válido y el archivo existe
        """
        if not self.activo or timezone.now() >= self.fecha_expiracion:
            return False
            
        # Verificar que el archivo existe
        return os.path.exists(self.get_apk_path())

    def tiempo_restante(self):
        """
        Calcula el tiempo restante en horas antes de que expire el enlace.
        
        Returns:
            float: Horas restantes antes de la expiración, 0 si ya expiró
        """
        if not self.is_valid():
            return 0
        diferencia = self.fecha_expiracion - timezone.now()
        return max(0, diferencia.total_seconds() / 3600)

    def get_full_url(self):
        """
        Genera la URL completa para la página de descarga.
        Esta URL corresponde a la ruta en el frontend donde el usuario
        podrá descargar el archivo.
        
        Returns:
            str: URL completa para acceder a la página de descarga
        """
        base_url = "http://localhost:4200/apk-link"
        return f"{base_url}/{self.token}/{self.id}"

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para implementar la lógica de negocio:
        - Solo puede existir un enlace activo por holding
        - Verifica que el archivo APK existe antes de guardar
        
        Raises:
            ValidationError: Si el archivo APK no existe en la ruta especificada
        """
        if self.activo:
            # Verifica que el archivo existe
            if not os.path.exists(self.get_apk_path()):
                raise ValidationError(
                    f"El archivo APK no existe en la ruta: {self.get_apk_path()}"
                )
            
            # Desactiva otros enlaces activos del mismo holding
            APKLink.objects.filter(
                holding=self.holding,
                activo=True
            ).exclude(id=self.id).update(activo=False)
            
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Representación en string del modelo para facilitar su identificación
        en el admin de Django y en los logs.
        """
        return f"Enlace APK para {self.holding} - {'Activo' if self.activo else 'Inactivo'}"
    
class CuentaOrigen(models.Model):
    sociedad = models.ForeignKey(Sociedad, on_delete=models.CASCADE, related_name='cuentas_origen')
    banco = models.ForeignKey(Banco, on_delete=models.PROTECT)
    tipo_cuenta = models.CharField(max_length=3) 
    numero_cuenta = models.CharField(max_length=30)
    
    class Meta:
        db_table = 'cuenta_origen'

class HistorialCambioPago(models.Model):
    """
    Mantiene un registro histórico de los cambios en los montos de pago
    cuando ocurre un reproceso.
    """
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    
    # Referencias a los registros de pago (solo uno estará activo)
    registro_transferencia = models.ForeignKey(
        'RegistroPagoTransferencia', 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    registro_efectivo = models.ForeignKey(
        'RegistroPagoEfectivo',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    # Valores anteriores y nuevos
    monto_pagado_anterior = models.IntegerField()
    monto_pagado_nuevo = models.IntegerField()
    saldo_anterior = models.IntegerField(null=True, blank=True)
    saldo_nuevo = models.IntegerField(null=True, blank=True)
    
    # Información del reproceso
    folio = models.ForeignKey(FolioComercial, on_delete=models.CASCADE)
    valor_pago_anterior = models.IntegerField()
    valor_pago_nuevo = models.IntegerField()
    motivo_cambio = models.TextField()

    class Meta:
        db_table = 'historial_cambios_pago'

class RegistroPagoTransferencia(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    sociedad = models.ForeignKey(Sociedad, on_delete=models.SET_NULL, null=True)
    cuenta_origen = models.ForeignKey(CuentaOrigen, on_delete=models.SET_NULL, null=True)
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.SET_NULL, null=True)
    monto_pagado = models.IntegerField()
    fecha_pago = models.DateTimeField(auto_now_add=True)
    producciones = models.ManyToManyField(ProduccionTrabajador)
    archivo_csv = models.FileField(upload_to='pagos_csv/', null=True, blank=True)
    saldo = models.IntegerField(null=True, blank=True)
    historial_cambios = models.ManyToManyField(
        HistorialCambioPago,
        related_name='transferencias_modificadas',
        blank=True
    )

    class Meta:
        db_table = 'registro_pagos_transferencia'

class RegistroPagoEfectivo(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    sociedad = models.ForeignKey(Sociedad, on_delete=models.SET_NULL, null=True)
    cuenta_origen = models.ForeignKey(CuentaOrigen, on_delete=models.SET_NULL, null=True)
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.SET_NULL, null=True)
    monto_pagado = models.IntegerField()
    fecha_pago = models.DateTimeField(auto_now_add=True)
    producciones = models.ManyToManyField(ProduccionTrabajador)
    multiplo_pago = models.IntegerField()
    saldo = models.IntegerField(null=True, blank=True)
    historial_cambios = models.ManyToManyField(
        HistorialCambioPago,
        related_name='efectivos_modificados',
        blank=True
    )

    class Meta:
        db_table = 'registro_pagos_efectivo'

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

class Tramos(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete= models.CASCADE, null=True)
    origen = models.TextField()
    destino = models.TextField()
    comentario = models.TextField()
    TIPO_CHOICES = [
        ('PASAJERO' ,'Pasajero'),
        ('VIAJE' , 'Viaje')
    ]
    unidad_pago = models.CharField(max_length=10, choices=TIPO_CHOICES, null=True, blank=True)

    class Meta:
        db_table = 'tramos_transportista'

class FolioTransportista(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    folio_comercial = models.ForeignKey(FolioComercial, on_delete=models.SET_NULL, null=True, blank=True)
    valor_pago_transportista = models.IntegerField()
    valor_facturacion_transportista = models.IntegerField()
    tramo = models.ForeignKey(Tramos, on_delete= models.SET_NULL, null=True, blank=True)

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
    cuenta_origen = models.ForeignKey(CuentaOrigen, on_delete=models.SET_NULL, null=True)  # Corregido aquí
    usuario_registra = models.ForeignKey(Usuarios, on_delete=models.SET_NULL, null=True)
    
    # Campos para tracking
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
    # Campos de identificación
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.CASCADE)
    
    # Periodo
    mes = models.IntegerField()
    year = models.IntegerField()
    
    # Datos de aprobación
    usuario_aprueba = models.ForeignKey(Usuarios, on_delete=models.SET_NULL, null=True, related_name='aprobaciones_dias')
    fecha_aprobacion = models.DateTimeField(auto_now_add=True)
    
    # Datos de días trabajados (almacenados como JSON)
    dias_por_cliente = models.JSONField(help_text="Formato: {cliente_id: dias_trabajados}")
    
    # Información sobre reducciones aplicadas
    reducciones_aplicadas = models.JSONField(null=True, blank=True, 
        help_text="Formato: {cliente_id: {porcentaje: X, diasOriginales: Y}}")
    
    # Campos para auditoría
    dias_totales = models.IntegerField()
    modificado_por = models.ForeignKey(Usuarios, on_delete=models.SET_NULL, null=True, related_name='modificaciones_dias_trabajados')
    ultima_modificacion = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        db_table = 'dias_trabajados_aprobados'
        unique_together = [['trabajador', 'mes', 'year']]  # Un trabajador solo puede tener un registro aprobado por mes
        
    def __str__(self):
        return f"{self.trabajador.nombres} - {self.mes}/{self.year}"

class LicenciaMedica(models.Model):
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.CASCADE, related_name='licencias')
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_totales = models.IntegerField()
    tipo_licencia = models.CharField(max_length=100, default='COMUN')  # Común, maternal, etc.
    numero_licencia = models.CharField(max_length=50, blank=True, null=True)
    documento = models.FileField(upload_to='licencias/', null=True, blank=True)
    
    class Meta:
        db_table = 'licencias_medicas'

class Vacaciones(models.Model):
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.CASCADE, related_name='vacaciones')
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
    usuario_cierre = models.ForeignKey(Usuarios, on_delete=models.SET_NULL, null=True, related_name='meses_cerrados')
    motivo = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'meses_cerrados'
        unique_together = [['holding', 'mes', 'year']]
        
    def __str__(self):
        return f"Mes {self.mes}/{self.year} - Holding {self.holding.nombre}"

class TrabajadorHaber(models.Model):
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.CASCADE, related_name='haberes_asignados')
    haber = models.ForeignKey(Haberes, on_delete=models.CASCADE, related_name='asignaciones')
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        db_table = 'trabajador_haber'
        unique_together = [['trabajador', 'haber']]

class TrabajadorDescuento(models.Model):
    trabajador = models.ForeignKey(PersonalTrabajadores, on_delete=models.CASCADE, related_name='descuentos_asignados')
    descuento = models.ForeignKey(Descuentos, on_delete=models.CASCADE, related_name='asignaciones')
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    num_cuotas = models.IntegerField(default=1)  # Número total de cuotas
    cuota_actual = models.IntegerField(default=1)  # Cuota actual
    valor_cuota = models.DecimalField(max_digits=12, decimal_places=2)  # Valor por cuota
    
    class Meta:
        db_table = 'trabajador_descuento'
        unique_together = [['trabajador', 'descuento']]

    def __str__(self):
        return f"{self.trabajador.nombres} - {self.descuento.nombre}"

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

#----------------MODELOS PARA EL LIBRO DE REMUNERACION ELECTRONICO------------------------------------------

class CalibrationSettings(models.Model):
    # Relaciones
    documento = models.ForeignKey(ContratoVariables, on_delete=models.CASCADE, related_name='calibraciones')
    
    # Identificación
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Parámetros de transformación
    escala_x = models.FloatField(default=0.72)
    escala_y = models.FloatField(default=0.72)
    offset_x = models.IntegerField(default=0)
    offset_y = models.IntegerField(default=0)
    invertir_y = models.BooleanField(default=True)
    
    # Metadatos
    tamaño_pdf_ancho = models.IntegerField(null=True, blank=True)
    tamaño_pdf_alto = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'calibraciones_pdf'
        unique_together = [['documento', 'nombre']]
    
    def __str__(self):
        return f"Calibración de {self.documento.nombre}: {self.nombre}"
    
    def aplicar_transformacion(self, x, y, altura_pagina):
        """
        Aplica la transformación de coordenadas usando los parámetros guardados
        """
        pdf_x = x * self.escala_x + self.offset_x
        
        if self.invertir_y:
            pdf_y = altura_pagina - (y * self.escala_y) + self.offset_y
        else:
            pdf_y = y * self.escala_y + self.offset_y
            
        return pdf_x, pdf_y
    
class CausalFiniquito(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=10)
    glosa = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'causales_finiquito'
        
    def __str__(self):
        return f"{self.codigo} - {self.glosa}"

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

#-----------------------------------------------------------------------------------------------------------

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
    fundo = models.ForeignKey(CamposClientes, on_delete=models.SET_NULL, null=True, blank=True)
    cliente = models.ForeignKey(Clientes, on_delete=models.SET_NULL, null=True, blank=True)
    empresa_transporte = models.ForeignKey(EmpresasTransporte, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'contratos_trabajadores'

class Cuenta(models.Model):
    """
    Modelo para las cuentas contables donde se pueden distribuir las facturas
    """
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    nombre_cuenta = models.CharField(max_length=255, help_text="Nombre descriptivo de la cuenta")
    cuenta_contable = models.CharField(max_length=50, help_text="Código de la cuenta contable")
    activa = models.BooleanField(default=True, help_text="Indica si la cuenta está activa")
    
    class Meta:
        db_table = 'cuentas'
        unique_together = [['holding', 'cuenta_contable']]
        ordering = ['nombre_cuenta']
    
    def __str__(self):
        return f"{self.nombre_cuenta} ({self.cuenta_contable})"

#=================================================================================================
#=========================DISTRIBUCION FACTURA COMPRA AUTOMATICA==================================
#=================================================================================================
class ConfiguracionSIIAutomaticaCompra(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    rut_sii = models.CharField(max_length=12)
    password_sii = models.CharField(max_length=255)  # Encriptado
    empresa_rut = models.CharField(max_length=12)
    empresa_nombre = models.CharField(max_length=255)
    hora_ejecucion = models.TimeField()
    mes = models.IntegerField(default=1)
    year = models.IntegerField(default=2025)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'configuracion_sii_automatica'
        
    def __str__(self):
        return f"Config SII - {self.empresa_nombre} - {self.mes:02d}/{self.year}"
   
class FacturaCompraSIIDistribuida(models.Model):
    """
    Modelo para almacenar las facturas SII que ya han sido distribuidas/asociadas.
    ACTUALIZADO para soportar distribución múltiple.
    """
    # Identificación
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE)
    
    # Campos de distribución adicionales (opcionales)
    fundo = models.ForeignKey(
        CamposClientes, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        help_text="Fundo/Campo del cliente"
    )
    labor = models.ForeignKey(
        Labores, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        help_text="Labor asociada"
    )
    cuenta = models.ForeignKey(
        Cuenta, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        help_text="Cuenta contable"
    )
    
    # Datos de la factura original (copiados desde FacturaCompraSIIDistribuida)
    folio = models.CharField(max_length=50, help_text="Folio único de la factura")
    tipo_doc = models.CharField(max_length=50, help_text="Tipo de documento")
    tipo_compra = models.CharField(max_length=50, blank=True, null=True)
    rut_proveedor = models.CharField(max_length=20)
    razon_social = models.CharField(max_length=255)
    fecha_docto = models.CharField(max_length=20)
    fecha_recepcion = models.CharField(max_length=20, blank=True, null=True)
    fecha_acuse = models.CharField(max_length=20, blank=True, null=True)
    
    # Montos proporcionales de esta distribución específica
    monto_exento = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_neto = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_iva_recuperable = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_iva_no_recuperable = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    codigo_iva_no_rec = models.CharField(max_length=10, blank=True, null=True)
    monto_total = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Monto distribuido a este cliente")
    monto_neto_activo_fijo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    iva_activo_fijo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    iva_uso_comun = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    impto_sin_derecho_credito = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    iva_no_retenido = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tabacos_puros = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tabacos_cigarrillos = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tabacos_elaborados = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    nce_nde_fact_compra = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    codigo_otro_impuesto = models.CharField(max_length=10, blank=True, null=True)
    valor_otro_impuesto = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tasa_otro_impuesto = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # NUEVOS CAMPOS PARA DISTRIBUCIÓN MÚLTIPLE
    monto_distribuido = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        help_text="Monto específico distribuido a este cliente",
        null=True
    )
    porcentaje_distribuido = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Porcentaje del total distribuido a este cliente",
        null=True
    )
    tipo_distribucion = models.CharField(
        max_length=10,
        choices=[('MONTO', 'Por Monto'), ('PORCENTAJE', 'Por Porcentaje')],
        default='MONTO',
        help_text="Indica si la distribución se hizo por monto o porcentaje",
        null=True
    )
    monto_total_factura = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        help_text="Monto total de la factura original (para referencia)",
        null=True
    )
    
    # Metadatos de distribución
    usuario_distribuyente = models.ForeignKey(Usuarios, on_delete=models.SET_NULL, null=True)
    fecha_distribucion = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(
        blank=True, 
        null=True, 
        help_text="Observaciones sobre la distribución"
    )
    
    class Meta:
        db_table = 'facturas_sii_distribuidas'
        # CAMBIO IMPORTANTE: Remover unique_together para permitir múltiples distribuciones
        unique_together = []  # Permitir múltiples distribuciones de la misma factura
        ordering = ['-fecha_distribucion']
        
        # Agregar índices para mejorar consultas
        indexes = [
            models.Index(fields=['holding', 'folio', 'rut_proveedor'], name='facturas_sii_dist_lookup_idx'),
            models.Index(fields=['cliente', 'fecha_distribucion'], name='facturas_sii_dist_cliente_idx'),
            models.Index(fields=['holding', 'fecha_distribucion'], name='facturas_sii_dist_holding_idx'),
            models.Index(fields=['tipo_distribucion'], name='facturas_sii_dist_tipo_idx'),
        ]
        
    def __str__(self):
        return f"Factura {self.tipo_doc} - {self.folio} - {self.cliente.nombre} ({self.porcentaje_distribuido}%)"
    
    # ==================== MÉTODOS PARA DISTRIBUCIÓN MÚLTIPLE ====================
    
    def get_distribucion_info(self):
        """Retorna información completa de esta distribución específica"""
        return {
            'id': self.id,
            'cliente': {
                'id': self.cliente.id,
                'nombre': self.cliente.nombre,
                'rut': self.cliente.rut
            },
            'fundo': {
                'id': self.fundo.id,
                'nombre': self.fundo.nombre_campo,
                'direccion': self.fundo.direccion_campo
            } if self.fundo else None,
            'labor': {
                'id': self.labor.id,
                'nombre': self.labor.nombre,
                'especie': self.labor.especie
            } if self.labor else None,
            'cuenta': {
                'id': self.cuenta.id,
                'nombre': self.cuenta.nombre_cuenta,
                'codigo': self.cuenta.cuenta_contable
            } if self.cuenta else None,
            
            # Información de distribución
            'monto_distribuido': float(self.monto_distribuido),
            'porcentaje_distribuido': float(self.porcentaje_distribuido),
            'tipo_distribucion': self.tipo_distribucion,
            'monto_total_factura': float(self.monto_total_factura),
            
            # Información de la factura
            'factura': {
                'folio': self.folio,
                'tipo_doc': self.tipo_doc,
                'rut_proveedor': self.rut_proveedor,
                'razon_social': self.razon_social,
                'fecha_docto': self.fecha_docto,
                'monto_total_original': float(self.monto_total_factura)
            },
            
            # Metadatos
            'fecha_distribucion': self.fecha_distribucion.strftime('%d/%m/%Y %H:%M'),
            'fecha_distribucion_iso': self.fecha_distribucion.isoformat(),
            'observaciones': self.observaciones,
            'usuario_distribuyente': {
                'id': self.usuario_distribuyente.id,
                'nombre': self.usuario_distribuyente.persona.nombres if self.usuario_distribuyente and self.usuario_distribuyente.persona else None,
                'rut': self.usuario_distribuyente.rut if self.usuario_distribuyente else None
            } if self.usuario_distribuyente else None
        }
    
    def get_porcentaje_del_total_factura(self):
        """Calcula el porcentaje que representa esta distribución del total de la factura"""
        if self.monto_total_factura and self.monto_total_factura > 0:
            return (self.monto_distribuido / self.monto_total_factura) * 100
        return 0
    
    def get_otras_distribuciones(self):
        """Obtiene las otras distribuciones de la misma factura"""
        return FacturaCompraSIIDistribuida.objects.filter(
            holding_id=self.holding_id,
            folio=self.folio,
            rut_proveedor=self.rut_proveedor
        ).exclude(id=self.id).order_by('-fecha_distribucion')
    
    def get_resumen_factura_completa(self):
        """Obtiene un resumen completo de todas las distribuciones de esta factura"""
        todas_distribuciones = FacturaCompraSIIDistribuida.objects.filter(
            holding_id=self.holding_id,
            folio=self.folio,
            rut_proveedor=self.rut_proveedor
        ).order_by('-fecha_distribucion')
        
        total_distribuido = sum(dist.monto_distribuido for dist in todas_distribuciones)
        total_porcentaje = sum(dist.porcentaje_distribuido for dist in todas_distribuciones)
        
        return {
            'factura': {
                'folio': self.folio,
                'tipo_doc': self.tipo_doc,
                'razon_social': self.razon_social,
                'monto_total': float(self.monto_total_factura)
            },
            'distribuciones': {
                'total_distribuciones': todas_distribuciones.count(),
                'monto_total_distribuido': float(total_distribuido),
                'porcentaje_total_distribuido': float(total_porcentaje),
                'monto_pendiente': float(self.monto_total_factura - total_distribuido),
                'porcentaje_pendiente': float(100 - total_porcentaje),
                'completamente_distribuida': total_porcentaje >= 100
            },
            'detalle_distribuciones': [
                {
                    'id': dist.id,
                    'cliente_nombre': dist.cliente.nombre,
                    'monto_distribuido': float(dist.monto_distribuido),
                    'porcentaje_distribuido': float(dist.porcentaje_distribuido),
                    'fecha_distribucion': dist.fecha_distribucion.strftime('%d/%m/%Y %H:%M')
                }
                for dist in todas_distribuciones
            ]
        }
    
    # ==================== MÉTODO ACTUALIZADO GET_DISTRIBUCION_COMPLETA ====================
    
    def get_distribucion_completa(self):
        """
        Retorna información completa de la distribución (versión actualizada)
        Mantiene compatibilidad con código existente
        """
        return {
            'cliente': {
                'id': self.cliente.id,
                'nombre': self.cliente.nombre,
                'rut': self.cliente.rut
            },
            'fundo': {
                'id': self.fundo.id,
                'nombre': self.fundo.nombre_campo,
                'direccion': self.fundo.direccion_campo
            } if self.fundo else None,
            'labor': {
                'id': self.labor.id,
                'nombre': self.labor.nombre,
                'especie': self.labor.especie
            } if self.labor else None,
            'cuenta': {
                'id': self.cuenta.id,
                'nombre': self.cuenta.nombre_cuenta,
                'codigo': self.cuenta.cuenta_contable
            } if self.cuenta else None,
            'factura': {
                'folio': self.folio,
                'tipo_doc': self.tipo_doc,
                'proveedor': self.razon_social,
                'fecha': self.fecha_docto,
                'monto_total': float(self.monto_total_factura),  # Monto original
                'monto_distribuido': float(self.monto_distribuido),  # Monto de esta distribución
                'porcentaje_distribuido': float(self.porcentaje_distribuido)
            }
        }
    
    def save(self, *args, **kwargs):
        """
        Override del método save para validaciones adicionales
        """
        # Asegurar que monto_distribuido = monto_total para esta distribución
        if self.monto_distribuido and self.monto_total != self.monto_distribuido:
            self.monto_total = self.monto_distribuido
        
        # Validar que el porcentaje no exceda 100%
        if self.porcentaje_distribuido > 100:
            raise ValueError("El porcentaje distribuido no puede ser mayor a 100%")
        
        # Validar que el monto no exceda el total de la factura
        if self.monto_distribuido > self.monto_total_factura:
            raise ValueError("El monto distribuido no puede ser mayor al total de la factura")
        
        super().save(*args, **kwargs)

class FacturaCompraSIIPorDistribuir(models.Model):
    """
    Modelo para facturas encontradas automáticamente que están pendientes de distribución.
    ACTUALIZADO para soportar distribución múltiple.
    """
    # Relación principal
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    
    # Datos de la factura del CSV del SII
    folio = models.CharField(max_length=50, help_text="Folio único de la factura")
    tipo_doc = models.CharField(max_length=50, help_text="Tipo de documento")
    tipo_compra = models.CharField(max_length=50, blank=True, null=True)
    rut_proveedor = models.CharField(max_length=20)
    razon_social = models.CharField(max_length=255)
    fecha_docto = models.CharField(max_length=20)
    fecha_recepcion = models.CharField(max_length=20, blank=True, null=True)
    fecha_acuse = models.CharField(max_length=20, blank=True, null=True)
    
    # Montos originales de la factura
    monto_exento = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_neto = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_iva_recuperable = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_iva_no_recuperable = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    codigo_iva_no_rec = models.CharField(max_length=10, blank=True, null=True)
    monto_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_neto_activo_fijo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    iva_activo_fijo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    iva_uso_comun = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    impto_sin_derecho_credito = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    iva_no_retenido = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tabacos_puros = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tabacos_cigarrillos = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tabacos_elaborados = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    nce_nde_fact_compra = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    codigo_otro_impuesto = models.CharField(max_length=10, blank=True, null=True)
    valor_otro_impuesto = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tasa_otro_impuesto = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Campos de control
    fecha_encontrada = models.DateTimeField(auto_now_add=True)
    procesada = models.BooleanField(default=False, help_text="True cuando está 100% distribuida")
    
    # NUEVOS CAMPOS PARA DISTRIBUCIÓN MÚLTIPLE
    monto_distribuido = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        help_text="Monto total ya distribuido",
        null=True
    )
    porcentaje_distribuido = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        help_text="Porcentaje total ya distribuido",
        null=True
    
    )
    
    # Campos para manejo de PDFs
    pdf_documento = models.FileField(
        upload_to='facturas_compra_sii_pdfs/', 
        blank=True, 
        null=True, 
        help_text="PDF de la factura descargado del SII"
    )
    codigo_sii = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        help_text="Código único del SII para acceder al PDF"
    )
    pdf_descargado = models.BooleanField(
        default=False, 
        help_text="Indica si el PDF fue descargado exitosamente"
    )
    fecha_descarga_pdf = models.DateTimeField(
        blank=True, 
        null=True, 
        help_text="Fecha en que se descargó el PDF"
    )
    error_descarga_pdf = models.TextField(
        blank=True, 
        null=True, 
        help_text="Error al intentar descargar el PDF"
    )
    intentos_descarga_pdf = models.IntegerField(
        default=0, 
        help_text="Número de intentos de descarga del PDF"
    )
    
    # Identificación de factura manual
    es_manual = models.BooleanField(default=False, help_text="True si es una factura creada manualmente")

    # Descripción del trabajo/servicio
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción del trabajo realizado")

    # Observaciones adicionales  
    observaciones_manual = models.TextField(blank=True, null=True, help_text="Observaciones adicionales")
    fecha_creacion_manual = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'facturas_sii_por_distribuir'
        unique_together = [['holding', 'folio', 'tipo_doc', 'rut_proveedor']]
        ordering = ['-fecha_encontrada']
        indexes = [
            models.Index(fields=['holding', 'procesada']),
            models.Index(fields=['holding', 'porcentaje_distribuido']),
            models.Index(fields=['pdf_descargado']),
        ]
        
    def __str__(self):
        return f"Factura {self.tipo_doc} - {self.folio} - {self.razon_social}"
    
    # ==================== MÉTODOS PARA DISTRIBUCIÓN MÚLTIPLE ====================
    
    def get_monto_pendiente(self):
        """Obtiene el monto pendiente de distribuir"""
        from decimal import Decimal
        monto_distribuido = self.monto_distribuido or Decimal('0')
        return self.monto_total - monto_distribuido
    
    def get_porcentaje_pendiente(self):
        """Obtiene el porcentaje pendiente de distribuir"""
        from decimal import Decimal
        porcentaje_distribuido = self.porcentaje_distribuido or Decimal('0')
        return Decimal('100') - porcentaje_distribuido
        
    def esta_completamente_distribuida(self):
        """Verifica si la factura está completamente distribuida"""
        from decimal import Decimal
        porcentaje_distribuido = self.porcentaje_distribuido or Decimal('0')
        return porcentaje_distribuido >= Decimal('100')
    
    def puede_distribuir_monto(self, monto):
        """Verifica si se puede distribuir un monto específico"""
        from decimal import Decimal
        return monto <= self.get_monto_pendiente()
    
    def puede_distribuir_porcentaje(self, porcentaje):
        """Verifica si se puede distribuir un porcentaje específico"""
        from decimal import Decimal
        return porcentaje <= self.get_porcentaje_pendiente()
    
    def get_distribuciones(self):
        """Obtiene todas las distribuciones de esta factura"""
        return FacturaCompraSIIDistribuida.objects.filter(
            holding_id=self.holding_id,
            folio=self.folio,
            rut_proveedor=self.rut_proveedor
        ).order_by('-fecha_distribucion')
    
    def get_resumen_distribuciones(self):
        """Obtiene un resumen de las distribuciones"""
        distribuciones = self.get_distribuciones()
        return {
            'total_distribuciones': distribuciones.count(),
            'clientes_distintos': distribuciones.values('cliente').distinct().count(),
            'distribuciones': [
                {
                    'id': dist.id,
                    'cliente_nombre': dist.cliente.nombre,
                    'monto_distribuido': float(dist.monto_distribuido),
                    'porcentaje_distribuido': float(dist.porcentaje_distribuido),
                    'fecha_distribucion': dist.fecha_distribucion.strftime('%d/%m/%Y %H:%M')
                }
                for dist in distribuciones[:10]  # Solo las primeras 10
            ]
        }
    
    def actualizar_totales_distribucion(self):
        """
        Recalcula los totales de distribución basándose en las distribuciones existentes.
        Útil para sincronizar datos en caso de inconsistencias.
        """
        distribuciones = self.get_distribuciones()
        
        total_monto = sum(dist.monto_distribuido for dist in distribuciones)
        total_porcentaje = sum(dist.porcentaje_distribuido for dist in distribuciones)
        
        self.monto_distribuido = total_monto
        self.porcentaje_distribuido = total_porcentaje
        self.procesada = self.esta_completamente_distribuida()
        
        self.save(update_fields=['monto_distribuido', 'porcentaje_distribuido', 'procesada'])
        
        return {
            'monto_distribuido': float(self.monto_distribuido),
            'porcentaje_distribuido': float(self.porcentaje_distribuido),
            'procesada': self.procesada
        }
    
    def get_pdf_disponible(self):
        """Verifica si el PDF está disponible (solo para facturas SII)"""
        if getattr(self, 'es_manual', False):
            return False  # Las facturas manuales no tienen PDF
        return getattr(self, 'pdf_descargado', False)
    # ==================== MÉTODO ACTUALIZADO GET_FACTURA_DATA ====================
    
    def get_factura_data(self):
        """
        Retorna información completa de la factura incluyendo distribución y PDF
        """
        return {
            'nro': str(self.id),
            'id': self.id,
            'tipo_doc': self.tipo_doc,
            'tipo_compra': self.tipo_compra,
            'rut_proveedor': self.rut_proveedor,
            'razon_social': self.razon_social,
            'folio': self.folio,
            'fecha_docto': self.fecha_docto,
            'fecha_recepcion': self.fecha_recepcion,
            'fecha_acuse': self.fecha_acuse,
            
            # Montos originales
            'monto_total': float(self.monto_total),
            'monto_neto': float(self.monto_neto),
            'monto_exento': float(self.monto_exento),
            'iva_recuperable': float(self.monto_iva_recuperable),
            
            # NUEVOS CAMPOS DE DISTRIBUCIÓN MÚLTIPLE
            'monto_distribuido': float(self.monto_distribuido),
            'monto_pendiente': float(self.get_monto_pendiente()),
            'porcentaje_distribuido': float(self.porcentaje_distribuido),
            'porcentaje_pendiente': float(self.get_porcentaje_pendiente()),
            'completamente_distribuida': self.esta_completamente_distribuida(),
            'distribuciones_count': self.get_distribuciones().count(),
            'distribuciones': self.get_resumen_distribuciones()['distribuciones'],
            
            # Campos de PDF
            'pdf_disponible': bool(self.pdf_documento),
            'pdf_url': self.pdf_documento.url if self.pdf_documento else None,
            'pdf_descargado': self.pdf_descargado,
            'fecha_descarga_pdf': self.fecha_descarga_pdf.isoformat() if self.fecha_descarga_pdf else None,
            'fecha_descarga_pdf_formatted': self.fecha_descarga_pdf.strftime('%d/%m/%Y %H:%M') if self.fecha_descarga_pdf else None,
            'error_descarga_pdf': self.error_descarga_pdf,
            'intentos_descarga_pdf': self.intentos_descarga_pdf,
            'codigo_sii': self.codigo_sii,
            
            # Campos de control
            'fecha_encontrada': self.fecha_encontrada.isoformat() if self.fecha_encontrada else '',
            'procesada': self.procesada,
            'selected': False  # Para el frontend
        }

#=================================================================================================
#=========================DISTRIBUCION FACTURA VENTA AUTOMATICA===================================
#=================================================================================================

class ConfiguracionSIIAutomaticaVenta(models.Model):
    """
    Configuración para el proceso automático de facturas de venta
    """
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    rut_sii = models.CharField(max_length=12)
    password_sii = models.CharField(max_length=255)  # Encriptado
    empresa_rut = models.CharField(max_length=12)
    empresa_nombre = models.CharField(max_length=255)
    hora_ejecucion = models.TimeField()
    mes = models.IntegerField(default=1)
    year = models.IntegerField(default=2025)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'configuracion_sii_automatica_venta'
        unique_together = [['holding']]  # Solo una configuración por holding
        
    def __str__(self):
        return f"Config SII - {self.empresa_nombre} - {self.mes:02d}/{self.year}"

class FacturaVentaSIIPorDistribuir(models.Model):
    """
    Modelo para facturas de venta encontradas automáticamente que están pendientes de distribución.
    Basado en la estructura de facturas de compra pero adaptado para ventas.
    """
    # Identificación
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    
    # Datos básicos de la factura de venta (según CSV del SII)
    nro = models.CharField(max_length=20, blank=True, null=True, help_text="Número secuencial en el CSV")
    tipo_doc = models.CharField(max_length=50, help_text="Tipo de documento (33=Factura, 34=Factura Exenta, etc.)")
    rut_receptor = models.CharField(max_length=20, help_text="RUT del receptor/cliente")
    razon_social_receptor = models.CharField(max_length=255, help_text="Razón social del receptor")
    folio = models.CharField(max_length=50, help_text="Folio único de la factura")
    fecha_emision = models.CharField(max_length=20, help_text="Fecha de emisión de la factura")
    
    # Montos de la factura de venta
    monto_total = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Monto total de la factura")
    monto_neto = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Monto neto")
    monto_exento = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Monto exento de IVA")
    monto_iva = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Monto del IVA")
    
    # Otros impuestos si aplican para ventas
    monto_otros_impuestos = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    codigo_otros_impuestos = models.CharField(max_length=10, blank=True, null=True)
    
    # Campos de control
    fecha_encontrada = models.DateTimeField(auto_now_add=True, help_text="Cuándo se encontró la factura")
    procesada = models.BooleanField(default=False, help_text="True cuando está 100% distribuida")
    
    # CAMPOS PARA DISTRIBUCIÓN MÚLTIPLE
    monto_distribuido = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        help_text="Monto total ya distribuido",
        null=True
    )
    porcentaje_distribuido = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        help_text="Porcentaje total ya distribuido",
        null=True
    )
    
    # Campos para manejo de PDFs
    pdf_documento = models.FileField(
        upload_to='facturas_venta_sii_pdfs/', 
        blank=True, 
        null=True, 
        help_text="PDF de la factura descargado del SII"
    )
    codigo_sii = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        help_text="Código único del SII para acceder al PDF"
    )
    pdf_descargado = models.BooleanField(
        default=False, 
        help_text="Indica si el PDF fue descargado exitosamente"
    )
    fecha_descarga_pdf = models.DateTimeField(
        blank=True, 
        null=True, 
        help_text="Cuándo se descargó el PDF"
    )
    error_descarga_pdf = models.TextField(
        blank=True, 
        null=True, 
        help_text="Error ocurrido al descargar el PDF"
    )
    intentos_descarga_pdf = models.IntegerField(
        default=0, 
        help_text="Número de intentos de descarga del PDF"
    )

    # Identificación de factura manual
    es_manual = models.BooleanField(default=False, help_text="True si es una factura creada manualmente")

    # Descripción del trabajo/servicio
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción del trabajo realizado")

    # Observaciones adicionales
    observaciones_manual = models.TextField(blank=True, null=True, help_text="Observaciones adicionales")
    fecha_creacion_manual = models.DateTimeField(blank=True, null=True)


    class Meta:
        db_table = 'facturas_venta_sii_por_distribuir'
        unique_together = [['holding', 'folio']]  # Un folio es único por holding
        ordering = ['-fecha_encontrada']
        indexes = [
            models.Index(fields=['holding', 'procesada']),
            models.Index(fields=['folio']),
            models.Index(fields=['pdf_descargado']),
            models.Index(fields=['fecha_encontrada']),
        ]
    

    def __str__(self):
        return f"Factura Venta {self.folio} - {self.razon_social_receptor} - ${self.monto_total:,.0f}"
    
    # MÉTODOS PARA DISTRIBUCIÓN MÚLTIPLE
    def get_monto_pendiente(self):
        """Retorna el monto pendiente por distribuir"""
        return self.monto_total - (self.monto_distribuido or 0)
    
    def get_porcentaje_pendiente(self):
        """Retorna el porcentaje pendiente por distribuir"""
        return 100 - (self.porcentaje_distribuido or 0)
    
    def esta_completamente_distribuida(self):
        """Indica si la factura está 100% distribuida"""
        return (self.porcentaje_distribuido or 0) >= 100
    
    def get_distribuciones(self):
        """Retorna las distribuciones existentes de esta factura"""
        return FacturaVentaSIIDistribuida.objects.filter(
            holding=self.holding,
            folio=self.folio
        ).order_by('-fecha_distribucion')
    
    def get_factura_data(self):
        """Retorna datos estructurados de la factura para APIs"""
        return {
            'id': self.id,
            'folio': self.folio,
            'tipo_doc': self.tipo_doc,
            'receptor': {
                'rut': self.rut_receptor,
                'razon_social': self.razon_social_receptor
            },
            'fechas': {
                'emision': self.fecha_emision,
                'encontrada': self.fecha_encontrada.isoformat() if self.fecha_encontrada else None
            },
            'montos': {
                'total': float(self.monto_total),
                'neto': float(self.monto_neto),
                'iva': float(self.monto_iva),
                'distribuido': float(self.monto_distribuido or 0),
                'pendiente': float(self.get_monto_pendiente())
            },
            'distribucion': {
                'porcentaje_distribuido': float(self.porcentaje_distribuido or 0),
                'porcentaje_pendiente': float(self.get_porcentaje_pendiente()),
                'completamente_distribuida': self.esta_completamente_distribuida(),
                'cantidad_distribuciones': self.get_distribuciones().count()
            },
            'pdf': {
                'descargado': self.pdf_descargado,
                'url': self.pdf_documento.url if self.pdf_documento else None,
                'intentos': self.intentos_descarga_pdf,
                'error': self.error_descarga_pdf
            }
        }

    def puede_distribuir_monto(self, monto):
        """Verifica si se puede distribuir un monto específico"""
        from decimal import Decimal
        return monto <= self.get_monto_pendiente()

    def puede_distribuir_porcentaje(self, porcentaje):
        """Verifica si se puede distribuir un porcentaje específico"""
        from decimal import Decimal
        return porcentaje <= self.get_porcentaje_pendiente()

    def actualizar_totales_distribucion(self):
        """
        Recalcula los totales de distribución basándose en las distribuciones existentes.
        Útil para sincronizar datos en caso de inconsistencias.
        """
        from decimal import Decimal
        from django.db.models import Sum
        
        # Obtener totales de distribuciones existentes
        distribuciones = self.get_distribuciones()
        
        monto_total_distribuido = distribuciones.aggregate(
            total=Sum('monto_distribuido')
        )['total'] or Decimal('0')
        
        # Calcular porcentaje basado en el monto total
        if self.monto_total > 0:
            porcentaje_total_distribuido = (monto_total_distribuido / self.monto_total) * 100
        else:
            porcentaje_total_distribuido = Decimal('0')
        
        # Actualizar campos
        self.monto_distribuido = monto_total_distribuido
        self.porcentaje_distribuido = porcentaje_total_distribuido
        
        # Determinar si está procesada (completamente distribuida)
        self.procesada = porcentaje_total_distribuido >= Decimal('100')
        
        self.save(update_fields=['monto_distribuido', 'porcentaje_distribuido', 'procesada'])
        
        return {
            'monto_distribuido': float(monto_total_distribuido),
            'porcentaje_distribuido': float(porcentaje_total_distribuido),
            'completamente_distribuida': self.procesada
        }
    def get_pdf_disponible(self):
        """Verifica si el PDF está disponible (solo para facturas SII)"""
        if getattr(self, 'es_manual', False):
            return False  # Las facturas manuales no tienen PDF
        return getattr(self, 'pdf_descargado', False)

    def actualizar_montos_distribucion(self):
        """
        Actualiza los montos de distribución basándose en las distribuciones existentes
        """
        # Importar aquí para evitar imports circulares
        from .models import FacturaVentaSIIDistribuida
        
        distribuciones = FacturaVentaSIIDistribuida.objects.filter(
            holding=self.holding,
            folio=self.folio,
            rut_receptor=self.rut_receptor
        )
        
        total_distribuido = sum(dist.monto_distribuido for dist in distribuciones)
        
        # Actualizar campos
        self.monto_distribuido = total_distribuido
        
        if self.monto_total > 0:
            self.porcentaje_distribuido = (total_distribuido / self.monto_total) * 100
        else:
            self.porcentaje_distribuido = 0
        
        # Marcar como procesada si está completamente distribuida
        self.procesada = self.esta_completamente_distribuida()
        
        self.save()

    @property
    def monto_pendiente(self):
        """Property para acceso directo al monto pendiente"""
        return self.get_monto_pendiente()

    @property
    def porcentaje_pendiente(self):
        """Property para acceso directo al porcentaje pendiente"""
        return self.get_porcentaje_pendiente()

    @property
    def completamente_distribuida(self):
        """Property para acceso directo al estado de distribución"""
        return self.esta_completamente_distribuida()

    @property
    def pdf_disponible(self):
        """Property para acceso directo al estado del PDF"""
        return self.get_pdf_disponible()

    def __str__(self):
        tipo = "Manual" if getattr(self, 'es_manual', False) else "SII"
        return f"[{tipo}] {self.tipo_doc} {self.folio} - {self.razon_social_receptor} - ${self.monto_total:,.0f}"   

class FacturaVentaSIIDistribuida(models.Model):
    """
    Modelo para almacenar las facturas de venta SII que ya han sido distribuidas/asociadas.
    Soporta distribución múltiple.
    """
    # Identificación
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE)
    
    # Campos de distribución adicionales (opcionales)
    fundo = models.ForeignKey(
        CamposClientes, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        help_text="Fundo/Campo del cliente"
    )
    labor = models.ForeignKey(
        Labores, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        help_text="Labor asociada"
    )
    cuenta = models.ForeignKey(
        Cuenta, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        help_text="Cuenta contable"
    )
    
    # Datos de la factura original (copiados desde FacturaVentaSIIPorDistribuir)
    folio = models.CharField(max_length=50, help_text="Folio único de la factura")
    tipo_doc = models.CharField(max_length=50, help_text="Tipo de documento")
    rut_receptor = models.CharField(max_length=20, help_text="RUT del receptor original")
    razon_social_receptor = models.CharField(max_length=255, help_text="Razón social del receptor original")
    fecha_emision = models.CharField(max_length=20, help_text="Fecha de emisión")
    
    
    # Montos proporcionales de esta distribución específica
    monto_total = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Monto distribuido a este cliente")
    monto_neto = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_exento = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_iva = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_otros_impuestos = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    codigo_otros_impuestos = models.CharField(max_length=10, blank=True, null=True)
    
    # CAMPOS DE DISTRIBUCIÓN MÚLTIPLE
    monto_distribuido = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        help_text="Monto específico distribuido en esta transacción"
    )
    porcentaje_distribuido = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        help_text="Porcentaje específico distribuido en esta transacción"
    )
    tipo_distribucion = models.CharField(
        max_length=20, 
        choices=[
            ('MONTO', 'Por monto específico'),
            ('PORCENTAJE', 'Por porcentaje')
        ],
        default='MONTO',
        help_text="Tipo de distribución utilizada"
    )
    monto_total_factura = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        help_text="Monto total original de la factura (referencia)"
    )
    
    # Metadatos
    observaciones = models.TextField(blank=True, null=True, help_text="Observaciones de la distribución")
    usuario_distribuyente = models.ForeignKey(
    Usuarios, 
    on_delete=models.SET_NULL, 
    null=True, 
    related_name='facturas_distribuidas',
    help_text="Usuario que realizó la distribución"
    )
    fecha_distribucion = models.DateTimeField(auto_now_add=True)
    usuario_creador = models.ForeignKey(
        Usuarios,
        null=True,
        blank=True, 
        on_delete=models.CASCADE,
        related_name='facturas_creadas'
    )
        
    class Meta:
        db_table = 'facturas_venta_sii_distribuidas'
        ordering = ['-fecha_distribucion']
        indexes = [
            models.Index(fields=['holding', 'cliente']),
            models.Index(fields=['folio']),
            models.Index(fields=['fecha_distribucion']),
        ]
    
    def __str__(self):
        return f"Distribución Venta {self.folio} -> {self.cliente.nombre} (${self.monto_distribuido:,.0f})"
    
    def get_monto_pendiente(self):
        """Retorna el monto pendiente por distribuir"""
        return self.monto_total - (self.monto_distribuido or 0)
    
    def get_porcentaje_pendiente(self):
        """Retorna el porcentaje pendiente por distribuir"""
        return 100 - (self.porcentaje_distribuido or 0)
    
    def puede_distribuir_monto(self, monto):
        """Verifica si se puede distribuir un monto específico"""
        from decimal import Decimal
        return monto <= self.get_monto_pendiente()

    def puede_distribuir_porcentaje(self, porcentaje):
        """Verifica si se puede distribuir un porcentaje específico"""
        from decimal import Decimal
        return porcentaje <= self.get_porcentaje_pendiente()

    def actualizar_totales_distribucion(self):
        """
        Recalcula los totales de distribución basándose en las distribuciones existentes.
        Útil para sincronizar datos en caso de inconsistencias.
        """
        from decimal import Decimal
        from django.db.models import Sum
        
        # Obtener totales de distribuciones existentes
        distribuciones = self.get_distribuciones()
        
        monto_total_distribuido = distribuciones.aggregate(
            total=Sum('monto_distribuido')
        )['total'] or Decimal('0')
        
        # Calcular porcentaje basado en el monto total
        if self.monto_total > 0:
            porcentaje_total_distribuido = (monto_total_distribuido / self.monto_total) * 100
        else:
            porcentaje_total_distribuido = Decimal('0')
        
        # Actualizar campos
        self.monto_distribuido = monto_total_distribuido
        self.porcentaje_distribuido = porcentaje_total_distribuido
        
        # Determinar si está procesada (completamente distribuida)
        self.procesada = porcentaje_total_distribuido >= Decimal('100')
        
        self.save(update_fields=['monto_distribuido', 'porcentaje_distribuido', 'procesada'])
        
        return {
            'monto_distribuido': float(monto_total_distribuido),
            'porcentaje_distribuido': float(porcentaje_total_distribuido),
            'completamente_distribuida': self.procesada
        }

    def get_distribucion_info(self):
        """Retorna información estructurada de la distribución para APIs"""
        return {
            'id': self.id,
            'distribucion': {
                'cliente': {
                    'id': self.cliente.id,
                    'nombre': self.cliente.nombre,
                    'rut': self.cliente.rut
                },
                'fundo': {
                    'id': self.fundo.id if self.fundo else None,
                    'nombre': self.fundo.nombre_campo if self.fundo else None
                } if self.fundo else None,
                'labor': {
                    'id': self.labor.id if self.labor else None,
                    'nombre': self.labor.nombre if self.labor else None,
                    'especie': self.labor.especie if self.labor else None
                } if self.labor else None,
                'cuenta': {
                    'id': self.cuenta.id if self.cuenta else None,
                    'nombre': self.cuenta.nombre_cuenta if self.cuenta else None,
                    'codigo': self.cuenta.cuenta_contable if self.cuenta else None
                } if self.cuenta else None,
                'monto_distribuido': float(self.monto_distribuido),
                'porcentaje_distribuido': float(self.porcentaje_distribuido),
                'tipo_distribucion': self.tipo_distribucion,
                'observaciones': self.observaciones,
                'fecha_distribucion': self.fecha_distribucion.isoformat() if self.fecha_distribucion else None,
                'usuario_distribuyente': {
                    'id': self.usuario_distribuyente.id if self.usuario_distribuyente else None,
                    'rut': self.usuario_distribuyente.rut if self.usuario_distribuyente else None,
                    'nombre': f"{self.usuario_distribuyente.persona.nombres} {self.usuario_distribuyente.persona.apellidos}" if self.usuario_distribuyente and self.usuario_distribuyente.persona else None
                } if self.usuario_distribuyente else None
            },
            'factura': {
                'folio': self.folio,
                'tipo_doc': self.tipo_doc,
                'receptor_original': self.razon_social_receptor,
                'fecha_emision': self.fecha_emision,
                'monto_total_factura': float(self.monto_total_factura),
                'monto_distribuido': float(self.monto_distribuido),
                'porcentaje_distribuido': float(self.porcentaje_distribuido)
            }
        }
    
    def save(self, *args, **kwargs):

        """
        Override del método save para validaciones adicionales
        """
        # Asegurar que monto_distribuido = monto_total para esta distribución
        if self.monto_distribuido and self.monto_total != self.monto_distribuido:
            self.monto_total = self.monto_distribuido
        
        # Validar que el porcentaje no exceda 100%
        if self.porcentaje_distribuido > 100:
            raise ValueError("El porcentaje distribuido no puede ser mayor a 100%")
        
        # Validar que el monto no exceda el total de la factura
        if self.monto_distribuido > self.monto_total_factura:
            raise ValueError("El monto distribuido no puede ser mayor al total de la factura")
        
        super().save(*args, **kwargs)

#=================================================================================================
#======================================TESORERIA==================================================
#=================================================================================================

class CartolaMovimiento(models.Model):
    """
    Modelo para almacenar los movimientos extraídos de la cartola bancaria
    """
    TIPO_MOVIMIENTO_CHOICES = [
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso'),
    ]
    
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    sociedad = models.ForeignKey(Sociedad, on_delete=models.CASCADE)
    cuenta_origen = models.ForeignKey(CuentaOrigen, on_delete=models.CASCADE)
    fecha = models.DateField()
    numero_operacion = models.CharField(max_length=50)
    descripcion = models.TextField()
    monto = models.DecimalField(max_digits=15, decimal_places=2)
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO_CHOICES)
    saldo = models.DecimalField(max_digits=15, decimal_places=2)
    procesado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cartola_movimiento'
        unique_together = [['cuenta_origen', 'numero_operacion', 'fecha']]
    
    def __str__(self):
        return f"{self.fecha} - {self.tipo_movimiento} - ${self.monto}"

class RegistroIngreso(models.Model):
    """
    Modelo para registrar los ingresos distribuidos
    """
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    movimiento_cartola = models.ForeignKey(CartolaMovimiento, on_delete=models.CASCADE)
    factura_venta = models.ForeignKey(FacturaVentaSIIDistribuida, on_delete=models.CASCADE)
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
        # Calcular los montos cubiertos basados en los porcentajes
        self.monto_neto_cubierto = (self.monto_distribuido * self.porcentaje_neto) / 100
        self.monto_iva_cubierto = (self.monto_distribuido * self.porcentaje_iva) / 100
        super().save(*args, **kwargs)

class RegistroEgreso(models.Model):
    """
    Modelo para registrar los egresos distribuidos (pagos a facturas de compra)
    """
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    movimiento_cartola = models.ForeignKey(CartolaMovimiento, on_delete=models.CASCADE)
    factura_compra = models.ForeignKey(FacturaCompraSIIDistribuida, on_delete=models.CASCADE)
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
        # Calcular los montos cubiertos basados en los porcentajes
        self.monto_neto_cubierto = (self.monto_distribuido * self.porcentaje_neto) / 100
        self.monto_iva_cubierto = (self.monto_distribuido * self.porcentaje_iva) / 100
        super().save(*args, **kwargs)