#contratista-local
from rest_framework import serializers
from datetime import date
from datetime import datetime
from django.utils import timezone
import random
import string
from django.core.mail import send_mail
from django.conf import settings
import logging
from rest_framework.validators import UniqueValidator

logger = logging.getLogger('contratista_test_app')

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
    EnlaceAutoRegistro,
    Supervisores,
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
    FacturaVentaSIIPorDistribuir,
    FacturaVentaSIIDistribuida,
    CartolaMovimiento,
    DocumentosChofer,
    DocumentosVehiculo,
    RegistroAsistencia,
    RegistroManoObraPersona,
    ContratoTrabajador,
    FolioComercialLabor,
    RegistroCasaTrabajador,
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

class HorarioSimpleSerializer(serializers.ModelSerializer):
    jornada = serializers.SerializerMethodField()
    
    class Meta:
        model = Horarios
        fields = ['id', 'nombre', 'jornada']
    
    def get_jornada(self, obj):
        from datetime import datetime
        
        total_minutos = 0
        dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        
        for dia in dias:
            inicio = getattr(obj, f'{dia}_inicio')
            fin = getattr(obj, f'{dia}_fin')
            colacion = getattr(obj, f'{dia}_minutos_colacion', 0)
            
            if inicio and fin:
                minutos_dia = (datetime.combine(datetime.today(), fin) - 
                             datetime.combine(datetime.today(), inicio)).seconds // 60
                total_minutos += minutos_dia - colacion
        
        return round(total_minutos / 60, 1)
class FundoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CamposClientes
        fields = ['id', 'nombre_campo']

class LaborSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labores
        fields = ['id', 'nombre']

