
import logging
from multiprocessing import Process, Lock, Queue, Value, Array

from nba_analytics import espngames
from nba_analytics.espnMomentsTools import retrieveDumpGameMoments
from dbinterface_python.dbconns import connectMon

LOG_FILENAME = 'gameMomentsPull.out'

logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.INFO,
                    )


def momentsWorker(jobs, lock,
                  db_name='NBASD', coll_name='Moments'):

    logger1 = logging.getLogger('worker')

    while True:
        game_id = jobs.get()
        if game_id is None:
            break
        try:
            game = espngames.NBAStatsGame(game_id)
            game.initFromEspn(to_init = ['moments'])
            db_conn = connectMon.MongoConn(db_name=db_name,
                                           coll_name=coll_name)
            with lock:
                try:
                    game_info_dict = game.dataToDict(which_data = ['moments'])
                    moments_info_list = game_info_dict.pop('moments')
                    if moments_info_list:
                        db_conn.insert(moments_info_list)
                        print('Moments for game %s inserted into mdb.' % game_id)
                        logger1.info('Moments for game ' + str(game_id) + ' inserted into mdb.')
                    else:
                        logger1.info('Empty moments data for game ' + str(game_id))
                except KeyError:
                    logger1.warning('No moments data for game ' + str(game_id))

        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as X:
            logger1.critical('caught: ' + str(X.__class__) + '; message: ' + X.message)
    
    

def getExistingGameIds(coll='Games'):
    conn = connectMon.MongoConn(db_name='NBASD',
                                coll_name=coll)
    results = conn.query(limit = 0,
                         fields = {'game_id' : True})
    gids = [r['game_id'] for r in results if 'game_id' in r.keys()]
    return(set(gids))


def main():
    """

    """


    
    logger_mp = logging.getLogger("main_phase")
    num_workers = 4
    jobs = Queue(maxsize = 2 * num_workers)
    lock = Lock()

    print('Retrieving existing game_ids')
    logger_mp.info('Retrieving existing game_ids')
    existing_gids = getExistingGameIds()
    moments_gids = getExistingGameIds(coll='Moments')
    game_ids = existing_gids.difference(moments_gids)

    # Init workers
    print('Initilizing workers...')
    logger_mp.info('Initilizing workers...')
    workers = [Process(target=momentsWorker, args=(jobs, lock))\
               for _ in xrange(num_workers)]
    for w in workers:
        w.daemon = True # make interrupting the process with ctrl+c easier
        w.start()

    # Create job queue
    print('Initilizing and populating queue...')
    logger_mp.info('Initilizing and populating queue...')
    for job_no,job in enumerate(game_ids):
        logger_mp.debug("putting job #%i in the queue" % (job_no))
        jobs.put(job)
    logger_mp.info("reached the end of input; waiting to finish outstanding jobs")
    for _ in xrange(k):
        jobs.put(None)  # give the workers heads up that they can finish -- no more work!
    
    for w in workers:
        w.join()


if __name__=="__main__":

   main()
