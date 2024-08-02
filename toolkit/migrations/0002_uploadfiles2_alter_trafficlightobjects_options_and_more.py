# Generated by Django 4.2.1 on 2024-08-02 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toolkit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadFiles2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='tmp2/')),
            ],
        ),
        migrations.AlterModelOptions(
            name='trafficlightobjects',
            options={'ordering': ['-time_create']},
        ),
        migrations.AddIndex(
            model_name='trafficlightobjects',
            index=models.Index(fields=['-time_create'], name='toolkit_tra_time_cr_95dbb4_idx'),
        ),
    ]