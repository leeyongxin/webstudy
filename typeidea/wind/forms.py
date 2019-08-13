'''
@Author: Yongxin
@Date: 2019-08-13 01:59:08
@LastEditors: Yongxin
@LastEditTime: 2019-08-13 08:33:57
@Description: 
'''
from django import forms
from django.forms import ModelForm

from .models import QueryTime, DbTable, Database


class DateInput(forms.DateTimeInput):
    # here is the tag used in html <input type="datetime-local", if only require date, use 'date' instead
    input_type = 'datetime-local'


class QueryTimeForm(ModelForm):

    class Meta:
        model = QueryTime
        fields = ['start_time', 'end_time']
        widgets = {
            'start_time': DateInput(),
            'end_time': DateInput(),
        }


class SelectTalbeForm(forms.Form):
    databases = Database.objects.all()
    choises = ((db, db) for db in databases)



class MapHeaderForm(forms.Form):
    headlist = DbTable.objects.get(col_name="t026_scada_30_raw").get_col_head()
    turbine_choices = (
        ("DIEF1", "DIEF1"),
        ("DongFang","东汽"),
        ("KeNuoWeiYe","科诺伟业",),
        ("MY", "明阳")

    )
    turbine_type = forms.ChoiceField(choices=turbine_choices)
    windspeed = forms.ChoiceField(choices=((hl, hl) for hl in headlist))
    power = forms.ChoiceField(choices=((hl, hl) for hl in headlist))
    temperature = forms.ChoiceField(choices=((hl, hl) for hl in headlist))
    blade_set = forms.ChoiceField(choices=((hl, hl) for hl in headlist))
    blade_act = forms.ChoiceField(choices=((hl, hl) for hl in headlist))
    torque_set = forms.ChoiceField(choices=((hl, hl) for hl in headlist))
    torque_act = forms.ChoiceField(choices=((hl, hl) for hl in headlist))