# Generated by Django 5.2.4 on 2025-07-21 08:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activos', '0001_initial'),
        ('users', '0002_rename_edit_activos_user_g_activos_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activos_line',
            name='oficina_ubicacion',
            field=models.CharField(blank=True, choices=[('DIRECCION GENERAL EJECUTIVA', 'DIRECCION GENERAL EJECUTIVA'), ('DGE-SECRETARIA GENERAL', 'DGE-SECRETARIA GENERAL'), ('DGE-VENTANILLA UNICA', 'DGE-VENTANILLA UNICA'), ('DGE-COMUNICACION', 'DGE-COMUNICACION'), ('DGE-FINANCIAMIENTO', 'DGE-FINANCIAMIENTO'), ('ASESORIA LEGAL', 'ASESORIA LEGAL'), ('AUDITORIA INTERNA', 'AUDITORIA INTERNA'), ('GESTION INSTITUDIONAL Y DESARROLLO ORGANIZACIONAL', 'GESTION INSTITUDIONAL Y DESARROLLO ORGANIZACIONAL'), ('COORDINACION ADMINISTRATIVA FINANCIERA', 'COORDINACION ADMINISTRATIVA FINANCIERA'), ('ADMINISTRACION', 'ADMINISTRACION'), ('ADMINISTRACION-RECURSOS HUMANOS', 'ADMINISTRACION-RECURSOS HUMANOS'), ('ADMINISTRACION-ACTIVOS FIJOS', 'ADMINISTRACION-ACTIVOS FIJOS'), ('ADMINISTRACION-CONTRATACIONES', 'ADMINISTRACION-CONTRATACIONES'), ('ADMINISTRACION-ALMACENES', 'ADMINISTRACION-ALMACENES'), ('FINANZAS', 'FINANZAS'), ('COORDINACION DE PLANIFICACION Y EVALUACION DE PROYECTOS', 'COORDINACION DE PLANIFICACION Y EVALUACION DE PROYECTOS'), ('PLANIFICACION Y EVALUACION DE PROYECTOS', 'PLANIFICACION Y EVALUACION DE PROYECTOS'), ('CONTROL, SEGUIMIENTO Y MONITORIO DE PROYECTOS', 'CONTROL, SEGUIMIENTO Y MONITORIO DE PROYECTOS'), ('TRANSPARENCIA Y LUCHA CONTRA LA CORRUPCION', 'TRANSPARENCIA Y LUCHA CONTRA LA CORRUPCION'), ('TECNOLOGIAS DE INFORMACION Y COMUNICACION', 'TECNOLOGIAS DE INFORMACION Y COMUNICACION'), ('DATA CENTER', 'DATA CENTER'), ('ENTRADA', 'ENTRADA'), ('PASILLO', 'PASILLO'), ('ALMACEN', 'ALMACEN'), ('EXTERNO', 'EXTERNO')], null=True),
        ),
        migrations.AlterField(
            model_name='activos_line',
            name='piso_ubicacion',
            field=models.CharField(blank=True, choices=[('PISO 5', 'PISO 5'), ('PISO 4', 'PISO 4'), ('PISO 3', 'PISO 3'), ('PISO 1', 'PISO 1'), ('SEGURIDAD', 'SEGURIDAD'), ('PATIO/GARAJE', 'PATIO/GARAJE'), ('TERRAZA', 'TERRAZA'), ('EXTRAVIADO/PERDIDO', 'EXTRAVIADO/PERDIDO'), ('EXTERNO', 'EXTERNO')], null=True),
        ),
        migrations.AlterField(
            model_name='activos_line',
            name='responsable',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.personal', to_field='slug'),
        ),
        migrations.AlterField(
            model_name='activos_line',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
    ]
