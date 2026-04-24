from django.db import models

class Holding(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)
    estado = models.BooleanField(default=True)
    firma_empleador = models.ImageField(
        upload_to='firmas/firma_empleador/', 
        null=True, 
        blank=True,
        help_text="Firma del empleador para contratos"
    )
    
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

