from django.db import models
import uuid
from django.utils.text import slugify
from django.db.models.signals import pre_save
from datetime import datetime

from activos.models import Activo
from users.models import Personal, User
from activos.choices import estados, oficinas_ubicacion, pisos_ubicacion

# Create your models here.
def set_slug1(sender, instance, *args, **kwargs):
    año = datetime.now().year
    mes = datetime.now().month
    if not instance.slug:
        slug = slugify(
            '{} {} {}'.format(año, mes, str(uuid.uuid4())[:4])
        )
        instance.slug = slug

class Asignacion_Devolucion(models.Model):
    slug = models.SlugField(null=True, blank=True, unique=False) 
    estado = models.BooleanField() #activo_inactivo
    fecha_asignacion = models.DateField(auto_now_add=True)
    carnet = models.IntegerField()
    fecha_devolucion = models.DateField()
    # Guardar los IDs/códigos de activos como lista JSON
    codigoActivo = models.JSONField(default=list, blank=True, help_text="Lista de códigos de activos asignados")
    
    def __str__(self):
        return f'{self.slug}-{self.carnet}'
    
    def agregar_activo(self, codigo_activo):
        """Agregar un código de activo a la lista"""
        if codigo_activo not in self.codigoActivo:
            self.codigoActivo.append(codigo_activo)
            self.save()
            
    def tiene_activo(self, codigo_activo):
        """Verificar si tiene un activo específico"""
        return codigo_activo in self.codigoActivo
    
    def cantidad_activos(self):
        """Obtener cantidad de activos"""
        return len(self.codigoActivo)
    
pre_save.connect(set_slug1, sender=Asignacion_Devolucion)
    
class Activo_responsable(models.Model):
    asig_devol = models.ForeignKey(Asignacion_Devolucion,  to_field='slug', on_delete=models.CASCADE, related_name='asignacionResponsable') #CodigoAsignacion
    activo = models.ForeignKey(Activo, to_field='codigo', on_delete=models.CASCADE, related_name = 'activoResponsable')
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

class Line_Asignacion_Devolucion(models.Model):
    slug = models.ForeignKey(Asignacion_Devolucion, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField() #activo_inactivo
    observacion = models.TextField()


class Line_Activo_Responsable(models.Model):
    slug = models.ForeignKey(Activo, on_delete=models.CASCADE)
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
        verbose_name = ('Line_Activo_Responsable')
        verbose_name_plural = ('Line_Activo_Responsable')
        db_table = 'Line_Activo_Responsable'

