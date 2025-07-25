# Generated by Django 5.2.4 on 2025-07-21 10:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activos', '0006_alter_activos_line_responsable'),
        ('users', '0003_alter_personal_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activos_line',
            name='responsable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.personal', to_field='slug'),
        ),
    ]
