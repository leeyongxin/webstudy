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
import logging
import datetime

# logger setting
lg = logging.getLogger('view')
ch = logging.StreamHandler()
formatter_f = logging.Formatter('[%(asctime)s][%(process)d:%(thread)d][%(levelname)s] %(message)s')
ch.setFormatter(formatter_f)
lg.setLevel(logging.DEBUG)
lg.addHandler(ch)

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

class TitleSearchMixin():

    def get_queryset(self,q=None):
        # fetch queryset from the parent's get_queryset
        lg.debug("now in {0}".format("TitleSearchMixin.get_queryset"))
        queryset = super().get_queryset()
        lg.debug("TitleSearchMixin.queryset =\n {0}".format(queryset))

        # get the q GET parameter
        v = self.request.GET.get(q)
        if v:
            #return a filtered queryset
            #return queryset.filter(title__iconstains=v)
            return v

        # no q is specified then we return queryset
        return queryset

class TableDetailView(ListView):
    template_name = 'wind/home.html'
    queryset = DbTable.objects.all()



    def get_queryset(self, *args,  **kwargs):
        lg.debug("now in {0}".format("TableDetailView.get_queryset"))
        if self.request.GET.get('time_btn_clicked'):
            tstart = self.request.GET.get('start_time').replace("T"," ")
            lg.debug("start time = {}".format(tstart))
            tstart = datetime.datetime.strptime(tstart, "%Y-%m-%d %H:%M")
            lg.debug("start time = {}".format(tstart))

            tstop = self.request.GET.get('end_time').replace("T"," ")
            tstop = datetime.datetime.strptime(tstop, "%Y-%m-%d %H:%M")
            lg.debug("TableListView.get_queryset.time_btn_clicked\nstart_time:{0} stop_time:{1}".
                    format(tstart, tstop)

                    )
            self.get_data(tstart, tstop)


    def get_data(self, start, stop):
        mon = Mongo()
        # add talbe if notexist
        #query1 = "find({'time':{'$gt':{0},'$lt':{1}}, \
        #                'Power':{'$lt':1700},                           \
        #                'SubState':{'$eq':30}},                         \
        #               {'_id':0,'time':1,'WindSpeed':1,'Power':1, 'PitchDemand':1})".format()
        query = {'TimeStamp':{'$gt':start,'$lt':stop}}
        lg.debug("query = {}".format(query))

        headlist = pd.DataFrame(list(mon.connect_mongo()[self.kwargs['db']][self.kwargs['table']].find(query).limit(2)))
        lg.debug("db = {0}\n table = {1}".format([self.kwargs['db']], [self.kwargs['table']]))
        lg.debug("here is findings:\n {}".format(headlist))


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        headlist = DbTable.objects.get(col_name=self.kwargs['table']).get_col_head()
        hlist = list(enumerate(headlist))
        context.update({
            'collections':DbTable.objects.filter(db=self.kwargs['db']),
            'headlist': hlist,
            'model_db': self.kwargs['db'],
            'model_table': self.kwargs['table'],
            'dbs': Database.objects.all(),
            'form':QueryTimeForm()

            })
        return context

    def post(self, request, db, table):
        lg.debug("now in {0}".format("TableDetailView.post"))

        return render(request, 'wind/base.html', {'db':db, 'table':table})



from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
import random
import io
import base64
import pandas as pd

class ImageView(TableDetailView):
    template_name = 'wind/pic.html'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.btn_sw = {}


    def get_context_data(self, *args, **kwargs):
        #lg.debug(self.kwargs)
        context = super().get_context_data(**kwargs)
        if self.btn_sw.get('draw',None):
            pic = self.getimage(self.request)['inline_png']
            context.update({
                'inline_png':pic
                })
        lg.debug("get message:\n{}".format(self.request.GET))
        return context

#    def get(self, *args, **kwargs):
#        lg.debug("get message:\n{}".format(self.request.GET))
#        qstart = self.request.GET.get("start_time")
#        qstop = self.request.GET.get("end_time")
#        lg.debug("now in ImageView.get:\n{}{}".format(qstart, qstop))
#        return render(self.request, 'wind/base.html')

    def get_queryset(self):
        lg.debug("now in {0}".format("ImageView.get_queryset"))
        lg("reuqestis:\n{}".format(self.request))
        if self.request.GET.get('draw_btn_clicked'):
            lg.debug("ImageView.get_queryset.draw_btn_clicked")
            self.btn_sw.update({
                'draw':True
                })
        if self.request.GET.get('time_btn_clicked'):
            tstart = self.request.GET.get('start_time')
            tstop = self.request.GET.get('end_time')
            lg.debug("ImageView.get_queryset.time_btn_clicked\nstart_time:{0} stop_time:{1}".
                    format(tstart, tstop)

                    )

            #self.get_data(tstart, tstop)

#

    def get_data(self, start, stop):
        mon = Mongo()
        # add talbe if notexist
        #query1 = "find({'time':{'$gt':{0},'$lt':{1}}, \
        #                'Power':{'$lt':1700},                           \
        #                'SubState':{'$eq':30}},                         \
        #               {'_id':0,'time':1,'WindSpeed':1,'Power':1, 'PitchDemand':1})".format()
        query = "find({'time':{'$gt':{0},'$lt':{1}})".format(start, stop)

        headlist = pd.DataFrame(list(mon.connect_mongo()[self.kwargs['db']][self.kwargs['table']].find(eval(query)).limit(2)))
        lg.debug("here is findings:\n {}".format(headlist))


    def getimage(self, request):
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
        #ret['inline_png']= base64.b64encode(buf.getvalue()) for python3, need to add decode
        ret['inline_png']= base64.b64encode(buf.getvalue()).decode()
        response=HttpResponse(buf.getvalue(),content_type='image/png')
        return ret
        #return render(request, 'wind/pic.html', ret)

def getimage(request):
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
    #return ret
    return render(request, 'wind/pic.html', ret)
