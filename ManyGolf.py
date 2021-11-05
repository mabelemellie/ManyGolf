from time import perf_counter as clock
import math
import random
import pygame, sys
from pygame.locals import *
from SlingBall import Ball
from SlingBall import ManyBall
from Wall import Wall

pygame.init()

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
BLACK = [0,0,0]
WHITE = [255,255,255]
GRAY = [128,128,128]
SILVER = [192,192,192]

def manyGame(height,width,scheme):
    DSURF = pygame.display.set_mode((width,height))
    pygame.display.set_caption('ManyGolf')
    time_scale = 10 # Initial time scaling knob
    G = 5 # Gravity scaling knob
    fricScalar = 0.97 # Friction scaling knob
    damp = 0.40 # Bounciness scaling knob

    a = clock()
    b = clock()
    
    while True:
        # Generate map
        start = [random.randrange(round(width/2)),random.randrange(round(2*height/5),round(4*height/5))]
##        holex = random.randrange(start[0] + width/10,9*width/10)
##        holey = random.randrange(height/4,7*height/8)
##        hole = [holex,holey]
        coordList = generatePolarMap(height,width,start)
        holex = holeFind(coordList)
        WallList = []
        WallList = Wall.WallfromPoints(coordList,False)
        lineColor = random.choice([SILVER,YELLOW,RED,OLIVE,TEAL,PURPLE])
        lineColor = [225,random.randrange(0,225),0]
        #mapObject = generateMap(height,width,start)
        # Initialize ball
        ball = ManyBall(6,G,width,height,start[0],0,SILVER)
        cannon = Cannon() # r, theta, r vel, theta vel
        loopStage = "Move"
    
        while True:
            t = (b - a) * time_scale
            b = clock()
            # Action loop
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        cannon.thetavel = math.radians(10)
                    elif event.key == K_RIGHT:
                        cannon.thetavel = -math.radians(10)
                    elif event.key == K_SPACE:
                        cannon.state = "Load"
                    elif event.key == K_n:
                        manyGame(height,width,scheme)
                elif event.type == KEYUP:
                    if event.key == K_LEFT or event.key == K_RIGHT:
                        cannon.thetavel = 0
                    elif event.key == K_SPACE:
                        cannon.state = "Fire"
            
            if loopStage == "Move":
                drawMap(coordList,DSURF,lineColor,height,width)
                ball.advanceBall(WallList,t)
                ball.drawBall(DSURF)
                cannon.switchCheck(ball,holex)
                if ball.xpos < 0 or ball.xpos > width:
                    ball.reset()
                    cannon.reset()

                pygame.display.update()

                if ball.state == "Stopped":
                    loopStage = "Action"
                    print("Action")

            elif loopStage == "Action":
                drawMap(coordList,DSURF,lineColor,height,width)
                cannon.advanceCannon(t)
                cannon.drawCannon(ball,holex,DSURF)
                ball.drawBall(DSURF)

                pygame.display.update()

                if cannon.state == "Fire":
                    ball.xvel = math.cos(cannon.theta)*cannon.r
                    ball.yvel = math.sin(cannon.theta)*cannon.r
                    ball.state = "Free"
                    cannon.rvel = 0
                    cannon.r = 0
                    cannon.state = "Null"
                    loopStage = "Move"
            
            # Hole end clause
            if ball.ypos > height:
                break
            
            pygame.display.update()
            a = clock()

    
class Cannon:
    def __init__(c,state = "Null"):
        c.r = 0
        c.theta = math.radians(-45)
        c.rvel = 0
        c.thetavel = 0
        c.state = state
        c.primer = 1 # power increasing or decreasing
        c.maxPower = 80

    
    def advanceCannon(c,t):
        if c.r > c.maxPower:
            c.primer = -1
        elif c.r < 0:
            c.primer = 1
            
        if c.state == "Load":
            c.rvel = 6 # plus or minus 5
        c.r += c.rvel*t * c.primer
        c.theta += c.thetavel*t

    def drawCannon(c,ball,holex,DSURF):
        pointa = (round(ball.xpos),round(ball.ypos))
        pointb = (round(ball.xpos + 40*math.cos(c.theta)),round(ball.ypos + 40*math.sin(c.theta)))
        pygame.draw.lines(DSURF, SILVER, True, [pointa,pointb], 3)
        if c.state == "Load":
            pygame.draw.lines(DSURF, WHITE, False, [(round(ball.xpos-15),round(ball.ypos+15)),(round(ball.xpos-15-c.r),round(ball.ypos+15))],10)

    def switchCheck(c,ball,holex):
        if (ball.xpos >= holex and ball.xposLast < holex) or (ball.xpos <= holex and ball.xposLast > holex):
            ycomp = math.sin(c.theta)
            xcomp = math.cos(c.theta)
            xcomp *= -1
            c.theta = math.atan2(ycomp,xcomp)
    def reset(c):
        ycomp = math.sin(c.theta)
        xcomp = abs(math.cos(c.theta))
        c.theta = math.atan2(ycomp,xcomp)


