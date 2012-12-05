# prereq stuff
import sys, os
import pandas
import numpy as py
import scipy.stats as stats
# for plotting 3d:
from mpl_toolkits.mplot3d import Axes3D

sys.path.append('/home/immersinn/Gits/Helper-Code/Python27')
import picklingIsEasy

# link to general bball court info:
# http://en.wikipedia.org/wiki/Basketball_court
# http://www.bettingexpress.com/national_basketball_association/nba_rules/rule1_court_dimensions.shtml

# set file names to use
pbp_n = '/home/immersinn/Gits/NBA-Data-Stuff/pbp_20111215to20111221.pkl'
box_n = '/home/immersinn/Gits/NBA-Data-Stuff/box_20111215to20111221.pkl'
sht_n = '/home/immersinn/Gits/NBA-Data-Stuff/sht_20111215to20111221.pkl'
# unpickle data
pbp = picklingIsEasy.unpickledata(pbp_n)
box = picklingIsEasy.unpickledata(box_n)
sht = picklingIsEasy.unpickledata(sht_n)

"""
General data overview for future ref.

sht --> dict w/ keys as game IDs (little redundant)
'Game ID' --> ['GameID', 'Shots']
    'GameID' --> as expected
    'Shots' --> dict
        <Play ID> --> shot info dict

If I were loading into MDB:
shots = [val for val in sht.values()]
drop shots into db..
"""
'''
Prep stuff...
'''
# get only made shots, throw to DF"
made_shots = list()
for val in sht.values():
    for ent in val['Shots'].values():
	if int(ent['made']):
            made_shots.append({'x':int(ent['x']),
                               'y':int(ent['y']),
                               'pts':int(ent['pts'])})
sm_df = pandas.DataFrame(data=made_shots, columns=['x','y','pts'])
# get all the shots, throw to DF:
shots = list()
for val in sht.values():
    for ent in val['Shots'].values():
        shots.append({'x':int(ent['x']),
                      'y':int(ent['y']),
                      'status':int(ent['made'])})
sht_df = pandas.DataFrame(data=shots, columns=['x','y','status'])
# plotting...scatter (1:2) and density (3)
pandas.scatter_matrix(sht_df)
scatter(sht_df.ix[:,'x'], sht_df.ix[:,'y'], c=sht_df['status'])
sht_df.plot(kind='kde', subplots=True, sharex=False)
# combine the opposite sides of the court:
revx = [50-x if y > 47 else x for (x,y) in  zip(sht_df.x, sht_df.y)]
revy = [94-y if y > 47 else y for y in sht_df.ix[:,'y']]
sht_df['newx'] = revx
sht_df['newy'] = revy
# plot again; note new peak @ -2 on y.  This is free throws
sht_df.plot(kind='kde', subplots=True, sharex=False)
# move free throws:
fty = [15 if y==-2 else y for y in sm_df['newy']]
sm_df['fty'] = fty


def densPlot(dataFrame, names, DDD=2):
    """
    Attempting to construct 3D mesh grid of shots made...
    help from:
    https://gist.github.com/1035069
    http://matplotlib.org/mpl_examples/mplot3d/surface3d_demo.py
    """
    ## Check that names are in dataFrame
    if valid:
        # Force DDD to be valid, fuckers
        DDD = 2 if DDD not in [2,3] else DDD
        
        # Data we want to plot; similar plan as before
        rvs = [[x,y] for (x,y) in zip(sm_df.newx,sm_df.fty)]
        rvs = np.array(rvs)
        # Create 2D kde from data; this will be used to create 'Z'
        kde = stats.kde.gaussian_kde(rvs.T)
        # create grid from data:
        X_flat = np.r_[0:50:128j]
        Y_flat = np.r_[0:47:128j]
        X,Y = np.meshgrid(X_flat,Y_flat)
        grid_coords = np.append(X.reshape(-1,1),Y.reshape(-1,1),axis=1)
        # generate Z
        Z = kde(grid_coords.T)
        Z = Z.reshape(128,128)
        if DDD==2:
            # 2d scatter with superimposed colored density plot
            scatter(rvs[:,0],rvs[:,1],alpha=0.5,color='white')
            imshow(Z,aspect=X_flat.ptp()/Y_flat.ptp(),
                   origin='lower',
                   extent=(rvs[:,0].min(),rvs[:,0].max(),rvs[:,1].min(),rvs[:,1].max()))
        elif DDD==3:
            # 3d mesh surface plot w/ height as density
            fig = plt.figure()
            ax = fig.gca(projection='3d')
            surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm,
                    linewidth=0, antialiased=False)
            ax.set_zlim(0, 0.025)   # more than enough in this case...
            fig.colorbar(surf, shrink=0.5, aspect=5)
            plt.show()
        


