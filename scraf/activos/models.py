from django.db import models
import uuid
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError

from users.models import Personal, User
from activos.choices import estados, oficinas_ubicacion, pisos_ubicacion
# Create your models here.

def set_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = slugify(
            '{}'.format(str(uuid.uuid4())[:4])
        )
        instance.slug = slug

class GrupoContable(models.Model):
    nombre = models.CharField(max_length=100, null=False, unique=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Grupo Contable"
        verbose_name_plural = "Grupos Contables"
        db_table = 'GruposContables'

class AuxiliarContable(models.Model):
    nombre = models.CharField(max_length=100, null=False)
    grupocontable = models.ForeignKey(GrupoContable, on_delete=models.CASCADE, related_name='auxiliares')
    
    def __str__(self):
        return f"{self.nombre} - {self.grupocontable.nombre}"
    
    class Meta:
        verbose_name = "Auxiliar Contable"
        verbose_name_plural = "Auxiliares Contables"
        # Opcional: evitar duplicados dentro del mismo grupo
        unique_together = ['nombre', 'grupocontable']
        db_table = 'AuxiliarContable'

class Activo(models.Model):
    codigo = models.CharField(max_length=50, null=False, blank=False, unique=True)
    descActivo= models.TextField(null=False, blank=False)
    grupoContable= models.ForeignKey(GrupoContable, on_delete=models.CASCADE, related_name='activos')
    auxiliar= models.ForeignKey(AuxiliarContable, on_delete=models.CASCADE, related_name='activos')
    estadoActivo = models.CharField(choices=estados, null=True, blank=True)
    estadoDesignacion = models.BooleanField() #asignado/sindesignar
    mantenimiento = models.BooleanField()

    def clean(self):
        if self.auxiliar and self.grupoContable:
            if self.auxiliar.grupocontable != self.grupoContable:
                raise ValidationError({'auxiliar_contable': 'El auxiliar contable debe pertenecer al grupo contable seleccionado'})
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.codigo}-{self.descActivo}'
    
    class Meta:
        verbose_name = ('Activo')
        verbose_name_plural = ('Activos')
        db_table = 'Activo'

class MantenimientoActivo(models.Model):
    activo = models.ForeignKey(Activo, on_delete=models.CASCADE, related_name='mantenimientosactivos')
    estado = models.BooleanField() #Activo/Inactivo
    fechaInicio = models.DateField()
    fechaFin=models.DateField(null=True, blank=True)
    descripcionInicio = models.TextField()
    descripcionFin = models.TextField(null=True, blank=True)
    asignadorInicio = models.ForeignKey(Personal, to_field='slug', on_delete=models.CASCADE, related_name = 'mantenimientoAsignadorInicio')
    asignadorFin = models.ForeignKey(Personal, to_field='slug', on_delete=models.CASCADE, null=True, blank=True, related_name = 'mantenimientoAsignadorFin')
    
    def __str__(self):
        return f'{self.activo.codigo}-{self.estado}'
    
    class Meta:
        verbose_name = ('MantenimientoActivo')
        verbose_name_plural = ('MantenimientosActivos')
        db_table = 'MantenimientoActivo'

class Line_Activo(models.Model):
    activo = models.ForeignKey(Activo, on_delete=models.CASCADE, related_name='lineActivo', default="1")
    creador = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estadoActivo = models.CharField(choices=estados, null=True, blank=True)
    estadoDesignacion = models.BooleanField() #asignado/sindesignar
    mantenimiento = models.BooleanField()
    observacion= models.TextField()
    
    def __str__(self):
        return f'{self.activo}'    
    class Meta:
        verbose_name = ('Line_Activo')
        verbose_name_plural = ('Line_Activos')
        db_table = 'Line_Activo'