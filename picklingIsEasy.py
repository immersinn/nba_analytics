import sys, os
import pickle

def picklehandle(data, argdict):
    '''Pickle data, if dicts are not empty'''
    pbp_store = data['pbp']
    box_store = data['box']
    print "Pickling files..."
    if pbp_store:
        fname = argdict['outname'] + "_PBP.pkl"
        fname = os.path.join(default_path, fname)
        pickledata(fname, pbp_store)
    if box_store:
        fname = argdict['outname'] + "_BOX.pkl"
        fname = os.path.join(default_path, fname)
        pickledata(fname, box_store)

def pickledata(fname, data):
    '''For easy pickling'''
    with open(fname, 'wb') as dbfile:       # use binary mode files in 3.X
        pickle.dump(data, dbfile)           # data is bytes, not str

def unpickledata(fname):
    '''For easy un-pickling'''
    with open(fname, 'rb') as dbfile:
        data = pickle.load(dbfile)
        return data
