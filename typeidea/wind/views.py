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

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
import random
import io
import base64
import pandas as pd
import sys

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


class TableDetailView(ListView):
    template_name = 'wind/home.html'
    queryset = ''

    def __init__(self, *args,  **kwargs):
        self.df ={}
        self.name = self.__class__.__name__
        lg.debug("now in {0}".format("TableDetailView.__init__"))
        super().__init__(*args, **kwargs)

#    def get(self, *args,  **kwargs):
#        #super().get(self, *args,  **kwargs)
#        lg.debug("now in {0}".format("TableDetailView.get\n{}".format(self.request)))
#
#        return render(self.request, 'wind/home.html', self.context)
#
    def post(self, *args,  **kwargs):
       lg.debug("now in {0}".format("TableDetailView.post{}".format(self.request)))
       fields = self.request.POST.getlist('check')
       lg.debug("checked items {}".format(fields))
       lg.debug("checked items {}".format(self.request))

       return render(self.request, 'wind/home.html')


    def get_queryset(self, *args,  **kwargs):
        lg.debug("now in {0}".format("TableDetailView.get_queryset"))

        if self.request.session.get('table') != None:
            if self.request.session['table'] == self.kwargs['table']:
                pass
            else:
                self.init_session()
        else:
            self.init_session()


        if self.request.GET.get('time_btn_clicked'):
            start, stop = self.get_time()
            self.request.session['timeset']= True
            self.request.session['tstart']= start
            self.request.session['tstop']= stop
            lg.debug("get_queryset.time_btn_clicked\nstart_time:{0} stop_time:{1}".
                format(start, stop)
                )

        if self.request.GET.get('check_btn_clicked'):
            fields = self.request.GET.getlist('check')
            lg.debug("checked items {}".format(fields))
            self.request.session['fields']= fields
            hlist = self.request.session['headlist']
            showlist = [(x, y) for x, y in hlist if str(x) in self.request.session['fields']]
            self.request.session['headlist']= showlist

    def get_session(self):
        return list(self.request.session.items())


    def init_session(self):
            lg.info("switch table, flush old session")
            lg.debug(self.get_session())

            self.request.session.flush()
            self.request.session['table'] = self.kwargs['table']
            headlist = DbTable.objects.get(col_name=self.kwargs['table']).get_col_head()
            self.request.session['headlist'] = list(enumerate(headlist))

    def get_time(self):
        tstart = self.request.GET.get('start_time').replace("T"," ")
        tstop = self.request.GET.get('end_time').replace("T"," ")
        return tstart, tstop

    def get_data(self):
        start = self.request.session.get('tstart', None)
        stop = self.request.session.get('tstop', None)
        newtime = self.request.session.get('timeset', None)
        if not (start and stop and newtime):
            lg.warning("time not set correct \nstart\t{0}\nstop\t{1}\ntimebutton={2}"
                    .format(start, stop, newtime))


            return -1

        lg.debug("start time:{}".format(start))
        lg.debug("stop time:{}".format(stop))

        start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M")
        stop = datetime.datetime.strptime(stop, "%Y-%m-%d %H:%M")
        mon = Mongo()
        # add talbe if notexist
        #query1 = "find({'time':{'$gt':{0},'$lt':{1}}, \
        #                'Power':{'$lt':1700},                           \
        #                'SubState':{'$eq':30}},                         \
        #               {'_id':0,'time':1,'WindSpeed':1,'Power':1, 'PitchDemand':1})".format()
        selected = dict(self.request.session['headlist'])
        selected = dict(zip(selected.values(), selected.keys()))
        selected = selected.fromkeys((k for k in selected.keys()), 1)
        projection = {'TimeStamp':1, '_id':0}
        projection.update(selected)
        lg.debug("selected columns{}".format(projection))
        qfilter = {'TimeStamp':{'$gt':start,'$lt':stop}}

        lg.debug("filter = {}".format(qfilter))
        lg.debug("projection = {}".format(projection))

        df = pd.DataFrame(list(mon.connect_mongo()[self.kwargs['db']][self.kwargs['table']].find(qfilter, projection)))
        lg.debug("db = {0}\n table = {1}".format([self.kwargs['db']], [self.kwargs['table']]))
        lg.debug("here is findings:\n {}".format(df))

        self.request.session['timeset']= None
        df.to_pickle("./dummy.pkl")
        return  df.to_html()



    def get_context_data(self, *args, **kwargs):
        lg.debug("now is in TableDetailView.{}".format(sys._getframe().f_code.co_name))
        self.context = {}
        lg.debug("session now is {}".format(self.get_session()))
        self.df = self.get_data()
        self.context.update({
            'collections':DbTable.objects.filter(db=self.kwargs['db']),
            'headlist': self.request.session['headlist'],
            'model_db': self.kwargs['db'],
            'model_table': self.kwargs['table'],
            'dbs': Database.objects.all(),
            # time picker
            'form':QueryTimeForm(),
            'df' : self.df

            })

        #lg.debug("context is  {0}".format(self.context))
        lg.debug("now exit {0}".format("TableDetailView.get_context_data"))
        return self.context

class SelectedView(TableDetailView):
    template_name = 'wind/home.html'



class ImageView(TableDetailView):
    template_name = 'wind/pic.html'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.btn_sw = {}

#    def get(self, *args,  **kwargs):
#        super().get(self, *args,  **kwargs)
#        lg.debug("now in {0}".format("ImageView.get{}".format(self.request)))
#
#        return render(self.request, 'wind/pic.html', self.context)
#

    def get_context_data(self, *args, **kwargs):
        lg.debug("now is in ImageView.{}".format(sys._getframe().f_code.co_name))
        self.context = super().get_context_data(*args, **kwargs)
        if self.btn_sw.get('draw',None):
            pic = self.get_image(self.request)['inline_png']
            self.context.update({
                'inline_png':pic
                })
        return self.context


    def get_queryset(self, *args, **kwargs):
        lg.debug("now is in ImageView.{}".format(sys._getframe().f_code.co_name))
        super().get_queryset(*args, **kwargs)
        if self.request.GET.get('draw_btn_clicked'):
            lg.debug("ImageView.get_queryset.draw_btn_clicked")
            self.btn_sw.update({
                'draw':True
                })




    def get_image(self, request):
        from pandas.plotting import register_matplotlib_converters
        register_matplotlib_converters()

        lg.debug("now is in ImageView.{}".format(sys._getframe().f_code.co_name))
        plt.style.use("./mystyle")
        # Construct the graph
        fig, ax = plt.subplots(nrows=3, ncols=1,figsize=(12,18))
        df = pd.read_pickle("./dummy.pkl")
        try:
            ax[0].plot(df['TimeStamp'],df['WindSpeed'])
            ax[0].plot(df['TimeStamp'],df['PitchPositionBlade1'])
            ax[0].xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
        except:
            pass
        try:
            sctr = ax[1].scatter(x=df['WindSpeed'], y=df['Power'],c=df['Power'], cmap='winter_r')
            #plt.colorbar(sctr, ax=ax[1], format='%d')
        except:
            lg.exception("exceptions")
        fig.autofmt_xdate()
        fig.tight_layout()
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

    def getimage1(self, request):
        lg.debug("now is in ImageView.{}".format(sys._getframe().f_code.co_name))
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

