# Generated by Django 5.0.2 on 2024-03-04 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_plotting_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plotting',
            name='plot',
            field=models.ImageField(blank=True, upload_to=''),
        ),
    ]
