# Generated by Django 5.2.4 on 2025-07-21 07:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_rename_edit_activos_user_g_activos_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=50, unique=True)),
                ('descActivo', models.TextField()),
                ('descripcion', models.CharField(max_length=100)),
                ('estado', models.CharField(choices=[('Bueno', 'Bueno'), ('Regular', 'Regular'), ('Malo', 'Malo')])),
            ],
            options={
                'verbose_name': 'Activo',
                'verbose_name_plural': 'Activos',
                'db_table': 'Activo',
            },
        ),
        migrations.CreateModel(
            name='Activo_responsable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('piso_ubicacion', models.CharField(choices=[('PISO 5', 'PISO 5'), ('PISO 4', 'PISO 4'), ('PISO 3', 'PISO 3'), ('PISO 1', 'PISO 1'), ('SEGURIDAD', 'SEGURIDAD'), ('PATIO/GARAJE', 'PATIO/GARAJE'), ('TERRAZA', 'TERRAZA'), ('EXTRAVIADO/PERDIDO', 'EXTRAVIADO/PERDIDO'), ('EXTERNO', 'EXTERNO')])),
                ('oficina_ubicacion', models.CharField(choices=[('DIRECCION GENERAL EJECUTIVA', 'DIRECCION GENERAL EJECUTIVA'), ('DGE-SECRETARIA GENERAL', 'DGE-SECRETARIA GENERAL'), ('DGE-VENTANILLA UNICA', 'DGE-VENTANILLA UNICA'), ('DGE-COMUNICACION', 'DGE-COMUNICACION'), ('DGE-FINANCIAMIENTO', 'DGE-FINANCIAMIENTO'), ('ASESORIA LEGAL', 'ASESORIA LEGAL'), ('AUDITORIA INTERNA', 'AUDITORIA INTERNA'), ('GESTION INSTITUDIONAL Y DESARROLLO ORGANIZACIONAL', 'GESTION INSTITUDIONAL Y DESARROLLO ORGANIZACIONAL'), ('COORDINACION ADMINISTRATIVA FINANCIERA', 'COORDINACION ADMINISTRATIVA FINANCIERA'), ('ADMINISTRACION', 'ADMINISTRACION'), ('ADMINISTRACION-RECURSOS HUMANOS', 'ADMINISTRACION-RECURSOS HUMANOS'), ('ADMINISTRACION-ACTIVOS FIJOS', 'ADMINISTRACION-ACTIVOS FIJOS'), ('ADMINISTRACION-CONTRATACIONES', 'ADMINISTRACION-CONTRATACIONES'), ('ADMINISTRACION-ALMACENES', 'ADMINISTRACION-ALMACENES'), ('FINANZAS', 'FINANZAS'), ('COORDINACION DE PLANIFICACION Y EVALUACION DE PROYECTOS', 'COORDINACION DE PLANIFICACION Y EVALUACION DE PROYECTOS'), ('PLANIFICACION Y EVALUACION DE PROYECTOS', 'PLANIFICACION Y EVALUACION DE PROYECTOS'), ('CONTROL, SEGUIMIENTO Y MONITORIO DE PROYECTOS', 'CONTROL, SEGUIMIENTO Y MONITORIO DE PROYECTOS'), ('TRANSPARENCIA Y LUCHA CONTRA LA CORRUPCION', 'TRANSPARENCIA Y LUCHA CONTRA LA CORRUPCION'), ('TECNOLOGIAS DE INFORMACION Y COMUNICACION', 'TECNOLOGIAS DE INFORMACION Y COMUNICACION'), ('DATA CENTER', 'DATA CENTER'), ('ENTRADA', 'ENTRADA'), ('PASILLO', 'PASILLO'), ('ALMACEN', 'ALMACEN'), ('EXTERNO', 'EXTERNO')])),
                ('activo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='activos.activo', to_field='codigo')),
                ('responsable', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.personal', to_field='slug')),
            ],
            options={
                'verbose_name': 'Activo_responsable',
                'verbose_name_plural': 'Activos_responsables',
                'db_table': 'Activo_responsable',
            },
        ),
        migrations.CreateModel(
            name='Activos_line',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('piso_ubicacion', models.CharField(choices=[('PISO 5', 'PISO 5'), ('PISO 4', 'PISO 4'), ('PISO 3', 'PISO 3'), ('PISO 1', 'PISO 1'), ('SEGURIDAD', 'SEGURIDAD'), ('PATIO/GARAJE', 'PATIO/GARAJE'), ('TERRAZA', 'TERRAZA'), ('EXTRAVIADO/PERDIDO', 'EXTRAVIADO/PERDIDO'), ('EXTERNO', 'EXTERNO')])),
                ('oficina_ubicacion', models.CharField(choices=[('DIRECCION GENERAL EJECUTIVA', 'DIRECCION GENERAL EJECUTIVA'), ('DGE-SECRETARIA GENERAL', 'DGE-SECRETARIA GENERAL'), ('DGE-VENTANILLA UNICA', 'DGE-VENTANILLA UNICA'), ('DGE-COMUNICACION', 'DGE-COMUNICACION'), ('DGE-FINANCIAMIENTO', 'DGE-FINANCIAMIENTO'), ('ASESORIA LEGAL', 'ASESORIA LEGAL'), ('AUDITORIA INTERNA', 'AUDITORIA INTERNA'), ('GESTION INSTITUDIONAL Y DESARROLLO ORGANIZACIONAL', 'GESTION INSTITUDIONAL Y DESARROLLO ORGANIZACIONAL'), ('COORDINACION ADMINISTRATIVA FINANCIERA', 'COORDINACION ADMINISTRATIVA FINANCIERA'), ('ADMINISTRACION', 'ADMINISTRACION'), ('ADMINISTRACION-RECURSOS HUMANOS', 'ADMINISTRACION-RECURSOS HUMANOS'), ('ADMINISTRACION-ACTIVOS FIJOS', 'ADMINISTRACION-ACTIVOS FIJOS'), ('ADMINISTRACION-CONTRATACIONES', 'ADMINISTRACION-CONTRATACIONES'), ('ADMINISTRACION-ALMACENES', 'ADMINISTRACION-ALMACENES'), ('FINANZAS', 'FINANZAS'), ('COORDINACION DE PLANIFICACION Y EVALUACION DE PROYECTOS', 'COORDINACION DE PLANIFICACION Y EVALUACION DE PROYECTOS'), ('PLANIFICACION Y EVALUACION DE PROYECTOS', 'PLANIFICACION Y EVALUACION DE PROYECTOS'), ('CONTROL, SEGUIMIENTO Y MONITORIO DE PROYECTOS', 'CONTROL, SEGUIMIENTO Y MONITORIO DE PROYECTOS'), ('TRANSPARENCIA Y LUCHA CONTRA LA CORRUPCION', 'TRANSPARENCIA Y LUCHA CONTRA LA CORRUPCION'), ('TECNOLOGIAS DE INFORMACION Y COMUNICACION', 'TECNOLOGIAS DE INFORMACION Y COMUNICACION'), ('DATA CENTER', 'DATA CENTER'), ('ENTRADA', 'ENTRADA'), ('PASILLO', 'PASILLO'), ('ALMACEN', 'ALMACEN'), ('EXTERNO', 'EXTERNO')])),
                ('observacion', models.TextField()),
                ('responsable', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.personal', to_field='slug')),
            ],
            options={
                'verbose_name': 'Activo_line',
                'verbose_name_plural': 'Activos_line',
                'db_table': 'Activo_line',
            },
        ),
    ]
