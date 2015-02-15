

def espnBoxFromSoup(soup, labels):
    """
    url is a box score url obtained from score-summary ESPN page;
    use BeautifulSoup to parse apart data_in; all relevant data found
    in 'table' HTML structures, hence we grab those;

        "details" are headers, teams stuff;
        "content" is actual player data;

    """
    sumary = espnSummaryFromBox(soup)
    player_info = espnPlayerInfoFromBox(summary)
    game_info = espnGameInfoFromBox(summary, player_info)
    return player_info, game_info


def espnSummaryFromBox(soup):
    """Extract important table from Box Soup"""
    tables  = soup.find_all('div', {labels[0]:labels[1]})
    summary = tables[0].findAll('tr')
    return summary


def espnPlayerInfoFromBox(summary):
    """
    Gets the ESPN page urls for players in the game from the box score page;
    keys are the full names of players used in box score, and values are
    the urls;

    does there need to be a "try" here?
    """
    playerlink_dict = dict()
    for line in summary:
        try:
            temp = line.findAll('a')[0]
            if str(temp.get('href')) != 'None':     # not team name...
                playerlink_dict[str(temp.text)] =\
                                                refineEspnPlayerlink(str(temp.text),
                                                                     str(temp.get('href')))
        except IndexError:
            pass
    return playerlink_dict


def refineEspnPlayerlink(key, value):
    """
    Takes info from playerlink_dict and turns it into dict
    for importing data into "
    players_site" MySQL table;
    """
    temp = dict()
    temp['first']   = ' '.join(key.split(' ')[:-1])
    temp['last']    = key.split(' ')[-1]
    temp['id']      = value.split('/')[-2]
    temp['pbp_name'] = ' '.join(value.split('/')[-1].split('-'))
    temp['web_page'] = value
    return temp  


def espnGameInfoFromBox(summary, player_info):
    details     = []
    content     = []
    for line in summary:
        details.append([str(h.text.encode('utf8')) for h in line.findAll('th')])
        content.append([str(h.text.encode('utf8')) for h in line.findAll('td')])


def structureBoxContent(data):
    '''
    Box score output from parseESPNPages to (loose) dictionary.  Not
    too much processing here, as the only real reasons to vist the box
    score page are to
    i) Get the player names used in the pbp data
    ii) Get the urls for each player
    iii) Obtain data for confirming any pbp parsing in the future (i.e,
    does the calculated rbs from player xxxx match the box score?)
    iv) Obtain the list of starters for the game, so that the
    "Who is on the court?" code can be verified.
    
    Boxscore page data from parseESPNPages:
    data['details']
    data['content']
    data['playerlinks']
    '''
    pageDict = dict()

    ## where are these functions?
    player_names = getUsedNames(data['playerlinks'])
    player_ids = getESPNIDs(data['playerlinks'])
    ## the last two names are not required.  IDs and Names in
    ## the dictionary created with "espnPlayerInfoFromBox"
    box_data = BoxInfo(box, details, player_names, player_ids)
    teamsheader = TeamsHeader(data['details'])
    boxinfo = BoxInfo(box, details, player_names, player_ids)

    '''Put home / away team and the stats header in the pageDict'''
    pageDict['header'] = teamsheader['header']
    pageDict['home'] = teamsheader['home']
    pageDict['away'] = teamsheader['away']
    '''Define starters, bench for home, away'''
    pageDict['StartersHome']    = "|".join(boxinfo['team_2'][:5])
    pageDict['BenchHome']       = "|".join(boxinfo['team_2'][5:])
    pageDict['StartersAway']    = "|".join(boxinfo['team_1'][:5])
    pageDict['BenchAway']       = "|".join(boxinfo['team_1'][5:])
    '''Set up player_name : player_id pairs'''
    for key in player_ids.keys():
        pageDict[key] = player_ids[key]
    '''Put info from boxinfo into pageDict; double-up on team_1, team_2'''
    for key in boxinfo.keys():
        pageDict[key] = boxinfo[key]
    return pageDict


def BoxInfo(box, details, player_names, player_ids):
    '''
    Helper function for 'page2dictBOX'; visits each component,
    does useful stuff for organizing, etc.
    '''
    boxdata = dict()
    '''Index of each important break in the data'''
    start_index = [i for i in range(len(details)) if details[i].find('STARTERS')>-1]
    bench_index = [i for i in range(len(details)) if details[i].find('BENCH')>-1]
    total_index = [i for i in range(len(details)) if details[i].find('TOTALS')>-1]
    '''Get players on each team'''
    boxdata['team_1'], boxdata['team_2'] = getTeamPlayers(box,
                                                          start_index,
                                                          bench_index,
                                                          total_index,
                                                          player_names)
    '''Get player box scores stats, team stats, teams, header'''
    playerdetails = getPlayerDetails(box, player_names, player_ids)
    extrasdetails = getExtrasDetails(box, start_index, total_index)
    for key in playerdetails.keys():
        boxdata[key] = playerdetails[key]
    for key in extrasdetails.keys():
        boxdata[key] = extrasdetails[key]
    return boxdata


def getTeamPlayers(box, start_index, bench_index, total_index, player_names):
    '''Determine all players for each team from the box score table'''
    team_1 = box[start_index[0]+1:start_index[0]+6]
    team_1.extend(box[bench_index[0]+1:total_index[0]])
    team_1 = [entry.split(',')[0].replace('  ',' ') for entry in team_1]
    team_1 = [player_names[name] for name in team_1]
    # somehow a space gets added or removed here...
    team_2 = box[start_index[1]:start_index[1]+5]
    team_2.extend(box[bench_index[1]:total_index[1]-1])
    team_2 = [entry.split(',')[0].replace('  ',' ') for entry in team_2]
    team_2 = [player_names[name] for name in team_2]
    return team_1, team_2


def getPlayerDetails(box, player_names, player_ids):
    '''
    Grabs box score details for each player;
    ESPN_ID : Box_Score_Line
    '''
    playerdetails = dict()
    for line in box:
        if line.split(',')[0].replace('  ',' ') in player_names.keys():
            playerdetails[player_ids[player_names[line.split(',')[0].replace('  ',' ')]]] = \
                                                                               line.split(',')[1]
    return playerdetails


def getExtrasDetails(box, start_index, total_index):
    '''
    Grabs all the extra stuff sitting after the team totals and such;
    accounts for extra space in details data stuff;
    '''
    extrasdetails = dict()
    extrasdetails['homeExtra'] = box[total_index[0]:start_index[1]]
    extrasdetails['awayExtra'] = box[total_index[1]-1:]
    return extrasdetails


def TeamsHeader(details, start_index):
    '''Grabs home / away team and stats header'''
    teamsheader = dict()
    teamsheader['away'] = details[0]
    teamsheader['home'] = details[start_index[1]-2]
    teamsheader['header'] = '\t'.join(details[start_index[0]-1].split('\t')[1:])
    return teamsheader