def buildMap(height,width,start,hole):
    # First make start and hole objects out of wall
    coordList = []
    startWidth = random.randrange(10,40)
    
    firstthird = [] # Before start
    secondthird = [] # Between start and hole
    thirdthird = [] # After hole
    pointNum = random.randrange(20,40) # Number of lines on the map
    firstlen = round(start[0]/width * pointNum + random.randrange(-3,3)) # Lines in the first third, proportionate w/ some randomness
    secondlen = round(hole[0]/width * pointNum + random.randrange(-3,3)) - firstlen # Lines in the second third by the same rules
    thirdlen = pointNum - firstlen - secondlen + random.randrange(-3,3) # Remaining length w/ randomness

    coord = (0,random.randrange(height/4,3*height/4))
    coordList.append(coord)
    for i in range(firstlen):
        # For each new point, max delta y is 1/3 of the height, max y is 1/4 of height, min y is 7/8ths of height
        # Delta x is between 1/3 of average distance and 2 times average distance
        coordx = coordList[i][0] + random.randrange(int(width/(3*pointNum)), int(2*width/pointNum))
        coordy = random.randrange ( int(max(coordList[i][1]-height/3,height/4)), int(min(coordList[i][1] + height/3,7*height/8) ) )
        coord = (coordx,coordy) 
        if coordx < start[0]:
            coordList.append(coord)
        else:
            break
    startPoint1 = (start[0]-startWidth/2,start[1])
    startPoint2 = (start[0]+startWidth/2,start[1])
    coordList.append(startPoint1)
    coordList.append(startPoint2)
    for j in range(firstlen+2,secondlen):
        coordx = coordList[j][0] + random.randrange(int(width/(3*pointNum) ), int(2*width/pointNum) )
        coordy = random.randrange ( int(max(coordList[j][1]-height/3,height/4))), int(min(coordList[j][1] + height/3,7*height/8)) 
        coord = (coordx,coordy)  # Same as first
        if coordx < start[0]:
            coordList.append(coord)
        else:
            break
    hole1 = hole
    hole2 = (hole[0],height+100)
    hole3 = (hole[0]+20,height+100)
    hole4 = (hole[0]+20,hole[1])
    coordList.append(hole1)
    coordList.append(hole2)
    coordList.append(hole3)
    coordList.append(hole4)
    for k in range(firstlen+secondlen+6,thirdlen):
        coordx = coordList[k][0] + random.randrange(int(width/(3*pointNum)), int(2*width/pointNum))
        coordy = random.randrange ( int(max(coordList[k][1]-height/3,height/4)), int(min(coordList[k][1] + height/3,7*height/8)) )                                         
        coord = (coordx,coordy) 
        coordList.append(coord)
    return coordList


def generatePolarMap(height,width,start):
    pointNum = 25 #random.randrange(30,60)
    startNum = round(pointNum*start[0]/width)
    holeNum = random.randrange(startNum+3,pointNum)

    mapObject = []
    for i in range(pointNum):
        if i == startNum:
            coords = [round(random.randrange(20,60)),0]
        elif i >= holeNum-1 and i <= holeNum+3:
            if i == holeNum:
                coords = [height,-math.pi/2]
            elif i == holeNum+1:
                coords = [25,0]
            elif i == holeNum+2:
                coords = [height,math.pi/2]
            elif i == holeNum-1 or i == holeNum+3:
                coords = [random.randrange(40,round(height/4)),random.randrange(-100,100)/100]
        else:
            coords = [random.randrange(40,round(height/4)),random.randrange(-150,150)/100]
        mapObject.append(coords)

    # Check to see if constraints are met
    maxHeight = height/2
    minHeight = height/2
    mapCoords = []
    for j in range(pointNum):
        #netLength += mapObject[j][0]*math.cos(mapObject[j][1])
        mapCoords.append([0,0])
    # Build coordinate map object
    mapCoords[startNum][0] = start[0]-mapObject[startNum][0]/2
    mapCoords[startNum][1] = start[1]
    for k in range(startNum):
        mapCoords[startNum-k-1][0] = round(mapCoords[startNum-k][0] - math.cos(mapObject[startNum-k-1][1])*mapObject[startNum-k-1][0])
        mapCoords[startNum-k-1][1] = round(mapCoords[startNum-k][1] + math.sin(mapObject[startNum-k-1][1])*mapObject[startNum-k-1][0])
        maxHeight = max(maxHeight,mapCoords[startNum-k-1][1])
        minHeight = min(minHeight,mapCoords[startNum-k-1][1])
    for m in range(1,pointNum-startNum):
        mapCoords[startNum+m][0] = round(mapCoords[startNum+m-1][0] + math.cos(mapObject[startNum+m-1][1])*mapObject[startNum+m-1][0])
        mapCoords[startNum+m][1] = round(mapCoords[startNum+m-1][1] - math.sin(mapObject[startNum+m-1][1])*mapObject[startNum+m-1][0])
        if startNum+m+1 != holeNum and startNum+m+1 != holeNum+1 and startNum+m+1 != holeNum+2 and startNum+m+1 != holeNum+3:
            maxHeight = max(maxHeight,mapCoords[startNum+m][1])
        minHeight = min(minHeight,mapCoords[startNum+m][1])
    netLength = mapCoords[pointNum-1][0]
    netStart = mapCoords[0][0]
    holeX = mapCoords[holeNum][0]
    if netLength < width or netStart > 0 or maxHeight > height or minHeight < 0 or holeX > width-40:
        mapCoords = generatePolarMap(height,width,start)
        
    return mapCoords

