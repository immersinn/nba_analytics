Loading data...
Processing games...
Game 0041400163
Preprocessing moments...
Preprocessing events...
Traceback (most recent call last):
  File "extract_game_graphs.py", line 37, in <module>
    main()
  File "extract_game_graphs.py", line 25, in main
    gs.preprocess()
  File "/home/immersinn/gits/nba_analytics/nbaGame.py", line 435, in preprocess
    self._events.preprocess()
  File "/home/immersinn/gits/nba_analytics/nbaGame.py", line 519, in preprocess
    self._playersOnCourt()
  File "/home/immersinn/gits/nba_analytics/nbaGame.py", line 551, in _playersOnCourt
    eventsHelper.playersForEventsGame(self)
  File "/home/immersinn/gits/nba_analytics/eventsHelper.py", line 713, in playersForEventsGame
    team_names)
  File "/home/immersinn/gits/nba_analytics/eventsHelper.py", line 756, in playersForEventsQuarter
    players = [sorted([lookup[p] for p in pl]) for pl in players]
  File "/home/immersinn/gits/nba_analytics/eventsHelper.py", line 756, in <listcomp>
    players = [sorted([lookup[p] for p in pl]) for pl in players]
  File "/home/immersinn/gits/nba_analytics/eventsHelper.py", line 756, in <listcomp>
    players = [sorted([lookup[p] for p in pl]) for pl in players]
KeyError: 'Green STEAL (2 ST'
