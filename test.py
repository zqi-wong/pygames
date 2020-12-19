import pgzrun
import random
import math
import time

WIDTH = 1200
HEIGHT = 800
global balls
balls=[]#balls[i]=[pos,verb,radium,color]
G=100
global position
position = ()
global trace_begin
trace_begin = ()
global co_just_now
co_just_now = []
global feed_back
feed_back = []

def draw():
    screen.clear()
    screen.fill((30,30,30))
    screen.draw.text("PRESS SPACE TO CLEAR UP",(500,10))
    if trace_begin:
        screen.draw.line(trace_begin,position,(204,204,204))
    for ball in balls:
        screen.draw.filled_circle(ball[0],ball[2],ball[3])

def update():
    #移动屏幕
    if keyboard.SPACE:
        global balls
        balls = []
    elif keyboard.UP:
        for ball in balls:
            ball[0] = (ball[0][0],ball[0][1]+10)
    elif keyboard.DOWN:
        for ball in balls:
            ball[0] = (ball[0][0],ball[0][1]-10)
    elif keyboard.LEFT:
        for ball in balls:
            ball[0] = (ball[0][0]+10,ball[0][1])
    elif keyboard.RIGHT:
        for ball in balls:
            ball[0] = (ball[0][0]-10,ball[0][1])
    #计算运动        
    for i in range(len(balls)):
        fx = 0
        fy = 0
        for j in range(len(balls)):
            if i == j:
                continue
            dis = [balls[j][0][0]-balls[i][0][0],balls[j][0][1]-balls[i][0][1]]
            d = math.sqrt(dis[0]**2+dis[1]**2)
            if d <=0.5:
                d = 0.5
            f = (G/(d**2))*((balls[j][2])**3)
            fx += f*(dis[0]/d)
            fy += f*(dis[1]/d)
        # if  5 in co_just_now[i] or\
        #     5 in [co_just_now[x][i] for x in range(len(balls))] :
        #     if feed_back[i] != (0,0):
        #         balls[i][1] = tuple(map(lambda x,y: x+(y/60),balls[i][1],feed_back[i]))
        #         feed_back[i] = (0,0)
        # elif 4 in co_just_now[i] or\
        #      4 in [co_just_now[x][i] for x in range(len(balls))]:
        #     if feed_back[i] != (0,0):
        #         balls[i][1] = tuple(map(lambda x,y: x+(y/60),balls[i][1],feed_back[i]))
        #     feed_back[i] = (fx,fy)
        # else:
        balls[i][1] = tuple(map(lambda x,y: x+(y/60),balls[i][1],[fx,fy]))
            # if feed_back[i] != (0,0):
            #     balls[i][1] = tuple(map(lambda x,y: x+(y/60),balls[i][1],feed_back[i]))
            #     feed_back[i] = (0,0)
    for ball in balls:
        ball[0] = tuple(map(lambda x,y: x+(y/60),ball[0],ball[1]))
    for i in range(len(balls)):
        for j in range(len(balls)):
            if i<=j:
                continue
            else:
                if d<=balls[i][2]+balls[j][2]:
                    print(balls[i][1],balls[j][1])
                dis = [balls[j][0][0]-balls[i][0][0],balls[j][0][1]-balls[i][0][1]]
                d = math.sqrt(dis[0]**2+dis[1]**2)
                if co_just_now[i][j]==0:
                    if (d<=balls[i][2]+balls[j][2]):
                        collide(i,j,d,dis)
                else:
                    if (d <= balls[i][2]+balls[j][2]):
                        reset(i,j,d,dis)
                    co_just_now[i][j] -= 1 

def addBall(pos,verb,radium):
    global co_just_now
    global feed_back
    global balls
    c = (random.randint(100,255),
         random.randint(100,255),
         random.randint(100,255))
    ball = [pos,verb,int(radium),c]
    balls.append(ball)
    for i in range(len(co_just_now)):
        co_just_now[i].append(0)
    co_just_now.append([0,]*(len(co_just_now)+1))
    feed_back.append((0,0))

def reset(i,j,d,dis):
    global balls
    print(balls[i],balls[j])
    verb_help = (abs(balls[i][1][0])+abs(balls[i][1][1])+abs(balls[j][1][0])+abs(balls[j][1][1]))/30
    de = (balls[i][2]+balls[j][2]-d)/2 +2
    if de >= 10* verb_help and verb_help<=5:
        deep = de + verb_help
    else:
        deep = de * 1.1
    if d <= 0.5:
        d = 0.5 
    balls[i][0] = (balls[i][0][0]-deep*(dis[0]/d)*balls[j][2]/(2*(balls[i][2]+balls[j][2])),
                   balls[i][0][1]-deep*(dis[1]/d)*balls[j][2]/(2*(balls[i][2]+balls[j][2])))
    balls[j][0] = (balls[j][0][0]+deep*(dis[0]/d)*balls[i][2]/(2*(balls[i][2]+balls[j][2])),
                   balls[j][0][1]+deep*(dis[1]/d)*balls[i][2]/(2*(balls[i][2]+balls[j][2])))
    
def collide(i,j,d,dis):
    global co_just_now
    global balls
    mass1 = (balls[i][2])**3
    mass2 = (balls[j][2])**3
    if d <= 1:
        d = 1
    v1c = balls[i][1][0]*(dis[0]/d)+balls[i][1][1]*(dis[1]/d)
    v1p = balls[i][1][0]*(dis[1]/d)-balls[i][1][1]*(dis[0]/d)
    v2c = balls[j][1][0]*(dis[0]/d)+balls[j][1][1]*(dis[1]/d)
    v2p = balls[j][1][0]*(dis[1]/d)-balls[j][1][1]*(dis[0]/d)
    v1ce = ((mass1-mass2)*v1c+2*mass2*v2c)/(mass1+mass2)
    v2ce = ((mass2-mass1)*v2c+2*mass1*v1c)/(mass1+mass2)
    balls[i][1] = (v1ce*(dis[0]/d)+v1p*(dis[1]/d),
                   v1ce*(dis[1]/d)-v1p*(dis[0]/d))
    balls[j][1] = (v2ce*(dis[0]/d)+v2p*(dis[1]/d),
                   v2ce*(dis[1]/d)-v2p*(dis[0]/d))
    reset(i,j,d,dis)
    co_just_now[i][j] = 5
    
def on_mouse_move(pos):
    global position
    position = pos
    
def on_mouse_down(pos):
    global tb
    tb = time.time()
    global trace_begin
    trace_begin = pos
    
    
def on_mouse_up(pos):
    global trace_begin
    verb = ((pos[0]-trace_begin[0])/3,(pos[1]-trace_begin[1])/3)
    radium = (time.time() - tb)*25 + 10
    addBall(trace_begin,verb,radium)
    trace_begin = ()


pgzrun.go()