#coding:utf-8
#!/usr/bin/env python
""""
********************************************
Program:
Description:
Author: Yongxin
Date: 2019-05-22 00:37:56
Last modified: 2019-05-22 00:37:56
********************************************
"""
from django.shortcuts import render, redirect, render_to_response, reverse
from django.shortcuts import HttpResponse
from django.views.generic import DetailView, ListView, TemplateView
from .models import Database, DbTable
from .funlib import Mongo
from .forms import QueryTimeForm
import json

# Create your views here.
class TestHtml(TemplateView):
    template_name = 'wind/example.html'
def test(request):
    return render_to_response('wind/example.html')



class DbListView(ListView):
    '''
    show dbs in a server
    '''
    context_object_name = 'dbs'
    template_name = 'wind/home.html'
    def get_queryset(self):
        '''
        utilize get_queryset (default action when GET triggered ), to trigger a update function
        '''
        self.update_db()
        return Database.objects.all()

    def update_db(self):
        mon = Mongo()
        # add talbe if notexist
        db_list = mon.connect_mongo().list_database_names()
        for dbname in db_list :
            try:
                Database.objects.get(db_name=dbname)
            except Database.DoesNotExist:
                Database.objects.create(db_name=dbname, db_type="Mongodb")
        # remove db if not exist
        for db in Database.objects.all():
            if db.db_name not in db_list:
                db.delete()

    def post(self, request):
        dbname = request.POST['db_name']
        mdb = Database.objects.get(db_name=dbname)
        print(dbname)
        mon = Mongo()
        for colname in mon.connect_mongo()[dbname].list_collection_names():
            try:
                DbTable.objects.get(col_name=colname)
            except DbTable.DoesNotExist:
                DbTable.objects.create(col_name=colname, db=mdb)
        return redirect('read_table')

class TableListView(DbListView, ListView):
    context_object_name = 'collections'
    template_name = 'wind/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            #'collections':DbTable.objects.filter(db=self.kwargs['slug']),
            'dbs':Database.objects.all()

            })
        return context

    def get_queryset(self):
        print(self.kwargs)
        super().get_queryset()

        self.update_table()
        return DbTable.objects.filter(db_id=self.kwargs['slug'])

    def update_table(self):
        mon = Mongo()
        mdb = Database.objects.get(db_name=self.kwargs['slug'])
        # add talbe if notexist
        table_list = mon.connect_mongo()[self.kwargs['slug']].list_collection_names()
        for colname in table_list :
            try:
                DbTable.objects.get(col_name=colname)
            except DbTable.DoesNotExist:
                headlist = list(mon.connect_mongo()[self.kwargs['slug']][colname].find_one({},{'_id':0}).keys())
                newtable = DbTable(col_name=colname, db=mdb)
                newtable.set_col_head(headlist)
                newtable.save()
        # remove talbe if not exist
        for col in DbTable.objects.filter(db_id=mdb.db_name):
            if col.col_name not in table_list:
                col.delete()


class TableDetailView(ListView):
    template_name = 'wind/home.html'
    queryset = ''


    def get_queryset(self, *args,  **kwargs):
        print("now in get")
        qs = super().get_queryset()
        qstart = self.request.GET.get("start_time")
        qstop = self.request.GET.get("end_time")
        qselected = self.request.GET.getlist("check")
        print(qstart)
        print(qstop)
        print(qselected)
        print(self.request.GET)
        return qs


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        headlist = DbTable.objects.get(col_name=self.kwargs['table']).get_col_head()
        hlist = list(enumerate(headlist))
        context.update({
            'collections':DbTable.objects.filter(db=self.kwargs['db']),
            'headlist': hlist,
            'model_db': self.kwargs['db'],
            #'model_table': self.kwargs['table'],
            'dbs': Database.objects.all(),
            'form':QueryTimeForm()

            })
        return context

    def post(self, request, db, table):
        print("now in post")
        #print(request.POST)

        return render(request, 'wind/base.html', {'db':db, 'table':table})


from django.http import HttpResponse
from django.shortcuts import render
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
import random
import datetime
import io
import base64

def getimage(request,db=None, table=None):
    # Construct the graph
    fig, ax = plt.subplots()
    x=[]
    y=[]
    now=datetime.datetime.now()
    delta=datetime.timedelta(days=1)
    for i in range(10):
        x.append(now)
        now+=delta
        y.append(random.randint(0, 1000))
    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas=FigureCanvasAgg(fig)
    buf = io.BytesIO()
    #plt.savefig(buf, format='png')
    canvas.print_png(buf)
    #plt.close(fig)
    ret = {}
    #ret['inline_png']= base64.b64encode(buf.getvalue())
    ret['inline_png']= base64.b64encode(buf.getvalue()).decode()
    response=HttpResponse(buf.getvalue(),content_type='image/png')
    return render(request, 'wind/detail.html', ret)
    #return response
