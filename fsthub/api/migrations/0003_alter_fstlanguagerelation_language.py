# Generated by Django 5.2.1 on 2025-06-21 13:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_fstlanguage_fstlanguagerelation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fstlanguagerelation',
            name='language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.fstlanguage'),
        ),
    ]
