import sys, os

main_path = '/Users/sinn/NBA-Data-Stuff/DataFiles'

# load data file from box score pages
box_path = os.path.join(main_path, 'another_text_BOX.pkl')
with open(box_path, 'r') as f1:
	box_data = pickle.load(f1)
# ditto for pbp
pbp_path = os.path.join(main_path, '/another_test_PBP.pkl')
with open(pbp_path, 'r') as f1:
	pbp_data = pickle.load(f1)


def processBoxes(box_data):
    '''Handle for all box data'''
    for box in box_data:
        pbox = processBox(box)


def processBox(box):
    '''
    Processes an individual set of box data; three parts of box data:
    content, plyerlinks, and details; content is the actual numeric values
    of stuff and player / team names; details shows team names, column
    headings, and differentiates starters from bench players; playerlinks
    are the ESPN links to each of the player pages (this can be used to
    verify player ids and such);
    '''
    '''This is actually players + totals, but the pattern is simple'''
    players = [int(len(k)==0) for k in box['details']]
    index = players.index(1)
    t1_start = [index, index+5]
    t1_bench = [players.index(1, t1_start[-1]),
                players.index(0, t1_start[-1]+1)]
    t2_start = [t1_bench[-1]+6, t1_bench[-1]+11]
    t2_bench = [t2_start[-1]+1, players.index(0, t2_start[-1]+1)]
