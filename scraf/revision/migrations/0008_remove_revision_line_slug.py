# Generated by Django 5.2.4 on 2025-07-29 14:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('revision', '0007_revision_activo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='revision_line',
            name='slug',
        ),
    ]
