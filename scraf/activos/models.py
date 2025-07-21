from django.db import models
import uuid
from django.utils.text import slugify
from django.db.models.signals import pre_save

from users.models import Personal
from activos.choices import estados, oficinas_ubicacion, pisos_ubicacion
# Create your models here.

def set_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = slugify(
            '{}'.format(str(uuid.uuid4())[:4])
        )
        instance.slug = slug

class Activo(models.Model):
    codigo = models.CharField(max_length=50, null=False, blank=False, unique=True)
    descActivo= models.TextField(null=False, blank=False)
    descripcion= models.CharField(max_length=100, null=False, blank=False)
    
    def __str__(self):
        return f'{self.slug}-{self.nombre}'    
    class Meta:
        verbose_name = ('Activo')
        verbose_name_plural = ('Activos')
        db_table = 'Activo'
        
class Activo_responsable(models.Model):
    slug = models.SlugField(null=False, blank=False, unique=True)
    activo = models.ForeignKey(Activo, to_field='codigo', on_delete=models.CASCADE)
    responsable = models.ForeignKey(Personal, to_field='slug', on_delete=models.CASCADE, null=True, blank=True)
    piso_ubicacion = models.CharField(choices=pisos_ubicacion, null=True, blank=True)
    oficina_ubicacion = models.CharField(choices=oficinas_ubicacion, null=True, blank=True)
    estado = models.CharField(choices=estados, null=True, blank=True, default='Bueno')
    
    def __str__(self):
        return f'{self.slug}-{self.activo}-{self.responsable}'    
    class Meta:
        verbose_name = ('Activo_responsable')
        verbose_name_plural = ('Activos_responsables')
        db_table = 'Activo_responsable'

pre_save.connect(set_slug, sender=Activo_responsable)

class Activos_line(models.Model):
    slug = models.SlugField(null=True, blank=True, unique=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    responsable = models.ForeignKey(Personal, to_field='slug', on_delete=models.PROTECT, null=True, blank=True)
    piso_ubicacion = models.CharField(choices=pisos_ubicacion, null=True, blank=True)
    oficina_ubicacion = models.CharField(choices=oficinas_ubicacion, null=True, blank=True)
    estado = models.CharField(choices=estados, null=True, blank=True, default='Bueno')
    observacion= models.TextField()    
    creador = models.CharField(max_length=100, null=False, blank=False, default="q")
    
    def __str__(self):
        return f'{self.slug}-{self.estado}'    
    class Meta:
        verbose_name = ('Activo_line')
        verbose_name_plural = ('Activos_line')
        db_table = 'Activo_line'