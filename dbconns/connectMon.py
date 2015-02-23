"""
Actual connection handles for Mongo; used by dbconn
to create the connections.  
"""
import sys, os
import datetime, time
import math

import pymongo, bson


######################################################################
#{ Main mongo connection class
######################################################################


class MongoConn:
    """
    General handle for making a connection to a local Mongo database
    from within python; utilizes pymongo package;
    """
    def __init__(self, args=dict(), **dargs):
        port = args['port'] \
                  if 'port' in args.keys() else 27017
        db_name = args['db_name'] \
                  if 'db_name' in args.keys() else None
        coll_name = args['coll_name'] \
                    if 'coll_name' in args.keys() else None
        self._store = dict()
        self.conn = pymongo.MongoClient(port=port)
        self.makeDBConn(db_name, verbose=False)
        if 'db' in self.__dict__.keys():
            self.makeCollConn(coll_name)
        self.LastQ = None
        self.LastQLen = 0

        
    def makeDBConn(self, db_name, verbose=True):
        try:
            if db_name in self.conn.database_names():
                self.db = self.conn[db_name]
                if verbose: print("Mongo db connection was a success!")
            elif not db_name:
                print("No db name provided; only conn to mdb privided.")
            elif db_name not in self.conn.database_names():
                print('Database "%s" does not currently exist' % db_name)
                print('Add new collection (Y/n)?')
                yn = input()
                if yn.lower() in ['y','yes']:
                    self.db = self.conn[db_name]
                    if verbose: print("Mongo db creation was a success!") 
        except:
            ## do some err handling here, yo...
            print('Failure to make connection to db, uknw reason')


    def makeCollConn(self, coll_name, verbose=True):
        if coll_name in self.db.collection_names():
            self.coll = self.db[coll_name]
            if verbose: print("Mongo coll connection was a success!")
        elif not coll_name:
            print("No collection name provided; only conn to db privided.")
        elif coll_name not in self.db.collection_names():
            print('Collection "%s" does not currently exist' % coll_name)
            print('Add new collection (Y/n)?')
            yn = input()
            if yn.lower() in ['y','yes']:
                self.coll = self.db[coll_name]
                if verbose: print("Mongo coll connection was a success!") 
        else:
            print('Failure to make connection to coll, uknw reason')


    def MongoInsert(self, data, return_ids=False, verbose=False):
        """
        Default insert for dict objects into mongo with this class
        """
        ids = self.coll.insert(data)
        self._store['lastIDs'] = ids
        if type(ids)==list():
            if len(ids)!=len(data):
                print("Something went wrong! Not all data inserted...")
            else:
                if verbose: print("Success!")
        elif ids:
            if verbose: print("Success!")
        else:
            print("Something went wrong! Not all data inserted...")
        if return_ids: return ids

    
    def RecursInsert(self, data):
        """
        Mongo has a maximum document size of 16MB; instead of trying
        to figure out the size of the data, just try, try again.
        Split after each fail, recursively.
        """
        ids,ers = list(),list()
        db_index = int(math.floor(len(data)/2.0))
        try:
            ids1 = self.coll.insert(data[:db_index])
            ids2 = self.coll.insert(data[db_index:])
            err = []
        except:
            err = sys.exc_info()
            if type(err[1]) in [pymongo.errors.AutoReconnect,
                                bson.errors.InvalidDocument]:
                ids1, err_lst1 = self.RecursInsert(data[:db_index])
                ids2, err_lst2 = self.RecursInsert(data[db_index:])
                err = [err, [err_lst1+err_list2]]
            else:
                ids1 = ids2 = []
                err = [err, 'Fatal']
        ids.append(ids1 + ids2)
        ers.append(err)
        return ids, ers


    def query(self,
              spec=None,
              fields=None,
              skip=0,
              limit=50,
              coll=None):
        if not coll:
            # for later when >1 coll per instance
            pass
        try:
            self.LastQ = self.coll.find(spec=spec,
                                        fields=fields,
                                        skip=skip,
                                        limit=limit)
            if self.LastQ.count()==0:
                print('No results in collection matched the query.')
            else:
                numReturned = self.LastQ.count()
                if numReturned>limit and limit!=0:
                    numReturned=limit
                self.LastQLen = numReturned
                print("%s documents returned" % numReturned) 
        except TypeError:
            print('TypeError:  Invalid query arguments!')


    def nextItem(self):
        try:
            return self.coll.__getitem__()
        except InvalidOperation:
            pass

    def close(self):
        if self.LastQ and self.LastQ.alive:
            self.LastQ.close()
            

######################################################################
#{ Test run; main method
######################################################################

        
if __name__=="__main__":
    conn = MongoConn({"db_name":'EduCrawl',
                      'coll_name':'Department'})
    print(conn.coll.count())
    conn.conn.disconnect()
