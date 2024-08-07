# Generated by Django 4.2.1 on 2024-08-04 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toolkit', '0007_rename_uploadfiles2_saveconfigfiles'),
    ]

    operations = [
        migrations.RenameField(
            model_name='saveconfigfiles',
            old_name='status_file',
            new_name='destination',
        ),
        migrations.RemoveField(
            model_name='saveconfigfiles',
            name='group',
        ),
        migrations.AddField(
            model_name='saveconfigfiles',
            name='controller_type',
            field=models.CharField(db_index=True, default='undefind', max_length=20),
        ),
    ]