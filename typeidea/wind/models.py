from django.db import models


# Create your models here.
class Database(models.Model):
    db_name = models.CharField(max_length=51, verbose_name='Name', unique=True)
    db_type = models.CharField(max_length=51, verbose_name='Type')


class DbTable(models.Model):
    # collection name
    col_name = models.CharField(max_length=51, verbose_name='Name', primary_key=True)
    db = models.ForeignKey(Database, to_field='db_name', related_name='collections', on_delete=models.CASCADE)




