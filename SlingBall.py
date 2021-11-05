# Structural overview

##
##initialize game
##    declare objects
##    draw
##
##game loop
##    advance objects
##    keyboard input
##    check game ending, do stuff
##    loop
import random
import math
import numpy as np
import pygame, sys
from pygame.locals import *
from Wall import Wall

class Ball:
    def __init__(b,r,xpos = 0,ypos = 0,color = [255,255,255]):
        b.xpos = xpos
        b.ypos = ypos
        b.r = r
        b.color = color
        b.xvel = 0
        b.yvel = 0
        b.xposLast = b.xpos
        b.yposLast = b.ypos
        b.xaccel = 0
        b.yaccel = 0
        b.state = "Null"
        b.s = 0 # Spin

    def drawBall(b,DSURF):
        pygame.draw.circle(DSURF,b.color, (int(b.xpos),int(b.ypos)), int(b.r),int(b.r))

    def getxintersect(b,y_line,width):
        x_intersect = b.xpos + ( (b.ypos-y_line)/abs(b.yvel) )*b.xvel
        while x_intersect < 0 or x_intersect > width:
            if x_intersect < 0:
                x_intersect = abs(x_intersect)
            elif x_intersect > width:
                x_intersect = 2*width - x_intersect
        return x_intersect



class ManyBall(Ball):
    def __init__(self,r,G,width,height,xpos = 0,ypos = 0,color = [255,255,255]):
        super().__init__(r,xpos,ypos,color)
        self.yvel = -2
        self.state = "Free"
        self.yaccel = G
        self.width = width
        self.height = height
        self.startx = self.xpos
        self.wallbool = False

    def reset(b):
        b.xpos = b.startx
        b.ypos = 0
        b.xvel = 0
        b.yvel = -2
        
    def advanceBall(b,WallList,t):
        # Test all walls
        b.wallbool = False
        for i in range(len(WallList)):
            b.testWall(WallList[i],t,0.5,0.8,True)

        # If ball isn't stopped, update
        if b.state != "Stopped":
            b.xposLast = b.xpos
            b.yposLast = b.ypos
            b.xpos += b.xvel*t
            b.ypos += b.yvel*t
            b.yvel += b.yaccel*t
            if b.wallbool == False:
                b.s = 0

    def testWall(b,W,t,damp = 1,fric = 1,Stoppable = False):
        parDistance = abs( b.xpos*W.slope - b.ypos + W.yint )/math.sqrt(math.pow(W.slope,2) + 1)
        perpDistance = abs( b.xpos*W.perpslope - b.ypos + W.perpyint )/math.sqrt(math.pow(W.perpslope,2) + 1)
        if parDistance <= 15:
            b.wallbool = True
            if b.s < 50:
                b.s += 1 # Spin
        # If within wall length and within 30 pixels of it
        if perpDistance <= W.length/2+1 and parDistance <= 10:
            if W.slope == 100000000:
                if b.xpos > W.x1 - 2 and b.xvel > 0 or b.xpos < W.x1 + 2 and b.xvel < 0:
                    b.xvel *= -1
            else:
                unitVec = [ (W.x2-W.x1)/W.length , (W.y2 - W.y1)/W.length ] # Map line unit vector
                dotProduct = b.xvel*unitVec[0] + b.yvel*unitVec[1] # Dot product for velocity vector parallel to map line
                parallelVec = [dotProduct*unitVec[0],dotProduct*unitVec[1]]
                perpVec = [parallelVec[0]-b.xvel , parallelVec[1]-b.yvel] # Velocity vector perpendicular to map line
                vel = math.hypot(b.xvel,b.yvel)
                if vel == 0:
                    vel = 0.001
                perpUnitVec = [perpVec[0]/vel,perpVec[1]/vel]

                # Getting perpendicular distance unit vector to compare to perpendicular vel
                ballVec = [b.xpos-W.x1, b.ypos-W.y1]
                ballDotProduct = ballVec[0]*unitVec[0]+ballVec[1]*unitVec[1]
                projection = [unitVec[0]*ballDotProduct, unitVec[1]*ballDotProduct]
                ballPerpVec = [projection[0]-ballVec[0], projection[1]-ballVec[1]]
                ballDistance = math.hypot(ballPerpVec[0],ballPerpVec[1])
                ballUnitVec = [ballPerpVec[0]/ballDistance, ballPerpVec[1]/ballDistance]

                if abs(ballUnitVec[0] - perpUnitVec[0] ) < 1 and abs(ballUnitVec[1] - perpUnitVec[1] ) < 1:
                    b.xvel = parallelVec[0]*(fric+b.s/400) + perpVec[0]*damp
                    b.yvel = parallelVec[1]*(fric+b.s/400) + perpVec[1]*damp
                    b.xpos += b.xvel*t # x = x + vt
                    b.ypos += b.yvel*t # y = y + vt
                newmag = math.hypot(b.xvel,b.yvel)
                if Stoppable == True and newmag < 1:
                    b.xvel = 0
                    b.yvel = 0
                    b.state = "Stopped"
                    if b.ypos >= W.slope*b.xpos + W.yint:
                        b.ypos = W.slope*b.xpos + W.yint - 1

                
        

