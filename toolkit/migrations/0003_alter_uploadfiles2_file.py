# Generated by Django 4.2.1 on 2024-08-02 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toolkit', '0002_uploadfiles2_alter_trafficlightobjects_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadfiles2',
            name='file',
            field=models.FileField(null=True, upload_to='tmp2/', verbose_name='config_file'),
        ),
    ]