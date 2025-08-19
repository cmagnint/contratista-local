# contratista_test/celery.py
import os
from celery import Celery
from django.conf import settings

# Establecer el módulo de configuración de Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contratista_test.settings')

# Crear la aplicación Celery
app = Celery('contratista_test')

# Configuración usando Django settings, con el prefijo CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configuraciones específicas para Celery
app.conf.update(
    # Broker settings (Redis)
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Santiago',
    enable_utc=False,
    
    # Task execution settings
    task_always_eager=False,  # Set to True for testing without Redis
    task_eager_propagates=True,
    task_ignore_result=False,
    task_store_eager_result=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Task routing
    #task_routes={
    #    'contratista_test_app.tasks.buscar_facturas_automaticamente': {'queue': 'facturas_automaticas'},
    #    'contratista_test_app.tasks.procesar_facturas_encontradas': {'queue': 'facturas_automaticas'},
    #    'contratista_test_app.tasks.limpiar_facturas_antiguas': {'queue': 'maintenance'},
    #},
    
    # Beat schedule (para tareas periódicas)
    beat_schedule={
        # Tarea principal: buscar facturas automáticamente
        'buscar-facturas-automaticamente': {
            'task': 'contratista_test_app.tasks.buscar_facturas_automaticamente',
            'schedule': 60.0,  # Cada 60 segundos para pruebas - cambiar en producción
            'options': {
                'queue': 'facturas_automaticas',
                'routing_key': 'facturas_automaticas'
            }
        },
        
        # Tarea de mantenimiento: limpiar facturas antiguas (cada día a las 2 AM)
        'limpiar-facturas-antiguas': {
            'task': 'contratista_test_app.tasks.limpiar_facturas_antiguas',
            'schedule': 60.0 * 60 * 24,  # Cada 24 horas
            'options': {
                'queue': 'maintenance',
                'routing_key': 'maintenance'
            }
        },
        
        # Tarea de monitoreo: verificar estado del sistema (cada 5 minutos)
        'verificar-estado-sistema': {
            'task': 'contratista_test_app.tasks.verificar_estado_sistema',
            'schedule': 60.0 * 5,  # Cada 5 minutos
            'options': {
                'queue': 'monitoring',
                'routing_key': 'monitoring'
            }
        }
    },
    
    # Configuración de colas
    #task_default_queue='default',
    #task_default_exchange='default',
    #task_default_exchange_type='direct',
    #task_default_routing_key='default',
    
    # Configuraciones de rendimiento
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Configuraciones de logs
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
    
    # Configuraciones de retry
    task_retry_delay=60,  # 1 minuto
    task_max_retries=3,
    
    # Configuraciones de timeout
    task_soft_time_limit=300,  # 5 minutos
    task_time_limit=600,       # 10 minutos
    
    # Configuraciones de resultado
    result_expires=3600,  # Los resultados expiran en 1 hora
    
    # Configuraciones de monitoreo
    worker_enable_remote_control=True,
)

# Auto-discover tasks from all installed Django apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Configuraciones específicas para el entorno de desarrollo
if settings.DEBUG:
    app.conf.update(
        # En desarrollo, usar eager execution si no hay Redis
        task_always_eager=False,  # Cambiar a True si no tienes Redis instalado
        broker_connection_retry_on_startup=True,
        broker_transport_options={
            'visibility_timeout': 3600,
            'max_retries': 3,
            'interval_start': 0,
            'interval_step': 0.2,
            'interval_max': 0.2,
        }
    )
# Configuraciones específicas para producción
else:
    app.conf.update(
        # Configuraciones más estrictas para producción
        worker_hijack_root_logger=False,
        worker_log_color=False,
        task_always_eager=False,
        broker_connection_retry_on_startup=True,
        broker_pool_limit=10,
        broker_transport_options={
            'visibility_timeout': 3600,
            'max_retries': 5,
            'interval_start': 0,
            'interval_step': 0.2,
            'interval_max': 0.2,
        }
    )

@app.task(bind=True)
def debug_task(self):
    """Tarea de debug para verificar que Celery está funcionando correctamente"""
    print(f'Request: {self.request!r}')
    return "Celery está funcionando correctamente!"

# Manejador de señales para logging
from celery.signals import task_prerun, task_postrun, task_failure

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Se ejecuta antes de que inicie una tarea"""
    print(f'Iniciando tarea: {task} con ID: {task_id}')

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds):
    """Se ejecuta después de que termina una tarea"""
    print(f'Tarea completada: {task} con ID: {task_id}, Estado: {state}')

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, einfo=None, **kwds):
    """Se ejecuta cuando una tarea falla"""
    print(f'Tarea fallida: {sender} con ID: {task_id}, Excepción: {exception}')

# Función para testing
def test_celery():
    """Función para probar la conectividad de Celery"""
    try:
        # Verificar que el broker esté accesible
        inspect = app.control.inspect()
        stats = inspect.stats()
        if stats:
            print("✅ Celery broker está accesible")
            return True
        else:
            print("❌ No se puede conectar al broker de Celery")
            return False
    except Exception as e:
        print(f"❌ Error conectando a Celery: {e}")
        return False

if __name__ == '__main__':
    app.start()