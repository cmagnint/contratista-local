from django.db import models
from .admin import (
    Holding,
    Sociedad,
)
from .clientes import (
    Clientes,
    CamposClientes,
)
from .auth import Usuarios
from .personal import PersonalTrabajadores
from .parametros import Labores


class Banco(models.Model):
    id = models.AutoField(primary_key=True)
    codigo_sbif = models.CharField(max_length=3, unique=True)
    nombre = models.TextField()

    class Meta:
        db_table = 'banco'
        ordering = ['codigo_sbif']

    def __str__(self):
        return f"{self.nombre} ({self.codigo_sbif})"


class Cuenta(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    nombre_cuenta = models.CharField(max_length=255)
    cuenta_contable = models.CharField(max_length=50)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'cuentas'
        unique_together = [['holding', 'cuenta_contable']]
        ordering = ['nombre_cuenta']

    def __str__(self):
        return f"{self.nombre_cuenta} ({self.cuenta_contable})"


class ConfiguracionSIIAutomaticaCompra(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    rut_sii = models.CharField(max_length=12)
    password_sii = models.CharField(max_length=255)
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
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE)
    fundo = models.ForeignKey(CamposClientes, on_delete=models.SET_NULL, null=True, blank=True)
    labor = models.ForeignKey(Labores, on_delete=models.SET_NULL, null=True, blank=True)
    cuenta = models.ForeignKey(Cuenta, on_delete=models.SET_NULL, null=True, blank=True)
    folio = models.CharField(max_length=50)
    tipo_doc = models.CharField(max_length=50)
    tipo_compra = models.CharField(max_length=50, blank=True, null=True)
    rut_proveedor = models.CharField(max_length=20)
    razon_social = models.CharField(max_length=255)
    fecha_docto = models.CharField(max_length=20)
    fecha_recepcion = models.CharField(max_length=20, blank=True, null=True)
    fecha_acuse = models.CharField(max_length=20, blank=True, null=True)
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
    monto_distribuido = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    porcentaje_distribuido = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    tipo_distribucion = models.CharField(
        max_length=10,
        choices=[('MONTO', 'Por Monto'), ('PORCENTAJE', 'Por Porcentaje')],
        default='MONTO', null=True
    )
    monto_total_factura = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    usuario_distribuyente = models.ForeignKey(Usuarios, on_delete=models.SET_NULL, null=True)
    fecha_distribucion = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'facturas_sii_distribuidas'
        unique_together = []
        ordering = ['-fecha_distribucion']
        indexes = [
            models.Index(fields=['holding', 'folio', 'rut_proveedor'], name='facturas_sii_dist_lookup_idx'),
            models.Index(fields=['cliente', 'fecha_distribucion'], name='facturas_sii_dist_cliente_idx'),
            models.Index(fields=['holding', 'fecha_distribucion'], name='facturas_sii_dist_holding_idx'),
            models.Index(fields=['tipo_distribucion'], name='facturas_sii_dist_tipo_idx'),
        ]

    def __str__(self):
        return f"Factura {self.tipo_doc} - {self.folio} - {self.cliente.nombre} ({self.porcentaje_distribuido}%)"

    def get_distribucion_info(self):
        return {
            'id': self.id,
            'cliente': {'id': self.cliente.id, 'nombre': self.cliente.nombre, 'rut': self.cliente.rut},
            'fundo': {'id': self.fundo.id, 'nombre': self.fundo.nombre_campo, 'direccion': self.fundo.direccion_campo} if self.fundo else None,
            'labor': {'id': self.labor.id, 'nombre': self.labor.nombre, 'especie': self.labor.especie} if self.labor else None,
            'cuenta': {'id': self.cuenta.id, 'nombre': self.cuenta.nombre_cuenta, 'codigo': self.cuenta.cuenta_contable} if self.cuenta else None,
            'monto_distribuido': float(self.monto_distribuido),
            'porcentaje_distribuido': float(self.porcentaje_distribuido),
            'tipo_distribucion': self.tipo_distribucion,
            'monto_total_factura': float(self.monto_total_factura),
            'factura': {
                'folio': self.folio, 'tipo_doc': self.tipo_doc,
                'rut_proveedor': self.rut_proveedor, 'razon_social': self.razon_social,
                'fecha_docto': self.fecha_docto, 'monto_total_original': float(self.monto_total_factura)
            },
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
        if self.monto_total_factura and self.monto_total_factura > 0:
            return (self.monto_distribuido / self.monto_total_factura) * 100
        return 0

    def get_otras_distribuciones(self):
        return FacturaCompraSIIDistribuida.objects.filter(
            holding_id=self.holding_id, folio=self.folio, rut_proveedor=self.rut_proveedor
        ).exclude(id=self.id).order_by('-fecha_distribucion')

    def get_resumen_factura_completa(self):
        todas = FacturaCompraSIIDistribuida.objects.filter(
            holding_id=self.holding_id, folio=self.folio, rut_proveedor=self.rut_proveedor
        ).order_by('-fecha_distribucion')
        total_distribuido = sum(d.monto_distribuido for d in todas)
        total_porcentaje = sum(d.porcentaje_distribuido for d in todas)
        return {
            'factura': {'folio': self.folio, 'tipo_doc': self.tipo_doc, 'razon_social': self.razon_social, 'monto_total': float(self.monto_total_factura)},
            'distribuciones': {
                'total_distribuciones': todas.count(),
                'monto_total_distribuido': float(total_distribuido),
                'porcentaje_total_distribuido': float(total_porcentaje),
                'monto_pendiente': float(self.monto_total_factura - total_distribuido),
                'porcentaje_pendiente': float(100 - total_porcentaje),
                'completamente_distribuida': total_porcentaje >= 100
            },
            'detalle_distribuciones': [
                {'id': d.id, 'cliente_nombre': d.cliente.nombre, 'monto_distribuido': float(d.monto_distribuido),
                 'porcentaje_distribuido': float(d.porcentaje_distribuido), 'fecha_distribucion': d.fecha_distribucion.strftime('%d/%m/%Y %H:%M')}
                for d in todas
            ]
        }

    def get_distribucion_completa(self):
        return {
            'cliente': {'id': self.cliente.id, 'nombre': self.cliente.nombre, 'rut': self.cliente.rut},
            'fundo': {'id': self.fundo.id, 'nombre': self.fundo.nombre_campo, 'direccion': self.fundo.direccion_campo} if self.fundo else None,
            'labor': {'id': self.labor.id, 'nombre': self.labor.nombre, 'especie': self.labor.especie} if self.labor else None,
            'cuenta': {'id': self.cuenta.id, 'nombre': self.cuenta.nombre_cuenta, 'codigo': self.cuenta.cuenta_contable} if self.cuenta else None,
            'factura': {
                'folio': self.folio, 'tipo_doc': self.tipo_doc, 'proveedor': self.razon_social,
                'fecha': self.fecha_docto, 'monto_total': float(self.monto_total_factura),
                'monto_distribuido': float(self.monto_distribuido), 'porcentaje_distribuido': float(self.porcentaje_distribuido)
            }
        }

    def save(self, *args, **kwargs):
        if self.monto_distribuido and self.monto_total != self.monto_distribuido:
            self.monto_total = self.monto_distribuido
        if self.porcentaje_distribuido > 100:
            raise ValueError("El porcentaje distribuido no puede ser mayor a 100%")
        if self.monto_distribuido > self.monto_total_factura:
            raise ValueError("El monto distribuido no puede ser mayor al total de la factura")
        super().save(*args, **kwargs)


class FacturaCompraSIIPorDistribuir(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    folio = models.CharField(max_length=50)
    tipo_doc = models.CharField(max_length=50)
    tipo_compra = models.CharField(max_length=50, blank=True, null=True)
    rut_proveedor = models.CharField(max_length=20)
    razon_social = models.CharField(max_length=255)
    fecha_docto = models.CharField(max_length=20)
    fecha_recepcion = models.CharField(max_length=20, blank=True, null=True)
    fecha_acuse = models.CharField(max_length=20, blank=True, null=True)
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
    fecha_encontrada = models.DateTimeField(auto_now_add=True)
    procesada = models.BooleanField(default=False)
    monto_distribuido = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True)
    porcentaje_distribuido = models.DecimalField(max_digits=5, decimal_places=2, default=0, null=True)
    pdf_documento = models.FileField(upload_to='facturas_compra_sii_pdfs/', blank=True, null=True)
    codigo_sii = models.CharField(max_length=50, blank=True, null=True)
    pdf_descargado = models.BooleanField(default=False)
    fecha_descarga_pdf = models.DateTimeField(blank=True, null=True)
    error_descarga_pdf = models.TextField(blank=True, null=True)
    intentos_descarga_pdf = models.IntegerField(default=0)
    es_manual = models.BooleanField(default=False)
    descripcion = models.TextField(blank=True, null=True)
    observaciones_manual = models.TextField(blank=True, null=True)
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

    def get_monto_pendiente(self):
        from decimal import Decimal
        return self.monto_total - (self.monto_distribuido or Decimal('0'))

    def get_porcentaje_pendiente(self):
        from decimal import Decimal
        return Decimal('100') - (self.porcentaje_distribuido or Decimal('0'))

    def esta_completamente_distribuida(self):
        from decimal import Decimal
        return (self.porcentaje_distribuido or Decimal('0')) >= Decimal('100')

    def puede_distribuir_monto(self, monto):
        return monto <= self.get_monto_pendiente()

    def puede_distribuir_porcentaje(self, porcentaje):
        return porcentaje <= self.get_porcentaje_pendiente()

    def get_distribuciones(self):
        return FacturaCompraSIIDistribuida.objects.filter(
            holding_id=self.holding_id, folio=self.folio, rut_proveedor=self.rut_proveedor
        ).order_by('-fecha_distribucion')

    def get_resumen_distribuciones(self):
        distribuciones = self.get_distribuciones()
        return {
            'total_distribuciones': distribuciones.count(),
            'clientes_distintos': distribuciones.values('cliente').distinct().count(),
            'distribuciones': [
                {'id': d.id, 'cliente_nombre': d.cliente.nombre, 'monto_distribuido': float(d.monto_distribuido),
                 'porcentaje_distribuido': float(d.porcentaje_distribuido), 'fecha_distribucion': d.fecha_distribucion.strftime('%d/%m/%Y %H:%M')}
                for d in distribuciones[:10]
            ]
        }

    def actualizar_totales_distribucion(self):
        distribuciones = self.get_distribuciones()
        total_monto = sum(d.monto_distribuido for d in distribuciones)
        total_porcentaje = sum(d.porcentaje_distribuido for d in distribuciones)
        self.monto_distribuido = total_monto
        self.porcentaje_distribuido = total_porcentaje
        self.procesada = self.esta_completamente_distribuida()
        self.save(update_fields=['monto_distribuido', 'porcentaje_distribuido', 'procesada'])
        return {'monto_distribuido': float(self.monto_distribuido), 'porcentaje_distribuido': float(self.porcentaje_distribuido), 'procesada': self.procesada}

    def get_pdf_disponible(self):
        if getattr(self, 'es_manual', False):
            return False
        return getattr(self, 'pdf_descargado', False)

    def get_factura_data(self):
        return {
            'nro': str(self.id), 'id': self.id, 'tipo_doc': self.tipo_doc,
            'tipo_compra': self.tipo_compra, 'rut_proveedor': self.rut_proveedor,
            'razon_social': self.razon_social, 'folio': self.folio,
            'fecha_docto': self.fecha_docto, 'fecha_recepcion': self.fecha_recepcion,
            'fecha_acuse': self.fecha_acuse, 'monto_total': float(self.monto_total),
            'monto_neto': float(self.monto_neto), 'monto_exento': float(self.monto_exento),
            'iva_recuperable': float(self.monto_iva_recuperable),
            'monto_distribuido': float(self.monto_distribuido),
            'monto_pendiente': float(self.get_monto_pendiente()),
            'porcentaje_distribuido': float(self.porcentaje_distribuido),
            'porcentaje_pendiente': float(self.get_porcentaje_pendiente()),
            'completamente_distribuida': self.esta_completamente_distribuida(),
            'distribuciones_count': self.get_distribuciones().count(),
            'distribuciones': self.get_resumen_distribuciones()['distribuciones'],
            'pdf_disponible': bool(self.pdf_documento),
            'pdf_url': self.pdf_documento.url if self.pdf_documento else None,
            'pdf_descargado': self.pdf_descargado,
            'fecha_descarga_pdf': self.fecha_descarga_pdf.isoformat() if self.fecha_descarga_pdf else None,
            'fecha_descarga_pdf_formatted': self.fecha_descarga_pdf.strftime('%d/%m/%Y %H:%M') if self.fecha_descarga_pdf else None,
            'error_descarga_pdf': self.error_descarga_pdf,
            'intentos_descarga_pdf': self.intentos_descarga_pdf,
            'codigo_sii': self.codigo_sii,
            'fecha_encontrada': self.fecha_encontrada.isoformat() if self.fecha_encontrada else '',
            'procesada': self.procesada, 'selected': False
        }


class ConfiguracionSIIAutomaticaVenta(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    rut_sii = models.CharField(max_length=12)
    password_sii = models.CharField(max_length=255)
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
        unique_together = [['holding']]

    def __str__(self):
        return f"Config SII - {self.empresa_nombre} - {self.mes:02d}/{self.year}"


class FacturaVentaSIIPorDistribuir(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    nro = models.CharField(max_length=20, blank=True, null=True)
    tipo_doc = models.CharField(max_length=50)
    rut_receptor = models.CharField(max_length=20)
    razon_social_receptor = models.CharField(max_length=255)
    folio = models.CharField(max_length=50)
    fecha_emision = models.CharField(max_length=20)
    monto_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_neto = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_exento = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_iva = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_otros_impuestos = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    codigo_otros_impuestos = models.CharField(max_length=10, blank=True, null=True)
    fecha_encontrada = models.DateTimeField(auto_now_add=True)
    procesada = models.BooleanField(default=False)
    monto_distribuido = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True)
    porcentaje_distribuido = models.DecimalField(max_digits=5, decimal_places=2, default=0, null=True)
    pdf_documento = models.FileField(upload_to='facturas_venta_sii_pdfs/', blank=True, null=True)
    codigo_sii = models.CharField(max_length=50, blank=True, null=True)
    pdf_descargado = models.BooleanField(default=False)
    fecha_descarga_pdf = models.DateTimeField(blank=True, null=True)
    error_descarga_pdf = models.TextField(blank=True, null=True)
    intentos_descarga_pdf = models.IntegerField(default=0)
    es_manual = models.BooleanField(default=False)
    descripcion = models.TextField(blank=True, null=True)
    observaciones_manual = models.TextField(blank=True, null=True)
    fecha_creacion_manual = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'facturas_venta_sii_por_distribuir'
        unique_together = [['holding', 'folio']]
        ordering = ['-fecha_encontrada']
        indexes = [
            models.Index(fields=['holding', 'procesada']),
            models.Index(fields=['folio']),
            models.Index(fields=['pdf_descargado']),
            models.Index(fields=['fecha_encontrada']),
        ]

    def __str__(self):
        return f"Factura Venta {self.folio} - {self.razon_social_receptor} - ${self.monto_total:,.0f}"

    def get_monto_pendiente(self):
        return self.monto_total - (self.monto_distribuido or 0)

    def get_porcentaje_pendiente(self):
        return 100 - (self.porcentaje_distribuido or 0)

    def esta_completamente_distribuida(self):
        return (self.porcentaje_distribuido or 0) >= 100

    def get_distribuciones(self):
        return FacturaVentaSIIDistribuida.objects.filter(
            holding=self.holding, folio=self.folio
        ).order_by('-fecha_distribucion')

    def get_factura_data(self):
        return {
            'id': self.id, 'folio': self.folio, 'tipo_doc': self.tipo_doc,
            'receptor': {'rut': self.rut_receptor, 'razon_social': self.razon_social_receptor},
            'fechas': {'emision': self.fecha_emision, 'encontrada': self.fecha_encontrada.isoformat() if self.fecha_encontrada else None},
            'montos': {
                'total': float(self.monto_total), 'neto': float(self.monto_neto),
                'iva': float(self.monto_iva), 'distribuido': float(self.monto_distribuido or 0),
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
                'intentos': self.intentos_descarga_pdf, 'error': self.error_descarga_pdf
            }
        }

    def puede_distribuir_monto(self, monto):
        return monto <= self.get_monto_pendiente()

    def puede_distribuir_porcentaje(self, porcentaje):
        return porcentaje <= self.get_porcentaje_pendiente()

    def actualizar_totales_distribucion(self):
        from decimal import Decimal
        from django.db.models import Sum
        distribuciones = self.get_distribuciones()
        monto_total_distribuido = distribuciones.aggregate(total=Sum('monto_distribuido'))['total'] or Decimal('0')
        porcentaje_total_distribuido = (monto_total_distribuido / self.monto_total * 100) if self.monto_total > 0 else Decimal('0')
        self.monto_distribuido = monto_total_distribuido
        self.porcentaje_distribuido = porcentaje_total_distribuido
        self.procesada = porcentaje_total_distribuido >= Decimal('100')
        self.save(update_fields=['monto_distribuido', 'porcentaje_distribuido', 'procesada'])
        return {'monto_distribuido': float(monto_total_distribuido), 'porcentaje_distribuido': float(porcentaje_total_distribuido), 'completamente_distribuida': self.procesada}

    def get_pdf_disponible(self):
        if getattr(self, 'es_manual', False):
            return False
        return getattr(self, 'pdf_descargado', False)

    @property
    def monto_pendiente(self):
        return self.get_monto_pendiente()

    @property
    def porcentaje_pendiente(self):
        return self.get_porcentaje_pendiente()

    @property
    def completamente_distribuida(self):
        return self.esta_completamente_distribuida()

    @property
    def pdf_disponible(self):
        return self.get_pdf_disponible()


class FacturaVentaSIIDistribuida(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE)
    fundo = models.ForeignKey(CamposClientes, on_delete=models.SET_NULL, null=True, blank=True)
    labor = models.ForeignKey(Labores, on_delete=models.SET_NULL, null=True, blank=True)
    cuenta = models.ForeignKey(Cuenta, on_delete=models.SET_NULL, null=True, blank=True)
    folio = models.CharField(max_length=50)
    tipo_doc = models.CharField(max_length=50)
    rut_receptor = models.CharField(max_length=20)
    razon_social_receptor = models.CharField(max_length=255)
    fecha_emision = models.CharField(max_length=20)
    monto_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_neto = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_exento = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_iva = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monto_otros_impuestos = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    codigo_otros_impuestos = models.CharField(max_length=10, blank=True, null=True)
    monto_distribuido = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    porcentaje_distribuido = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tipo_distribucion = models.CharField(
        max_length=20,
        choices=[('MONTO', 'Por monto específico'), ('PORCENTAJE', 'Por porcentaje')],
        default='MONTO'
    )
    monto_total_factura = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True, null=True)
    usuario_distribuyente = models.ForeignKey(
        Usuarios, on_delete=models.SET_NULL, null=True,
        related_name='facturas_distribuidas'
    )
    fecha_distribucion = models.DateTimeField(auto_now_add=True)
    usuario_creador = models.ForeignKey(
        Usuarios, null=True, blank=True, on_delete=models.CASCADE,
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
        return self.monto_total - (self.monto_distribuido or 0)

    def get_porcentaje_pendiente(self):
        return 100 - (self.porcentaje_distribuido or 0)

    def puede_distribuir_monto(self, monto):
        return monto <= self.get_monto_pendiente()

    def puede_distribuir_porcentaje(self, porcentaje):
        return porcentaje <= self.get_porcentaje_pendiente()

    def get_distribucion_info(self):
        return {
            'id': self.id,
            'distribucion': {
                'cliente': {'id': self.cliente.id, 'nombre': self.cliente.nombre, 'rut': self.cliente.rut},
                'fundo': {'id': self.fundo.id, 'nombre': self.fundo.nombre_campo} if self.fundo else None,
                'labor': {'id': self.labor.id, 'nombre': self.labor.nombre, 'especie': self.labor.especie} if self.labor else None,
                'cuenta': {'id': self.cuenta.id, 'nombre': self.cuenta.nombre_cuenta, 'codigo': self.cuenta.cuenta_contable} if self.cuenta else None,
                'monto_distribuido': float(self.monto_distribuido),
                'porcentaje_distribuido': float(self.porcentaje_distribuido),
                'tipo_distribucion': self.tipo_distribucion,
                'observaciones': self.observaciones,
                'fecha_distribucion': self.fecha_distribucion.isoformat() if self.fecha_distribucion else None,
                'usuario_distribuyente': {
                    'id': self.usuario_distribuyente.id,
                    'rut': self.usuario_distribuyente.rut,
                    'nombre': f"{self.usuario_distribuyente.persona.nombres} {self.usuario_distribuyente.persona.apellidos}" if self.usuario_distribuyente and self.usuario_distribuyente.persona else None
                } if self.usuario_distribuyente else None
            },
            'factura': {
                'folio': self.folio, 'tipo_doc': self.tipo_doc,
                'receptor_original': self.razon_social_receptor, 'fecha_emision': self.fecha_emision,
                'monto_total_factura': float(self.monto_total_factura),
                'monto_distribuido': float(self.monto_distribuido),
                'porcentaje_distribuido': float(self.porcentaje_distribuido)
            }
        }

    def save(self, *args, **kwargs):
        if self.monto_distribuido and self.monto_total != self.monto_distribuido:
            self.monto_total = self.monto_distribuido
        if self.porcentaje_distribuido > 100:
            raise ValueError("El porcentaje distribuido no puede ser mayor a 100%")
        if self.monto_distribuido > self.monto_total_factura:
            raise ValueError("El monto distribuido no puede ser mayor al total de la factura")
        super().save(*args, **kwargs)


class CuentaOrigen(models.Model):
    sociedad = models.ForeignKey(Sociedad, on_delete=models.CASCADE, related_name='cuentas_origen')
    banco = models.ForeignKey(Banco, on_delete=models.PROTECT)
    tipo_cuenta = models.CharField(max_length=3)
    numero_cuenta = models.CharField(max_length=30)

    class Meta:
        db_table = 'cuenta_origen'


class CartolaMovimiento(models.Model):
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


class HistorialCambioPago(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    registro_transferencia = models.ForeignKey(
        'RegistroPagoTransferencia', on_delete=models.CASCADE, null=True, blank=True
    )
    registro_efectivo = models.ForeignKey(
        'RegistroPagoEfectivo', on_delete=models.CASCADE, null=True, blank=True
    )
    monto_pagado_anterior = models.IntegerField()
    monto_pagado_nuevo = models.IntegerField()
    saldo_anterior = models.IntegerField(null=True, blank=True)
    saldo_nuevo = models.IntegerField(null=True, blank=True)
    folio = models.ForeignKey('FolioComercial', on_delete=models.CASCADE)
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
    producciones = models.ManyToManyField('ProduccionTrabajador')
    archivo_csv = models.FileField(upload_to='pagos_csv/', null=True, blank=True)
    saldo = models.IntegerField(null=True, blank=True)
    historial_cambios = models.ManyToManyField(
        HistorialCambioPago, related_name='transferencias_modificadas', blank=True
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
    producciones = models.ManyToManyField('RegistroManoObraPersona')
    multiplo_pago = models.IntegerField()
    saldo = models.IntegerField(null=True, blank=True)
    historial_cambios = models.ManyToManyField(
        HistorialCambioPago, related_name='efectivos_modificados', blank=True
    )

    class Meta:
        db_table = 'registro_pagos_efectivo'