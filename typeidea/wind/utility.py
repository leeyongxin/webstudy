#coding:utf-8
#!/usr/bin/env python
""""
********************************************
Program:
Description:
Author: Yongxin
Date: 2019-06-12 09:21:07
Last modified: 2019-06-12 09:21:07
********************************************
"""
import io
import sys
import base64

import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg

import pandas as pd
from pandas.plotting import register_matplotlib_converters
import numpy as np

from django.shortcuts import HttpResponse

def get_data(request,lg):
    lg.debug("now is in TableDetailView.{}".format(sys._getframe().f_code.co_name))
    start = request.session.get('tstart', None)
    stop = request.session.get('tstop', None)
    newtime = request.session.get('timeset', None)
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

    request.session['timeset']= None
    df.to_pickle("./dummy.pkl")
    df.to_csv("./export.csv")
    # put first 200 row into html
    df = df.iloc[:200,:]
    return  df.to_html()

def yaw_align(lg):
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
        lg.exception("exceptions")

    try:
        sctr = ax[1].scatter(x=df['WindSpeed'], y=df['Power'],c=df['Power'], cmap='winter_r')
    except:
        lg.exception("exceptions")

    try:
        x =  df['风向'] - 180
        y = df['风向']
        z = df['有功功率']
        sctr = ax[2].scatter(x,z, cmap='winter_r')
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
    return ret['inline_png']
