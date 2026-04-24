from django.db import models

from .admin import (
    Holding
)

class Clientes(models.Model):
    id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    rut =  models.CharField(max_length=255, unique=True)
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    giro = models.CharField(max_length=255)
    nombre_rep_legal = models.CharField(max_length=255,null=True, blank=True)
    direccion_rep_legal = models.CharField(max_length=255,null=True, blank=True)
    comuna_cliente = models.CharField(max_length=255, null=True, blank=True)
  
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
    telefono = models.CharField(max_length=20, null=True, blank=True)  # CAMBIO AQUÍ
    correo = models.EmailField(unique=True)
    
    class Meta:
        db_table = 'contactos_clientes'
