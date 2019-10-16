'''
@Author: Yongxin
@Date: 2019-08-13 01:59:08
@LastEditors: Yongxin
@LastEditTime: 2019-08-14 05:55:25
@Description: 
'''
from django import forms
from django.forms import ModelForm

from .models import QueryTime, DbTable, Database, Turbine


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
    pass



class MapHeaderForm(forms.Form):

    turbine_choices = (
        ("DIEF1", "DIEF1"),
        ("DongFang","东汽"),
        ("KeNuoWeiYe","科诺伟业",),
        ("MY", "明阳")

    )
    turbine_type = forms.ChoiceField(choices=turbine_choices)

    # headlist = DbTable.objects.get(turbine_type=turbine_type),"t008_scada_600_raw").get_col_head()
    headlist = range(1,6)

    windspeed = forms.ChoiceField(choices=((hl, hl) for hl in headlist))
    power = forms.ChoiceField(choices=((hl, hl) for hl in headlist))
    temperature = forms.ChoiceField(choices=((hl, hl) for hl in headlist))
    blade_set = forms.ChoiceField(choices=((hl, hl) for hl in headlist))
    blade_act = forms.ChoiceField(choices=((hl, hl) for hl in headlist))
    torque_set = forms.ChoiceField(choices=((hl, hl) for hl in headlist))
    torque_act = forms.ChoiceField(choices=((hl, hl) for hl in headlist))
    timestamp = forms.ChoiceField(choices=((hl, hl) for hl in headlist))