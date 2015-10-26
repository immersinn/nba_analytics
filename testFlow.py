

from nba_analytics import fileHelper
from nba_analytics import momentsHelper
from nba_analytics import pbpHelper

moments, pbp = momentsParse.grabGameFromLoad()
segments_info = momentsHelper.preprocessSegments(moments)
events_info = pbpHelper.preprocessEvents(pbp)
