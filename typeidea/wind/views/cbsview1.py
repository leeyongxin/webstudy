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
from django.http import StreamingHttpResponse
from django.http import JsonResponse
from django.views.generic import DetailView, ListView, TemplateView

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

from ..utility import yaw_align
from ..models import Database, DbTable
from ..funlib import Mongo
from ..forms import QueryTimeForm

# logger setting
lg = logging.getLogger('view')
ch = logging.StreamHandler()
formatter_f = logging.Formatter('[%(asctime)s][%(process)d:%(thread)d][%(levelname)s] %(message)s')
ch.setFormatter(formatter_f)
lg.setLevel(logging.INFO)
lg.addHandler(ch)

# Create your views here.



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

class BaseMixin():
    '''
    base mixin, return None to mark as top
    '''
    def get(self, *args,  **kwargs):
        return None

class DrawMixin(BaseMixin):
    def get(self, *args,  **kwargs):
        lg.info("now is in DrawMixin.{}".format(sys._getframe().f_code.co_name))
        if self.request.GET.get('draw_btn_clicked'):
            context = self.get_context_data(*args, **kwargs)
            #self.request.session['pic'] = self.get_image(self.request)['inline_png']
            self.request.session['pic'] = yaw_align(lg)
            context.update({
                  'inline_png':self.request.session['pic']
                           })
            lg.info("Exit DrawMixin.{} with pic updated".format(sys._getframe().f_code.co_name))
            return render(self.request, 'wind/pic.html', context)
        else:
            lg.info("now is exit DrawMixin.{} without pic updated".format(sys._getframe().f_code.co_name))
            ret = super().get(*args,  **kwargs)
            lg.info("DrawMixin return is {}".format(ret))
            return ret



class DownloadMixin(BaseMixin):

    def get(self, *args,  **kwargs):
        lg.info("now is in DownloadMixin.{}".format(sys._getframe().f_code.co_name))
        if self.request.GET.get('download_btn_clicked'):
            lg.debug("click download button")
            lg.info("now is exit DownloadMixin.{} with download".format(sys._getframe().f_code.co_name))
            return self.big_file_download()

        lg.info("now is exit DownloadMixin.{} without download".format(sys._getframe().f_code.co_name))
        ret = super().get(*args,  **kwargs)
        lg.info("DownloadMixin return is {}".format(ret))
        return ret


class SetTimeMixin(BaseMixin):
    def get(self, *args,  **kwargs):
        lg.info("now is in SetTimeMixin.{}".format(sys._getframe().f_code.co_name))
        if self.request.GET.get('time_btn_clicked'):
            lg.debug("click set time button")
            start, stop = self.get_time()
            self.request.session['timeset']= True
            self.request.session['tstart']= start
            self.request.session['tstop']= stop
            lg.debug("get_queryset.time_btn_clicked\nstart_time:{0} stop_time:{1}".
                format(start, stop)
                )
            #read data after time changed
            self.df = self.get_data()

            # keep in image view page
            if isinstance(self, ImageView):
                self.get_queryset(*args,  **kwargs)
                context = self.get_context_data(*args,  **kwargs)
                # use previous drawed pic
                context.update({
                    'inline_png':self.request.session['pic']
                })
                lg.info("now is exit SetTimeMixin.{} with new time and Image page".format(sys._getframe().f_code.co_name))
                return render(self.request, 'wind/pic.html', context)

            lg.info("now is exit SetTimeMixin.{} with new time".format(sys._getframe().f_code.co_name))
            ret = super().get(*args,  **kwargs)
            lg.info("SetTimeMixin return is {}".format(ret))
            return ret

        lg.info("now is exit SetTimeMixin.{} with old time".format(sys._getframe().f_code.co_name))
        ret = super().get(*args,  **kwargs)
        lg.info("SetTimeMixin return is {}".format(ret))
        return ret


