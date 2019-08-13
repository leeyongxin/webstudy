from django.db import models
import json

# Create your models here.
class Database(models.Model):
    db_name = models.CharField(max_length=51, verbose_name='Name', unique=True)
    db_type = models.CharField(max_length=51, verbose_name='Type')


class DbTable(models.Model):
    # collection name
    col_name = models.CharField(max_length=51, verbose_name='Name', primary_key=True)
    db = models.ForeignKey(Database, to_field='db_name', related_name='collections', on_delete=models.CASCADE)
    # table first line
    col_headlist = models.CharField(max_length=5000, verbose_name='col_head', default='')

    def set_col_head(self, x):
        self.col_headlist = json.dumps(x, ensure_ascii=False)

    def get_col_head(self):
        return json.loads(self.col_headlist)



class QueryTime(models.Model):
    '''
    query timeset for db lookup
    '''
    start_time = models.DateField()
    end_time = models.DateField()


class MapColumn(models.Model):
    '''
    map coloumn head in raw table and in plot function's command
    '''
    pass


