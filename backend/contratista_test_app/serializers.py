# serializers.py
from rest_framework import serializers
from datetime import date
from datetime import datetime
from django.utils import timezone
import random
import string
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    Holding, 
    Sociedad, 
    Usuarios, 
    Perfiles, 
    ModulosWeb,
    SubModulosWeb,
    ModulosMovil,
    SubModulosMovil,
    Clientes,
    Areas,
    Cargos,
    EmpresasTransporte,
    VehiculosTransporte,
    ChoferesTransporte,
    SaludTrabajadores,
    AFPTrabajadores,
    PersonalTrabajadores,
    CamposClientes,
    AreasCliente,
    CargosCliente,
    ContactosClientes,
    UnidadControl,
    Labores,
    FolioComercial,
    CasasTrabajadores,
    AreasAdministracion,
    CargosAdministracion,
    Horarios,
    ProduccionTrabajador,
    CodigoQR,
    Cuadrillas,
    EnlaceAutoRegistro,
    Supervisores,
    JefesDeCuadrilla,
    APKLink,
    Banco,
    CuentaOrigen,
    RegistroPagoTransferencia,
    RegistroPagoEfectivo,
    Tramos,
    FolioTransportista,
    PagoTransportista,
    DetallePagoTransportista,
    ProformaTransportista,
    MesCerrado,
    Haberes,
    Descuentos,
    TrabajadorHaber,
    TrabajadorDescuento,
    FacturaCompraSIIDistribuida,
    Cuenta,
    FacturaCompraSIIPorDistribuir,
    ConfiguracionSIIAutomaticaVenta,
    FacturaVentaSIIPorDistribuir,
    FacturaVentaSIIDistribuida,
    CartolaMovimiento,
    RegistroIngreso,
    RegistroEgreso,
)

class LoginSerializer(serializers.Serializer):
    rut = serializers.CharField(max_length=255)
    password = serializers.CharField(style={'input_type': 'password'})

class HoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Holding
        fields = ['id', 'nombre','estado']  # Se incluyen ambos campos
        read_only_fields = ['id']  # Se marca 'id' como solo lectura

class SociedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sociedad
        fields = ['id','holding','estado','rol_sociedad','nombre','nombre_representante','rut_representante','comuna','ciudad','calle']  
        read_only_fields = ['id'] 

class ModulosWebSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModulosWeb
        fields = '__all__'

class SubModulosWebSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubModulosWeb
        fields = '__all__'

class ModulosMovilSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModulosMovil
        fields = '__all__'

class SubModulosMovilSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubModulosMovil
        fields = '__all__'

class AdminSerializer(serializers.ModelSerializer):
    holding_nombre = serializers.CharField(source='holding.nombre', read_only=True)
    nombre = serializers.CharField(source='persona.nombres', read_only=True)  # Nombre desde PersonalTrabajadores
    rut = serializers.CharField(source='persona.rut', read_only=True)  # RUT desde PersonalTrabajadores
    
    class Meta:
        model = Usuarios
        fields = [
            'id', 'nombre', 'rut', 'email', 'holding', 'holding_nombre', 
            'estado', 'is_admin', 'persona'
        ]
        read_only_fields = ['id', 'nombre', 'rut', 'holding_nombre']
        extra_kwargs = {
            'is_admin': {'default': True},
            'estado': {'default': True}
        }

    def to_representation(self, instance):
        """
        Personalizar la representación para manejar casos donde no hay persona asociada
        """
        data = super().to_representation(instance)
        
        # Si no hay persona asociada, usar valores por defecto
        if not instance.persona:
            data['nombre'] = 'Sin nombre asignado'
            data['rut'] = 'Sin RUT asignado'
        
        return data

class PerfilesSerializer(serializers.ModelSerializer):
    modulos_web = serializers.SerializerMethodField()
    submodulos_web = serializers.SerializerMethodField()
    modulos_movil = serializers.SerializerMethodField()
    submodulos_movil = serializers.SerializerMethodField()

    class Meta:
        model = Perfiles
        fields = '__all__'

    def get_modulos_web(self, obj):
        return [modulo.nombre for modulo in obj.modulos_web.all()]

    def get_submodulos_web(self, obj):
        return [submodulo.nombre for submodulo in obj.submodulos_web.all()]

    def get_modulos_movil(self, obj):
        return [modulo.nombre for modulo in obj.modulos_movil.all()]

    def get_submodulos_movil(self, obj):
        return [submodulo.nombre for submodulo in obj.submodulos_movil.all()]

#------------------------------------------------------------------------------------------------------------------------------------------------------    
#-------------------------------USUARIOS SERIALIZADORES------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------
from django.conf import settings

class PersonalForUserSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = PersonalTrabajadores
        fields = ['id', 'nombre_completo', 'rut', 'correo']

    def get_nombre_completo(self, obj):
        apellidos = obj.apellidos if obj.apellidos else ''
        return f"{obj.nombres} {apellidos}".strip()
    
class UserSerializer(serializers.ModelSerializer):
    nombre_perfil = serializers.SerializerMethodField(read_only=True)
    nombre_persona = serializers.SerializerMethodField(read_only=True)
    nombre_empresas_asignadas = serializers.SerializerMethodField(read_only=True)
    empresas_asignadas = serializers.PrimaryKeyRelatedField(queryset=Sociedad.objects.all(), many=True, required=False)
    
    # ✅ CAMPO OPCIONAL PARA CONTROLAR ENVÍO DE EMAIL
    enviar_credenciales = serializers.BooleanField(write_only=True, required=False, default=True)
    
    class Meta:
        model = Usuarios
        fields = ['id', 'holding', 'empresas_asignadas', 'nombre_persona', 'persona', 'rut', 'email', 
                  'perfil', 'nombre_perfil', 'nombre_empresas_asignadas', 'estado', 'enviar_credenciales']
        extra_kwargs = {
            'holding': {'write_only': True},
            'is_admin': {'default': False},
            'estado': {'default': True},
        }

    def get_nombre_perfil(self, obj):
        if obj.perfil:
            return obj.perfil.nombre_perfil
        return None

    def get_nombre_persona(self, obj):
        if obj.persona:
            return obj.persona.nombres
        return None

    def get_nombre_empresas_asignadas(self, obj):
        return [empresa.nombre for empresa in obj.empresas_asignadas.all()]

    def generate_random_password(self, length=10):
        """
        ✅ Genera una contraseña random segura
        Formato: Al menos 1 mayúscula, 1 minúscula, 1 número, 1 símbolo
        """
        print(f"🔐 Generando contraseña de {length} caracteres...")
        
        # Caracteres seguros
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase  
        digits = string.digits
        symbols = "!@#$%&*"
        all_chars = uppercase + lowercase + digits + symbols
        
        # Garantizar al menos uno de cada tipo
        password = [
            random.choice(uppercase),   # Al menos 1 mayúscula
            random.choice(lowercase),   # Al menos 1 minúscula
            random.choice(digits),      # Al menos 1 número
            random.choice(symbols)      # Al menos 1 símbolo
        ]
        
        # Completar con caracteres aleatorios
        for _ in range(length - 4):
            password.append(random.choice(all_chars))
        
        # Mezclar para que no sea predecible
        random.shuffle(password)
        
        password_str = ''.join(password)
        print(f"✅ Contraseña generada exitosamente: {password_str}")
        
        return password_str

    def send_credentials_email(self, usuario, password):
        """
        ✅ Envía credenciales por email con formato profesional
        """
        print(f"📧 Intentando enviar credenciales a: {usuario.email}")
        
        try:
            # Obtener datos del usuario
            nombre_usuario = "Usuario"
            if usuario.persona and usuario.persona.nombres:
                nombre_completo = f"{usuario.persona.nombres}"
                if usuario.persona.apellidos:
                    nombre_completo += f" {usuario.persona.apellidos}"
                nombre_usuario = nombre_completo
            
            perfil_nombre = "Sin perfil asignado"
            if usuario.perfil:
                perfil_nombre = usuario.perfil.nombre_perfil
            
            holding_nombre = "Sistema"
            if usuario.holding:
                holding_nombre = usuario.holding.nombre
            
            # Configurar email
            subject = f'🔐 Credenciales de acceso - {holding_nombre}'
            
            message = f"""
¡Hola {nombre_usuario}!

Se ha creado tu cuenta de usuario en el sistema {holding_nombre}. 

📋 DETALLES DE TU CUENTA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 Nombre: {nombre_usuario}
🆔 RUT: {usuario.rut}
📧 Email: {usuario.email}
🎭 Perfil: {perfil_nombre}

🔐 CREDENCIALES DE ACCESO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Usuario: {usuario.rut}
Contraseña: {password}

⚠️ IMPORTANTE - SEGURIDAD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Esta es una contraseña TEMPORAL
• Te recomendamos cambiarla en tu primer inicio de sesión
• Puedes cambiarla usando la opción "¿Olvidaste tu contraseña?" 
• No compartas estas credenciales con nadie
• Guarda esta información en un lugar seguro

🌐 CÓMO ACCEDER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Ve http://contratista.
2. Ingresa tu RUT: {usuario.rut}
3. Ingresa tu contraseña temporal
4. Cambia tu contraseña por una personal

Si tienes problemas para acceder, contacta al administrador del sistema.

¡Bienvenido/a al equipo!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Este es un mensaje automático del sistema.
Terrasoft © 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """
            
            # Enviar email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=False,
            )
            
            print(f"✅ Email enviado exitosamente a {usuario.email}")
            return True
            
        except Exception as e:
            print(f"❌ Error enviando email a {usuario.email}: {str(e)}")
            print(f"   Detalles del error: {type(e).__name__}")
            return False

    def create(self, validated_data):
        """
        ✅ Crea usuario con contraseña random y envío automático de credenciales
        """
        print(f"🚀 Iniciando creación de usuario...")
        
        # Extraer datos
        empresas_asignadas_data = validated_data.pop('empresas_asignadas', [])
        enviar_credenciales = validated_data.pop('enviar_credenciales', True)
        
        # Generar contraseña temporal
        password_temporal = self.generate_random_password()
        
        # Crear usuario
        print(f"👤 Creando usuario con RUT: {validated_data.get('rut')}")
        usuario = Usuarios.objects.create(**validated_data)
        
        # Establecer contraseña hasheada
        usuario.set_password(password_temporal)
        usuario.save()
        print(f"✅ Usuario creado con ID: {usuario.id}")
        
        # Asignar empresas
        if empresas_asignadas_data:
            usuario.empresas_asignadas.set(empresas_asignadas_data)
            print(f"🏢 Empresas asignadas: {len(empresas_asignadas_data)}")
        
        # Enviar credenciales por email
        if enviar_credenciales and usuario.email:
            email_enviado = self.send_credentials_email(usuario, password_temporal)
            if email_enviado:
                print(f"📧 Credenciales enviadas exitosamente")
            else:
                print(f"⚠️ No se pudieron enviar las credenciales por email")
        elif not enviar_credenciales:
            print(f"📧 Envío de credenciales deshabilitado por configuración")
        else:
            print(f"⚠️ Usuario sin email, no se pueden enviar credenciales")
        
        print(f"🎉 Usuario creado completamente: {usuario.rut}")
        return usuario

    def update(self, instance, validated_data):
        """
        ✅ Actualizar usuario (sin modificar contraseña)
        """
        print(f"✏️ Actualizando usuario ID: {instance.id}")
        
        empresas_asignadas_data = validated_data.pop('empresas_asignadas', [])
        validated_data.pop('enviar_credenciales', None)  # No aplicable en update
        
        # Actualizar campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar empresas
        if 'empresas_asignadas' in validated_data or empresas_asignadas_data:
            instance.empresas_asignadas.set(empresas_asignadas_data)
        
        print(f"✅ Usuario actualizado: {instance.rut}")
        return instance

class SupervisorSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.persona.nombres', read_only=True)
    usuario_rut = serializers.CharField(source='usuario.rut', read_only=True)
    trabajadores_count = serializers.SerializerMethodField()
    trabajadores_detail = serializers.SerializerMethodField()
    jefes_cuadrilla = serializers.SerializerMethodField()
    
    class Meta:
        model = Supervisores
        fields = ['id', 'holding', 'usuario', 'usuario_nombre', 'usuario_rut', 
                 'trabajadores', 'trabajadores_count', 'trabajadores_detail',
                 'jefes_cuadrilla']
        read_only_fields = ['id']

    def get_trabajadores_count(self, obj):
        # Cuenta trabajadores directos + trabajadores bajo jefes de cuadrilla
        trabajadores_directos = obj.trabajadores.count()
        trabajadores_indirectos = PersonalTrabajadores.objects.filter(
            jefe_cuadrilla__supervisor=obj
        ).count()
        return {
            'directos': trabajadores_directos,
            'indirectos': trabajadores_indirectos,
            'total': trabajadores_directos + trabajadores_indirectos
        }

    def get_trabajadores_detail(self, obj):
        return [{
            'id': t.id,
            'nombre': t.nombres,
            'rut': t.rut,
            'tipo': 'directo'
        } for t in obj.trabajadores.all()]

    def get_jefes_cuadrilla(self, obj):
        jefes = JefesDeCuadrilla.objects.filter(supervisor=obj)
        return [{
            'id': j.id,
            'nombre': j.usuario.persona.nombres if j.usuario and j.usuario.persona else 'Sin nombre',
            'rut': j.usuario.rut if j.usuario else 'Sin RUT',
            'trabajadores_count': j.trabajadores.count()
        } for j in jefes]

class JefesDeCuadrillaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.persona.nombres', read_only=True)
    usuario_rut = serializers.CharField(source='usuario.rut', read_only=True)
    supervisor_nombre = serializers.CharField(source='supervisor.usuario.persona.nombres', read_only=True)
    supervisor_rut = serializers.CharField(source='supervisor.usuario.rut', read_only=True)
    trabajadores_count = serializers.SerializerMethodField()
    trabajadores_detail = serializers.SerializerMethodField()

    class Meta:
        model = JefesDeCuadrilla
        fields = ['id', 'holding', 'supervisor', 'usuario', 'trabajadores', 
                 'usuario_nombre', 'usuario_rut', 'supervisor_nombre', 
                 'supervisor_rut', 'trabajadores_count', 'trabajadores_detail']
        read_only_fields = ['id']

    def get_trabajadores_count(self, obj):
        return obj.trabajadores.count()

    def get_trabajadores_detail(self, obj):
        return [
            {
                'id': t.id,
                'nombre': t.nombres,
                'rut': t.rut,
            } for t in obj.trabajadores.all()
        ]

#------------------------------------------------------------------------------------------------------------------------------------------------------

class CamposClientesSerializer(serializers.ModelSerializer):
    nombre_cliente = serializers.SerializerMethodField()

    class Meta:
        model = CamposClientes
        fields = ['id','holding','cliente','nombre_cliente','nombre_campo', 'direccion_campo', 'comuna_campo']
        extra_kwargs = {
            'id': {'read_only': True},
            
        }

    def get_nombre_cliente(self, obj):
        if obj.cliente:
            return obj.cliente.nombre
        return None  

class ClienteSerializer(serializers.ModelSerializer):
    campos_personalizados = CamposClientesSerializer(many=True, read_only=True, source='campos_clientes')

    class Meta:
        model = Clientes
        fields = ['id','holding', 'rut', 'nombre', 'direccion', 'giro', 'campos_personalizados','rut_rep_legal','nombre_rep_legal','direccion_rep_legal']
        extra_kwargs = {
            'holding': {'write_only': True},
            'id': {'read_only': True},
        }

class AreaClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model =  AreasCliente
        fields = ['holding','id','nombre']
        extra_kwargs = {
            'holding': {'write_only': True},
            'id':{'read_only': True},
        }
        
class CargoClienteSerializer(serializers.ModelSerializer):
    nombre_area = serializers.SerializerMethodField()
    
    class Meta:
        model =  CargosCliente
        fields = ['holding','id','area','nombre','nombre_area']
        extra_kwargs = {
            'holding': {'write_only': True},
            'id':{'read_only': True},
        }

    def get_nombre_area(self, obj):
        if obj.area:
            return obj.area.nombre
        return None  

class AreaAdministracionSerializer(serializers.ModelSerializer):
    class Meta:
        model =  AreasAdministracion
        fields = ['holding','id','nombre']
        extra_kwargs = {
            'holding': {'write_only': True},
            'id':{'read_only': True},
        }
        
class CargoAdministracionSerializer(serializers.ModelSerializer):
    nombre_area = serializers.SerializerMethodField()
    class Meta:
        model =  CargosAdministracion
        fields = ['holding','id','area','nombre','nombre_area']
        extra_kwargs = {
            'holding': {'write_only': True},
            'id':{'read_only': True},
        }
    
    def get_nombre_area(self, obj):
        if obj.area:
            return obj.area.nombre
        return None  

class ContactosClienteSerializer(serializers.ModelSerializer):
    nombre_cliente = serializers.SerializerMethodField()
    nombre_campo_cliente = serializers.SerializerMethodField()
    nombre_area_cliente = serializers.SerializerMethodField()
    nombre_cargo_cliente = serializers.SerializerMethodField()

    class Meta:
        model =  ContactosClientes
        fields = ['id','holding','cliente','campo_cliente','area_cliente','cargo_cliente','nombre_contacto',
                  'rut_contacto','telefono','correo','nombre_cliente','nombre_campo_cliente','nombre_area_cliente',
                  'nombre_cargo_cliente']
        extra_kwargs = {
            'holding': {'write_only': True},
            'id':{'read_only': True},
        }

    def get_nombre_cliente(self, obj):
        if obj.cliente:
            return obj.cliente.nombre
        return None  

    def get_nombre_campo_cliente(self, obj):
        if obj.campo_cliente:
            return obj.campo_cliente.nombre_campo
        return None  
    
    def get_nombre_area_cliente(self, obj):
        if obj.area_cliente:
            return obj.area_cliente.nombre
        return None  
    
    def get_nombre_cargo_cliente(self, obj):
        if obj.cargo_cliente:
            return obj.cargo_cliente.nombre
        return None  
    
class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model =  Areas
        fields = '__all__'
        extra_kwargs = {
            'holding': {'write_only': True},
            'id':{'read_only': True},
        }

class CargoSerializer(serializers.ModelSerializer):
    nombre_area = serializers.SerializerMethodField()

    class Meta:
        model =  Cargos
        fields = ['holding','id','area','nombre','nombre_area']
        extra_kwargs = {
            'holding': {'write_only': True},
            'id':{'read_only': True},
        }

    def get_nombre_area(self, obj):
    # Verificar si el usuario tiene un perfil asociado y retornar el nombre del perfil
        if obj.area:
            return obj.area.nombre
        return None  # Retorna None o cualquier valor por defecto si no hay perfil

class EmpresaTransporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpresasTransporte
        fields = '__all__'
        extra_kwargs = {
            'holding': {'write_only': True},
            'id':{'read_only': True},
        }

class VehiculosTransporteSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.SerializerMethodField()

    class Meta:
        model =  VehiculosTransporte
        fields = ['holding','id','empresa','ppu','modelo','year','color','num_pasajeros','marca','nombre_empresa']
        extra_kwargs = {
            'holding': {'write_only': True},
            'id':{'read_only': True},
        }

    def get_nombre_empresa(self, obj):
    # Verificar si el usuario tiene un perfil asociado y retornar el nombre del perfil
        if obj.empresa:
            return obj.empresa.nombre
        return None  # Retorna None o cualquier valor por defecto si no hay perfil

class ChoferesTransporteSerializer(serializers.ModelSerializer):
    nombre_empresa =  serializers.SerializerMethodField()
    modelo_vehiculo = serializers.SerializerMethodField()

    class Meta:
        model = ChoferesTransporte
        fields = ['holding','id','empresa','nombre','rut','licencia','nombre_empresa','vehiculo','modelo_vehiculo']
        extra_kwargs = {
            'holding': {'write_only': True},
            'id':{'read_only': True},
        }
    def get_nombre_empresa(self, obj):
    # Verificar si el usuario tiene un perfil asociado y retornar el nombre del perfil
        if obj.empresa:
            return obj.empresa.nombre
        return None  # Retorna None o cualquier valor por defecto si no hay perfil
    
    def get_modelo_vehiculo(self, obj):
    # Verificar si el usuario tiene un perfil asociado y retornar el nombre del perfil
        if obj.vehiculo:
            return obj.vehiculo.modelo
        return None  # Retorna None o cualquier valor por defecto si no hay perfil
    
class SaludTrabajadoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaludTrabajadores
        fields = ['holding', 'id', 'nombre', 'porcentaje_descuento']
        extra_kwargs = {
            'holding': {'write_only': True},
            'id': {'read_only': True},
        }

class AFPTrabajadoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = AFPTrabajadores
        fields = ['holding', 'id', 'nombre', 'porcentaje_descuento']
        extra_kwargs = {
            'holding': {'write_only': True},
            'id': {'read_only': True},
        }

class CasasTrabajadoresSerializer(serializers.ModelSerializer):

    class Meta:
        model= CasasTrabajadores
        fields = ['id','holding','nombre','estado']
        extra_kwargs = {
            'holding': {'write_only': True},
            'id':{'read_only': True},
        }

class PersonalTrabajadoresSerializer(serializers.ModelSerializer):
    
    nombre_area = serializers.SerializerMethodField()
    nombre_cargo = serializers.SerializerMethodField()
    nombre_afp = serializers.SerializerMethodField()
    nombre_salud = serializers.SerializerMethodField()
    nombre_sociedad = serializers.SerializerMethodField()
    nombre_casa = serializers.SerializerMethodField()
    nombre_fundo = serializers.SerializerMethodField()
    nombre_banco = serializers.SerializerMethodField()
    rut = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    dni = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    nic = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    carnet_front_image = serializers.ImageField(required=False, allow_null=True)
    carnet_back_image = serializers.ImageField(required=False, allow_null=True)
    firma = serializers.ImageField(required=False, allow_null=True)
    sueldo_base = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    
    class Meta:
        model = PersonalTrabajadores
        fields = [
            'id', 'holding', 'sociedad', 'nombre_sociedad', 'area', 'nombre_area', 'cargo', 'nombre_cargo', 'nombres', 'apellidos',
            'rut', 'dni', 'nic', 'direccion', 'afp', 'nombre_afp', 'salud','nombre_salud', 'fecha_ingreso',
            'fecha_finiquito', 'metodo_pago', 'banco','nombre_banco', 'tipo_cuenta_bancaria',
            'numero_cuenta', 'nacionalidad', 'sexo', 'telefono', 'correo', 'estado', 'carnet_front_image','carnet_back_image',
            'firma', 'estado_civil', 'fecha_nacimiento', 'casa', 'nombre_casa', 'fundo', 'nombre_fundo', 'sueldo_base'
        ]
        extra_kwargs = {
            'holding': {'write_only': True},
            'id': {'read_only': True},
        }

    def get_nombre_banco(self, obj):
        if obj.banco:
            return obj.banco.nombre
        return None

    def get_nombre_fundo(self, obj):
        if obj.fundo:
            return obj.fundo.nombre_campo
        return None

    def get_nombre_area(self, obj):
        if obj.area:
            return obj.area.nombre
        return None  
   
    def get_nombre_cargo(self, obj):
        if obj.cargo:
            return obj.cargo.nombre
        return None  
    
    def get_nombre_afp(self, obj):
        if obj.afp:
            return obj.afp.nombre
        return None  
    
    def get_nombre_salud(self, obj):
        if obj.salud:
            return obj.salud.nombre
        return None  

    def get_nombre_sociedad(self, obj):
        if obj.sociedad:
            return obj.sociedad.nombre
        return None

    def get_nombre_casa(self, obj):
        if obj.casa:
            return obj.casa.nombre
        return None

    def create(self, validated_data):
        # Manejar la carga de archivos de manera específica si es necesario
        carnet_front = validated_data.pop('carnet_front_image', None)
        carnet_back = validated_data.pop('carnet_back_image', None)
        firma = validated_data.pop('firma', None)

        personal = PersonalTrabajadores.objects.create(**validated_data)

        if carnet_front:
            personal.carnet_front_image = carnet_front
        if carnet_back:
            personal.carnet_back_image = carnet_back
        if firma:
            personal.firma = firma

        personal.save()
        return personal

    def update(self, instance, validated_data):
        # Evitar la actualización de imágenes si no se proporcionaron nuevas
        validated_data.pop('carnet_front_image', None)
        validated_data.pop('carnet_back_image', None)
        validated_data.pop('firma', None)
        
        return super().update(instance, validated_data)
    
class UnidadControlSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnidadControl
        fields = ['holding','id','nombre','cantidad','estado']
        extra_kwargs = {
            'holding': {'write_only': True},
            'id':{'read_only': True},
        }

class LaboresSerializer(serializers.ModelSerializer):
    nombre_unidad_control = serializers.SerializerMethodField()

    class Meta:
        model = Labores
        fields = ['holding','id','nombre','especie','unidad_control','nombre_unidad_control','estado']
        extra_kwargs = {
            'holding': {'write_only': True},
            'id':{'read_only': True},
            'nombre_unidad_control':{'read_only': True},
        }
    def get_nombre_unidad_control(self,obj):
        if obj.unidad_control:
            return obj.unidad_control.nombre
        return None

