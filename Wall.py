from time import perf_counter as clock
import math
import random
import pygame, sys
from pygame.locals import *
import numpy as np

# Colors
LIME = [0,255,0]
BLUE = [0,0,255]
RED = [255,0,0]
MAROON = [128,0,0]
GREEN = [0,128,0]
NAVY = [0,0,128]
YELLOW = [255,255,0]
FUCHSIA = [255,0,255]
AQUA = [0,255,255]
OLIVE = [128,128,0]
PURPLE = [128,0,128]
TEAL = [0,128,128]
ORANGE = [255,120,0]
BLACK = [0,0,0]
WHITE = [255,255,255]
GRAY = [128,128,128]
SILVER = [192,192,192]
DGRAY = [64,64,64]


class Wall:
    def __init__(self,x1,y1,x2,y2,free = True,color = WHITE):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.p1 = (x1,y1)
        self.p2 = (x2,y2)
        self.maxx = max(x1,x2) + 1
        self.maxy = max(y1,y2) + 1
        self.minx = min(x1,x2) - 1
        self.miny = min(y1,y2) - 1
        self.midx = np.mean((self.x1,self.x2))
        self.midy = np.mean((self.y1,self.y2))
        self.color = color
        self.length = math.hypot(self.x2-self.x1,self.y2-self.y1)
        if self.x2 != self.x1:
            self.slope = (self.y2 - self.y1) / (self.x2 - self.x1)
        else:
            self.slope = 100000000
        if self.y2 != self.y1:
            self.perpslope = (self.x1 - self.x2) / (self.y2 - self.y1)
        else:
            self.perpslope = 100000000
        self.yint = self.y2 - self.slope*self.x2
        self.perpyint = self.midy - self.perpslope*self.midx
        self.bounced = False
        self.free = free # single wall or connected to other walls. Important for corners


        
    def drawWall(w,DSURF):
        points = (w.p1,w.p2)
        pygame.draw.lines(DSURF, w.color, False, points, 2)


    def WallfromPoints(points,wrap = True):
        WallList = []
        for i in range(len(points)-1):
##            print(points[i][0],points[i][1],points[i+1][0],points[i+1][1])
            wall = Wall(points[i][0],points[i][1],points[i+1][0],points[i+1][1],False)
            WallList.append(wall)
        if wrap == True:
            wall = Wall(points[i+1][0],points[i+1][1],points[0][0],points[0][1],False)
            WallList.append(wall)
        else:
            WallList[i].free = True
        return WallList

    def WallMotif(motif,height,width):
        wallpoints = []
        if motif == "Random Polygon":
            for i in range(5):
                wallpoints.append((random.randrange(width),random.randrange(height)))
            WallList = Wall.WallfromPoints(wallpoints)
        elif motif == "Left Rect":
            wallpoints = [ (0,height/2+20), (0,height/2-20), (width/2 - 50,height/2-20), (width/2-50,height/2+20) ]
            WallList = Wall.WallfromPoints(wallpoints)
        elif motif == "Middle Slant":
            WallList = Wall.WallfromPoints(((width/2-100,height/2-40),(width/2+100,height/2+40)),False)
        elif motif == "Middle Flat":
            WallList = Wall.WallfromPoints(((width/2-100,height/2),(width/2+100,height/2)),False)
        elif motif == "Small corners":
            wall1 = Wall(-10,height/5,height/5,-10)
            wall2 = Wall(width+10,height/5,width-height/5,-10)
            wall3 = Wall(-10,4*height/5,height/5,height+10)
            wall4 = Wall(width-height/5,height+10,width+10,4*height/5)
            WallList = (wall1,wall2,wall3,wall4)
        elif motif == "Box":
            wallpoints = [(10,10),(10,height-10),(width-10,height-10),(width-10,10)]
            WallList = Wall.WallfromPoints(wallpoints)
            
        return WallList

    def testWallFlat(W,b,t):
        parDistance = abs( b.xpos*W.slope - b.ypos + W.yint )/math.sqrt(math.pow(W.slope,2) + 1)
        perpDistance = abs( b.xpos*W.perpslope - b.ypos + W.perpyint )/math.sqrt(math.pow(W.perpslope,2) + 1)
        p1Distance = math.hypot(W.x1-b.xpos,W.y1-b.ypos)
        p2Distance = math.hypot(W.x2-b.xpos,W.y2-b.ypos)
        bvel = [b.xvel,b.yvel]
        bpos = [b.xpos,b.ypos]
        bvelAbs = math.hypot(b.xvel,b.yvel)
        perpVel = [0,0]

        # Exception handling
        if parDistance == 0 and b.xpos == b.tail[0][0] and b.ypos == b.tail[0][1]: # If ball spawns in wall
            b.xpos += random.choice([-1,1])*b.r/2
            b.ypos += random.choice([-1,1])*b.r/2
        
        if perpDistance <= W.length/2+1 and parDistance <= b.r:
            wallUnitVec = np.divide(np.subtract(W.p2,W.p1),W.length)
            parProject = int(np.dot(bvel,wallUnitVec) )
            parVec = np.multiply(wallUnitVec, parProject)
            perpVel = np.subtract(parVec,bvel)

        elif p1Distance <= b.r:
            norm = np.divide(np.subtract(W.p1,bpos),p1Distance)
            perpProject = int(np.dot(bvel,norm))
            perpVel = np.multiply(norm, -perpProject)

        elif p2Distance <= b.r and W.free == True:
            norm = np.divide(np.subtract(W.p2,bpos),p2Distance)
            perpProject = int(np.dot(bvel,norm))
            perpVel = np.multiply(norm, -perpProject)

        if W.bounced == False: # Can't get bounced twice by the same wall two instants in a row
            b.xvel += float(2*perpVel[0])
            b.yvel += float(2*perpVel[1])
        if perpVel[0] != 0 or perpVel[1] != 0:
            W.bounced = True
        else:
            W.bounced = False












        


    


