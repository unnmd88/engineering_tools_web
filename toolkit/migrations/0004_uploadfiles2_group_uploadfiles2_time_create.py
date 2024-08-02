# Generated by Django 4.2.1 on 2024-08-02 18:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('toolkit', '0003_alter_uploadfiles2_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadfiles2',
            name='group',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='uploadfiles2',
            name='time_create',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]