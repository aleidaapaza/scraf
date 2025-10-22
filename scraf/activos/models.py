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
        return f"{self.nombre} - {self.grupo_contable.nombre}"
    
    class Meta:
        verbose_name = "Auxiliar Contable"
        verbose_name_plural = "Auxiliares Contables"
        # Opcional: evitar duplicados dentro del mismo grupo
        unique_together = ['nombre', 'grupo_contable']
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
        # Validar que el auxiliar contable pertenece al grupo contable seleccionado
        if self.auxiliar_contable and self.grupo_contable:
            if self.auxiliar_contable.grupo_contable != self.grupo_contable:
                raise ValidationError({'auxiliar_contable': 'El auxiliar contable debe pertenecer al grupo contable seleccionado'})
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.slug}-{self.nombre}'
    
    class Meta:
        verbose_name = ('Activo')
        verbose_name_plural = ('Activos')
        db_table = 'Activo'

class MantenimientoActivo(models.Model):
    activo = models.ForeignKey(Activo, on_delete=models.CASCADE, related_name='mantenimiento')
    estado = models.BooleanField() #Activo/Inactivo
    fechaInicio = models.DateField()
    fechaFin=models.DateField(null=True, blank=True)
    descripcionInicio = models.TextField()
    descripcionFin = models.TextField(null=True, blank=True)
    asignadorInicio = models.ForeignKey(Personal, to_field='slug', on_delete=models.CASCADE, related_name = 'mantenimientoAsignador')
    asignadorFin = models.ForeignKey(Personal, to_field='slug', on_delete=models.CASCADE, null=True, blank=True, related_name = 'mantenimientoAsignador')
    
    def __str__(self):
        return f'{self.activo.codigo}-{self.estado}'
    
    class Meta:
        verbose_name = ('MantenimientoActivo')
        verbose_name_plural = ('MantenimientosActivos')
        db_table = 'MantenimientoActivo'

class Activo_responsable(models.Model):
    slug = models.SlugField(null=True, blank=True, unique=False) #CodigoAsignacion
    activo = models.ForeignKey(Activo, to_field='codigo', on_delete=models.CASCADE, related_name = 'activoresponsablet')
    responsable = models.ForeignKey(Personal, to_field='slug', on_delete=models.CASCADE, null=True, blank=True, related_name = 'personaResponsable')
    piso_ubicacion = models.CharField(choices=pisos_ubicacion, null=True, blank=True)
    oficina_ubicacion = models.CharField(choices=oficinas_ubicacion, null=True, blank=True)
    
    def __str__(self):
        return f'{self.slug}-{self.activo}-{self.responsable}'
    def lugar(self):
        return f'{self.piso_ubicacion} {self.oficina_ubicacion}'
    def ultima_fecha_registro(self):
        from activos.models import Activos_line
        ultimo = Activos_line.objects.filter(slug=self.slug).order_by('-fecha_registro').first()
        return ultimo.fecha_registro if ultimo else None
    
    class Meta:
        verbose_name = ('Activo_responsable')
        verbose_name_plural = ('Activos_responsables')
        db_table = 'Activo_responsable'

pre_save.connect(set_slug, sender=Activo_responsable)

class Activos_line(models.Model):
    slug = models.SlugField(null=True, blank=True, unique=False)
    creador = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    responsable = models.ForeignKey(Personal, to_field='slug', on_delete=models.PROTECT, null=True, blank=True)
    piso_ubicacion = models.CharField(choices=pisos_ubicacion)
    oficina_ubicacion = models.CharField(choices=oficinas_ubicacion)
    estado = models.CharField(choices=estados)
    observacion= models.TextField()
    
    def __str__(self):
        return f'{self.slug}-{self.estado}'    
    class Meta:
        verbose_name = ('Activo_line')
        verbose_name_plural = ('Activos_line')
        db_table = 'Activo_line'