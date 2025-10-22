from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
import uuid
from django.utils.text import slugify
# Create your models here.
def set_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = slugify(
            '{}'.format(str(uuid.uuid4())[:4])
        )
        instance.slug = slug

class Persona(models.Model):
    nombre = models.CharField(max_length=100, null=False, blank=False)
    apellido = models.CharField(max_length=100, null=False, blank=False)
    cargo = models.CharField(max_length=255, null=False, blank=False)
    contacto = models.IntegerField(null=False, blank=False)
    carnet = models.IntegerField(null=False, blank=False, unique=True)

    def __str__(self):
        return f'{self.nombre} {self.apellido}'
    
    def nombrecompleto(self):
        return f'{self.nombre} {self.apellido}'

    def save(self, *args, **kwargs):
        self.nombre = (self.nombre).upper()
        self.apellido = (self.apellido).upper()
        self.cargo = (self.cargo).upper()
        return super(Persona, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('Persona')
        verbose_name_plural = _('Personas')
        db_table = 'Persona'

    def nombrecompleto(self):
        return f'{self.nombre} {self.apellido}'

class AccountManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, username, password, **extra_fields):
        values = [username]
        field_value_map = dict(zip(self.model.REQUIRED_FIELDS, values))

        for field_usuario, value in field_value_map.items():
            if not value:
                raise ValueError('Se debe establecer {}'.format(field_usuario))
        user = self.model(
              username=username,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_revisor', False)
        extra_fields.setdefault('is_personal', False)
        return self._create_user(username, password, **extra_fields)
    
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_personal', False)
        extra_fields.setdefault('is_revisor', False)
        if extra_fields.get('is_personal') is True:
            raise ValueError('El SUPERUSER debe tener is_personal=False.')
        if extra_fields.get('is_revisor') is True:
            raise ValueError('El SUPERUSER debe tener is_revisor=False.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El Superuser debe tener is_superuser=True.')
        
        return SuperUser.objects.create(
            persona = Persona.objects.create(nombre = 'NOMBRE', apellido = 'APELLIDO', cargo = 'CARGO', contacto = '000000', carnet = '1111111'),
            user=self._create_user(username, password, **extra_fields),
            )
        
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('Usuario'), max_length=255, unique=True)
    fecha_registro = models.DateTimeField(_('Fecha Registro'), auto_now_add=True)
    is_active = models.BooleanField(_('Activo'), default=True)
    is_personal = models.BooleanField(_('Estado Personal'), default=False)    
    is_revisor = models.BooleanField(_('Estado Revisor'), default=False)
    is_superuser = models.BooleanField(_('Estado Superuser'), default=False)
    is_encargado = models.BooleanField(default=False)
    g_personal = models.BooleanField(default=False) #gestionPersonal
    g_Activos = models.BooleanField(default=False) #gestionaActivos
    v_Activos = models.BooleanField(default=False)  #VisualizaTodosActivos
    g_mantenimiento = models.BooleanField(default=False) #Puede poner en mantenimiento un activo
    
    objects = AccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.username}'

    class Meta:
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')
        db_table = 'User'


class Personal(models.Model):
    slug = models.SlugField(null=False, blank=False, unique=True)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, related_name="personal_perfil",on_delete=models.CASCADE)
    
    def __str__(self):
        return f' {self.slug}-{self.persona.nombre}-{self.persona.apellido}'
    
    class Meta:
        verbose_name = _('Personal')
        verbose_name_plural = _('Personal')
        db_table = 'Personal'

pre_save.connect(set_slug, sender=Personal)

class SuperUser(models.Model):
    slug = models.SlugField(null=False, blank=False, unique=True)
    persona = models.OneToOneField(Persona, related_name="superuser_persona", on_delete=models.CASCADE)
    user = models.OneToOneField(User,related_name="superuser_perfil", on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.persona.nombre} {self.persona.apellido}'
    
    class Meta:
        verbose_name = _('SuperUser')
        verbose_name_plural = _('SuperUsers')
        db_table = 'SuperUser'

pre_save.connect(set_slug, sender=SuperUser)
 
class LinePersona(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='LinePersona')
    fechaRegistro = models.DateField(auto_now_add=True)
    cargo_anterior = models.CharField(max_length=150, null=True, blank=True)
    contacto_anterior = models.CharField(max_length=150, null=True, blank=True)
    encargado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='LinePersonaResponsable')

    def __str__(self):
        return f'Línea de {self.persona} - {self.fechaRegistro}'
    
    class Meta:
        verbose_name = _('LinePersona')
        verbose_name_plural = _('LinePersona')
        ordering = ['-fechaRegistro']
        db_table = 'LinePersona'