# Generated by Django 4.2.1 on 2024-07-14 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TrafficLightObjects',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_CO', models.CharField(max_length=10)),
                ('type_controller', models.CharField(max_length=10)),
                ('ip_adress', models.CharField(max_length=12)),
                ('adress', models.TextField(blank=True)),
                ('time_create', models.DateTimeField(auto_now_add=True)),
                ('time_update', models.DateTimeField(auto_now=True)),
                ('connection', models.BooleanField(default=False)),
            ],
        ),
    ]
