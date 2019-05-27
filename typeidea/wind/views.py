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
from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse
from django.views.generic import DetailView, ListView
from .models import Database, DbTable
from .funlib import Mongo

# Create your views here.
def showdb(request):
    read_db_name()
    db_names=get_dblist()
    content = '<br>'.join(db_names)

    return HttpResponse(content)


class DbListView(ListView):
    '''
    show dbs in a server
    '''
    model = Database
    context_object_name = 'dbs'
    template_name = 'wind_home.html'

    def post(self, request):
        print('here')

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

class TableListView(ListView):
    model = DbTable
    context_object_name = 'collections'
    template_name = 'wind_home.html'
    #def get_queryset(self, **kwargs):
    #    col_list = DbViewer.objects.all()
    #    dbs = MongoViewer.objects.all()
    #    mon = Mongo()
    #    for col in mon.connect_mongo()[self.kwargs['db_name']].list_collection_names():
    #        if col not in col_list:
    #            for db in dbs:
    #                if db.db_name == self.kwargs['db_name']:
    #                    collection = DbViewer(col_name=col, db=db)
    #                    collection.save()
    #    return DbViewer.objects.all()




def read_db_name(request):
    mon = Mongo()
    for dbname in mon.connect_mongo().list_database_names():
        try:
            Database.objects.get(db_name=dbname)
        except Database.DoesNotExist:
            Database.objects.create(db_name=dbname)
    dbs = Database.objects.all()
    return render(request, 'wind_home.html',{'dbs': dbs} )

def read_table_name(request):

    if request.method =='POST':
        dbname = request.POST['db_name']
        mon = Mongo()
        for colname in mon.connect_mongo()[dbname].list_collection_names():
            mdb = MongoViewer.objects.get(db_name=dbname)
            db_table = DbViewer(col_name=colname, db=mdb)
            db_table.save()
        collections = DbViewer.objects.all()
        return redirect('read_table', {'collections': collections} )


def get_dblist():
    '''
    current db models in MongoViewer
    '''
    dbs = MongoViewer.objects.all()
    db_list = list()
    for db in dbs:
        db_list.append(db.db_name)
    return db_list
