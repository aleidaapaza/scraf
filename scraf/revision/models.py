from django.db import models
import uuid
from django.utils.text import slugify
from django.db.models.signals import pre_save

from users.models import Personal, User
from activos.models import Activo
from revision.upload import doc_respaldo
from revision.choices import motivos
# Create your models here.
def set_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = slugify(
            '{}'.format(str(uuid.uuid4())[:4])
        )
        instance.slug = slug

class Revision(models.Model):
    slug = models.SlugField(null=False, blank=False, unique=True)
    motivo = models.CharField(choices=motivos, null=False, blank=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(null=True)
    nombre = models.CharField(max_length=255, null=False, blank=False)
    descripcion = models.TextField(blank=False, null=False)
    encargado = models.ForeignKey(Personal, to_field='slug', null=False, blank=False, on_delete=models.CASCADE)
    revisores = models.ManyToManyField(Personal, to_field='slug', related_name='revisiones_apoyadas', blank=True)
    fechaHora_inicio = models.DateTimeField(blank=True, null=True)
    fechaHora_finalizacion = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f'{self.slug}-{self.nombre}'    
    class Meta:
        verbose_name = ('Revision')
        verbose_name_plural = ('Revision')
        db_table = 'Revisiones'

pre_save.connect(set_slug, sender=Revision)

class Revision_line(models.Model):
    revision = models.ForeignKey(Revision, related_name='revision_datos', on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=255, blank=False, null=False)
    creador = models.CharField(max_length=255, blank=False, null=False)
    observacion = models.TextField()
    
    def __str__(self):
        return f'{self.slug}-{self.estado}'    
    class Meta:
        verbose_name = ('Revision_line')
        verbose_name_plural = ('Revision_line')
        db_table = 'Revision_line'

class Revision_Activo(models.Model):
    revision = models.ForeignKey(Revision, on_delete=models.CASCADE, related_name='revision_activos')
    activo = models.ForeignKey(Activo, to_field='codigo', on_delete=models.CASCADE, related_name='ActivoRevision', )
    estado = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    encargado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='encargadoRevision')
    observacion = models.TextField()

    def __str__(self):
        return f'{self.slug}-{self.revision.nombre}-{self.activo_res.activo.codigo}'    
    class Meta:
        verbose_name = ('Revision_Activo')
        verbose_name_plural = ('Revision_Activo')
        db_table = 'Revision_Activo'
