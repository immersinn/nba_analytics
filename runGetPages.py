
import sys, os
import datetime

import getESPNPagesNBA
import picklingIsEasy

days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}

def iterOverDays(start, stop=None):
    """
    Tired of waiting; iterates over dates from start 2 stop;
    grabs games, data from that day from ESPN pages; places all
    data into 3 dicts, one for each (pbp, box, shots) w/ game IDs
    as keys;
    """
    pbp_all = {}
    box_all = {}
    sht_all = {}

    
    if not stop:
        date = datetime.datetime.now()
        stop = str(date.year)+\
               ('0' if date.month<10 else '') + \
               str(date.month)+\
               ('0' if date.day<10 else '') + \
               str(date.day)
        stop = ''.join(decrease_date(stop[:4],stop[4:6],stop[6:]))
    year    = start[:4]
    month   = start[4:6]
    day     = start[6:]

    print "Start date: " + start
    print "Stop date:  " + stop

    while int(year+month+day) <= int(stop):
        new_data = getESPNPagesNBA.wrapper(year+month+day)
        if len(new_data['pbp'].keys())>0:
            pbp_all.update(new_data['pbp'])
            box_all.update(new_data['box'])
            sht_all.update(new_data['sht'])
        year,month,day = increase_date(year,month,day)
    return {'pbp':pbp_all, 'box':box_all, 'sht':sht_all}, stop


def increase_date(year,month,day):
    year = int(year)
    month = int(month)
    day = int(day)

    if day+1 > days[month]:
        if month==2 and year%4==0 and day==28:      # leap year
            day = day + 1
        else:
            day = 1
            if month+1 > 12:
                month = 1
                year = year + 1
            else:
                month = month + 1
    else:
        day = day+1
    return str(year), \
           ('0' if month<10 else '')+str(month), \
           ('0' if day<10 else '')+str(day)

def decrease_date(year,month,day):
    year = int(year)
    month = int(month)
    day = int(day)

    if day==1:
        if month==3 and year%4==0:
            day = 29
            month = 2
        else:
            if month==1:
                year = year - 1
                month = 12
                day = 31
            else:
                month = month - 1
                day = days[momth]
    else:
        day = day-1
    return str(year), \
           ('0' if month<10 else '')+str(month), \
           ('0' if day<10 else '')+str(day)

if __name__=="__main__":
    """
    Run iterPverDays from terminal window; input is start and stop dates
    """
    args = sys.argv[1:]
    start = args[0]
    stop = None if len(args)==1 else args[1]
    print "Starting data aquisition..."
    pages_dict, stop = iterOverDays(start, stop)
    print "Data aquisition complete; pickling data..."
    for name in ('pbp', 'box', 'sht'):
        print "Picking "+name+" data"
        picklingIsEasy.pickledata(name+"_"+start+'to'+stop+'.pkl',
                                  pages_dict[name])
    print "Process complete"

    
    
