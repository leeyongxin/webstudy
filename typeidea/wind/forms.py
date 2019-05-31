from django import forms
from django.forms import ModelForm

from .models import QueryTime


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

