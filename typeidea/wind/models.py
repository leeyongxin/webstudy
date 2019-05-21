from django.db import models

# Create your models here.
class MongoViewer(models.Model):
    name = models.CharField(max_length=50, verbose_name='Name')



