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
    template_name = 'wind/showcol.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            #'collections':DbTable.objects.filter(db=self.kwargs['slug']),
            'dbs':Database.objects.all()

            })
        print(context)
        return context

    def get_queryset(self):
        self.update_table()
        return DbTable.objects.filter(db_id=self.kwargs['slug'])

    def update_table(self):
        mon = Mongo()
        mdb = Database.objects.get(db_name=self.kwargs['slug'])
        # add talbe if notexist
        table_list = mon.connect_mongo()[self.kwargs['slug']].list_collection_names()
        print(table_list)
        for colname in table_list :
            try:
                DbTable.objects.get(col_name=colname)
            except DbTable.DoesNotExist:
                DbTable.objects.create(col_name=colname, db=mdb)
        # remove talbe if not exist
        for col in DbTable.objects.filter(db_id=mdb.db_name):
            if col.col_name not in table_list:
                col.delete()




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