#-----------------------------------------------------------------------------------------------------------    
#-------------------------------FOLIOCOMERCIAL SERIALIZADORES-----------------------------------------------
#-----------------------------------------------------------------------------------------------------------

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiculosTransporte
        fields = ['id', 'modelo']

class TransportistaConVehiculosSerializer(serializers.ModelSerializer):
    vehiculos = serializers.SerializerMethodField()
    
    class Meta:
        model = EmpresasTransporte
        fields = ['id', 'nombre', 'vehiculos']
    
    def get_vehiculos(self, obj):
        # Filtramos los vehículos que pertenecen a este transportista y están en el folio actual
        folio = self.context.get('folio')
        if not folio:
            return []
        vehiculos = folio.vehiculos.filter(empresa=obj)
        return VehiculoSerializer(vehiculos, many=True).data

class FundoSimpleSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='nombre_campo')
    
    class Meta:
        model = CamposClientes
        fields = ['id', 'nombre']

class LaborSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labores
        fields = ['id', 'nombre']

class FolioComercialSerializer(serializers.ModelSerializer):
    # Campos de lectura
    cliente = serializers.PrimaryKeyRelatedField(queryset=Clientes.objects.all())
    nombre_cliente = serializers.CharField(source='cliente.nombre', read_only=True)
    fundos = FundoSimpleSerializer(many=True, read_only=True)
    labores = LaborSimpleSerializer(many=True, read_only=True)
    nombres_fundos = serializers.SerializerMethodField()
    nombres_labores = serializers.SerializerMethodField()
    nombres_transportistas = serializers.SerializerMethodField()
    nombres_vehiculos = serializers.SerializerMethodField()
    
    # Campos para escritura
    fundos_ids = serializers.PrimaryKeyRelatedField(
        source='fundos',
        write_only=True,
        many=True,
        queryset=CamposClientes.objects.all()
    )
    labores_ids = serializers.PrimaryKeyRelatedField(
        source='labores',
        write_only=True,
        many=True,
        queryset=Labores.objects.all()
    )
    transportistas_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = FolioComercial
        fields = [
            'id', 'cliente', 'nombre_cliente','holding',
            'fundos', 'fundos_ids', 'nombres_fundos',
            'labores', 'labores_ids', 'nombres_labores',
            'transportistas_data', 'nombres_transportistas',
            'nombres_vehiculos',
            'fecha_inicio_contrato', 'fecha_termino_contrato',
            'valor_pago_trabajador', 'valor_facturacion',
            'estado'
        ]

    def get_nombres_fundos(self, obj):
        return ', '.join([fundo.nombre_campo for fundo in obj.fundos.all()])

    def get_nombres_labores(self, obj):
        return ', '.join([labor.nombre for labor in obj.labores.all()])

    def get_nombres_transportistas(self, obj):
        return ', '.join([transportista.nombre for transportista in obj.transportistas.all()])

    def get_nombres_vehiculos(self, obj):
        vehiculos = obj.vehiculos.all()
        return ', '.join([f"{vehiculo.modelo} ({vehiculo.ppu})" for vehiculo in vehiculos])

    def create(self, validated_data):
        fundos = validated_data.pop('fundos', [])
        labores = validated_data.pop('labores', [])
        transportistas_data = validated_data.pop('transportistas_data', [])
        
        # Crear el folio comercial con los datos básicos
        folio = FolioComercial.objects.create(**validated_data)
        
        # Asignar fundos y labores
        folio.fundos.set(fundos)
        folio.labores.set(labores)
        
        # Procesar transportistas y sus vehículos
        for transportista_data in transportistas_data:
            transportista_id = transportista_data.get('id')
            vehiculos = transportista_data.get('vehiculos', [])
            
            if transportista_id:
                folio.transportistas.add(transportista_id)
                # Agregar vehículos asociados
                vehiculo_ids = [v.get('id') for v in vehiculos if v.get('id')]
                folio.vehiculos.add(*vehiculo_ids)
        
        return folio

    def update(self, instance, validated_data):
        # Extraer las relaciones ManyToMany
        fundos = validated_data.pop('fundos', None)
        labores = validated_data.pop('labores', None)
        transportistas_data = validated_data.pop('transportistas_data', None)

        # Actualizar el cliente si está presente
        if 'cliente' in validated_data:
            instance.cliente = validated_data.pop('cliente')
        
        # Actualizar campos básicos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Actualizar relaciones si se proporcionaron
        if fundos is not None:
            instance.fundos.set(fundos)
        
        if labores is not None:
            instance.labores.set(labores)
        
        if transportistas_data is not None:
            instance.transportistas.clear()
            instance.vehiculos.clear()
            
            for transportista_data in transportistas_data:
                transportista_id = transportista_data.get('id')
                vehiculos = transportista_data.get('vehiculos', [])
                
                if transportista_id:
                    instance.transportistas.add(transportista_id)
                    vehiculo_ids = [v.get('id') for v in vehiculos if v.get('id')]
                    instance.vehiculos.add(*vehiculo_ids)
        
        instance.save()
        return instance

    def to_representation(self, instance):
        # Obtener la representación base
        representation = super().to_representation(instance)
        
        # Asegurarnos de que los campos de fecha estén en el formato correcto
        if representation.get('fecha_inicio_contrato'):
            representation['fecha_inicio_contrato'] = instance.fecha_inicio_contrato.strftime('%Y-%m-%d')
        if representation.get('fecha_termino_contrato'):
            representation['fecha_termino_contrato'] = instance.fecha_termino_contrato.strftime('%Y-%m-%d')
            
        return representation

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------


class PersonalTrabajadoresMobileSerializer(serializers.ModelSerializer):
    """
    Serializer para la creación de trabajadores desde móviles.
    CORREGIDO: Solo campos que existen en el modelo con tipos correctos.
    """
    carnet_front_image = serializers.ImageField(required=False, allow_null=True)
    carnet_back_image = serializers.ImageField(required=False, allow_null=True)
    firma = serializers.ImageField(required=False, allow_null=True)
    
    # Campos opcionales para trabajadores chilenos/extranjeros
    rut = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    dni = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    nic = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    
    class Meta:
        model = PersonalTrabajadores
        fields = [
            # Campos básicos que SÍ existen en el modelo
            'id', 'holding', 'sociedad', 'fundo', 'area', 'cargo', 
            'afp', 'salud', 'banco', 'casa', 'transportista', 'vehiculo',
            
            # Información personal
            'nombres', 'apellidos', 'rut', 'dni', 'nic', 
            'nacionalidad', 'sexo', 'estado_civil', 'telefono', 
            'correo', 'direccion', 'fecha_nacimiento',
            
            # Fechas laborales
            'fecha_ingreso', 'fecha_finiquito',
            
            # Información bancaria
            'metodo_pago', 'tipo_cuenta_bancaria', 'numero_cuenta',
            
            # Archivos
            'carnet_front_image', 'carnet_back_image', 'firma',
            
            # Otros campos
            'estado', 'sueldo_base',
        ]
        
        extra_kwargs = {
            'id': {'read_only': True},
            'holding': {'write_only': True},
            
            # ForeignKeys - SOLO allow_null, NO allow_blank
            'sociedad': {'required': False, 'allow_null': True},
            'fundo': {'required': False, 'allow_null': True},
            'area': {'required': False, 'allow_null': True},
            'cargo': {'required': False, 'allow_null': True},
            'afp': {'required': False, 'allow_null': True},
            'salud': {'required': False, 'allow_null': True},
            'banco': {'required': False, 'allow_null': True},
            'casa': {'required': False, 'allow_null': True},
            'transportista': {'required': False, 'allow_null': True},
            'vehiculo': {'required': False, 'allow_null': True},
            
            # CharFields/TextFields - allow_blank=True
            'apellidos': {'required': False, 'allow_blank': True},
            'nacionalidad': {'required': False, 'allow_blank': True},
            'sexo': {'required': False, 'allow_blank': True},
            'estado_civil': {'required': False, 'allow_blank': True},
            'telefono': {'required': False, 'allow_blank': True},
            'correo': {'required': False, 'allow_blank': True},
            'direccion': {'required': False, 'allow_blank': True},
            'metodo_pago': {'required': False, 'allow_blank': True},
            'tipo_cuenta_bancaria': {'required': False, 'allow_blank': True},
            
            # DateFields - allow_null=True
            'fecha_nacimiento': {'required': False, 'allow_null': True},
            'fecha_ingreso': {'required': False, 'allow_null': True},
            'fecha_finiquito': {'required': False, 'allow_null': True},
            
            # IntegerField
            'numero_cuenta': {'required': False, 'allow_null': True},
            
            # DecimalField
            'sueldo_base': {'required': False, 'allow_null': True},
            
            # BooleanField
            'estado': {'default': True},
        }

    def to_internal_value(self, data):
        """
        Filtrar automáticamente campos que NO existen en el modelo
        y limpiar campos enteros que pueden llegar vacíos
        """
        # Campos válidos según el modelo PersonalTrabajadores
        valid_fields = set(self.Meta.fields)
        
        # Filtrar solo campos válidos
        filtered_data = {}
        ignored_fields = []
        
        for key, value in data.items():
            if key in valid_fields:
                # Limpiar campos enteros que pueden llegar como strings vacíos
                if key in ['numero_cuenta'] and value in ('', 'null', 'undefined', None):
                    filtered_data[key] = None
                else:
                    filtered_data[key] = value
            else:
                ignored_fields.append(f"{key}={value}")
        
        # Debug: mostrar campos ignorados
        if ignored_fields:
            print(f"[DEBUG] Campos ignorados: {', '.join(ignored_fields)}")
        
        # Llamar al método padre con datos filtrados
        return super().to_internal_value(filtered_data)
    def validate(self, data):
        """
        Validaciones personalizadas
        """
        # Validar que tenga RUT o DNI
        rut = data.get('rut', '').strip() if data.get('rut') else ''
        dni = data.get('dni', '').strip() if data.get('dni') else ''
        
        if not rut and not dni:
            raise serializers.ValidationError(
                "Debe proporcionar RUT (para chilenos) o DNI (para extranjeros)"
            )
        
        # Validar nombres (obligatorio)
        nombres = data.get('nombres', '').strip() if data.get('nombres') else ''
        
        if not nombres:
            raise serializers.ValidationError("Los nombres son obligatorios")
            
        return data

    def create(self, validated_data):
        """
        Crear un nuevo trabajador
        """
        return PersonalTrabajadores.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Actualizar trabajador existente
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class DataProduccionSerializer(serializers.Serializer):
    trabajadores = serializers.SerializerMethodField()
    labores = serializers.SerializerMethodField()
    unidades_control = serializers.SerializerMethodField()

    def get_trabajadores(self, obj):
        holding_id = self.context.get('holding_id')
        trabajadores = PersonalTrabajadores.objects.filter(holding_id=holding_id).exclude(codigo_supervisor__isnull=True)
        fecha_actual = date.today()

        resultado_trabajadores = []

        for t in trabajadores:
            registros = ProduccionTrabajador.objects.filter(trabajador=t, fecha_ingreso_produccion=fecha_actual)
            horas_registradas = sum(registro.horas for registro in registros)
            horario = Horarios.objects.filter(holding_id=holding_id).first()
            jornada = horario.jornada if horario else 0
            horas_restantes = max(jornada - horas_registradas, 0)

            if horas_restantes > 0:
                resultado_trabajadores.append({
                    'id': t.id,
                    'nombre': t.nombre,
                    'folio': t.folio.id,
                    'horas_restantes': horas_restantes
                })

        return resultado_trabajadores

    def get_labores(self, obj):
        holding_id = self.context.get('holding_id')
        labores = Labores.objects.filter(holding_id=holding_id)
        return [{'id': l.id, 'nombre': l.nombre, 'unidad_control': l.unidad_control.nombre} for l in labores]

    def get_unidades_control(self, obj):
        holding_id = self.context.get('holding_id')
        unidades_control = UnidadControl.objects.filter(holding_id=holding_id)
        return [{'id': uc.id, 'nombre': uc.nombre} for uc in unidades_control]

class HorarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Horarios
        fields = ['id', 'holding','jornada']
        extra_kwargs = {
            'holding': {'write_only' : True},
            'id':{'read_only' : True},
        }