class TableDetailView(SetTimeMixin, DownloadMixin, ListView):
    template_name = 'wind/home.html'
    queryset = ''


    def __init__(self, *args,  **kwargs):
        lg.info("now is in TableDetailView.{}".format(sys._getframe().f_code.co_name))
        self.df ={}
        self.conn = Mongo().connect_mongo()
        lg.info("now is exit TableDetailView.{}".format(sys._getframe().f_code.co_name))

    def get(self, *args,  **kwargs):
        lg.info("now is in TableDetailView.{}".format(sys._getframe().f_code.co_name))

        # check if any mixin triggered
        sget = super().get(self, *args,  **kwargs)
        if sget:
            lg.info("now use TableDetailView.{} super's get content".format(sys._getframe().f_code.co_name))
            # use mixin's get response
            return sget
        else:
            lg.info("now use TableDetailView.{} 's get content".format(sys._getframe().f_code.co_name))
            self.get_queryset(*args,  **kwargs)
            context = self.get_context_data(*args,  **kwargs)
            lg.info("now exit in TableDetailView.{}".format(sys._getframe().f_code.co_name))
            return render(self.request, 'wind/home.html', context)

    def post(self, *args,  **kwargs):
        lg.debug("now is in TableDetailView.{}".format(sys._getframe().f_code.co_name))
        fields = self.request.POST.getlist('check')
        lg.debug("checked items {}".format(fields))
        lg.debug("checked items {}".format(self.request))

        return render(self.request, 'wind/home.html')


    def get_queryset(self, *args,  **kwargs):
        lg.info("now is in TableDetailView.{}".format(sys._getframe().f_code.co_name))

        if self.request.session.get('table') != None:
            if self.request.session['table'] == self.kwargs['table']:
                pass
            else:
                self.init_session()
        else:
            self.init_session()

#
        if self.request.GET.get('check_btn_clicked'):
            fields = self.request.GET.getlist('check')
            lg.debug("checked items {}".format(fields))
            self.request.session['fields']= fields
            hlist = self.request.session['headlist']
            showlist = [(x, y) for x, y in hlist if str(x) in self.request.session['fields']]
            self.request.session['headlist']= showlist

        lg.info("now is exit TableDetailView.{}".format(sys._getframe().f_code.co_name))

    def read_avail(self,database, collection,columns):


         cursor1 = self.conn[database][collection].find({},{'_id':1,columns:1}).sort([(columns,1)]).limit(1)
         cursor2 = self.conn[database][collection].find({},{'_id':1,columns:1}).sort([(columns,-1)]).limit(1)
         df1 = pd.DataFrame(list(cursor1))
         df2 = pd.DataFrame(list(cursor2))
         if isinstance(df1[columns][0],pd._libs.tslibs.timestamps.Timestamp):
             start_data = df1[columns][0]
         if isinstance(df1[columns][0],pd._libs.tslibs.timestamps.Timestamp):
             end_data =df2[columns][0]
         else:
             start_data =pd.datetime.now()
             end_data= pd.datetime.now()
         return start_data,end_data



    def big_file_download(request):
        # do something...

        def file_iterator(file_name, chunk_size=512):
            with open('./export.csv') as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        the_file_name = "export.csv"
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)

        return response



    def get_session(self):
        return list(self.request.session.items())


    def init_session(self):
        lg.debug("now is in TableDetailView.{}".format(sys._getframe().f_code.co_name))
        lg.info("switch table, flush old session")
        lg.debug(self.get_session())

        self.request.session.flush()
        self.request.session['table'] = self.kwargs['table']
        headlist = DbTable.objects.get(col_name=self.kwargs['table']).get_col_head()
        self.request.session['headlist'] = list(enumerate(headlist))

    def get_time(self):
        lg.debug("now is in TableDetailView.{}".format(sys._getframe().f_code.co_name))
        tstart = self.request.GET.get('start_time').replace("T"," ")
        tstop = self.request.GET.get('end_time').replace("T"," ")
        return tstart, tstop

    def get_data(self):
        lg.debug("now is in TableDetailView.{}".format(sys._getframe().f_code.co_name))
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
        selected = dict(self.request.session['headlist'])
        selected = dict(zip(selected.values(), selected.keys()))
        selected = selected.fromkeys((k for k in selected.keys()), 1)
        projection = {'TimeStamp':1, '_id':0}
        projection.update(selected)
        lg.debug("selected columns{}".format(projection))
        qfilter = {'TimeStamp':{'$gt':start,'$lt':stop}}

        lg.debug("filter = {}".format(qfilter))
        lg.debug("projection = {}".format(projection))

        df = pd.DataFrame(list(self.conn[self.kwargs['db']][self.kwargs['table']].find(qfilter, projection)))
        lg.debug("db = {0}\n table = {1}".format([self.kwargs['db']], [self.kwargs['table']]))
        lg.debug("here is findings:\n {}".format(df))

        self.request.session['timeset']= None

        # remove this line after namemap developed
        namemap = None

        if isinstance(namemap, dict):
            self.column_rename(df,namemap)
        df.to_pickle("./dummy.pkl")
        df.to_csv("./export.csv")
        # put first 200 row into html
        df = df.iloc[:200,:]
        return  df.to_html()

    def column_rename(self,df, namemap):
        '''
        replace column name with given map, if exist
        '''
        df.rename(column=namemap, inplace=True)


    def get_context_data(self, *args, **kwargs):
        lg.info("now is in TableDetailView.{}".format(sys._getframe().f_code.co_name))
        #context = super().get_context_data(*args, **kwargs)
        context = {}
        lg.debug("session now is {}".format(self.get_session()))

        # read db first and last piece time
        try:
            self.time = self.read_avail(self.kwargs['db'],self.kwargs['table'], "TimeStamp")
        except:
            self.time = None
            lg.exception("read time fail:")

        context.update({
            'collections':DbTable.objects.filter(db=self.kwargs['db']),
            'headlist': self.request.session['headlist'],
            'model_db': self.kwargs['db'],
            'model_table': self.kwargs['table'],
            'dbs': Database.objects.all(),
            # time picker
            'form':QueryTimeForm(),
            'df' : self.df,
            'table_time': self.time

            })

        #lg.debug("context is  {0}".format(self.context))
        lg.info("now is exit TableDetailView.{}".format(sys._getframe().f_code.co_name))
        return context

