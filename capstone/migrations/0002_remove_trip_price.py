# Generated by Django 3.0.8 on 2020-08-11 23:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capstone', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trip',
            name='price',
        ),
    ]
