# Generated by Django 5.1.3 on 2024-11-18 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_alter_equipement_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='equipement_emprunté',
            field=models.CharField(default='Aucun', max_length=100),
        ),
    ]