class ProduccionTrabajadorSerializer(serializers.ModelSerializer):
    nombre_sociedad = serializers.SerializerMethodField()
    nombre_usuario_ingresa = serializers.SerializerMethodField()
    nombre_trabajador = serializers.SerializerMethodField()
    nombre_labor = serializers.SerializerMethodField()
    nombre_unidad_control = serializers.SerializerMethodField()

    class Meta:
        model = ProduccionTrabajador
        fields = ['id', 'holding', 'sociedad', 'nombre_sociedad', 'usuario_ingresa', 'nombre_usuario_ingresa', 'trabajador',
                   'nombre_trabajador','labor', 'nombre_labor', 'unidad_control', 'nombre_unidad_control', 'folio'
                   , 'hora_fecha_ingreso_produccion', 'peso_neto','peso_bruto', 'unidades_control']
        extra_kwargs = {
            'id': {'read_only': True},
        }
    
    def get_nombre_sociedad(self, obj):
        return obj.sociedad.nombre if obj.sociedad else None
    
    def get_nombre_usuario_ingresa(self, obj):
        return obj.usuario_ingresa.persona.nombres if obj.usuario_ingresa else None

    def get_nombre_trabajador(self, obj):
        return obj.trabajador.nombres if obj.trabajador else None
    
    def get_nombre_labor(self, obj):
        return obj.labor.nombre if obj.labor else None
    
    def get_nombre_unidad_control(self, obj):
        return obj.unidad_control.nombre if obj.unidad_control else None
    
class CodigoQRSerializer(serializers.ModelSerializer):

    class Meta:
        model = CodigoQR
        fields = ['id', 'trabajador', 'codigo_qr']
        extra_kwargs = {
            'id': {'read_only': True},
        }

class TrabajadoresCosechaQRSerializer(serializers.Serializer):
    nombres = serializers.CharField()
    apellidos = serializers.CharField()
    rut = serializers.CharField()

class PersonalTrabajadoresCuadrillaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalTrabajadores
        fields = ['id', 'nombres', 'apellidos', 'folio', 'codigo_supervisor']

class GrupoTrabajadoresSerializer(serializers.Serializer):
    folio_id = serializers.IntegerField()
    supervisor_id = serializers.IntegerField()
    folio_nombre = serializers.CharField()
    supervisor_nombre = serializers.CharField()
    trabajadores = PersonalTrabajadoresCuadrillaSerializer(many=True)

class CuadrillasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuadrillas
        fields = ['id', 'holding', 'usuario', 'trabajadores']

class EnlaceAutoRegistroSerializer(serializers.ModelSerializer):
    perfil_nombre = serializers.CharField(source='perfil.nombre_perfil', read_only=True)
    duracion_horas = serializers.IntegerField(write_only=True)
    url = serializers.CharField(source='get_full_url', read_only=True)
    ruts_permitidos = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        allow_null=True
    )

    class Meta:
        model = EnlaceAutoRegistro
        fields = ['id', 'token', 'holding', 'perfil', 'perfil_nombre', 
                 'fecha_expiracion', 'ruts_permitidos', 'activo', 
                 'duracion_horas', 'url']
        read_only_fields = ['id', 'token', 'fecha_creacion', 'url', 'fecha_expiracion']

    def create(self, validated_data):
        # Extraer y eliminar duracion_horas de los datos validados
        duracion_horas = validated_data.pop('duracion_horas', 24)
        
        # Calcular fecha de expiración
        fecha_expiracion = timezone.now() + timezone.timedelta(hours=duracion_horas)
        
        # Agregar fecha_expiracion a los datos validados
        validated_data['fecha_expiracion'] = fecha_expiracion
        
        # Limpiar ruts_permitidos si está vacío
        if 'ruts_permitidos' in validated_data and not validated_data['ruts_permitidos']:
            validated_data['ruts_permitidos'] = None
            
        return super().create(validated_data)

    def to_representation(self, instance):
        # Añadir tiempo restante en la respuesta
        data = super().to_representation(instance)
        tiempo_restante = instance.fecha_expiracion - timezone.now()
        data['horas_restantes'] = max(0, tiempo_restante.total_seconds() / 3600)
        return data

class APKLinkSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo APKLink que maneja la conversión de los enlaces
    de descarga a JSON y viceversa. Incluye campos calculados para la URL de descarga
    y el tiempo restante.
    """
    url = serializers.CharField(source='get_full_url', read_only=True)
    duracion_horas = serializers.IntegerField(write_only=True, default=24)
    tiempo_restante = serializers.FloatField(read_only=True)

    class Meta:
        model = APKLink
        fields = [
            'id', 
            'holding', 
            'token',
            'fecha_creacion', 
            'fecha_expiracion', 
            'activo',
            'url', 
            'duracion_horas', 
            'tiempo_restante'
        ]
        read_only_fields = [
            'id', 
            'token', 
            'fecha_creacion', 
            'fecha_expiracion', 
            'url'
        ]

    def create(self, validated_data):
        """
        Sobrescribe el método create para manejar el campo duracion_horas,
        calculando la fecha de expiración antes de crear el enlace.
        """
        duracion_horas = validated_data.pop('duracion_horas', 24)
        fecha_expiracion = timezone.now() + timezone.timedelta(hours=duracion_horas)
        validated_data['fecha_expiracion'] = fecha_expiracion
        return super().create(validated_data)

    def to_representation(self, instance):
        """
        Personaliza la representación del enlace para incluir el tiempo restante
        calculado en el momento de la serialización.
        """
        data = super().to_representation(instance)
        data['tiempo_restante'] = instance.tiempo_restante()
        return data
    
class PersonalAsignadoSerializer(serializers.ModelSerializer):

    codigo_qr = serializers.SerializerMethodField()
    nombres = serializers.CharField()
    codigo_usuario = serializers.SerializerMethodField()
    cantidad_unidad_control = serializers.FloatField(default=0.0)

    class Meta:
        model = PersonalTrabajadores
        fields = ['id', 'nombres', 'codigo_qr', 'codigo_usuario', 'cantidad_unidad_control']

    def get_codigo_qr(self, obj):
        # Obtener el código QR asociado al trabajador
        try:
            qr = CodigoQR.objects.get(trabajador=obj)
            return qr.codigo_qr
        except CodigoQR.DoesNotExist:
            return None

    def get_codigo_usuario(self, obj):
        # Retornar el ID del usuario que tiene asignado este trabajador
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return request.user.id
        return None

class ProduccionTrabajadorReporteSerializer(serializers.ModelSerializer):
    trabajador_nombre = serializers.CharField(source='trabajador.nombres', read_only=True)
    supervisor_nombre = serializers.CharField(source='trabajador.supervisor_directo.first.usuario.persona.nombres', read_only=True)
    jefe_cuadrilla_nombre = serializers.CharField(source='trabajador.jefe_cuadrilla.first.usuario.persona.nombres', read_only=True)
    labor_nombre = serializers.CharField(source='labor.nombre', read_only=True)
    unidad_control_nombre = serializers.CharField(source='unidad_control.nombre', read_only=True)
    
    class Meta:
        model = ProduccionTrabajador
        fields = '__all__'

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------SERIALIZADORES DROPDWON INFORME PAGO-------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class CampoClienteDropdownPagoSerializer(serializers.ModelSerializer):
    """
    Serializer for Pago fundo (campo) information needed in the payment report
    """
    class Meta:
        model = CamposClientes
        fields = ['id', 'nombre_campo']

class SupervisorDropdownPagoSerializer(serializers.ModelSerializer):
    """
    Serializer for Pago supervisor information needed in the payment report.
    Includes the supervisor's name from the related user and personal info.
    """
    nombre = serializers.SerializerMethodField()

    class Meta:
        model = Supervisores
        fields = ['id', 'nombre']
    
    def get_nombre(self, obj):
        if obj.usuario and obj.usuario.persona:
            return f"{obj.usuario.persona.nombres} {obj.usuario.persona.apellidos}".strip()
        return "Sin nombre"

class CasaTrabajadorDropdownPagoSerializer(serializers.ModelSerializer):
    """
    Serializer for Pago worker house information needed in the payment report
    """
    class Meta:
        model = CasasTrabajadores
        fields = ['id', 'nombre']

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------SERIALIZADORES DATA INFORME PAGO-------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class ProduccionInformePagoDetalleSerializer(serializers.ModelSerializer):
    """
    Serializer for the detailed production payment report that calculates
    total payment based on production metrics and folio rates
    """
    nombre_labor = serializers.SerializerMethodField()
    valor_total = serializers.SerializerMethodField()
    unidad_medida = serializers.SerializerMethodField()
    cantidad = serializers.SerializerMethodField()

    class Meta:
        model = ProduccionTrabajador
        fields = [
            'nombre_labor',
            'cantidad',
            'unidad_medida',
            'valor_total'
        ]
    
    def get_nombre_labor(self, obj):
        return obj.labor.nombre if obj.labor else "Sin labor"

    def get_cantidad(self, obj):
        return obj.peso_neto if obj.peso_neto and obj.peso_neto > 0 else obj.unidades_control

    def get_unidad_medida(self, obj):
        if obj.peso_neto and obj.peso_neto > 0:
            return "Kg"
        
        if obj.unidad_control:
            return obj.unidad_control.nombre
        
        return "Sin unidad"

    def get_valor_total(self, obj):
        if not obj.folio:
            return 0
            
        cantidad = self.get_cantidad(obj)
        if cantidad is None:
            return 0
            
        return obj.folio.valor_pago_trabajador * cantidad
    
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------SERIALIZADORES CSV INFORME PAGO-------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class ProduccionCSVSerializer(serializers.ModelSerializer):
    """
    Serializer specifically designed for CSV export of worker production data.
    Includes worker details and daily production amounts.
    """
    nombre_trabajador = serializers.SerializerMethodField()
    rut_trabajador = serializers.SerializerMethodField()
    fecha_produccion = serializers.SerializerMethodField()
    valor_dia = serializers.SerializerMethodField()

    class Meta:
        model = ProduccionTrabajador
        fields = [
            'nombre_trabajador',
            'rut_trabajador',
            'fecha_produccion',
            'valor_dia'
        ]

    def get_nombre_trabajador(self, obj):
        if obj.trabajador:
            return f"{obj.trabajador.nombres} {obj.trabajador.apellidos}".strip()
        return "Sin nombre"

    def get_rut_trabajador(self, obj):
        return obj.trabajador.rut if obj.trabajador else "Sin RUT"

    def get_fecha_produccion(self, obj):
        """
        Convert datetime to date string in YYYY-MM-DD format.
        This handles the timezone information properly by extracting just the date.
        """
        if obj.hora_fecha_ingreso_produccion:
            return obj.hora_fecha_ingreso_produccion.date().isoformat()
        return None

    def get_valor_dia(self, obj):
        if not obj.folio:
            return 0
            
        cantidad = obj.peso_neto if obj.peso_neto and obj.peso_neto > 0 else obj.unidades_control
        if cantidad is None:
            return 0
            
        return obj.folio.valor_pago_trabajador * cantidad

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------SERIALIZADORES SOCIEDAD Y CUENTA BANCO-------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class BancoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banco
        fields = ['id','codigo_sbif', 'nombre']

class CuentaOrigenSerializer(serializers.ModelSerializer):
    banco_nombre = serializers.CharField(source='banco.nombre', read_only=True)
    
    class Meta:
        model = CuentaOrigen
        fields = ['id', 'sociedad', 'banco', 'banco_nombre', 'tipo_cuenta', 'numero_cuenta']
        read_only_fields = ['sociedad']

class SociedadCuentaSerializer(serializers.ModelSerializer):
    cuentas_origen = CuentaOrigenSerializer(many=True, read_only=True)
    
    class Meta:
        model = Sociedad
        fields = ['id', 'holding', 'rol_sociedad', 'nombre', 'nombre_representante', 
                 'rut_representante', 'comuna', 'ciudad', 'calle', 'cuentas_origen']
        read_only_fields = ['holding', 'nombre']

class ProduccionPendienteSerializer(serializers.ModelSerializer):
    trabajador_nombre = serializers.CharField(source='trabajador.nombres')
    trabajador_rut = serializers.CharField(source='trabajador.rut')
    monto_a_pagar = serializers.SerializerMethodField()

    class Meta:
        model = ProduccionTrabajador
        fields = ['id', 'trabajador_nombre', 'trabajador_rut', 'monto_a_pagar']

    def get_monto_a_pagar(self, obj):
        if obj.peso_neto and obj.peso_neto > 0:
            return obj.folio.valor_pago_trabajador * obj.peso_neto
        return obj.folio.valor_pago_trabajador * obj.unidades_control

class CamposClientesPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CamposClientes
        fields = ['id', 'nombre_campo', 'direccion_campo', 'comuna_campo']

class ClientesFiltroPagoSerializer(serializers.ModelSerializer):
    campos_clientes = CamposClientesPagoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Clientes
        fields = ['id', 'nombre', 'campos_clientes']

class CasasTrabajadoresPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CasasTrabajadores
        fields = ['id', 'nombre']

class CargosAdministracionPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CargosAdministracion
        fields = ['id', 'nombre']

class FiltrosPagoSerializer(serializers.ModelSerializer):
    cliente = ClientesFiltroPagoSerializer(source='folio.cliente', read_only=True)
    fundo = CamposClientesPagoSerializer(source='folio.fundos', many=True, read_only=True)
    trabajador_nombre = serializers.CharField(source='trabajador.nombres')
    trabajador_rut = serializers.CharField(source='trabajador.rut')
    trabajador_casa = serializers.CharField(source='trabajador.casa.nombre', allow_null=True)
    trabajador_cargo = serializers.CharField(source='trabajador.cargo.nombre', allow_null=True)
    monto_a_pagar = serializers.SerializerMethodField()

    class Meta:
        model = ProduccionTrabajador
        fields = [
            'id', 'cliente', 'fundo', 'trabajador_nombre', 'trabajador_rut',
            'trabajador_casa', 'trabajador_cargo', 'monto_a_pagar'
        ]

    def get_monto_a_pagar(self, obj):
        if obj.peso_neto and obj.peso_neto > 0:
            return obj.folio.valor_pago_trabajador * obj.peso_neto
        return obj.folio.valor_pago_trabajador * obj.unidades_control
    
class RegistroPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroPagoTransferencia
        fields = '__all__'

class PagoRealizadoSerializer(serializers.ModelSerializer):
    sociedad = SociedadSerializer()
    cuenta_origen = CuentaOrigenSerializer()
    trabajador = serializers.SerializerMethodField()
    tipo_pago = serializers.SerializerMethodField()
    multiplo = serializers.SerializerMethodField()

    class Meta:
        model = RegistroPagoTransferencia  # Base model, but will work for both
        fields = ['id', 'sociedad', 'cuenta_origen', 'trabajador', 
                 'monto_pagado', 'fecha_pago', 'tipo_pago', 'multiplo','saldo']

    def get_trabajador(self, obj):
        if obj.trabajador:
            return {
                'nombres': obj.trabajador.nombres,
                'rut': obj.trabajador.rut
            }
        return None

    def get_tipo_pago(self, obj):
        return 'Efectivo' if isinstance(obj, RegistroPagoEfectivo) else 'Transferencia'

    def get_multiplo(self, obj):
        return obj.multiplo_pago if isinstance(obj, RegistroPagoEfectivo) else None
    
class ProduccionPendienteEfectivoSerializer(serializers.ModelSerializer):
    trabajador_nombre = serializers.CharField(source='trabajador.nombres')
    trabajador_rut = serializers.CharField(source='trabajador.rut')
    monto_a_pagar = serializers.SerializerMethodField()

    class Meta:
        model = ProduccionTrabajador
        fields = ['id', 'trabajador_nombre', 'trabajador_rut', 'monto_a_pagar']

    def get_monto_a_pagar(self, obj):
        if obj.peso_neto and obj.peso_neto > 0:
            return obj.folio.valor_pago_trabajador * obj.peso_neto
        return obj.folio.valor_pago_trabajador * obj.unidades_control

class PlanillaEfectivoSerializer(serializers.ModelSerializer):
    trabajador_nombre = serializers.CharField(source='trabajador.nombres')
    trabajador_rut = serializers.CharField(source='trabajador.rut')
    pagos_diarios = serializers.SerializerMethodField()
    saldo_anterior = serializers.DecimalField(max_digits=10, decimal_places=2)
    monto_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    monto_redondeado = serializers.DecimalField(max_digits=10, decimal_places=2)
    saldo_pendiente = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = ProduccionTrabajador
        fields = ['trabajador_nombre', 'trabajador_rut', 'pagos_diarios', 
                 'saldo_anterior', 'monto_total', 'monto_redondeado', 'saldo_pendiente']

    def get_pagos_diarios(self, obj):
        return {
            str(obj.hora_fecha_ingreso_produccion.date()): obj.monto_a_pagar
        }
    
class TramosSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tramos
        fields = '__all__'

class FolioTransportistaSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para mostrar información relacionada
    nombre_folio_comercial = serializers.SerializerMethodField()
    nombre_tramo = serializers.SerializerMethodField()
    
    class Meta:
        model = FolioTransportista
        fields = [
            'id', 
            'holding', 
            'folio_comercial', 
            'nombre_folio_comercial',
            'valor_pago_transportista', 
            'valor_facturacion_transportista', 
            'tramo',
            'nombre_tramo'
        ]

    def get_nombre_folio_comercial(self, obj):
        if obj.folio_comercial and obj.folio_comercial.cliente:
            return f"{obj.folio_comercial.cliente.nombre}"
        return None

    def get_nombre_tramo(self, obj):
        if obj.tramo:
            return f"{obj.tramo.origen} - {obj.tramo.destino}"
        return None

    def validate(self, data):
        # Validar que los montos sean positivos
        if data.get('valor_pago_transportista', 0) <= 0:
            raise serializers.ValidationError(
                {'valor_pago_transportista': 'El valor de pago debe ser mayor que 0'}
            )
        if data.get('valor_facturacion_transportista', 0) <= 0:
            raise serializers.ValidationError(
                {'valor_facturacion_transportista': 'El valor de facturación debe ser mayor que 0'}
            )
        
        # Validar que el folio comercial pertenezca al holding correcto
        if data.get('folio_comercial') and data.get('holding'):
            if data['folio_comercial'].holding.id != data['holding'].id:
                raise serializers.ValidationError(
                    {'folio_comercial': 'El folio comercial debe pertenecer al mismo holding'}
                )

        # Validar que el tramo pertenezca al holding correcto
        if data.get('tramo') and data.get('holding'):
            if data['tramo'].holding.id != data['holding'].id:
                raise serializers.ValidationError(
                    {'tramo': 'El tramo debe pertenecer al mismo holding'}
                )

        return data

class PagoTransportistaSerializer(serializers.ModelSerializer):
    transportista_nombre = serializers.CharField(source='transportista.nombre', read_only=True)
    transportista_rut = serializers.CharField(source='transportista.rut', read_only=True)
    sociedad_nombre = serializers.CharField(source='sociedad.nombre', read_only=True)
    detalles = serializers.SerializerMethodField()
    
    class Meta:
        model = PagoTransportista
        fields = '__all__'
        
    def get_detalles(self, obj):
        return DetallePagoTransportistaSerializer(obj.detalles.all(), many=True).data

class DetallePagoTransportistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePagoTransportista
        fields = '__all__'

class CalculoPagoTransportistaSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    transportista_nombre = serializers.CharField()
    transportista_rut = serializers.CharField()
    tipo_pago = serializers.CharField()  # PASAJERO o VIAJE
    valor_unidad = serializers.DecimalField(max_digits=10, decimal_places=2)
    cantidad_personas = serializers.IntegerField()
    monto_calculado = serializers.DecimalField(max_digits=10, decimal_places=2)
    tramo = serializers.SerializerMethodField()

    def get_tramo(self, obj):
        if 'tramo' in obj:
            return {
                'origen': obj['tramo'].origen,
                'destino': obj['tramo'].destino
            }
        return None

class InformeTransportistaSerializer(serializers.Serializer):
    # Fields for POST request (report generation)
    # Date fields remain required=False to maintain compatibility
    fecha_inicio = serializers.DateField(required=False)
    fecha_fin = serializers.DateField(required=False)
    
    # Updated fields to handle multiple selections
    cliente_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_null=True,
        default=None
    )
    transportista_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_null=True,
        default=None
    )
    vehiculo_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_null=True,
        default=None
    )

    # Fields for GET request (dropdown data)
    clientes = serializers.SerializerMethodField()
    transportistas = serializers.SerializerMethodField()

    def get_clientes(self, obj):
        """
        Retrieves the list of clients for a given holding.
        For GET requests, obj will be the holding_id.
        """
        if isinstance(obj, str):
            try:
                clientes = Clientes.objects.filter(holding_id=obj)
                return [
                    {
                        'id': cliente.id,
                        'nombre': cliente.nombre
                    } 
                    for cliente in clientes
                ]
            except Exception as e:
                # Log the error but return empty list to prevent breaking the API
                print(f"Error fetching clientes: {str(e)}")
                return []
        return []

    def get_transportistas(self, obj):
        """
        Retrieves the list of transport companies and their vehicles for a given holding.
        For GET requests, obj will be the holding_id.
        """
        if isinstance(obj, str):
            try:
                transportistas = EmpresasTransporte.objects.filter(
                    holding_id=obj
                ).prefetch_related('vehiculostransporte_set')
                
                return [
                    {
                        'id': transportista.id,
                        'nombre': transportista.nombre,
                        'vehiculos': [
                            {
                                'id': vehiculo.id,
                                'ppu': vehiculo.ppu,
                                'modelo': vehiculo.modelo
                            } 
                            for vehiculo in transportista.vehiculostransporte_set.all()
                        ]
                    } 
                    for transportista in transportistas
                ]
            except Exception as e:
                # Log the error but return empty list to prevent breaking the API
                print(f"Error fetching transportistas: {str(e)}")
                return []
        return []

    def validate(self, data):
        """
        Performs cross-field validation and ensures data consistency.
        """
        # Validate date range if both dates are provided
        if data.get('fecha_inicio') and data.get('fecha_fin'):
            if data['fecha_inicio'] > data['fecha_fin']:
                raise serializers.ValidationError(
                    "La fecha de inicio debe ser anterior a la fecha de fin"
                )

        # Validate vehicle selection requires transporter selection
        if data.get('vehiculo_ids') and not data.get('transportista_ids'):
            raise serializers.ValidationError(
                "Debe seleccionar transportistas para filtrar por vehículos"
            )

        # Convert empty lists to None for consistent handling in the view
        for field in ['cliente_ids', 'transportista_ids', 'vehiculo_ids']:
            if field in data and not data[field]:
                data[field] = None

        return data

    def to_internal_value(self, data):
        """
        Handles conversion of input data before validation.
        Ensures backward compatibility with single ID fields.
        """
        # Convert single ID fields to list fields if present
        if 'cliente_id' in data and data['cliente_id']:
            data['cliente_ids'] = [data.pop('cliente_id')]
        if 'transportista_id' in data and data['transportista_id']:
            data['transportista_ids'] = [data.pop('transportista_id')]
        if 'vehiculo_id' in data and data['vehiculo_id']:
            data['vehiculo_ids'] = [data.pop('vehiculo_id')]

        return super().to_internal_value(data)
    
class ProformaTransportistaSerializer(serializers.ModelSerializer):
    sociedad_nombre = serializers.CharField(source='sociedad.nombre', read_only=True)
    transportista_nombre = serializers.CharField(source='transportista.nombre', read_only=True)
    transportista_rut = serializers.CharField(source='transportista.rut', read_only=True)

    class Meta:
        model = ProformaTransportista
        fields = [
            'id', 
            'sociedad_nombre',
            'transportista_nombre',
            'transportista_rut',
            'fecha_emision',
            'fecha_vencimiento',
            'fecha_inicio_periodo',
            'fecha_fin_periodo',
            'estado',
            'tramo',
            'tipo_servicio',
            'cantidad_personas',
            'valor_pago_transportista',
            'total',
            'factura_fecha',
            'factura_numero',
            'factura_rut',
            'factura_monto'
        ]

class InformeDiasTrabajadosSerializer(serializers.Serializer):
    """
    Serializador para el informe de días trabajados por trabajador y cliente.
    Ahora recibe año y mes en lugar de un rango de fechas.
    """
    year = serializers.IntegerField(required=True)
    mes = serializers.IntegerField(required=True, min_value=1, max_value=12)
    trabajador_id = serializers.IntegerField(required=False)
    cliente_id = serializers.IntegerField(required=False)
    fundo_id = serializers.IntegerField(required=False)
    supervisor_id = serializers.IntegerField(required=False)
    
    def validate(self, data):
        """
        Valida que el mes y año sean válidos
        """
        if data.get('mes') < 1 or data.get('mes') > 12:
            raise serializers.ValidationError("El mes debe estar entre 1 y 12")
        return data

class MesCerradoSerializer(serializers.ModelSerializer):
    usuario_cierre_nombre = serializers.CharField(source='usuario_cierre.persona.nombres', read_only=True)
    
    class Meta:
        model = MesCerrado
        fields = ['id', 'holding', 'mes', 'year', 'fecha_cierre', 'usuario_cierre', 
                  'usuario_cierre_nombre', 'motivo']
        read_only_fields = ['id', 'fecha_cierre', 'usuario_cierre_nombre']

class HaberesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Haberes
        fields = '__all__'
        extra_kwargs = {
            'holding': {'write_only': True},
            'id': {'read_only': True},
        }

class PersonalSimpleSerializer(serializers.ModelSerializer):
    """Serializador básico que muestra solo información básica del trabajador"""
    class Meta:
        model = PersonalTrabajadores
        fields = ['id', 'nombres', 'apellidos', 'rut']

class HaberSimpleSerializer(serializers.ModelSerializer):
    """Serializador simple para mostrar información básica de un haber"""
    class Meta:
        model = Haberes
        fields = ['id', 'nombre', 'tipo_valor', 'imponible']

class DescuentosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descuentos
        fields = '__all__'
        extra_kwargs = {
            'holding': {'write_only': True},
            'id': {'read_only': True},
        }

class DescuentoSimpleSerializer(serializers.ModelSerializer):
    """Serializador simple para mostrar información básica de un descuento"""
    class Meta:
        model = Descuentos
        fields = ['id', 'nombre', 'orden', 'cuota', 'cuenta_contable']


class TrabajadorHaberSerializer(serializers.ModelSerializer):
    haber = HaberSimpleSerializer(read_only=True)
    
    class Meta:
        model = TrabajadorHaber
        fields = ['haber', 'valor']

class TrabajadorDescuentoSerializer(serializers.ModelSerializer):
    """Serializador para la relación Trabajador-Descuento con información de cuotas"""
    descuento = DescuentoSimpleSerializer(read_only=True)  # Removed redundant source parameter
    id = serializers.IntegerField(source='descuento.id')
    nombre = serializers.CharField(source='descuento.nombre')
    valor = serializers.DecimalField(source='valor_total', max_digits=12, decimal_places=2)
    tipo = serializers.CharField(source='descuento.tipo', default='')
    tipo_valor = serializers.CharField(source='descuento.tipo_valor', default='')
    num_cuotas = serializers.IntegerField(default=1)
    cuota_actual = serializers.IntegerField(default=1)
    valor_cuota = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        model = TrabajadorDescuento
        fields = ['id', 'nombre', 'valor', 'tipo', 'tipo_valor', 'num_cuotas', 'cuota_actual', 'valor_cuota', 'descuento']

class PersonalConAsignacionesSerializer(serializers.ModelSerializer):
    """Serializador que muestra un trabajador con sus descuentos"""
    descuentos = TrabajadorDescuentoSerializer(source='descuentos_asignados', many=True, read_only=True)
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = PersonalTrabajadores
        fields = ['id', 'nombre_completo', 'rut', 'nacionalidad', 'descuentos']
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombres} {obj.apellidos or ''}".strip()
    
class ArchivoPreviewSerializer(serializers.Serializer):
    """
    Serializador para generar el archivo Previred.
    Recibe los IDs de trabajadores y el período (mes y año).
    """
    trabajador_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    mes = serializers.IntegerField(
        min_value=1,
        max_value=12,
        required=True
    )
    ano = serializers.IntegerField(
        required=True
    )

    def validate(self, data):
        """
        Validaciones adicionales:
        - El período no debe ser futuro
        - La lista de trabajadores no debe estar vacía
        """
        # Verificar que el período no sea futuro
        fecha_actual = timezone.now().date()
        fecha_periodo = datetime(data['ano'], data['mes'], 1).date()
        
        if fecha_periodo > fecha_actual:
            raise serializers.ValidationError(
                "No se puede generar un archivo Previred para un período futuro."
            )
        
        # Verificar que la lista de trabajadores no esté vacía
        if not data['trabajador_ids']:
            raise serializers.ValidationError(
                "Debe seleccionar al menos un trabajador."
            )
        
        return data

# Agregar al archivo serializers.py

class CuentaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Cuenta
    """
    class Meta:
        model = Cuenta
        fields = ['id', 'holding', 'nombre_cuenta', 'cuenta_contable', 'activa']
        extra_kwargs = {
            'holding': {'write_only': True},
            'id': {'read_only': True},
        }

class FacturaCompraSIIDistribuidaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo FacturaCompraSIIDistribuida
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_rut = serializers.CharField(source='cliente.rut', read_only=True)
    fundo_nombre = serializers.CharField(source='fundo.nombre_campo', read_only=True)
    labor_nombre = serializers.CharField(source='labor.nombre', read_only=True)
    cuenta_nombre = serializers.CharField(source='cuenta.nombre_cuenta', read_only=True)
    cuenta_codigo = serializers.CharField(source='cuenta.cuenta_contable', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario_distribuyente.persona.nombres', read_only=True)
    
    class Meta:
        model = FacturaCompraSIIDistribuida
        fields = [
            'id', 'holding', 'cliente', 'cliente_nombre', 'cliente_rut',
            'fundo', 'fundo_nombre', 'labor', 'labor_nombre',
            'cuenta', 'cuenta_nombre', 'cuenta_codigo',
            'folio', 'tipo_doc', 'tipo_compra', 'rut_proveedor', 'razon_social',
            'fecha_docto', 'fecha_recepcion', 'monto_total', 'monto_neto',
            'monto_exento', 'monto_iva_recuperable', 'observaciones',
            'usuario_distribuyente', 'usuario_nombre', 'fecha_distribucion'
        ]
        read_only_fields = ['id', 'fecha_distribucion', 'usuario_distribuyente']

class DistribucionFacturasSIISerializer(serializers.Serializer):
    """
    Serializer para manejar la distribución de facturas SII
    """
    facturas_seleccionadas = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        help_text="Lista de facturas seleccionadas para distribuir"
    )
    cliente_id = serializers.IntegerField(required=True)
    fundo_id = serializers.IntegerField(required=False, allow_null=True)
    labor_id = serializers.IntegerField(required=False, allow_null=True)
    cuenta_id = serializers.IntegerField(required=False, allow_null=True)
    observaciones = serializers.CharField(
        required=False, 
        allow_blank=True, 
        allow_null=True,
        max_length=1000,
        help_text="Observaciones sobre la distribución"
    )
    
    def validate_facturas_seleccionadas(self, value):
        """
        Valida que se hayan seleccionado facturas
        """
        if not value:
            raise serializers.ValidationError("Debe seleccionar al menos una factura")
        
        # Validar que cada factura tenga los campos requeridos
        required_fields = ['folio', 'tipo_doc', 'rut_proveedor', 'razon_social']
        for factura in value:
            for field in required_fields:
                if field not in factura or not factura[field]:
                    raise serializers.ValidationError(f"Falta el campo '{field}' en una de las facturas")
        
        return value
    
    def validate_cliente_id(self, value):
        """
        Valida que el cliente existe y pertenece al holding del usuario
        """
        try:
            # Obtener el holding del contexto de la request
            request = self.context.get('request')
            if not request or not request.user.holding:
                raise serializers.ValidationError("No se pudo determinar el holding")
            
            cliente = Clientes.objects.get(id=value, holding=request.user.holding)
            return value
        except Clientes.DoesNotExist:
            raise serializers.ValidationError("Cliente no encontrado")
    
    def validate_fundo_id(self, value):
        """
        Valida que el fundo existe (si se proporciona)
        """
        if value is not None:
            try:
                fundo = CamposClientes.objects.get(id=value)
                return value
            except CamposClientes.DoesNotExist:
                raise serializers.ValidationError("Fundo no encontrado")
        return value
    
    def validate_labor_id(self, value):
        """
        Valida que la labor existe (si se proporciona)
        """
        if value is not None:
            try:
                labor = Labores.objects.get(id=value)
                return value
            except Labores.DoesNotExist:
                raise serializers.ValidationError("Labor no encontrada")
        return value
    
    def validate_cuenta_id(self, value):
        """
        Valida que la cuenta existe (si se proporciona)
        """
        if value is not None:
            try:
                cuenta = Cuenta.objects.get(id=value)
                return value
            except Cuenta.DoesNotExist:
                raise serializers.ValidationError("Cuenta no encontrada")
        return value

class FundosClienteSerializer(serializers.ModelSerializer):
    """
    Serializer simple para fundos/campos de clientes
    """
    class Meta:
        model = CamposClientes
        fields = ['id', 'nombre_campo', 'direccion_campo', 'comuna_campo']

class LaboresSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simple para labores
    """
    class Meta:
        model = Labores
        fields = ['id', 'nombre', 'especie']

class DistribucionDataSerializer(serializers.Serializer):
    """
    Serializer para obtener los datos necesarios para la distribución
    """
    clientes = serializers.SerializerMethodField()
    fundos = serializers.SerializerMethodField()
    labores = serializers.SerializerMethodField()
    cuentas = serializers.SerializerMethodField()
    
    def get_clientes(self, obj):
        """
        Obtiene los clientes del holding
        """
        holding_id = obj.get('holding_id')
        if holding_id:
            clientes = Clientes.objects.filter(holding_id=holding_id)
            return [{'id': c.id, 'nombre': c.nombre, 'rut': c.rut} for c in clientes]
        return []
    
    def get_fundos(self, obj):
        """
        Obtiene los fundos disponibles (puede filtrarse por cliente)
        """
        holding_id = obj.get('holding_id')
        cliente_id = obj.get('cliente_id')
        
        if cliente_id:
            # Filtrar fundos por cliente específico
            fundos = CamposClientes.objects.filter(cliente_id=cliente_id)
        elif holding_id:
            # Obtener todos los fundos del holding
            fundos = CamposClientes.objects.filter(holding_id=holding_id)
        else:
            fundos = CamposClientes.objects.none()
        
        return FundosClienteSerializer(fundos, many=True).data
    
    def get_labores(self, obj):
        """
        Obtiene las labores del holding
        """
        holding_id = obj.get('holding_id')
        if holding_id:
            labores = Labores.objects.filter(holding_id=holding_id, estado=True)
            return LaboresSimpleSerializer(labores, many=True).data
        return []
    
    def get_cuentas(self, obj):
        """
        Obtiene las cuentas del holding
        """
        holding_id = obj.get('holding_id')
        if holding_id:
            cuentas = Cuenta.objects.filter(holding_id=holding_id, activa=True)
            return CuentaSerializer(cuentas, many=True).data
        return []
    
class DistribucionMultipleFacturaCompraSIISerializer(serializers.Serializer):
    """
    Serializer para manejar la distribución múltiple de UNA factura
    """
    # Identificación de la factura
    factura_id = serializers.IntegerField(required=True, help_text="ID de la factura a distribuir")
    
    # Datos de distribución
    cliente_id = serializers.IntegerField(required=True, help_text="ID del cliente al que se distribuye")
    fundo_id = serializers.IntegerField(required=False, allow_null=True, help_text="ID del fundo/campo")
    labor_id = serializers.IntegerField(required=False, allow_null=True, help_text="ID de la labor")
    cuenta_id = serializers.IntegerField(required=False, allow_null=True, help_text="ID de la cuenta contable")
    
    # Distribución por monto o porcentaje
    tipo_distribucion = serializers.ChoiceField(
        choices=[('MONTO', 'Por Monto'), ('PORCENTAJE', 'Por Porcentaje')],
        required=True,
        help_text="Tipo de distribución"
    )
    monto_a_distribuir = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        required=False, 
        allow_null=True,
        help_text="Monto específico a distribuir (requerido si tipo_distribucion = MONTO)"
    )
    porcentaje_a_distribuir = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False, 
        allow_null=True,
        help_text="Porcentaje a distribuir (requerido si tipo_distribucion = PORCENTAJE)"
    )
    
    # Observaciones
    observaciones = serializers.CharField(
        required=False, 
        allow_blank=True, 
        allow_null=True,
        max_length=1000,
        help_text="Observaciones sobre esta distribución específica"
    )
    
    def validate(self, data):
        """Validaciones cruzadas"""
        tipo_distribucion = data.get('tipo_distribucion')
        monto = data.get('monto_a_distribuir')
        porcentaje = data.get('porcentaje_a_distribuir')
        
        # Validar que se proporcione el campo correcto según el tipo
        if tipo_distribucion == 'MONTO':
            if not monto or monto <= 0:
                raise serializers.ValidationError(
                    "Debe especificar un monto válido mayor a 0 para distribución por monto"
                )
            if porcentaje is not None:
                raise serializers.ValidationError(
                    "No debe especificar porcentaje cuando se distribuye por monto"
                )
        elif tipo_distribucion == 'PORCENTAJE':
            if not porcentaje or porcentaje <= 0 or porcentaje > 100:
                raise serializers.ValidationError(
                    "Debe especificar un porcentaje válido entre 0.01 y 100 para distribución por porcentaje"
                )
            if monto is not None:
                raise serializers.ValidationError(
                    "No debe especificar monto cuando se distribuye por porcentaje"
                )
        
        return data
    
    def validate_factura_id(self, value):
        """Valida que la factura existe y no está completamente distribuida"""
        request = self.context.get('request')
        if not request or not request.user.holding:
            raise serializers.ValidationError("No se pudo determinar el holding")
        
        try:
            factura = FacturaCompraSIIPorDistribuir.objects.get(
                id=value,
                holding_id=request.user.holding.id
            )
        except FacturaCompraSIIPorDistribuir.DoesNotExist:
            raise serializers.ValidationError("Factura no encontrada")
        
        if factura.esta_completamente_distribuida():
            raise serializers.ValidationError("La factura ya está completamente distribuida")
        
        return value
    
    def validate_cliente_id(self, value):
        """Valida que el cliente existe y pertenece al holding"""
        request = self.context.get('request')
        if not request or not request.user.holding:
            raise serializers.ValidationError("No se pudo determinar el holding")
        
        try:
            Clientes.objects.get(id=value, holding=request.user.holding)
        except Clientes.DoesNotExist:
            raise serializers.ValidationError("Cliente no encontrado")
        
        return value

class DistribucionMultipleFacturaVentaSIISerializer(serializers.Serializer):
    """
    Serializer para manejar la distribución múltiple de UNA factura
    """
    # Identificación de la factura
    factura_id = serializers.IntegerField(required=True, help_text="ID de la factura a distribuir")
    
    # Datos de distribución
    cliente_id = serializers.IntegerField(required=True, help_text="ID del cliente al que se distribuye")
    fundo_id = serializers.IntegerField(required=False, allow_null=True, help_text="ID del fundo/campo")
    labor_id = serializers.IntegerField(required=False, allow_null=True, help_text="ID de la labor")
    cuenta_id = serializers.IntegerField(required=False, allow_null=True, help_text="ID de la cuenta contable")
    
    # Distribución por monto o porcentaje
    tipo_distribucion = serializers.ChoiceField(
        choices=[('MONTO', 'Por Monto'), ('PORCENTAJE', 'Por Porcentaje')],
        required=True,
        help_text="Tipo de distribución"
    )
    monto_a_distribuir = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        required=False, 
        allow_null=True,
        help_text="Monto específico a distribuir (requerido si tipo_distribucion = MONTO)"
    )
    porcentaje_a_distribuir = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False, 
        allow_null=True,
        help_text="Porcentaje a distribuir (requerido si tipo_distribucion = PORCENTAJE)"
    )
    
    # Observaciones
    observaciones = serializers.CharField(
        required=False, 
        allow_blank=True, 
        allow_null=True,
        max_length=1000,
        help_text="Observaciones sobre esta distribución específica"
    )
    
    def validate(self, data):
        """Validaciones cruzadas"""
        tipo_distribucion = data.get('tipo_distribucion')
        monto = data.get('monto_a_distribuir')
        porcentaje = data.get('porcentaje_a_distribuir')
        
        # Validar que se proporcione el campo correcto según el tipo
        if tipo_distribucion == 'MONTO':
            if not monto or monto <= 0:
                raise serializers.ValidationError(
                    "Debe especificar un monto válido mayor a 0 para distribución por monto"
                )
            if porcentaje is not None:
                raise serializers.ValidationError(
                    "No debe especificar porcentaje cuando se distribuye por monto"
                )
        elif tipo_distribucion == 'PORCENTAJE':
            if not porcentaje or porcentaje <= 0 or porcentaje > 100:
                raise serializers.ValidationError(
                    "Debe especificar un porcentaje válido entre 0.01 y 100 para distribución por porcentaje"
                )
            if monto is not None:
                raise serializers.ValidationError(
                    "No debe especificar monto cuando se distribuye por porcentaje"
                )
        
        return data
    
    def validate_factura_id(self, value):
        """Valida que la factura existe y no está completamente distribuida"""
        request = self.context.get('request')
        if not request or not request.user.holding:
            raise serializers.ValidationError("No se pudo determinar el holding")
        
        try:
            factura = FacturaVentaSIIPorDistribuir.objects.get(
                id=value,
                holding_id=request.user.holding.id
            )
        except FacturaVentaSIIPorDistribuir.DoesNotExist:
            raise serializers.ValidationError("Factura no encontrada")
        
        if factura.esta_completamente_distribuida():
            raise serializers.ValidationError("La factura ya está completamente distribuida")
        
        return value
    
    def validate_cliente_id(self, value):
        """Valida que el cliente existe y pertenece al holding"""
        request = self.context.get('request')
        if not request or not request.user.holding:
            raise serializers.ValidationError("No se pudo determinar el holding")
        
        try:
            Clientes.objects.get(id=value, holding=request.user.holding)
        except Clientes.DoesNotExist:
            raise serializers.ValidationError("Cliente no encontrado")
        
        return value

class FacturaCompraSIIDistribuidaMultipleSerializer(serializers.ModelSerializer):
    """
    Serializer actualizado para el modelo FacturaCompraSIIDistribuida con campos de distribución múltiple
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_rut = serializers.CharField(source='cliente.rut', read_only=True)
    fundo_nombre = serializers.CharField(source='fundo.nombre_campo', read_only=True)
    labor_nombre = serializers.CharField(source='labor.nombre', read_only=True)
    cuenta_nombre = serializers.CharField(source='cuenta.nombre_cuenta', read_only=True)
    cuenta_codigo = serializers.CharField(source='cuenta.cuenta_contable', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario_distribuyente.persona.nombres', read_only=True)
    
    # Campos calculados
    porcentaje_del_total = serializers.SerializerMethodField()
    monto_original_factura = serializers.DecimalField(source='monto_total_factura', max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = FacturaCompraSIIDistribuida
        fields = [
            'id', 'holding', 'cliente', 'cliente_nombre', 'cliente_rut',
            'fundo', 'fundo_nombre', 'labor', 'labor_nombre',
            'cuenta', 'cuenta_nombre', 'cuenta_codigo',
            'folio', 'tipo_doc', 'tipo_compra', 'rut_proveedor', 'razon_social',
            'fecha_docto', 'fecha_recepcion', 'monto_total', 'monto_neto',
            'monto_exento', 'monto_iva_recuperable',
            
            # NUEVOS CAMPOS DE DISTRIBUCIÓN MÚLTIPLE
            'monto_distribuido', 'porcentaje_distribuido', 'tipo_distribucion',
            'monto_total_factura', 'monto_original_factura', 'porcentaje_del_total',
            
            'observaciones', 'usuario_distribuyente', 'usuario_nombre', 'fecha_distribucion'
        ]
        read_only_fields = ['id', 'fecha_distribucion', 'usuario_distribuyente', 'monto_total_factura']
    
    def get_porcentaje_del_total(self, obj):
        """Calcula el porcentaje que representa esta distribución del total de la factura"""
        if obj.monto_total_factura and obj.monto_total_factura > 0:
            return round((obj.monto_distribuido / obj.monto_total_factura) * 100, 2)
        return 0

class FacturaVentaSIIDistribuidaMultipleSerializer(serializers.ModelSerializer):
    """
    Serializer actualizado para el modelo FacturaCompraSIIDistribuida con campos de distribución múltiple
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_rut = serializers.CharField(source='cliente.rut', read_only=True)
    fundo_nombre = serializers.CharField(source='fundo.nombre_campo', read_only=True)
    labor_nombre = serializers.CharField(source='labor.nombre', read_only=True)
    cuenta_nombre = serializers.CharField(source='cuenta.nombre_cuenta', read_only=True)
    cuenta_codigo = serializers.CharField(source='cuenta.cuenta_contable', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario_distribuyente.persona.nombres', read_only=True)
    
    # Campos calculados
    porcentaje_del_total = serializers.SerializerMethodField()
    monto_original_factura = serializers.DecimalField(source='monto_total_factura', max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = FacturaVentaSIIDistribuida
        fields = [
            'id', 'holding', 'cliente', 'cliente_nombre', 'cliente_rut',
            'fundo', 'fundo_nombre', 'labor', 'labor_nombre',
            'cuenta', 'cuenta_nombre', 'cuenta_codigo',
            'folio', 'tipo_doc', 'tipo_compra', 'rut_proveedor', 'razon_social',
            'fecha_docto', 'fecha_recepcion', 'monto_total', 'monto_neto',
            'monto_exento', 'monto_iva_recuperable',
            
            # NUEVOS CAMPOS DE DISTRIBUCIÓN MÚLTIPLE
            'monto_distribuido', 'porcentaje_distribuido', 'tipo_distribucion',
            'monto_total_factura', 'monto_original_factura', 'porcentaje_del_total',
            
            'observaciones', 'usuario_distribuyente', 'usuario_nombre', 'fecha_distribucion'
        ]
        read_only_fields = ['id', 'fecha_distribucion', 'usuario_distribuyente', 'monto_total_factura']
    
    def get_porcentaje_del_total(self, obj):
        """Calcula el porcentaje que representa esta distribución del total de la factura"""
        if obj.monto_total_factura and obj.monto_total_factura > 0:
            return round((obj.monto_distribuido / obj.monto_total_factura) * 100, 2)
        return 0
    
class FacturaPorDistribuirMultipleSerializer(serializers.ModelSerializer):
    """
    Serializer para FacturaCompraSIIPorDistribuir con información de distribución múltiple
    """
    # Campos de distribución
    monto_pendiente = serializers.SerializerMethodField()
    porcentaje_pendiente = serializers.SerializerMethodField()
    completamente_distribuida = serializers.SerializerMethodField()
    distribuciones_count = serializers.SerializerMethodField()
    distribuciones = serializers.SerializerMethodField()
    
    # Campos de PDF
    pdf_disponible = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = FacturaCompraSIIPorDistribuir
        fields = [
            'id', 'holding', 'folio', 'tipo_doc', 'tipo_compra', 
            'rut_proveedor', 'razon_social', 'fecha_docto', 'fecha_recepcion',
            'monto_total', 'monto_neto', 'monto_exento', 'monto_iva_recuperable',
            'fecha_encontrada', 'procesada',
            
            # CAMPOS DE DISTRIBUCIÓN MÚLTIPLE
            'monto_distribuido', 'porcentaje_distribuido',
            'monto_pendiente', 'porcentaje_pendiente', 
            'completamente_distribuida', 'distribuciones_count', 'distribuciones',
            
            # CAMPOS DE PDF
            'pdf_descargado', 'pdf_disponible', 'pdf_url', 'error_descarga_pdf'
        ]
        read_only_fields = ['id', 'fecha_encontrada']
    
    def get_monto_pendiente(self, obj):
        return float(obj.get_monto_pendiente())
    
    def get_porcentaje_pendiente(self, obj):
        return float(obj.get_porcentaje_pendiente())
    
    def get_completamente_distribuida(self, obj):
        return obj.esta_completamente_distribuida()
    
    def get_distribuciones_count(self, obj):
        return obj.get_distribuciones().count()
    
    def get_distribuciones(self, obj):
        """Retorna las distribuciones existentes de esta factura"""
        distribuciones = obj.get_distribuciones()[:5]  # Máximo 5 para no sobrecargar
        return [dist.get_distribucion_info() for dist in distribuciones]
    
    def get_pdf_disponible(self, obj):
        return bool(obj.pdf_documento)
    
    def get_pdf_url(self, obj):
        return obj.pdf_documento.url if obj.pdf_documento else None

class ResumenDistribucionMultipleSerializer(serializers.Serializer):
    """
    Serializer para mostrar el resumen de distribución de una factura
    """
    factura_id = serializers.IntegerField()
    folio = serializers.CharField()
    tipo_doc = serializers.CharField()
    razon_social = serializers.CharField()
    monto_total = serializers.DecimalField(max_digits=15, decimal_places=2)
    monto_distribuido = serializers.DecimalField(max_digits=15, decimal_places=2)
    monto_pendiente = serializers.DecimalField(max_digits=15, decimal_places=2)
    porcentaje_distribuido = serializers.DecimalField(max_digits=5, decimal_places=2)
    porcentaje_pendiente = serializers.DecimalField(max_digits=5, decimal_places=2)
    distribuciones = FacturaCompraSIIDistribuidaMultipleSerializer(many=True, read_only=True)
    completamente_distribuida = serializers.BooleanField()

# Serializer para validación de disponibilidad de distribución
class ValidarDistribucionSerializer(serializers.Serializer):
    """
    Serializer para validar si se puede realizar una distribución específica
    """
    factura_id = serializers.IntegerField()
    tipo_distribucion = serializers.ChoiceField(choices=[('MONTO', 'Por Monto'), ('PORCENTAJE', 'Por Porcentaje')])
    monto = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    porcentaje = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    
    def validate(self, data):
        """Valida que la distribución sea posible"""
        request = self.context.get('request')
        if not request or not request.user.holding:
            raise serializers.ValidationError("No se pudo determinar el holding")
        
        try:
            factura = FacturaCompraSIIPorDistribuir.objects.get(
                id=data['factura_id'],
                holding_id=request.user.holding.id
            )
        except FacturaCompraSIIPorDistribuir.DoesNotExist:
            raise serializers.ValidationError("Factura no encontrada")
        
        if factura.esta_completamente_distribuida():
            raise serializers.ValidationError("La factura ya está completamente distribuida")
        
        tipo = data['tipo_distribucion']
        if tipo == 'MONTO':
            monto = data.get('monto')
            if not monto or not factura.puede_distribuir_monto(monto):
                raise serializers.ValidationError(
                    f"No se puede distribuir ${monto:,.2f}. Monto disponible: ${factura.get_monto_pendiente():,.2f}"
                )
        elif tipo == 'PORCENTAJE':
            porcentaje = data.get('porcentaje')
            if not porcentaje or not factura.puede_distribuir_porcentaje(porcentaje):
                raise serializers.ValidationError(
                    f"No se puede distribuir {porcentaje}%. Porcentaje disponible: {factura.get_porcentaje_pendiente()}%"
                )
        
        return data
    
#NUEVOS SERIALIZERS PARA FACTURAS DE VENTA AUTOMATIZADAS

class FacturaVentaSIIDistribuidaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo FacturaVentaSIIDistribuida con información de distribución múltiple
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_rut = serializers.CharField(source='cliente.rut', read_only=True)
    fundo_nombre = serializers.CharField(source='fundo.nombre_campo', read_only=True)
    labor_nombre = serializers.CharField(source='labor.nombre', read_only=True)
    labor_especie = serializers.CharField(source='labor.especie', read_only=True)
    cuenta_nombre = serializers.CharField(source='cuenta.nombre_cuenta', read_only=True)
    cuenta_codigo = serializers.CharField(source='cuenta.cuenta_contable', read_only=True)
    usuario_nombre = serializers.SerializerMethodField()
    
    # Campos calculados
    porcentaje_del_total = serializers.SerializerMethodField()
    monto_original_factura = serializers.DecimalField(source='monto_total_factura', max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = FacturaVentaSIIDistribuida
        fields = [
            'id', 'holding', 'cliente', 'cliente_nombre', 'cliente_rut',
            'fundo', 'fundo_nombre', 'labor', 'labor_nombre', 'labor_especie',
            'cuenta', 'cuenta_nombre', 'cuenta_codigo',
            'folio', 'tipo_doc', 'rut_receptor', 'razon_social_receptor',
            'fecha_emision', 'monto_total', 'monto_neto',
            'monto_exento', 'monto_iva', 'monto_otros_impuestos',
            
            # CAMPOS DE DISTRIBUCIÓN MÚLTIPLE
            'monto_distribuido', 'porcentaje_distribuido', 'tipo_distribucion',
            'monto_total_factura', 'monto_original_factura', 'porcentaje_del_total',
            
            'observaciones', 'usuario_distribuyente', 'usuario_nombre', 'fecha_distribucion'
        ]
        read_only_fields = ['id', 'fecha_distribucion', 'usuario_distribuyente', 'monto_total_factura']
    
    def get_usuario_nombre(self, obj):
        """Nombre completo del usuario distribuyente"""
        if obj.usuario_distribuyente and obj.usuario_distribuyente.persona:
            return f"{obj.usuario_distribuyente.persona.nombres} {obj.usuario_distribuyente.persona.apellidos}"
        return None
    
    def get_porcentaje_del_total(self, obj):
        """Calcula el porcentaje que representa esta distribución del total de la factura"""
        if obj.monto_total_factura and obj.monto_total_factura > 0:
            return round((obj.monto_distribuido / obj.monto_total_factura) * 100, 2)
        return 0

class FacturaVentaPorDistribuirMultipleSerializer(serializers.ModelSerializer):
    """
    Serializer para FacturaVentaSIIPorDistribuir con información de distribución múltiple
    """
    # Campos de distribución
    monto_pendiente = serializers.SerializerMethodField()
    porcentaje_pendiente = serializers.SerializerMethodField()
    completamente_distribuida = serializers.SerializerMethodField()
    distribuciones_count = serializers.SerializerMethodField()
    distribuciones = serializers.SerializerMethodField()
    
    # Campos de PDF
    pdf_disponible = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = FacturaVentaSIIPorDistribuir
        fields = [
            'id', 'holding', 'folio', 'tipo_doc', 
            'rut_receptor', 'razon_social_receptor', 'fecha_emision',
            'monto_total', 'monto_neto', 'monto_exento', 'monto_iva',
            'monto_otros_impuestos', 'codigo_otros_impuestos',
            'fecha_encontrada', 'procesada',
            
            # CAMPOS DE DISTRIBUCIÓN MÚLTIPLE
            'monto_distribuido', 'porcentaje_distribuido',
            'monto_pendiente', 'porcentaje_pendiente', 
            'completamente_distribuida', 'distribuciones_count', 'distribuciones',
            
            # CAMPOS DE PDF
            'pdf_descargado', 'pdf_disponible', 'pdf_url', 'error_descarga_pdf',
            'intentos_descarga_pdf'
        ]
        read_only_fields = ['id', 'fecha_encontrada']
    
    def get_monto_pendiente(self, obj):
        return float(obj.get_monto_pendiente())
    
    def get_porcentaje_pendiente(self, obj):
        return float(obj.get_porcentaje_pendiente())
    
    def get_completamente_distribuida(self, obj):
        return obj.esta_completamente_distribuida()
    
    def get_distribuciones_count(self, obj):
        return obj.get_distribuciones().count()
    
    def get_distribuciones(self, obj):
        """Retorna las distribuciones existentes de esta factura"""
        distribuciones = obj.get_distribuciones()[:5]  # Máximo 5 para no sobrecargar
        return [dist.get_distribucion_info() for dist in distribuciones]
    
    def get_pdf_disponible(self, obj):
        return bool(obj.pdf_documento)
    
    def get_pdf_url(self, obj):
        return obj.pdf_documento.url if obj.pdf_documento else None

class DistribucionFacturasVentaSIISerializer(serializers.Serializer):
    """
    Serializer para manejar la distribución de facturas de venta SII
    """
    facturas_seleccionadas = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        help_text="Lista de facturas de venta seleccionadas para distribuir"
    )
    cliente_id = serializers.IntegerField(required=True)
    fundo_id = serializers.IntegerField(required=False, allow_null=True)
    labor_id = serializers.IntegerField(required=False, allow_null=True)
    cuenta_id = serializers.IntegerField(required=False, allow_null=True)
    tipo_distribucion = serializers.ChoiceField(
        choices=[('MONTO', 'Por monto'), ('PORCENTAJE', 'Por porcentaje')],
        required=True
    )
    monto_a_distribuir = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        required=False, 
        allow_null=True
    )
    porcentaje_a_distribuir = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False, 
        allow_null=True
    )
    observaciones = serializers.CharField(
        max_length=1000, 
        required=False, 
        allow_blank=True
    )
    
    # CAMPOS ESPECÍFICOS PARA DISTRIBUCIÓN MÚLTIPLE DE VENTAS
    tipo_distribucion_multiple = serializers.ChoiceField(
        choices=[('INDIVIDUAL', 'Individual'), ('GRUPAL', 'Grupal')],
        required=False,
        default='INDIVIDUAL'
    )
    
    def validate(self, data):
        """Validaciones del serializer"""
        tipo_distribucion = data.get('tipo_distribucion')
        monto = data.get('monto_a_distribuir')
        porcentaje = data.get('porcentaje_a_distribuir')
        facturas = data.get('facturas_seleccionadas', [])
        
        # Validar que haya facturas seleccionadas
        if not facturas:
            raise serializers.ValidationError("Debe seleccionar al menos una factura de venta")
        
        # Validar según tipo de distribución
        if tipo_distribucion == 'MONTO':
            if not monto or monto <= 0:
                raise serializers.ValidationError("Debe especificar un monto válido para distribución por monto")
        elif tipo_distribucion == 'PORCENTAJE':
            if not porcentaje or porcentaje <= 0 or porcentaje > 100:
                raise serializers.ValidationError("Debe especificar un porcentaje válido (0.01 - 100)")
        
        # Validar que el cliente existe
        try:
            from .models import Clientes
            Clientes.objects.get(id=data['cliente_id'])
        except Clientes.DoesNotExist:
            raise serializers.ValidationError("Cliente no encontrado")
        
        return data

class ResumenDistribucionVentaMultipleSerializer(serializers.Serializer):
    """
    Serializer para mostrar el resumen de distribución múltiple de facturas de venta
    """
    total_facturas = serializers.IntegerField()
    total_monto_facturas = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_monto_distribuido = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_monto_pendiente = serializers.DecimalField(max_digits=15, decimal_places=2)
    porcentaje_distribuido_promedio = serializers.DecimalField(max_digits=5, decimal_places=2)
    facturas_completamente_distribuidas = serializers.IntegerField()
    facturas_parcialmente_distribuidas = serializers.IntegerField()
    facturas_sin_distribuir = serializers.IntegerField()
    
    # Estadísticas de distribución por cliente
    distribuciones_por_cliente = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )

class EstadisticasPDFVentaSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de PDFs de facturas de venta
    """
    total_facturas = serializers.IntegerField()
    facturas_con_pdf = serializers.IntegerField()
    facturas_sin_pdf = serializers.IntegerField()
    facturas_error_pdf = serializers.IntegerField()
    porcentaje_con_pdf = serializers.DecimalField(max_digits=5, decimal_places=2)
    porcentaje_sin_pdf = serializers.DecimalField(max_digits=5, decimal_places=2)
    porcentaje_error_pdf = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Estadísticas detalladas por intentos
    facturas_0_intentos = serializers.IntegerField(required=False)
    facturas_1_2_intentos = serializers.IntegerField(required=False)
    facturas_3_mas_intentos = serializers.IntegerField(required=False)
    fecha_actualizacion = serializers.DateTimeField(required=False)

class ProcesoAutomaticoVentaStatusSerializer(serializers.Serializer):
    """
    Serializer para el estado del proceso automático de facturas de venta
    """
    estado = serializers.ChoiceField(
        choices=[
            ('inactivo', 'Inactivo'),
            ('ejecutando', 'Ejecutando'),
            ('completado', 'Completado'),
            ('error', 'Error'),
            ('sin_configuracion', 'Sin configuración')
        ]
    )
    ultima_ejecucion = serializers.DateTimeField(required=False, allow_null=True)
    proxima_ejecucion = serializers.DateTimeField(required=False, allow_null=True)
    facturas_encontradas = serializers.IntegerField()
    mensaje = serializers.CharField(max_length=500, required=False)
    configuracion_activa = serializers.BooleanField()
    
    # Información adicional del proceso
    empresa_configurada = serializers.CharField(max_length=255, required=False)
    periodo_configurado = serializers.CharField(max_length=20, required=False)
    
class FacturaVentaCSVSerializer(serializers.Serializer):
    """
    Serializer para procesar datos de facturas de venta desde CSV del SII
    """
    nro = serializers.CharField(max_length=20)
    tipo_doc = serializers.CharField(max_length=10)
    rut_receptor = serializers.CharField(max_length=20)
    razon_social_receptor = serializers.CharField(max_length=255)
    folio = serializers.CharField(max_length=50)
    fecha_emision = serializers.CharField(max_length=20)
    monto_total = serializers.DecimalField(max_digits=15, decimal_places=2)
    monto_neto = serializers.DecimalField(max_digits=15, decimal_places=2)
    monto_exento = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, default=0)
    monto_iva = serializers.DecimalField(max_digits=15, decimal_places=2)
    monto_otros_impuestos = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, default=0)
    codigo_otros_impuestos = serializers.CharField(max_length=10, required=False, allow_blank=True)
    
    def validate_folio(self, value):
        """Validar que el folio sea válido"""
        if not value or not value.strip():
            raise serializers.ValidationError("Folio es requerido")
        return value.strip()
    
    def validate_monto_total(self, value):
        """Validar que el monto total sea válido"""
        if value <= 0:
            raise serializers.ValidationError("Monto total debe ser mayor a 0")
        return value

#=======================================================================================
#===============================SERIALIZERS TESORERIA===================================
#=======================================================================================

class CartolaMovimientoSerializer(serializers.ModelSerializer):
    tipo_movimiento_display = serializers.CharField(source='get_tipo_movimiento_display', read_only=True)
    cuenta_origen_info = serializers.SerializerMethodField()
    
    class Meta:
        model = CartolaMovimiento
        fields = [
            'id', 'fecha', 'numero_operacion', 'descripcion', 
            'monto', 'tipo_movimiento', 'tipo_movimiento_display',
            'saldo', 'procesado', 'cuenta_origen_info'
        ]
    
    def get_cuenta_origen_info(self, obj):
        return {
            'id': obj.cuenta_origen.id,
            'numero_cuenta': obj.cuenta_origen.numero_cuenta,
            'banco_nombre': obj.cuenta_origen.banco.nombre,
            'tipo_cuenta': obj.cuenta_origen.tipo_cuenta
        }