def holeFind(mapObject):
    minHeight = 0
    holeNum = 0
    for p in range(len(mapObject)):
        if mapObject[p][1] > minHeight:
            minHeight = mapObject[p][1]
            holeNum = p
    holex = mapObject[holeNum][0]
    return holex

def drawMap(mapObject,DSURF,color,height,width):
    DSURF.fill([64,0,0]) # Wipe display
    tempMap = []
    for n in range(len(mapObject)):
        tempMap.append([mapObject[n][0],mapObject[n][1]-6])
    
    tempMap.append([5000,5000])
    tempMap.append([-5000,5000])
        
    for j in range(10):
        points = [ [-10,round((10-j)*height/30)],[width+10,round((10-j)*height/30)],[width+10,round((9-j)*height/30)],[-10,round((9-j)*height/30)] ]
        pygame.draw.polygon(DSURF,[64-4*j,0,0],points)
    pygame.draw.polygon(DSURF,BLACK,tempMap)
    pygame.draw.lines(DSURF, color, False, tempMap, 3)

##def advanceBall(height,width,ball,mapObject,holeNum,fricScalar,damp,start,G,t):
##    if ball.xpos < 1 or ball.xpos > width - 1:
##        ball.xpos = start[0]
##        ball.ypos = 0
##        ball.xvel = 0
##        ball.yvel = -2
##        ball.xaccel = 0
##
##    ball.state = ballState(ball,mapObject)
##    # Interaction with map
##
##    if ball.state == "Caught":
##        ball.xaccel = G*abs(ball.xvel)/math.hypot(ball.xvel,ball.yvel)
##        ball.yaccel = G*abs(ball.xvel)/math.hypot(ball.xvel,ball.yvel)
##        ball.xvel += ball.xaccel*t # v = v + at
##        ball.yvel += ball.yaccel*t # v = v + at
##        ball.xpos += ball.xvel*t # x = x + vt
##        ball.ypos += ball.yvel*t # y = y + vt
##
##
##    
##    for i in range(len(mapObject)-1):
##        if ball.xpos > mapObject[i][0] and ball.xpos < mapObject[i+1][0]+1: # If the ball is within a map section
##            if ball.ypos > min(mapObject[i][1],mapObject[i+1][1])-4: # and ball.ypos < max(mapObject[i][1],mapObject[i+1][1])+4:
##                unitVecScalar = math.hypot(mapObject[i][0]-mapObject[i+1][0],mapObject[i][1]-mapObject[i+1][1]) # Map line hypotenuse length
##                unitVec = [ (mapObject[i+1][0] - mapObject[i][0])/unitVecScalar , (mapObject[i+1][1] - mapObject[i][1])/unitVecScalar ] # Map line unit vector
##                # Calculate perpendicular vector
##                ballVec = [ball.xpos-mapObject[i][0], ball.ypos-mapObject[i][1]]
##                ballDotProduct = ballVec[0]*unitVec[0]+ballVec[1]*unitVec[1]
##                projection = [unitVec[0]*ballDotProduct, unitVec[1]*ballDotProduct]
##                ballPerpVec = [ballVec[0]-projection[0], ballVec[1]-projection[1]]
##                ballDistance = math.hypot(ballPerpVec[0],ballPerpVec[1])
##
##                if ballDistance < 5:
##                    dotProduct = ball.xvel*unitVec[0] + ball.yvel*unitVec[1] # Dot product for velocity vector parallel to map line
##                    parallelVec = [dotProduct*unitVec[0],dotProduct*unitVec[1]]
##                    perpVec = [parallelVec[0]-ball.xvel , parallelVec[1]-ball.yvel] # Velocity vector perpendicular to map line
##                    if math.hypot(perpVec[0],perpVec[1]) > 0.1 and perpVec[1]>1:
##                        ball.xvel = parallelVec[0]*fricScalar + perpVec[0]*damp
##                        ball.yvel = parallelVec[1]*fricScalar + perpVec[1]*damp
##                    elif math.hypot(perpVec[0],perpVec[1]) < 0.1 and perpVec[1]>1:
##                        ball.xvel = parallelVec[0]*fricScalar + perpVec[0]*damp + unitVec[1]*ball.yaccel*0.8
##                        ball.yvel = parallelVec[1]*fricScalar + perpVec[1]*damp + unitVec[0]*ball.yaccel*0.8
##                        ball.xpos += ball.xvel*t # x = x + vt
##                        ball.ypos += ball.yvel*t # y = y + vt
##
####                        if math.hypot(ball.xvel,ball.yvel)>1 and math.hypot(x_vel,y_vel)>1:
####                            ball.xvel = x_vel # Adding vector components to get final velocity vector
####                            ball.yvel = y_vel # Adding vector components to get final velocity vector
####                        else:
####                            ball.xvel = 0
####                            ball.yvel = 0
##                    
##            elif i == holeNum and ball.ypos > mapObject[i-1][1] and ball.ypos < height:
##                if ball.xpos < mapObject[i][0]+4 and ball.xvel>0:
##                    ball.xvel *= -1
##                elif ball.xpos > mapObject[i+1][0]-3 and ball.xvel<0:
##                    ball.xvel *= -1
##    if ball.yvel < -110: # Max negative y 
##        ball.yvel = -110


