'''
@Author: Yongxin
@Date: 2019-08-14 00:31:34
@LastEditors: Yongxin
@LastEditTime: 2019-08-15 01:22:45
@Description:
'''
from django.db import models
import json

import sys
sys.path.insert(0, '/mnt/ubuntu')
from usrlib.log_reader import Mongodb

# Create your models here.
class Database(models.Model):
    db_name = models.CharField(max_length=51, verbose_name='Name', unique=True)
    db_type = models.CharField(max_length=51, verbose_name='Type')

    def __str__(self):
        return self.db_name


class Turbine(models.Model):

    turbine = models.CharField(max_length=100, verbose_name='turbine', unique=True)
    timestamp = models.CharField(max_length=100, verbose_name='timestamp', blank=True)
    # timestamp = models.CharField(choices=self.get_headlist())
    turbine_state = models.CharField(max_length=100, verbose_name='turbine_state', blank=True)
    windspeed = models.CharField(max_length=100, verbose_name='wind_speed_1s', blank=True)
    winddir = models.CharField(max_length=100, verbose_name='wind_direction_1s', blank=True)
    ambient_temp = models.CharField(max_length=100, verbose_name='ambient_temp', blank=True)
    ambient_pressure = models.CharField(max_length=100, verbose_name='ambient_pressure', blank=True)
    air_dencity = models.CharField(max_length=100, verbose_name='air_dencity', blank=True)
    power = models.CharField(max_length=100, verbose_name='power', blank=True)
    torque = models.CharField(max_length=100, verbose_name='torque', blank=True)
    torque_set = models.CharField(max_length=100, verbose_name='torque_set', blank=True)
    genspeed = models.CharField(max_length=100, verbose_name='gen_speed', blank=True)
    genspeed_set = models.CharField(max_length=100, verbose_name='gen_speed_set', blank=True)
    rotorspeed = models.CharField(max_length=100, verbose_name='rotor_speed', blank=True)
    blade1_set = models.CharField(max_length=100, verbose_name='blade1_set', blank=True)
    blade1_act = models.CharField(max_length=100, verbose_name='blade1_act', blank=True)
    blade2_set = models.CharField(max_length=100, verbose_name='blade2_set', blank=True)
    blade2_act = models.CharField(max_length=100, verbose_name='blade2_act', blank=True)
    blade3_set = models.CharField(max_length=100, verbose_name='blade3_set', blank=True)
    blade3_act = models.CharField(max_length=100, verbose_name='blade3_act', blank=True)

    def get_headlist(self):
        hl = DbTable.objects.get(turbine_type=self.turbine).get_col_head()
        return  ((hl, hl) for hl in self.get_headlist())
    # mapdata = {
    #     "turbine":turbine, "turbine_state":turbine_state, "windspeed":windspeed,
    #     "winddir":winddir, "ambient_temp":ambient_temp, "ambient_pressure":ambient_pressure,
    #     "air_dencity":air_dencity, "power":power, "torque":torque, "torque_set":torque_set,
    #     "genspeed":genspeed, "genspeed_set":genspeed_set, "rotorspeed":rotorspeed,
    #     "blade1_set":blade1_set, "blade2_set":blade2_set, "blade3_set":blade3_set,
    #     "blade1_act":blade1_act, "blade2_act":blade2_act, "blade3_act":blade3_act
    # }



    def save(self, *args, **kwargs):
        mg = Mongodb("192.168.193.40", "MapDB")
        mapdata = {
        "turbine":self.turbine, "timestamp":self.timestamp, "turbine_state":self.turbine_state, "windspeed":self.windspeed,
        "winddir":self.winddir, "ambient_temp":self.ambient_temp, "ambient_pressure":self.ambient_pressure,
        "air_dencity":self.air_dencity, "power":self.power, "torque":self.torque, "torque_set":self.torque_set,
        "genspeed":self.genspeed, "genspeed_set":self.genspeed_set, "rotorspeed":self.rotorspeed,
        "blade1_set":self.blade1_set, "blade2_set":self.blade2_set, "blade3_set":self.blade3_set,
        "blade1_act":self.blade1_act, "blade2_act":self.blade2_act, "blade3_act":self.blade3_act
        }
        fdict = {"turbine":self.turbine}
        if mg.count_cursor('turbine_type', fdict) == 0:
            mg.load_db(mapdata, 'turbine_type')
        else:
            mg.replace_document('turbine_type', fdict, mapdata)
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        return self.turbine

class DbTable(models.Model):
    # collection name
    col_name = models.CharField(max_length=51, verbose_name='Name', primary_key=True)
    db = models.ForeignKey(Database, to_field='db_name', related_name='collections', on_delete=models.CASCADE)
    turbine_type = models.ForeignKey(Turbine, to_field='turbine', related_name='turbine_type', on_delete=models.CASCADE)
    # table first line
    col_headlist = models.CharField(max_length=5000, verbose_name='col_head', default='')

    def set_col_head(self, x):
        self.col_headlist = json.dumps(x, ensure_ascii=False)

    def get_col_head(self):
        return json.loads(self.col_headlist)

    def __str__(self):
        return self.col_name


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