"""
Problem number 1:  where to misses occur more often??
"""
# all shots
shots = list()
for val in sht.values():
    for ent in val['Shots'].values():
            shots.append({'x':int(ent['x']),
                          'y':int(ent['y'])})
shots = pandas.DataFrame(shots, columns = ['x','y'])
shots['newx'] = [50-x if y > 47 else x for (x,y) in  zip(shots.x, shots.y)]
shots['newy'] = [94-y if y > 47 else y for (x,y) in  zip(shots.x, shots.y)]
shots = shots[shots['newy']>-2]
# made shots, throw to DF
made_shots = list()
for val in sht.values():
    for ent in val['Shots'].values():
	if int(ent['made']):
            made_shots.append({'x':int(ent['x']),
                               'y':int(ent['y']),
                               'pts':int(ent['pts'])})
made_df = pandas.DataFrame(data=made_shots, columns=['x','y','pts'])
# missed shots too
miss_shots = list()
for val in sht.values():
    for ent in val['Shots'].values():
	if not int(ent['made']):
            miss_shots.append({'x':int(ent['x']),
                               'y':int(ent['y']),
                               'pts':int(ent['pts'])})
miss_df = pandas.DataFrame(data=miss_shots, columns=['x','y','pts'])
# Shift to only 1 side of the court
made_df['newx'] = [50-x if y > 47 else x for (x,y) in  zip(made_df.x, made_df.y)]
made_df['newy'] = [94-y if y > 47 else y for (x,y) in  zip(made_df.x, made_df.y)]
miss_df['newx'] = [50-x if y > 47 else x for (x,y) in  zip(miss_df.x, miss_df.y)]
miss_df['newy'] = [94-y if y > 47 else y for (x,y) in  zip(miss_df.x, miss_df.y)]
# look right?
scatter(made_df['newx'],made_df['newy'])
# remove freethrows from consideration for now; distort kde
made_nft_df = made_df[made_df['newy']>-2]
miss_nft_df = miss_df[miss_df['newy']>-2]
# check again...
scatter(made_nft_df['newx'],made_nft_df['newy'])
# simnple compare:
made = made_nft_df[['newx','newy']]
miss = miss_nft_df[['newx','newy']]
pandas.scatter_matrix(shots, diagonal='kde')
pandas.scatter_matrix(made, diagonal='kde')
pandas.scatter_matrix(miss, diagonal='kde')
# prep kdes
made_rvs = np.array([[x,y] for (x,y) in zip(made_nft_df.newx,made_nft_df.newy)])
miss_rvs = np.array([[x,y] for (x,y) in zip(miss_nft_df.newx,miss_nft_df.newy)])
made_kde = stats.kde.gaussian_kde(made_rvs.T)
miss_kde = stats.kde.gaussian_kde(miss_rvs.T)
# make grid, Z plot:
X_flat = np.r_[0:50:100j]
Y_flat = np.r_[0:47:94j]
X,Y = np.meshgrid(X_flat,Y_flat)
grid_coords = np.append(X.reshape(-1,1),Y.reshape(-1,1),axis=1)
Z = miss_kde(grid_coords.T) - made_kde(grid_coords.T)
Z = Z.reshape(94,100)
# plot that shit
scatter(made_rvs[:,0],made_rvs[:,1],alpha=0.5,color='green')
scatter(miss_rvs[:,0],miss_rvs[:,1],alpha=0.5,color='blue')
imshow(Z,aspect=X_flat.ptp()/Y_flat.ptp(),
       origin='lower',
       extent=(0,50,0,50),
       cmap=cm.spectral)
plt.colorbar()