def ballState(ball,mapObject):
    bDistance = ballDistance(mapObject,ball)
    perpVec = [0,0]
    for i in range(len(mapObject)-1):
        if ball.xpos > mapObject[i][0] and ball.xpos < mapObject[i+1][0]+1: # If the ball is within a map section
            if ball.ypos > min(mapObject[i][1],mapObject[i+1][1])-4 and ball.ypos < max(mapObject[i][1],mapObject[i+1][1])+4:
                unitVecScalar = math.hypot(mapObject[i][0]-mapObject[i+1][0],mapObject[i][1]-mapObject[i+1][1]) # Map line hypotenuse length
                unitVec = [ (mapObject[i+1][0] - mapObject[i][0])/unitVecScalar , (mapObject[i+1][1] - mapObject[i][1])/unitVecScalar ] # Map line unit vector
                dotProduct = ball.xvel*unitVec[0] + ball.yvel*unitVec[1] # Dot product for velocity vector parallel to map line
                parallelVec = [dotProduct*unitVec[0],dotProduct*unitVec[1]]
                perpVec[0] += parallelVec[0]-ball.xvel
                perpVec[1] += parallelVec[1]-ball.yvel # Velocity vector perpendicular to map line
    
    if bDistance > 5 or perpVec[1] > 0.1:
        return "Free"
    elif ball.xvel > 0.01 and ball.yvel > 0.01:
        return "Caught"
    else:
        return "Stopped"

    
def ballDistance(mapObject,ball):
    ballDistance = 100
    for i in range(len(mapObject)-1):
        if ball.xpos > mapObject[i][0] and ball.xpos < mapObject[i+1][0]+1: # If the ball is within a map section
            if ball.ypos > min(mapObject[i][1],mapObject[i+1][1])-4 and ball.ypos < max(mapObject[i][1],mapObject[i+1][1])+4:
                unitVecScalar = math.hypot(mapObject[i][0]-mapObject[i+1][0],mapObject[i][1]-mapObject[i+1][1]) # Map line hypotenuse length
                unitVec = [ (mapObject[i+1][0] - mapObject[i][0])/unitVecScalar , (mapObject[i+1][1] - mapObject[i][1])/unitVecScalar ] # Map line unit vector
                # Calculate perpendicular vector
                ballVec = [ball.xpos-mapObject[i][0], ball.ypos-mapObject[i][1]]
                ballDotProduct = ballVec[0]*unitVec[0]+ballVec[1]*unitVec[1]
                projection = [unitVec[0]*ballDotProduct, unitVec[1]*ballDotProduct]
                ballPerpVec = [ballVec[0]-projection[0], ballVec[1]-projection[1]]
                ballDistance = min(math.hypot(ballPerpVec[0],ballPerpVec[1]),ballDistance)
    return ballDistance


        
manyGame(800,1700,1)