class SlingBall(Ball):
    def __init__(b,size,longtailSwitch = False):
        b.width = size[1]
        b.height = size[0]
        Ball.__init__(b,8,b.width/2,b.height/2)
        b.xvel = 30*random.choice([-1,1])
        b.yvel = 150*random.choice([-1,1])
        b.mass = 1
        fill = [b.xpos,b.ypos]
        b.taillength = 8
        b.tail = []
        for i in range(b.taillength):
            b.tail.append(fill)
        b.longtail = []
        b.longtailSwitch = longtailSwitch
        if longtailSwitch == True:
            for j in range(b.taillength*5):
                b.longtail.append(fill)
            b.longtaillength = len(b.longtail)
        b.tailtimer = 0
        b.longtailtimer = 0
        b.xvelhist = int(b.xvel)
        b.yvelhist = int(b.yvel)
        b.bounced = False
        

    def advanceBall(b,paddleList,WallList,t):
        # Sling, solid paddle, wall, spin
        for k in range(len(paddleList)):
            paddle = paddleList[k]
            b.slingCheck(paddle,t)
            
        # Wall
        if b.xpos < 1 and b.xvel < 0 or b.xpos > b.width-1 and b.xvel > 0: # Just accounts for side walls rn for simplicity
            b.xvel = -b.xvel
        for i in range(len(WallList)):
            WallList[i].testWallFlat(b,t)
            if WallList[i].bounced == True:
                break
            
        b.tailtimer += t # Ticker for ball tail
        b.longtailtimer += t
        if b.tailtimer > 0.08: # Ball tail mechanic. Update every .08 seconds
            b.tailtimer = 0
            b.updateTail()
        if b.longtailtimer > 0.016 and b.longtailSwitch == True:
            b.longtailtimer = 0
            b.updateLongTail()
        
        # Update last pos trackers
        b.xposLast = b.xpos
        b.yposLast = b.ypos
        # Update current pos
        b.xpos += t*b.xvel
        b.ypos += t*b.yvel

        b.xaccel = 0
        b.yaccel = 0


    def slingCheck(b,paddle,t):
        if paddle.slingmode == 'hard':
            b.paddleHit(paddle)
        elif paddle.grabbed == True:
            b.ballInSling(paddle,t)
        
    def drawBall(b,DSURF):
        # Uses tail, draws each point as balls of decreasing size
        for j in range(b.taillength):
            tailx = int(round(b.tail[round(b.taillength-j-1)][0]))
            taily = int(round(b.tail[round(b.taillength-j-1)][1]))
            pygame.draw.circle(DSURF,(200,200,200,round(255-30*j)), (tailx,taily), round(8-j),round(8-j))
        if b.longtailSwitch == True:
            for k in range(b.longtaillength):
                longtailx = round(b.longtail[b.longtaillength-k-1][0])
                longtaily = round(b.longtail[b.longtaillength-k-1][1])
                pygame.draw.circle(DSURF,(200,200,200,150), (longtailx,longtaily), 2, 2)

    def updateTail(b):
        b.tail.pop(0)
        b.tail.append([b.xpos,b.ypos])

    def updateLongTail(b):
        b.longtail.pop(0)
        b.longtail.append([b.xpos,b.ypos])


    def ballInSling(b,paddle,t): # Ball is caught by a sling
        x_accel_scalar = 2*paddle.strength # Adjustment to strength of accel in x/y directions
        y_accel_scalar = 14*paddle.strength
        b.xvel += t*x_accel_scalar*(paddle.x - b.xpos)/b.mass # Adds sling accel directly to vel
        b.yvel += t*y_accel_scalar*(paddle.y - b.ypos)/b.mass

    def paddleHit(b,paddle): # Ball hits a solid sling
        if b.ypos > paddle.y - 4 and b.ypos < paddle.y + 4: # hits paddle in y
            if b.xpos < paddle.x + paddle.length/2 and b.xpos > paddle.x - paddle.length/2: # hits paddle in x
                team_mod = paddle.side*2 - 3
                if team_mod*b.yvel < 0: # If ball is going towards goal for paddle in question or in pupshooter mode
                    b.yvel = -b.yvel + paddle.yvel # Reverse direction & add paddle y velocity
                    b.xvel = b.xvel + (b.xpos-paddle1.x)*1.5 # Add x vel based on hit location

    def getxintersect(b,y_line):
        x_intersect = b.xpos + ( (b.ypos-y_line)/abs(b.yvel) )*b.xvel
        while x_intersect < 0 or x_intersect > b.width:
            if x_intersect < 0:
                x_intersect = abs(x_intersect)
            elif x_intersect > b.width:
                x_intersect = 2*b.width - x_intersect
        return x_intersect

    def spawnReplayBall(b,ballInit):
        b.xpos = b.width/2
        b.ypos = b.height/2
        b.xvel = ballInit[0]
        b.yvel = ballInit[1]
        b.mass = 1
        fill = [b.xpos,b.ypos]
        b.taillength = 8
        b.tail = [fill,fill,fill,fill,fill,fill,fill,fill]

    def testWall(b,W,t):
        ## Make a line segment in slope-intercept form
        ## take last ball pos
        ## if current y < current x function and last y > current x function
        ## or vice versa
        ## keep magnitude, flip direction across normal of line

        
        parDistance = abs( b.xpos*W.slope - b.ypos + W.yint )/math.sqrt(math.pow(W.slope,2) + 1)
        perpDistance = abs( b.xpos*W.perpslope - b.ypos + W.perpyint )/math.sqrt(math.pow(W.perpslope,2) + 1)
        if perpDistance <= W.length/2 and parDistance <= 30:
        #if b.ypos < Wall.maxy and b.ypos > Wall.miny and b.xpos < Wall.maxx and b.xpos > Wall.minx:
            if (b.ypos < W.slope*b.xpos + W.yint and b.yposLast > W.slope*b.xposLast + W.yint) or (b.ypos > W.slope*b.xpos + W.yint and b.yposLast < W.slope*b.xposLast + W.yint):
                print(round(b.xpos,2),round(b.ypos,2),round(b.xposLast,2),round(b.yposLast,2),round(b.xvel,2))
                if W.slope == 0:
                    b.yvel = -b.yvel
                elif W.perpslope == 0:
                    b.xvel = -b.xvel
                else:
                    slope = W.slope
                    yint = W.yint
                    perpslope = W.perpslope
                    magnitude = math.hypot(b.xvel,b.yvel)
                    velTheta = math.atan2(b.yvel,b.xvel)                
                    if b.ypos <= W.slope*b.xpos + W.yint:
                        normTheta = math.atan2(-perpslope,-1)
                    else:
                        normTheta = math.atan2(perpslope,1)
                    difTheta = normTheta - velTheta
                    inverseVel = velTheta - math.pi
                    newTheta = inverseVel + 2*difTheta
                    b.xvel = magnitude * math.cos(newTheta)
                    b.yvel = magnitude * math.sin(newTheta)

                b.xpos += b.xvel*t
                b.ypos += b.yvel*t
                b.xposLast = b.xpos
                b.yposLast = b.ypos
                print(round(b.xpos,2),round(b.ypos,2),round(b.xposLast,2),round(b.yposLast,2),round(b.xvel,2))



##                    
##                    xnew = (b.ypos - b.xpos*perpslope - yint) / (slope - perpslope)
##                    ynew = xnew*slope + yint
####                    print(W.slope,W.perpslope,W.yint)
####                    print(b.xpos,b.ypos)
####                    print(xnew,ynew)
##                    b.xvel = (xnew-b.xpos)
##                    b.yvel = (ynew-b.ypos)
##                    
##                    newmag = math.hypot(b.xvel,b.yvel)
##                    scaler = magnitude/newmag
##                    b.xvel *= scaler
##                    b.yvel *= scaler
##                magnitude = math.hypot(b.xvel,b.yvel)
##                if slope == 0:
##                    normTheta = math.pi/2
##                else:
##                    normTheta = math.atan2((Wall.y2 - Wall.y1) , (Wall.x2 - Wall.x1))
##                velTheta = math.atan2(b.yvel,b.xvel)
##                print(math.degrees(velTheta))
##                difTheta = (normTheta - velTheta)
##                newVelTheta = velTheta + 2*difTheta
##                print(math.degrees(newVelTheta))
##                b.xvel = magnitude * math.cos(newVelTheta)
##                b.yvel = magnitude * math.sin(newVelTheta)
                










        
