

from nba_analytics import fileHelper
from nba_analytics import momentsHelper
from nba_analytics import pbpHelper

print('Loading data')
moments, pbp = fileHelper.grabGameFromLoad()
print('Creating and cleaning moments, segments')
segments_info = momentsHelper.preprocessSegments(moments)
print('Creating events')
events_info = pbpHelper.preprocessEvents(pbp)
