
import pymongo


######################################################################
#{ Main mongo connection class
######################################################################


class MongoConn:
    """
    General handle for making a connection to a local Mongo database
    from within python; utilizes pymongo package;
    """
    def __init__(self, args=dict(), **dargs):
        port = args['port'] if 'port' in args.keys() else 27017
        db_name = args['db_name'] if 'db_name' in args.keys() else ''
        coll_name = args['coll_name'] if 'coll_name' in args.keys() else ''
        self.store = dict()
        self.conn = pymongo.MongoClient(port=port)
        if db_name:
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
            elif db_name not in self.conn.database_names():
                print('Database "%s" does not currently exist' % db_name)
                print('Add new collection (Y/n)?')
                yn = input()
                if yn.lower() in ['y','yes']:
                    self.db = self.conn[db_name]
                    if verbose: print("Mongo db creation was a success!")
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            ## do some error handling here, yo...
            print('Failure to make connection to db, uknw reason')


    def makeCollConn(self, coll_name, verbose=True):
        if 'db' not in self.__dict__:
            err_msg = "Not currently connected to a database"
            raise AttributeError, err_msg
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


    def insert(self, data, return_ids=False, verbose=False):
        """
        Default insert for dict objects into mongo with this class
        """
        ids = self.coll.insert(data)
        self.store['lastIDs'] = ids
        if type(ids) == list():
            if len(ids) != len(data):
                print("Something went wrong! Not all data inserted...")
            else:
                if verbose: print("Success!")
        elif ids:
            if verbose: print("Success!")
        else:
            print("Something went wrong! Not all data inserted...")
        if return_ids:
            return ids


    def query(self, spec={}, fields=None,
              skip=0, limit=50,
              no_cursor_timeout=False,
              verbose=False):
        """

        """
        try:
            Cursor = self.coll.find(filter=spec, projection=fields,
                                    skip=skip, limit=limit,
                                    no_cursor_timeout=no_cursor_timeout)
            if Cursor.count(with_limit_and_skip=True)==0:
                if verbose:
                    print('No results in collection matched the query.')
            else:
                numReturned = Cursor.count(with_limit_and_skip=True)
                if verbose:
                    print("%s documents returned" % numReturned)
            return Cursor
        except TypeError:
            print('TypeError:  Invalid query arguments!')



######################################################################
#{ Test run; main method
######################################################################

            
class NBAMonConn(MongoConn):

    
    def __init__(self, **dargs):
        MongoConn.__init__(self, args=dargs)


    '''
    Handles the general call to the fucntions for updating the
    MySQL database with new information;
    '''
    def addInfo(self, pageType ,data):
        if pageType=='pbp':
            pass
        elif pageType=='box':
            self.updateBox(self, data)

        elif pageType=='ext':
            pass
        else:
            print "Warning! non valid page type; not updating"


######################################################################
#{ Test run; main method
######################################################################

            
class RSSMonConn(MongoConn):
    def __init__(self, sub=None):
        db_name = 'WebPages'
        coll_name = 'Wired'
        if sub:
            coll_name += '.'+sub
        MongoConn.__init__(self,
                           {'db_name':db_name,
                           'coll_name':coll_name})


######################################################################
#{ General Create and Connect
######################################################################


def createAndReturnMDB(db_name='', coll_name=''):
    mdb_obj = MongoConn()
    if not db_name:
        print("Enter new DB name or hit return for default:")
        db_name = input()
        db_name = db_name if db_name else 'SentimentSentenceData'
    if not coll_name:
        print("Enter new collection name or hit return for default:")
        coll_name = input()
        coll_name = coll_name if coll_name else 'Sentences'
    mdb_obj.makeDBConn(db_name)
    mdb_obj.makeCollConn(coll_name)
    return mdb_obj
       

######################################################################
#{ Test run; main method
######################################################################

        
if __name__=="__main__":
    conn = MongoConn({"db_name":'EduCrawl',
                      'coll_name':'Department'})
    print(conn.coll.count())
    conn.conn.disconnect()
