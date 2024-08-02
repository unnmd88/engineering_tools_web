from django.db import models

# Create your models here.


class TrafficLightObjects(models.Model):
    num_CO = models.CharField(max_length=10)
    type_controller = models.CharField(max_length=10)
    ip_adress = models.CharField(max_length=12)
    adress = models.TextField(blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    connection = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.num_CO} + {self.type_controller}'

    class Meta:
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]


class UploadFiles2(models.Model):
    file = models.FileField(upload_to='tmp2/', null=True, verbose_name='config_file')
    time_create = models.DateTimeField(auto_now_add=True)
    group = models.IntegerField()

