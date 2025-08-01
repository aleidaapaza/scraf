# Generated by Django 5.2.4 on 2025-07-28 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('revision', '0004_remove_revision_doc_respaldo1'),
        ('users', '0004_alter_personal_persona_alter_personal_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='revision',
            name='estado',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='revision',
            name='revisores',
            field=models.ManyToManyField(blank=True, related_name='revisiones_apoyadas', to='users.personal'),
        ),
    ]