class FolioComercialPreContratacionSerializer(serializers.ModelSerializer):
    """
    Serializer específico para la pantalla de pre-contratación en el móvil.
    Devuelve los transportistas con su lista completa de vehículos.
    """
    nombre_cliente = serializers.CharField(source='cliente.nombre', read_only=True)
    fundos = FundoSimpleSerializer(many=True, read_only=True)
    labores = LaborSimpleSerializer(many=True, read_only=True)
    horarios = HorarioSimpleSerializer(many=True, read_only=True)  # ✅ NUEVO
    transportistas = serializers.SerializerMethodField()
    
    class Meta:
        model = FolioComercial
        fields = [
            'id', 'cliente', 'nombre_cliente',
            'fundos', 'labores', 'horarios',  
            'transportistas',
            'fecha_inicio_contrato', 'fecha_termino_contrato',
            'valor_pago_trabajador', 'valor_facturacion',
            'estado'
        ]
    
    def get_transportistas(self, obj):
        transportistas_data = []
        for transportista in obj.transportistas.all():
            vehiculos = obj.vehiculos.filter(empresa=transportista)
            transportistas_data.append({
                'id': transportista.id,
                'nombre': transportista.nombre,
                'vehiculos': VehiculoSerializer(vehiculos, many=True).data
            })
        return transportistas_data

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
    supervisor_id = serializers.SerializerMethodField(read_only=True)
    supervisor_nombre = serializers.SerializerMethodField(read_only=True)
    enviar_credenciales = serializers.BooleanField(write_only=True, required=False, default=True)
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=Usuarios.objects.all(),
                message='Ya existe un usuario con este correo electrónico.'
            )
        ],
        error_messages={
            'required': 'El correo electrónico es obligatorio.',
            'blank': 'El correo electrónico no puede estar vacío.',
            'invalid': 'Ingrese un correo electrónico válido.',
        }
    )
    rut = serializers.CharField(
        required=False, allow_null=True, allow_blank=True,
        validators=[
            UniqueValidator(
                queryset=Usuarios.objects.all(),
                message='Ya existe un usuario con este RUT.'
            )
        ]
    )
    class Meta:
        model = Usuarios
        fields = ['id', 'holding', 'empresas_asignadas', 'nombre_persona', 'persona', 'rut', 'email', 
                  'perfil', 'nombre_perfil', 'nombre_empresas_asignadas', 'estado', 'enviar_credenciales',
                  'supervisor_id', 'supervisor_nombre']
        extra_kwargs = {
            'is_admin': {'default': False},
            'estado': {'default': True},

            'perfil': {
                'error_messages': {
                    'required': 'El perfil es obligatorio.',
                    'null': 'Debe seleccionar un perfil.',
                }
            },
            'holding': {
                'write_only': True,
                'error_messages': {
                    'required': 'El holding es obligatorio.',
                    'null': 'Debe seleccionar un holding.',
                }
            },
        }

    def validate_rut(self, value):
        if not value:
            return value
        
        valor_original = value
        rut_limpio = (value.replace('.', '').replace('-', '').replace(' ', '').strip().upper())
        
        if valor_original != rut_limpio:
            logger.info(f"RUT limpiado - Antes: '{valor_original}' | Después: '{rut_limpio}'")
        
        if len(rut_limpio) < 7:
            raise serializers.ValidationError("RUT inválido: debe tener al menos 7 dígitos")
        
        verificador = rut_limpio[-1]
        if not (verificador.isdigit() or verificador == 'K'):
            raise serializers.ValidationError("RUT inválido: el dígito verificador debe ser un número o K")
        
        cuerpo = rut_limpio[:-1]
        if not cuerpo.isdigit():
            raise serializers.ValidationError("RUT inválido: debe contener solo números y dígito verificador")
        
        return rut_limpio
    
    def get_supervisor_nombre(self, obj):
        try:
            supervisor = Supervisores.objects.get(usuario=obj)
            return supervisor.usuario.persona.nombres
        except Supervisores.DoesNotExist:
            return None

    def get_supervisor_id(self, obj):
        try:
            supervisor = Supervisores.objects.get(usuario=obj)
            return supervisor.id
        except Supervisores.DoesNotExist:
            return None

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
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase  
        digits = string.digits
        symbols = "!@#$%&*"
        all_chars = uppercase + lowercase + digits + symbols
        
        password = [
            random.choice(uppercase),
            random.choice(lowercase),
            random.choice(digits),
            random.choice(symbols)
        ]
        for _ in range(length - 4):
            password.append(random.choice(all_chars))
        
        random.shuffle(password)
        return ''.join(password)

    def send_credentials_email(self, usuario, password):
        logger.info(f"Intentando enviar credenciales a: {usuario.email}")
        
        try:
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
                1. Ve a http://contratista.terramobile.cl/
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
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=False,
            )
            
            logger.info(f"Email enviado exitosamente a {usuario.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email a {usuario.email}: {type(e).__name__}: {str(e)}", exc_info=True)
            return False

    def create(self, validated_data):
        logger.info(f"CREANDO USUARIO - RUT: {validated_data.get('rut')} | Email: {validated_data.get('email')}")
        
        empresas_asignadas_data = validated_data.pop('empresas_asignadas', [])
        enviar_credenciales = validated_data.pop('enviar_credenciales', True)
        
        password_temporal = self.generate_random_password()
        
        usuario = Usuarios.objects.create(**validated_data)
        usuario.set_password(password_temporal)
        usuario.save()
        
        logger.info(f"Usuario guardado - ID: {usuario.id} | RUT: '{usuario.rut}'")
        
        if empresas_asignadas_data:
            usuario.empresas_asignadas.set(empresas_asignadas_data)
            logger.info(f"Empresas asignadas: {len(empresas_asignadas_data)}")
        
        if enviar_credenciales and usuario.email:
            if self.send_credentials_email(usuario, password_temporal):
                logger.info("Credenciales enviadas exitosamente")
            else:
                logger.error("No se pudieron enviar las credenciales por email")
        
        return usuario

    def update(self, instance, validated_data):
        logger.info(f"ACTUALIZANDO USUARIO - ID: {instance.id} | RUT nuevo: {validated_data.get('rut', instance.rut)}")
        
        empresas_asignadas_data = validated_data.pop('empresas_asignadas', [])
        validated_data.pop('enviar_credenciales', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        logger.info(f"Usuario actualizado - RUT guardado: '{instance.rut}'")
        
        if 'empresas_asignadas' in validated_data or empresas_asignadas_data:
            instance.empresas_asignadas.set(empresas_asignadas_data)
        
        return instance

class SupervisorSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.persona.nombres', read_only=True)
    usuario_rut = serializers.CharField(source='usuario.rut', read_only=True)
    trabajadores_count = serializers.SerializerMethodField()
    trabajadores_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = Supervisores
        fields = ['id', 'holding', 'usuario', 'usuario_nombre', 'usuario_rut', 
                 'trabajadores', 'trabajadores_count', 'trabajadores_detail',
                 ]
        read_only_fields = ['id']

    def get_trabajadores_count(self, obj):
        # Cuenta trabajadores directos
        trabajadores_directos = obj.trabajadores.count()
        
        return {
            'directos': trabajadores_directos,
            'total': trabajadores_directos
        }

    def get_trabajadores_detail(self, obj):
        return [{
            'id': t.id,
            'nombre': t.nombres,
            'rut': t.rut,
            'tipo': 'directo'
        } for t in obj.trabajadores.all()]

    
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
        fields = ['id','holding', 'rut', 'nombre', 'direccion', 'giro', 
                  'campos_personalizados','nombre_rep_legal','direccion_rep_legal','comuna_cliente']
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
        fields = ['id','holding','cliente','campo_cliente','area_cliente','cargo_cliente','nombre_contacto'
                  ,'telefono','correo','nombre_cliente','nombre_campo_cliente','nombre_area_cliente',
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
    
class EmpresaTransporteSerializer(serializers.ModelSerializer):
    # Para lectura: devuelve objeto completo del banco
    banco = serializers.SerializerMethodField(read_only=True)
    
    # Para escritura: acepta solo el ID
    banco_id = serializers.PrimaryKeyRelatedField(
        queryset=Banco.objects.all(),
        source='banco',
        write_only=True,
        allow_null=True,
        required=False
    )
    
    class Meta:
        model = EmpresasTransporte
        fields = ['id', 'holding', 'nombre', 'rut', 'direccion', 'comuna', 
                  'metodo_pago', 'banco', 'banco_id', 'tipo_cuenta', 'numero_cuenta',
                  'emite_factura','alias']
    
    def get_banco(self, obj):
        if obj.banco:
            return {
                'id': obj.banco.id,
                'nombre': obj.banco.nombre,
                'codigo_sbif': obj.banco.codigo_sbif
            }
        return None

class DocumentosVehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentosVehiculo
        fields = '__all__'
        extra_kwargs = {
            'vehiculo': {'write_only': True},
            'fecha_subida': {'read_only': True},
        }

# MODIFICAR el VehiculosTransporteSerializer existente
class VehiculosTransporteSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.SerializerMethodField()
    documentos = DocumentosVehiculoSerializer(many=True, read_only=True)  # NUEVO
    documentos_urls = serializers.SerializerMethodField()  # NUEVO

    class Meta:
        model = VehiculosTransporte
        fields = [
            'holding','id','empresa','tipo','ppu','modelo','year','color','num_pasajeros','marca',
            'nombre_empresa','documentos','documentos_urls'  # AGREGADOS
        ]
        extra_kwargs = {
            'holding': {'write_only': True},
            'id': {'read_only': True},
        }

    def get_nombre_empresa(self, obj):
        if obj.empresa:
            return obj.empresa.nombre
        return None
    
    # NUEVO MÉTODO
    def get_documentos_urls(self, obj):
        """Retorna las URLs completas de los documentos del vehículo"""
        try:
            documento = DocumentosVehiculo.objects.get(vehiculo=obj, tipo='documentos_varios')
            if documento.documentos_rutas:
                urls_completas = []
                for ruta in documento.documentos_rutas:
                    if self.context and 'request' in self.context:
                        # Construir URL completa usando el request
                        request = self.context['request']
                        if ruta.startswith('/'):
                            url_completa = request.build_absolute_uri(ruta)
                        else:
                            # Si es ruta de MEDIA, construir correctamente
                            media_url = f"/media/{ruta}" if not ruta.startswith('/media/') else ruta
                            url_completa = request.build_absolute_uri(media_url)
                    else:
                        # Fallback: construir URL manualmente
                        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
                        if ruta.startswith('/'):
                            url_completa = f"{base_url.rstrip('/')}{ruta}"
                        else:
                            url_completa = f"{base_url.rstrip('/')}/media/{ruta}"
                    urls_completas.append(url_completa)
                return urls_completas
            return []
        except DocumentosVehiculo.DoesNotExist:
            return []

class DocumentosChoferSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentosChofer
        fields = '__all__'
        extra_kwargs = {
            'chofer': {'write_only': True},
            'fecha_subida': {'read_only': True},
        }

class ChoferesTransporteSerializer(serializers.ModelSerializer):
    nombre_empresa = serializers.SerializerMethodField()
    modelo_vehiculo = serializers.SerializerMethodField()
    documentos = DocumentosChoferSerializer(many=True, read_only=True)
    imagenes_urls = serializers.SerializerMethodField()
    documentos_urls = serializers.SerializerMethodField()
    
    class Meta:
        model = ChoferesTransporte
        fields = [
            'holding','id','empresa','nombre','rut','licencia',
            'nombre_empresa','vehiculo','modelo_vehiculo','documentos',
            'imagenes_urls','documentos_urls'
        ]
        extra_kwargs = {
            'holding': {'write_only': True},
            'id':{'read_only': True},
        }
        
    def get_nombre_empresa(self, obj):
        if obj.empresa:
            return obj.empresa.nombre
        return None
    
    def get_modelo_vehiculo(self, obj):
        if obj.vehiculo:
            return obj.vehiculo.modelo
        return None
    
    def get_imagenes_urls(self, obj):
        """Retorna las URLs completas de las 4 imágenes específicas"""
        from django.conf import settings
        
        imagenes = {}
        tipos_imagen = [
            'foto_licencia_frontal', 
            'foto_licencia_trasera', 
            'foto_cedula_frontal', 
            'foto_cedula_trasera'
        ]
        
        for tipo in tipos_imagen:
            try:
                documento = DocumentosChofer.objects.get(chofer=obj, tipo=tipo)
                if documento.imagen and documento.imagen.name:
                    # CORRECCIÓN: Construir URL completa correctamente
                    if hasattr(self.context.get('request'), 'build_absolute_uri'):
                        # Si tenemos contexto de request, usar build_absolute_uri
                        imagenes[tipo] = self.context['request'].build_absolute_uri(documento.imagen.url)
                    else:
                        # Fallback: construir URL manualmente
                        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
                        imagenes[tipo] = f"{base_url.rstrip('/')}{documento.imagen.url}"
                else:
                    imagenes[tipo] = None
            except DocumentosChofer.DoesNotExist:
                imagenes[tipo] = None
        
        return imagenes
    
    def get_documentos_urls(self, obj):
        """Retorna las URLs completas de los documentos varios"""
        from django.conf import settings
        
        try:
            documento = DocumentosChofer.objects.get(chofer=obj, tipo='documentos_varios')
            if documento.documentos_rutas:
                urls_completas = []
                for ruta in documento.documentos_rutas:
                    if ruta:  # Verificar que la ruta no esté vacía
                        if hasattr(self.context.get('request'), 'build_absolute_uri'):
                            # Si la ruta es relativa, construir URL completa
                            if ruta.startswith('/'):
                                url_completa = self.context['request'].build_absolute_uri(ruta)
                            else:
                                # Si es ruta de MEDIA, construir correctamente
                                media_url = f"/media/{ruta}" if not ruta.startswith('/media/') else ruta
                                url_completa = self.context['request'].build_absolute_uri(media_url)
                        else:
                            # Fallback: construir URL manualmente
                            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
                            if ruta.startswith('/'):
                                url_completa = f"{base_url.rstrip('/')}{ruta}"
                            else:
                                url_completa = f"{base_url.rstrip('/')}/media/{ruta}"
                        urls_completas.append(url_completa)
                return urls_completas
            return []
        except DocumentosChofer.DoesNotExist:
            return []

#For Docker
'''


class ChoferesTransporteSerializer(serializers.ModelSerializer):
   nombre_empresa = serializers.SerializerMethodField()
   modelo_vehiculo = serializers.SerializerMethodField()
   documentos = DocumentosChoferSerializer(many=True, read_only=True)
   imagenes_urls = serializers.SerializerMethodField()
   documentos_urls = serializers.SerializerMethodField()
   
   class Meta:
       model = ChoferesTransporte
       fields = [
           'holding','id','empresa','nombre','rut','licencia',
           'nombre_empresa','vehiculo','modelo_vehiculo','documentos',
           'imagenes_urls','documentos_urls'
       ]
       extra_kwargs = {
           'holding': {'write_only': True},
           'id':{'read_only': True},
       }
       
   def get_nombre_empresa(self, obj):
       if obj.empresa:
           return obj.empresa.nombre
       return None
   
   def get_modelo_vehiculo(self, obj):
       if obj.vehiculo:
           return obj.vehiculo.modelo
       return None
   
   def get_imagenes_urls(self, obj):
       """Retorna las URLs de las 4 imágenes específicas para Docker"""
       imagenes = {}
       tipos_imagen = [
           'foto_licencia_frontal', 
           'foto_licencia_trasera', 
           'foto_cedula_frontal', 
           'foto_cedula_trasera'
       ]
       
       for tipo in tipos_imagen:
           try:
               documento = DocumentosChofer.objects.get(chofer=obj, tipo=tipo)
               if documento.imagen and documento.imagen.name:
                   if hasattr(self.context.get('request'), 'build_absolute_uri'):
                       imagenes[tipo] = self.context['request'].build_absolute_uri(documento.imagen.url)
                   else:
                       # Para Docker: usar URL relativa que HAProxy/Nginx resolverá
                       imagenes[tipo] = documento.imagen.url
               else:
                   imagenes[tipo] = None
           except DocumentosChofer.DoesNotExist:
               imagenes[tipo] = None
       
       return imagenes
   
   def get_documentos_urls(self, obj):
       """Retorna las URLs de los documentos varios para Docker"""
       try:
           documento = DocumentosChofer.objects.get(chofer=obj, tipo='documentos_varios')
           if documento.documentos_rutas:
               urls_completas = []
               for ruta in documento.documentos_rutas:
                   if ruta:
                       if hasattr(self.context.get('request'), 'build_absolute_uri'):
                           if ruta.startswith('/'):
                               url_completa = self.context['request'].build_absolute_uri(ruta)
                           else:
                               media_url = f"/media/{ruta}" if not ruta.startswith('/media/') else ruta
                               url_completa = self.context['request'].build_absolute_uri(media_url)
                       else:
                           # Para Docker: usar URL relativa
                           if ruta.startswith('/'):
                               url_completa = ruta
                           else:
                               url_completa = f"/media/{ruta}"
                       urls_completas.append(url_completa)
               return urls_completas
           return []
       except DocumentosChofer.DoesNotExist:
           return []
'''    

#======================================================================
#========================= SALUD ======================================
#======================================================================

class SaludTrabajadoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaludTrabajadores
        fields = [
            'holding', 
            'id',       # AutoField (solo lectura)
            'codigo',   # Código Previred (mostrar en tabla)
            'nombre',   
            'porcentaje'
        ]
        extra_kwargs = {
            'holding': {'write_only': True},
            'id': {'read_only': True},
        }

#======================================================================
#=========================== AFP ======================================
#======================================================================

class AFPTrabajadoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = AFPTrabajadores
        fields = [
            'holding', 
            'id',       # AutoField (solo lectura)
            'codigo',   # Código Previred (mostrar en tabla)
            'nombre',   
            'porcentaje_cotizacion_individual',
            'comision_afp',
            'porcentaje_cargo_empleador',
            'porcentaje_seguro_social'
        ]
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
    nombre_banco = serializers.SerializerMethodField()
    rut = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    dni = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    nic = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    carnet_front_image = serializers.ImageField(required=False, allow_null=True)
    carnet_back_image = serializers.ImageField(required=False, allow_null=True)
    firma = serializers.ImageField(required=False, allow_null=True)
    huella_digital = serializers.ImageField(required=False, allow_null=True)  # ✅ NUEVO
    sueldo_base = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    
    class Meta:
        model = PersonalTrabajadores
        fields = [
            'id', 'holding', 'sociedad', 'nombre_sociedad', 'area', 'nombre_area', 'cargo', 'nombre_cargo', 'nombres', 'apellidos',
            'rut', 'dni', 'nic', 'direccion', 'afp', 'nombre_afp', 'salud','nombre_salud', 'fecha_ingreso',
            'metodo_pago', 'banco','nombre_banco', 'tipo_cuenta_bancaria',
            'numero_cuenta', 'nacionalidad', 'sexo', 'telefono', 'correo', 'estado', 'carnet_front_image','carnet_back_image',
            'firma', 'huella_digital', 'estado_civil', 'fecha_nacimiento', 'sueldo_base'  # ✅ AGREGADO huella_digital
        ]
        extra_kwargs = {
            'holding': {'write_only': True},
            'id': {'read_only': True},
        }

    def get_nombre_banco(self, obj):
        if obj.banco:
            return obj.banco.nombre
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

    def validate_rut(self, value):
        # Convertir string vacío a None
        if value == '' or value is None:
            return None
        
        # Validar unicidad manualmente
        qs = PersonalTrabajadores.objects.filter(rut=value)
        if self.instance:  # En update, excluir el mismo registro
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un trabajador registrado con este RUT.")
        
        return value
    
    def validate(self, data):
        campos_nullable = [
            'dni', 'nic', 'correo', 'direccion',
            'telefono', 'metodo_pago', 'tipo_cuenta_bancaria',
            'nacionalidad', 'sexo', 'estado_civil', 'apellidos'
        ]
        for campo in campos_nullable:
            if campo in data and data[campo] == '':
                data[campo] = None
        return data

    def create(self, validated_data):
        carnet_front = validated_data.pop('carnet_front_image', None)
        carnet_back = validated_data.pop('carnet_back_image', None)
        firma = validated_data.pop('firma', None)
        huella = validated_data.pop('huella_digital', None)  # ✅ NUEVO

        personal = PersonalTrabajadores.objects.create(**validated_data)

        if carnet_front:
            personal.carnet_front_image = carnet_front
        if carnet_back:
            personal.carnet_back_image = carnet_back
        if firma:
            personal.firma = firma
        if huella:  # ✅ NUEVO
            personal.huella_digital = huella

        personal.save()
        return personal

    def update(self, instance, validated_data):
        validated_data.pop('carnet_front_image', None)
        validated_data.pop('carnet_back_image', None)
        validated_data.pop('firma', None)
        validated_data.pop('huella_digital', None)  # ✅ NUEVO
        
        return super().update(instance, validated_data)
    
class PersonalTrabajadoresMobileSerializer(serializers.ModelSerializer):
    carnet_front_image = serializers.ImageField(required=False, allow_null=True, default=None)
    carnet_back_image = serializers.ImageField(required=False, allow_null=True, default=None)
    firma = serializers.ImageField(required=False, allow_null=True)
    huella_digital = serializers.ImageField(required=False, allow_null=True)

    rut = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    dni = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    nic = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    class Meta:
        model = PersonalTrabajadores
        fields = [
            'id', 'holding', 'sociedad', 'area', 'cargo',
            'afp', 'salud', 'banco',
            'nombres', 'apellidos', 'rut', 'dni', 'nic',
            'nacionalidad', 'sexo', 'estado_civil', 'telefono',
            'correo', 'direccion', 'fecha_nacimiento',
            'fecha_ingreso',
            'metodo_pago', 'tipo_cuenta_bancaria', 'numero_cuenta',
            'carnet_front_image', 'carnet_back_image', 'firma', 'huella_digital',
            'estado', 'sueldo_base', 'area', 'cargo'
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'holding': {'write_only': True},
            'sociedad': {'required': False, 'allow_null': True},
            'area': {'required': False, 'allow_null': True},
            'cargo': {'required': False, 'allow_null': True},
            'afp': {'required': False, 'allow_null': True},
            'salud': {'required': False, 'allow_null': True},
            'banco': {'required': False, 'allow_null': True},
            'apellidos': {'required': False, 'allow_blank': True},
            'nacionalidad': {'required': False, 'allow_blank': True},
            'sexo': {'required': False, 'allow_blank': True},
            'estado_civil': {'required': False, 'allow_blank': True},
            'telefono': {'required': False, 'allow_blank': True},
            'correo': {'required': False, 'allow_blank': True},
            'direccion': {'required': False, 'allow_blank': True},
            'metodo_pago': {'required': False, 'allow_blank': True},
            'tipo_cuenta_bancaria': {'required': False, 'allow_blank': True},
            'fecha_nacimiento': {'required': False, 'allow_null': True},
            'fecha_ingreso': {'required': False, 'allow_null': True},
            'numero_cuenta': {'required': False, 'allow_null': True},
            'sueldo_base': {'required': False, 'allow_null': True},
            'estado': {'default': True},
        }

    def to_internal_value(self, data):
        valid_fields = set(self.Meta.fields)
        filtered_data = {}
        ignored_fields = []

        for key, value in data.items():
            if key in valid_fields:
                if key in ['numero_cuenta'] and value in ('', 'null', 'undefined', None):
                    filtered_data[key] = None
                # ✅ Si carnet viene como string (no archivo), ignorarlo
                elif key in ['carnet_front_image', 'carnet_back_image', 'firma', 'huella_digital']:
                    if isinstance(value, str):
                        # Es string base64 o vacío, no un archivo — ignorar
                        ignored_fields.append(f"{key}=<string, ignorado>")
                        continue
                    else:
                        filtered_data[key] = value
                else:
                    filtered_data[key] = value
            else:
                ignored_fields.append(f"{key}={value}")

        if ignored_fields:
            print(f"[DEBUG] Campos ignorados: {', '.join(ignored_fields)}")

        return super().to_internal_value(filtered_data)

    def validate(self, data):
        rut = data.get('rut', '').strip() if data.get('rut') else ''
        dni = data.get('dni', '').strip() if data.get('dni') else ''

        if not rut and not dni:
            raise serializers.ValidationError(
                "Debe proporcionar RUT (para chilenos) o DNI (para extranjeros)"
            )

        nombres = data.get('nombres', '').strip() if data.get('nombres') else ''
        if not nombres:
            raise serializers.ValidationError("Los nombres son obligatorios")

        return data

    def create(self, validated_data):
        return PersonalTrabajadores.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
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


class FolioComercialPreContratacionSerializer(serializers.ModelSerializer):
    """
    Serializer específico para la pantalla de pre-contratación.
    """
    nombre_cliente = serializers.CharField(source='cliente.nombre', read_only=True)
    fundos = FundoSimpleSerializer(many=True, read_only=True)
    labores = LaborSimpleSerializer(many=True, read_only=True)
    horarios = HorarioSimpleSerializer(many=True, read_only=True)
    transportistas = serializers.SerializerMethodField()
    
    class Meta:
        model = FolioComercial
        fields = [
            'id', 'cliente', 'nombre_cliente',
            'fundos', 'labores', 'horarios',
            'transportistas',
            'fecha_inicio_contrato', 'fecha_termino_contrato',
            'estado'
        ]
    
    def get_transportistas(self, obj):
        transportistas_data = []
        for transportista in obj.transportistas.all():
            vehiculos = obj.vehiculos.filter(empresa=transportista)
            transportistas_data.append({
                'id': transportista.id,
                'nombre': transportista.nombre,
                'vehiculos': [
                    {
                        'id': v.id,
                        'tipo': v.tipo,
                        'marca': v.marca,
                        'modelo': v.modelo,
                        'patente': v.ppu,
                    }
                    for v in vehiculos
                ]
            })
        return transportistas_data

class VehiculoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiculosTransporte  # o el nombre de tu modelo
        fields = ['id', 'modelo', 'ppu', 'capacidad', 'estado']

class TransportistaNestedSerializer(serializers.ModelSerializer):
    vehiculos = VehiculoSimpleSerializer(many=True, read_only=True)
    
    class Meta:
        model = EmpresasTransporte  # o el nombre de tu modelo
        fields = ['id', 'nombre', 'rut', 'direccion', 'vehiculos']  # ✅ Solo campos que existen

class FolioComercialLaborSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='labor.id')
    nombre = serializers.CharField(source='labor.nombre', read_only=True)
    
    class Meta:
        model = FolioComercialLabor
        fields = ['id', 'nombre', 'valor_pago_trabajador', 'valor_facturacion']

class TransportistaNestedSerializer(serializers.ModelSerializer):
    """Serializer para transportistas con vehículos anidados"""
    vehiculos = serializers.SerializerMethodField()
    
    class Meta:
        model = EmpresasTransporte
        fields = ['id', 'nombre', 'rut', 'direccion', 'vehiculos']
    
    def get_vehiculos(self, obj):
        # Obtener el folio del contexto
        folio = self.context.get('folio')
        if not folio:
            return []
        
        # Filtrar solo los vehículos de esta empresa que están en el folio
        vehiculos = folio.vehiculos.filter(empresa=obj)
        
        # Serializar los vehículos con información del chofer
        vehiculos_data = []
        for vehiculo in vehiculos:
            # Buscar el chofer asignado a este vehículo
            chofer = ChoferesTransporte.objects.filter(vehiculo=vehiculo).first()
            
            vehiculos_data.append({
                'id': vehiculo.id,
                'modelo': vehiculo.modelo,
                'ppu': vehiculo.ppu,
                'chofer': chofer.nombre if chofer else 'SIN CHOFER'
            })
        
        return vehiculos_data


class FolioComercialSerializer(serializers.ModelSerializer):
    cliente = serializers.PrimaryKeyRelatedField(queryset=Clientes.objects.all())
    nombre_cliente = serializers.CharField(source='cliente.nombre', read_only=True)
    fundos = FundoSimpleSerializer(many=True, read_only=True)
    
    # Labores con valores
    labores = serializers.SerializerMethodField()
    
    horarios = HorarioSimpleSerializer(many=True, read_only=True)
    nombres_fundos = serializers.SerializerMethodField()
    nombres_labores = serializers.SerializerMethodField()
    nombres_horarios = serializers.SerializerMethodField()
    nombres_transportistas = serializers.SerializerMethodField()
    nombres_vehiculos = serializers.SerializerMethodField()
    
    # 🔥 CAMBIO: Usar método para pasar contexto
    transportistas = serializers.SerializerMethodField()
    
    # Write-only fields
    fundos_ids = serializers.PrimaryKeyRelatedField(
        source='fundos',
        write_only=True,
        many=True,
        queryset=CamposClientes.objects.all()
    )
    
    labores_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    horarios_ids = serializers.PrimaryKeyRelatedField(
        source='horarios',
        write_only=True,
        many=True,
        queryset=Horarios.objects.all(),
        required=False
    )

    transportistas_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = FolioComercial
        fields = [
            'id', 'cliente', 'nombre_cliente', 'holding',
            'fundos', 'fundos_ids', 'nombres_fundos',
            'labores', 'labores_data', 'nombres_labores',
            'horarios', 'horarios_ids', 'nombres_horarios',
            'transportistas', 'transportistas_data', 'nombres_transportistas',
            'nombres_vehiculos',
            'fecha_inicio_contrato', 'fecha_termino_contrato',
            'estado'
        ]

    def get_labores(self, obj):
        """Devuelve las labores con sus valores desde FolioComercialLabor"""
        folios_labores = FolioComercialLabor.objects.filter(folio=obj)
        return [{
            'id': fl.labor.id,
            'nombre': fl.labor.nombre,
            'valor_pago_trabajador': fl.valor_pago_trabajador,
            'valor_facturacion': fl.valor_facturacion
        } for fl in folios_labores]
    
    def get_transportistas(self, obj):
        """Devuelve transportistas con sus vehículos anidados"""
        transportistas_queryset = obj.transportistas.all()
        return TransportistaNestedSerializer(
            transportistas_queryset, 
            many=True, 
            context={'folio': obj}
        ).data

    def get_nombres_fundos(self, obj):
        return ', '.join([fundo.nombre_campo for fundo in obj.fundos.all()])

    def get_nombres_labores(self, obj):
        labores = FolioComercialLabor.objects.filter(folio=obj)
        return ', '.join([f"{l.labor.nombre} (Pago: ${l.valor_pago_trabajador}, Fact: ${l.valor_facturacion})" for l in labores])
    
    def get_nombres_horarios(self, obj):
        from datetime import datetime
        
        nombres = []
        for horario in obj.horarios.all():
            total_minutos = 0
            dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
            
            for dia in dias:
                inicio = getattr(horario, f'{dia}_inicio')
                fin = getattr(horario, f'{dia}_fin')
                colacion = getattr(horario, f'{dia}_minutos_colacion', 0)
                
                if inicio and fin:
                    minutos_dia = (datetime.combine(datetime.today(), fin) - 
                                datetime.combine(datetime.today(), inicio)).seconds // 60
                    total_minutos += minutos_dia - colacion
            
            jornada = round(total_minutos / 60, 1)
            nombres.append(f"{horario.nombre} ({jornada}h)")
        
        return ', '.join(nombres)

    def get_nombres_transportistas(self, obj):
        return ', '.join([transportista.nombre for transportista in obj.transportistas.all()])

    def get_nombres_vehiculos(self, obj):
        vehiculos = obj.vehiculos.all()
        vehiculos_con_chofer = []
        for vehiculo in vehiculos:
            chofer = ChoferesTransporte.objects.filter(vehiculo=vehiculo).first()
            chofer_nombre = chofer.nombre if chofer else 'SIN CHOFER'
            vehiculos_con_chofer.append(f"{vehiculo.modelo} (CHOFER: {chofer_nombre})")
        return ', '.join(vehiculos_con_chofer)

    def create(self, validated_data):
        fundos = validated_data.pop('fundos', [])
        horarios = validated_data.pop('horarios', [])
        labores_data = validated_data.pop('labores_data', [])
        transportistas_data = validated_data.pop('transportistas_data', [])
        
        folio = FolioComercial.objects.create(**validated_data)
        
        folio.fundos.set(fundos)
        folio.horarios.set(horarios)
        
        for labor_data in labores_data:
            FolioComercialLabor.objects.create(
                holding=folio.holding,
                folio=folio,
                labor_id=labor_data['id'],
                valor_pago_trabajador=labor_data['valor_pago_trabajador'],
                valor_facturacion=labor_data['valor_facturacion']
            )
        
        for transportista_data in transportistas_data:
            transportista_id = transportista_data.get('id')
            vehiculos = transportista_data.get('vehiculos', [])
            
            if transportista_id:
                folio.transportistas.add(transportista_id)
                vehiculo_ids = [v.get('id') for v in vehiculos if v.get('id')]
                folio.vehiculos.add(*vehiculo_ids)
        
        return folio

    def update(self, instance, validated_data):
        fundos = validated_data.pop('fundos', None)
        horarios = validated_data.pop('horarios', None)
        labores_data = validated_data.pop('labores_data', None)
        transportistas_data = validated_data.pop('transportistas_data', None)

        if 'cliente' in validated_data:
            instance.cliente = validated_data.pop('cliente')
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if fundos is not None:
            instance.fundos.set(fundos)
        
        if horarios is not None:
            instance.horarios.set(horarios)
        
        if labores_data is not None:
            FolioComercialLabor.objects.filter(folio=instance).delete()
            for labor_data in labores_data:
                FolioComercialLabor.objects.create(
                    holding=instance.holding,
                    folio=instance,
                    labor_id=labor_data['id'],
                    valor_pago_trabajador=labor_data['valor_pago_trabajador'],
                    valor_facturacion=labor_data['valor_facturacion']
                )
        
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
        representation = super().to_representation(instance)
        
        if representation.get('fecha_inicio_contrato'):
            representation['fecha_inicio_contrato'] = instance.fecha_inicio_contrato.strftime('%Y-%m-%d')
        if representation.get('fecha_termino_contrato'):
            representation['fecha_termino_contrato'] = instance.fecha_termino_contrato.strftime('%Y-%m-%d')
            
        return representation#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

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
    sociedad_nombre = serializers.CharField(source='sociedad.nombre', read_only=True)
    
    class Meta:
        model = Horarios
        fields = [
            'id', 'holding', 'sociedad', 'sociedad_nombre', 'nombre',
            'lunes_inicio', 'lunes_fin', 'lunes_colacion', 'lunes_minutos_colacion',
            'martes_inicio', 'martes_fin', 'martes_colacion', 'martes_minutos_colacion',
            'miercoles_inicio', 'miercoles_fin', 'miercoles_colacion', 'miercoles_minutos_colacion',
            'jueves_inicio', 'jueves_fin', 'jueves_colacion', 'jueves_minutos_colacion',
            'viernes_inicio', 'viernes_fin', 'viernes_colacion', 'viernes_minutos_colacion',
            'sabado_inicio', 'sabado_fin', 'sabado_colacion', 'sabado_minutos_colacion',
            'domingo_inicio', 'domingo_fin', 'domingo_colacion', 'domingo_minutos_colacion'
        ]
        extra_kwargs = {
            'holding': {'write_only': True},
            'id': {'read_only': True},
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
            'valor_cancelacion',
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
        if data.get('valor_cancelacion', 0) <= 0:
            raise serializers.ValidationError(
                {'valor_cancelacion': 'El valor de pago debe ser mayor que 0'}
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
    tiene_contrato = serializers.BooleanField(read_only=True)
    descuentos = TrabajadorDescuentoSerializer(source='descuentos_asignados', many=True, read_only=True)
    nombre_completo = serializers.SerializerMethodField()
    cargo = CargoAdministracionSerializer(read_only=True)  # ✅ Si tienes CargoSerializer
    
    class Meta:
        model = PersonalTrabajadores
        fields = ['id', 'nombres', 'apellidos', 'nombre_completo', 'rut', 
                  'nacionalidad', 'cargo', 'fecha_ingreso', 'descuentos', 'tiene_contrato']
    
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

class RegistroAsistenciaSerializer(serializers.ModelSerializer):
    nombre_trabajador = serializers.CharField(source='trabajador.nombres', read_only=True)
    rut_trabajador = serializers.CharField(source='trabajador.rut', read_only=True)
    nombre_supervisor = serializers.SerializerMethodField()
    
    class Meta:
        model = RegistroAsistencia
        fields = [
            'id', 'holding', 'trabajador', 'supervisor', 'fecha_asistencia',
            'estado', 'horas_registradas', 'fecha_registro', 'modificado_por',
            'observaciones', 'nombre_trabajador', 'rut_trabajador', 'nombre_supervisor'
        ]
        extra_kwargs = {
            'holding': {'write_only': True},
            'id': {'read_only': True},
            'fecha_registro': {'read_only': True},
        }
    
    def get_nombre_supervisor(self, obj):
        if obj.supervisor and obj.supervisor.usuario and obj.supervisor.usuario.persona:
            return obj.supervisor.usuario.persona.nombres
        return None


class TrabajadorAsistenciaSerializer(serializers.ModelSerializer):
    """
    Serializer para retornar trabajadores con información de asistencia del día.
    """
    horas_registradas_hoy = serializers.SerializerMethodField()
    tiene_asistencia_hoy = serializers.SerializerMethodField()
    estado_asistencia_hoy = serializers.SerializerMethodField()
    
    class Meta:
        model = PersonalTrabajadores
        fields = [
            'id', 'nombres', 'apellidos', 'rut', 'horas_registradas_hoy',
            'tiene_asistencia_hoy', 'estado_asistencia_hoy'
        ]
    
    def get_horas_registradas_hoy(self, obj):
        """Retorna las horas registradas hoy para este trabajador"""
        fecha_hoy = self.context.get('fecha_hoy', timezone.now().date())
        try:
            asistencia = RegistroAsistencia.objects.get(
                trabajador=obj,
                fecha_asistencia=fecha_hoy
            )
            return float(asistencia.horas_registradas)
        except RegistroAsistencia.DoesNotExist:
            return 0.0
    
    def get_tiene_asistencia_hoy(self, obj):
        """Verifica si el trabajador ya tiene asistencia registrada hoy"""
        fecha_hoy = self.context.get('fecha_hoy', timezone.now().date())
        return RegistroAsistencia.objects.filter(
            trabajador=obj,
            fecha_asistencia=fecha_hoy
        ).exists()
    
    def get_estado_asistencia_hoy(self, obj):
        """Retorna el estado de asistencia si existe"""
        fecha_hoy = self.context.get('fecha_hoy', timezone.now().date())
        try:
            asistencia = RegistroAsistencia.objects.get(
                trabajador=obj,
                fecha_asistencia=fecha_hoy
            )
            return asistencia.estado
        except RegistroAsistencia.DoesNotExist:
            return None
        
class RegistroManoObraPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroManoObraPersona
        fields = '__all__'

class ContratoTrabajadorSerializer(serializers.ModelSerializer):
    # Campos relacionados para mostrar nombres
    nombres_trabajador     = serializers.CharField(source='trabajador.nombres', read_only=True)
    apellidos_trabajador   = serializers.CharField(source='trabajador.apellidos', read_only=True)
    nacionalidad_trabajador = serializers.CharField(source='trabajador.nacionalidad', read_only=True)
    rut_trabajador = serializers.CharField(source='trabajador.rut', read_only=True)
    nombre_sociedad = serializers.CharField(source='trabajador.sociedad.nombre', read_only=True)
    nombre_documento = serializers.CharField(source='documento.nombre', read_only=True)
    nombre_cliente = serializers.CharField(source='cliente.nombre', read_only=True)
    nombre_fundo = serializers.CharField(source='fundo.nombre_campo', read_only=True)
    nombre_horario = serializers.SerializerMethodField()

    # Campo calculado para estado
    estado_contrato = serializers.SerializerMethodField()
    dias_restantes = serializers.SerializerMethodField()
    
    class Meta:
        model = ContratoTrabajador
        fields = [
            'id', 
            'trabajador',
             'nombres_trabajador',      
            'apellidos_trabajador',     
            'nacionalidad_trabajador',
            'rut_trabajador',
            'nombre_sociedad',
            'nombre_documento',
            'nombre_cliente',
            'nombre_fundo',
            'fecha_inicio_contrato',
            'fecha_termino_contrato',
            'estado_contrato',
            'dias_restantes',
            'nombre_horario',
            'ESTADO_CHOICES'  # Para el dropdown
        ]
        
    def get_estado_contrato(self, obj):
        """Calcula si el contrato está vigente o vencido"""
        from datetime import date
        
        if obj.fecha_termino_contrato is None:
            return 'VIGENTE'
        
        if obj.fecha_termino_contrato < date.today():
            return 'VENCIDO'
        
        return 'VIGENTE'
    
    def get_nombre_horario(self, obj):
        if not obj.horario:
            return None
        h = obj.horario
        total_minutos = 0
        dias = ['lunes','martes','miercoles','jueves','viernes','sabado','domingo']
        for dia in dias:
            inicio = getattr(h, f'{dia}_inicio', None)
            fin    = getattr(h, f'{dia}_fin', None)
            colacion = getattr(h, f'{dia}_minutos_colacion', 0)
            if inicio and fin:
                from datetime import datetime
                minutos = (datetime.combine(datetime.today(), fin) - datetime.combine(datetime.today(), inicio)).seconds // 60
                total_minutos += minutos - colacion
        jornada = round(total_minutos / 60, 1)
        return f"{h.nombre} ({jornada}h)"
    
    def get_dias_restantes(self, obj):
        """Calcula días restantes del contrato"""
        from datetime import date
        
        if obj.fecha_termino_contrato is None:
            return None
        
        dias = (obj.fecha_termino_contrato - date.today()).days
        return dias if dias > 0 else 0

    def get_nombre_trabajador(self, obj):
        return f"{obj.trabajador.nombres} {obj.trabajador.apellidos or ''}".strip()


class FiltrosPagoEfectivoSerializer(serializers.ModelSerializer):
    cliente = serializers.SerializerMethodField()
    fundo = serializers.SerializerMethodField()
    trabajador_nombre = serializers.CharField(source='trabajador.nombres')
    trabajador_apellidos = serializers.CharField(source='trabajador.apellidos', allow_null=True, default='')
    trabajador_id = serializers.IntegerField(source='trabajador.id')
    trabajador_rut = serializers.CharField(source='trabajador.rut', allow_null=True)
    trabajador_dni = serializers.CharField(source='trabajador.dni', allow_null=True)
    trabajador_casa = serializers.SerializerMethodField()
    trabajador_cargo = serializers.CharField(source='trabajador.cargo.nombre', allow_null=True)
    monto_a_pagar = serializers.SerializerMethodField()
    numero_cuenta = serializers.CharField(source='trabajador.numero_cuenta', allow_null=True, default='')
    banco_rut = serializers.CharField(source='trabajador.banco.rut', allow_null=True, default='')
    tipo_cuenta = serializers.CharField(source='trabajador.tipo_cuenta', allow_null=True, default='CTD')
    pagado = serializers.BooleanField(read_only=True)


    class Meta:
        model = RegistroManoObraPersona
        fields = [
            'id', 'cliente', 'fundo', 'trabajador_id', 'trabajador_nombre', 'trabajador_apellidos',
            'trabajador_rut', 'trabajador_dni', 'trabajador_casa', 'trabajador_cargo',
            'monto_a_pagar', 'fecha_ingreso', 'numero_cuenta', 'banco_rut', 'tipo_cuenta',
            'pagado',
        ]

    def get_cliente(self, obj):
        if obj.folio and obj.folio.cliente:
            return {'id': obj.folio.cliente.id, 'nombre': obj.folio.cliente.nombre}
        return None

    def get_fundo(self, obj):
        if obj.folio:
            return [{'id': f.id, 'nombre_campo': f.nombre_campo} for f in obj.folio.fundos.all()]
        return []

    def get_trabajador_casa(self, obj):
        if not obj.trabajador:
            return None
        registro = RegistroCasaTrabajador.objects.filter(
            trabajador=obj.trabajador,
            fecha_fin__isnull=True
        ).select_related('casa').first()
        return registro.casa.nombre if registro and registro.casa else None

    def get_monto_a_pagar(self, obj):
        if not obj.folio or not obj.produccion:
            return 0
        # Obtener valor_pago_trabajador desde FolioComercialLabor si hay labor, sino del folio directo
        if obj.labor:
            from .models import FolioComercialLabor
            fc_labor = FolioComercialLabor.objects.filter(
                folio=obj.folio, labor=obj.labor
            ).first()
            if fc_labor:
                return float(obj.produccion * fc_labor.valor_pago_trabajador)
        return 0



