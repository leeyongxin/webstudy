#coding:utf-8
#!/usr/bin/env python
""""
********************************************
Program:
Description:
Author: Yongxin
Date: 2019-05-22 14:36:33
Last modified: 2019-05-22 14:36:33
********************************************
"""
from pymongo import MongoClient
import pandas as pd
class Mongo:
    def __init__(self,host='192.168.193.40', port=27017,user='',password=''):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.conn = self.connect_mongo()

    def connect_mongo(self):
        """ A util for making a connection to mongo. """
        if self.user and self.password:
            mongo_uri = "mongodb://%s:%s@%s:%s/%s" % (self.user, self.password, self.host, self.port)
            conn = MongoClient(mongo_uri)
        else:
            conn = MongoClient(self.host,self.port)

        return conn

    def read_db_name(self):
        return self.connect_mongo().list_database_names()

    def read_collection_name(self,db):
        return self.connect_mongo()[db].list_collection_names()

    def read_columns(self,database, collection):
        """ Read first line from Mongo and get the columns list. """

        cursor = self.conn[database][collection].find().limit(1)

        df = pd.DataFrame(list(cursor))
        # del df['_id']
        res = df.columns
        return res

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

    def read_mongo(self,database, collection, query='',limit='',skip='', no_id=True):
        """ Read from Mongo and Store into DataFrame. """
        # 查询语句 = "find({'60m水平风向(°)':{'$gt':16},'60m水平风向(°)':{'$lt':98}},{'_id':0,'Time':1,'60m水平风速(m/s)':1,'60m水平风向(°)':1})"
        # Make a query to the specific DB and Collection
        if query == '':
            cursor = self.conn[database][collection].find()
        elif limit=='' and skip == '' :
            cursor = self.conn[database][collection].find(query)
        else:
            cursor = self.conn[database][collection].find(query).limit(limit).skip(skip)

        # Expand the cursor and construct the DataFrame
        df = pd.DataFrame(list(cursor))
        # df.to_csv("abc.csv", encoding="utf_8_sig")  # 处理中文乱码问题

        # if no_id:
        #     del df['_id']
        return df

    def read_count(self,database, collection, query=''):
        if query == '':
            cursor = self.conn[database][collection].find()
        else:
            cursor = self.conn[database][collection].find(query)

        # Expand the cursor and construct the DataFrame
        res = cursor.count()
        return res

    def to_mongo(self,df,database,collection, no_id=True):
        """ Write to Mongo and Store into DataFrame. """
        my_set = self.conn[database][collection]
        my_set.insert_many(df.to_dict('records'))

    def update_meta(self):
        '''
        !!! run this function each time insert new document to db
        meta set save key infomation in DB, like first, last document for each collection'''
        for cn in self.read_collection_name(self.databa):
            self.cnn[database][cn].find().sort([('TimeStamp',1)]).limit(1)



