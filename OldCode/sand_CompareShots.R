##Load the data
# load data and restrict to players in top 75% of minutes...
shots <- read.csv('/home/immersinn/Gits/NBA-Data-Stuff/DataFiles/shot_by_player_att_all.txt', header=TRUE)
play.mins.list <- 
	read.csv('/home/immersinn/Gits/NBA-Data-Stuff/DataFiles/playmins20112012.csv',header=TRUE)
play.mins.list[["Indx"]] <- play.mins.list[["Indx"]]+1		#bc I'm an idiot...

##Remove players playing lower 25% of minutes
summary(play.mins.list[["SimpleMin"]])	#cutoff is abotu 290 mins...
play.mins.list <- subset(play.mins.list,play.mins.list[['SimpleMin']]>=290)
shots <- shots[,play.mins.list[['Indx']]]

##Remove locations with no shots / small number of shots (<10 in this case)
#Remove all locs with less that 11 shots...
shots.per.loc <- apply(shots,1,sum)
shots <- subset(shots, shots.per.loc>=10)
#Remvoe shots from foul line
shots <- shots[1:nrow(shots)-1,]

##Inital distances, plotting etc; not nec for gfinal analysis
# mds plotting; kinda cool....
shots.dist <- dist(t(shots))
shots.mds <- as.data.frame(cmdscale(shots.dist))
base <- ggplot(shots.mds, aes(x=V1,y=V2))
print(base+geom_text(aes(label=names(shots))))

# corr plotting; ehhh...summ
shots.cor <- cor(shots)
shots.evd <- eigen(shots.cor)
shots.vec <- as.data.frame(t(shots.evd[["vectors"]]))
base <- ggplot(shots.vec, aes(x=V1,y=V2))+geom_point()
print(base+geom_text(aes(label=names(shots))))

##Prepare each of the three A matricies (0.2, 0.4, and 0.6 cutoffs)
# 0.2 cutoff; ~110K
A0.indx <- shots.cor>.2
A0 <- matrix(data=0,nrow=nrow(shots.cor),ncol=ncol(shots.cor))
A0[A0.indx] <- 1
# 0.4 cutoff
A1.indx <- shots.cor>.4
A1 <- matrix(data=0,nrow=nrow(shots.cor),ncol=ncol(shots.cor))
A1[A1.indx] <- 1
# 0.6 cutoff; ~13K
A2.indx <- shots.cor>.6
A2 <- matrix(data=0,nrow=nrow(shots.cor),ncol=ncol(shots.cor))
A2[A2.indx] <- 1


# ##Remove shot locations with little / no attempted shots:
# # no shots
# shots.per.loc <- apply(shots,1,sum)
# no.shots <- shots.per.loc==0
# shots <- subset(shots, no.shots!=1)
# # foul line
# shots <- shots[1:nrow(shots)-1,]
# # few shots (<10) from a location, remove...
# shots.per.loc <- apply(shots,1,sum)
# few.shots <- shots.per.loc<=10
# shots <- subset(shots,few.shots!=1)

# # w/ P subtracted...
# cor.tot.play <- as.matrix(apply(shots.ltf.cor,1,sum))
# P <- cor.tot.play %*% t(cor.tot.play)
# B <- shots.ltf.cor - P
# B.evd <- eigen(B)
# B.vec <- as.data.frame(t(B.evd[["vectors"]]))
# base <- ggplot(B.vec, aes(x=V1,y=V2))+geom_point()
# print(base+geom_text(aes(label=names(shots)[less.thantft!=1])))