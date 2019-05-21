#coding:utf-8
#!/usr/bin/env python
""""
********************************************
Program:
Description:
Author: Yongxin
Date: 2019-04-27 14:17:19
Last modified: 2019-04-27 14:17:19
********************************************
"""
from django import forms


class PostAdminForm(forms.ModelForm):
    desc = forms.CharField(widget=forms.Textarea, label='abstract', required=False)