class SelectedView(TableDetailView):
    template_name = 'wind/home.html'

        #return render(self.request, 'wind/home.html', self.context)


class ImageView(DrawMixin, TableDetailView):
    template_name = 'wind/pic.html'


#
    def get_image(self, request):
        lg.info("now is in {}".format(sys._getframe().f_code.co_name))
        from pandas.plotting import register_matplotlib_converters
        register_matplotlib_converters()

        #set style
        plt.style.use(['ggplot', "./mystyle"])
        # Construct the graph
        fig, ax = plt.subplots(nrows=3, ncols=1,figsize=(12,18))

        df = pd.read_pickle("./dummy.pkl")
        try:
            ax[0].plot(df['TimeStamp'],df['WindSpeed'])
            #ax[0].plot(df['TimeStamp'],df['PitchPositionBlade1'])
            ax[0].xaxis.set_major_formatter(DateFormatter('%m-%d %H:%M'))
            fig.autofmt_xdate()
        except:
            pass
        try:
            sctr = ax[1].scatter(x=df['WindSpeed'], y=df['Power'],c=df['Power'], cmap='winter_r')
        except:
            lg.exception("exceptions")
        fig.tight_layout()
        canvas=FigureCanvasAgg(fig)
        buf = io.BytesIO()

        canvas.print_png(buf)
        plt.close(fig)
        ret = {}
        #ret['inline_png']= base64.b64encode(buf.getvalue()) for python3, need to add decode
        ret['inline_png']= base64.b64encode(buf.getvalue()).decode()
        response=HttpResponse(buf.getvalue(),content_type='image/png')
        lg.info("now is exit {}".format(sys._getframe().f_code.co_name))
        return ret

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

class JS(TemplateView):
    template_name = 'wind/js.html'
    def get_data(self, request):
        item = {"a":1, "b":2}
        return JsonResponse(item)
