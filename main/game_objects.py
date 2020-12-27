import pgzrun
from pgzero.actor import Actor
from pgzero.clock import clock
from pgzero.game import exit
from pgzero.music import _music as music
from pgzero.animation import animate
import math
import random
import os
import sys
from config import WIDTH, HEIGHT, G


class Player(Actor):
    '''
    用于储存关于火箭的类
    '''

    def __init__(self, image, pos, verb=(0, 0), **kwargs):
        super().__init__(image, pos=pos, **kwargs)
        self.verb = verb
        self.isjet = False
        self.timer = 0
        self.cd_jet = 3
        self.jet_strength = 1
        self.cd_shoot = 4.5
        self.score = 0
        self.crusharea = ((11, 0), (29, 2.747), (29, -2.474))
        # 极坐标下的碰撞监测点
        self.WHOSYOURDADDY = False

    def update_verb(self, stars, flag_gravity, rel):
        fx = 15*((self.jet_strength*self.timer)**1.5)*rel[0] if self.isjet else 0
        fy = 15*((self.jet_strength*self.timer)**1.5)*rel[1] if self.isjet else 0  # 喷汽部分
        if flag_gravity:
            for star in stars:
                dis = [star.pos[0]-self.pos[0], star.pos[1]-self.pos[1]]
                d = math.sqrt(dis[0]**2+dis[1]**2)
                if d <= 2:
                    d = 2
                f = (G/(d**2))*star.mass
                fx += f*(dis[0]/d)
                fy += f*(dis[1]/d)
        self.verb = (self.verb[0]+fx/60,
                     self.verb[1]+fy/60)
        self.verb = (self.verb[0]*0.996,
                     self.verb[1]*0.996)
        # 逐帧计算速度

    def update_pos(self):
        # self.pos = (self.pos[0] + self.verb[0]/60,
        #             self.pos[1] + self.verb[1]/60)
        if self.verb != (0, 0) and self.verb[1] != 0:
            ang = math.atan(self.verb[0]/self.verb[1])*(180/math.pi)
            self.angle = ang if self.verb[1] <= 0 else ang + 180
        # 逐帧计算位置，并重新定位方向

    def jet(self):
        if self.timer == 0:
            self.isjet = True
            self.image = 'rocket_withfire'
            self.timer = self.cd_jet
            if self.verb != (0, 0) and self.verb[1] != 0:
                ang = math.atan(self.verb[0]/self.verb[1])*(180/math.pi)
                self.angle = ang if self.verb[1] <= 0 else ang + 180
            clock.schedule_unique(self.stop_jet, 2)
        # 实现喷气

    def shoot(self, rel, stars):
        if self.timer == 0:
            self.verb = (self.verb[0]+40*rel[0], self.verb[1]+40*rel[1])
            pos = (self.pos[0]-40*rel[0], self.pos[1]-40*rel[1])
            verb = (-300*rel[0], -300*rel[1])
            c = (244, 244, 244)
            bullet = Star(pos, verb, 5, c, bullet=True)
            stars.append(bullet)
            self.timer = self.cd_shoot
        # 实现子弹

    def stop_jet(self):
        self.isjet = False
        if self.image == 'rocket_withfire':
            self.image = 'rocket'
        if self.verb != (0, 0) and self.verb[1] != 0:
            ang = math.atan(self.verb[0]/self.verb[1])*(180/math.pi)
            self.angle = ang if self.verb[1] <= 0 else ang + 180
        # 实现停止喷气

    def check_points(self):
        ang_r = self.angle*(math.pi/180)
        check_points = [(self.pos[0]-math.sin(ang_r+self.crusharea[0][1])*self.crusharea[0][0],
                         self.pos[1]-math.cos(ang_r+self.crusharea[0][1])*self.crusharea[0][0]),
                        (self.pos[0]-math.sin(ang_r+self.crusharea[1][1])*self.crusharea[1][0],
                         self.pos[1]-math.cos(ang_r+self.crusharea[1][1])*self.crusharea[1][0]),
                        (self.pos[0]-math.sin(ang_r+self.crusharea[2][1])*self.crusharea[2][0],
                         self.pos[1]-math.cos(ang_r+self.crusharea[2][1])*self.crusharea[2][0])]
        return check_points

    def is_collide(self, star):
        check_points = self.check_points()
        dis = map(lambda x: (star.pos[0]-x[0], star.pos[1]-x[1]),
                  check_points)
        d = map(lambda x: math.sqrt(x[0]**2+x[1]**2), dis)
        return any((x <= star.radium for x in d))
        # 判断是否碰撞

    def crush(self):
        self.image = 'crushed_rocket'
        play('crushed', 1)
        # 变成碰坏的形态


class Boss(Actor):
    '''
    用于储存boss的类
    '''

    def __init__(self, image, pos, **kwargs):
        super().__init__(image, pos=pos, **kwargs)
        self.li = [5, 5, 5]
        self.attack_time = 8
        self.timer = self.attack_time
        self.move = [0, 0]
        self.crusharea = ((-170, -140), (-25, 25), (140, 170))

    def set_image(self):
        image = 'boss'
        for i in range(3):
            if self.li[i]:
                image += str(i+1)
        self.image = image
        if image == 'boss':
            self.die()
        # 设置图像

    def update(self):
        self.timer -= 1/60
        if self.move[1] > 0:
            self.pos = (self.pos[0]+self.move[0], self.pos[1])
            self.move[1] -= 1/60
        elif self.move[1] < 0:
            self.move = [0, 0]
        elif random.randint(0, 360) == 0:
            move = random.randint(-400, 400)/10
            time = random.randint(20, 50)/10
            self.move = [move, time]
        if self.pos[0] <= 0.2*WIDTH:
            self.pos = (0.2*WIDTH, self.pos[1])
        elif self.pos[0] >= 0.8*WIDTH:
            self.pos = (0.8*WIDTH, self.pos[1])
        self.set_image()
        # 随机移动

    def is_co_bu(self, bullet):
        delta_x = bullet.pos[0]-self.pos[0]
        delta_y = bullet.pos[1]-self.pos[1]
        if -175 <= delta_x <= 175 and\
           -62+abs(delta_x)*0.13 <= delta_y <= 62-abs(delta_x)*0.2:
            if self.crusharea[0][0] <= delta_x <= self.crusharea[0][1] and\
               self.li[0]:
                self.li[0] -= 1
                return 1
            elif self.crusharea[1][0] <= delta_x <= self.crusharea[1][1] and\
                    self.li[1]:
                self.li[1] -= 1
                return 1
            elif self.crusharea[2][0] <= delta_x <= self.crusharea[2][1] and\
                    self.li[2]:
                self.li[2] -= 1
                return 1
            else:
                self.update()
                return 0
        else:
            return 0
        # 检测有没有打中：打中返回1 没有返回0

    def is_co_player(self, player):
        check_points = player.check_points()
        delta_xs = [x[0]-self.pos[0] for x in check_points]
        delta_ys = [x[1]-self.pos[1] for x in check_points]
        if any([-175 <= delta_x <= 175 and -62+abs(delta_x)*0.13 <= delta_y <= 62-abs(delta_x)*0.2
                for delta_x, delta_y in zip(delta_xs, delta_ys)]):
            return 1
        else:
            return 0
        # 检测是否碰撞玩家

    def is_co_star(self, star):
        delta_x = star.pos[0]-self.pos[0]
        delta_y = star.pos[1]-self.pos[1]
        r = star.radium
        if -175-r <= delta_x <= 175+r and\
           -62+abs(delta_x)*0.13-r <= delta_y <= 62-abs(delta_x)*0.2+r:
            return 1
        else:
            return 0
        # 检测是否碰到star

    def attack(self, player, stars):
        ran = random.randint(0, 100)
        if abs(self.timer) <= (ran/100) or self.timer <= -1:
            for i in range(len(self.li)):
                if self.li[i] != 0:
                    for j in range(1+sum(self.li)//4):
                        pos = (self.pos[0]+sum(self.crusharea[i])/2,
                               self.pos[1]+70+20*j)
                        dis = (player.pos[0]-pos[0], player.pos[1]-pos[1])
                        d = math.sqrt(dis[0]**2+dis[1]**2)
                        rel = (dis[0]/d, dis[1]/d)
                        verb = (rel[0]*250, rel[1]*250)
                        addStar(pos, verb, 10, stars)
            self.timer = self.attack_time - \
                len(list(filter(lambda x: x == 0, self.li[:])))
        # 攻击方式

    def die(self):
        animate(self, angle=180)


class Star():
    '''
    用于储存行星的类
    '''

    def __init__(self, pos, verb, radium, color, bullet=False):
        self.pos = pos
        self.verb = verb
        self.radium = radium
        self.mass = radium**3
        self.color = color
        self.bullet = bullet
        self.co_just_now = []

    def collide(self, other):
        if other not in [x[0] for x in self.co_just_now]:
            dis = (other.pos[0]-self.pos[0], other.pos[1]-self.pos[1])
            d = math.sqrt(dis[0]**2+dis[1]**2)
            if d <= 1:
                d = 1
            v1c = self.verb[0]*(dis[0]/d)+self.verb[1]*(dis[1]/d)
            v1p = self.verb[0]*(dis[1]/d)-self.verb[1]*(dis[0]/d)
            v2c = other.verb[0]*(dis[0]/d)+other.verb[1]*(dis[1]/d)
            v2p = other.verb[0]*(dis[1]/d)-other.verb[1]*(dis[0]/d)
            v1ce = ((self.mass-other.mass)*v1c+2*other.mass*v2c) / \
                (self.mass+other.mass)
            v2ce = ((other.mass-self.mass)*v2c+2*self.mass*v1c) / \
                (self.mass+other.mass)
            self.verb = (v1ce*(dis[0]/d)+v1p*(dis[1]/d),
                         v1ce*(dis[1]/d)-v1p*(dis[0]/d))
            other.verb = (v2ce*(dis[0]/d)+v2p*(dis[1]/d),
                          v2ce*(dis[1]/d)-v2p*(dis[0]/d))
            # 实现行星之间的碰撞
            self.co_just_now.append((other, 0.5))
            other.co_just_now.append((self, 0.5))
            # 记录刚刚碰撞过
        self.reset(other)

    def reset(self, other):
        dis = (other.pos[0]-self.pos[0], other.pos[1]-self.pos[1])
        d = math.sqrt(dis[0]**2+dis[1]**2)
        verb_help = (abs(self.verb[0])+abs(self.verb[1]) +
                     abs(other.verb[0])+abs(other.verb[1]))/30
        de = (self.radium+self.radium-d)/2 + 2
        if de >= 10 * verb_help and verb_help <= 5:
            deep = de + verb_help
        else:
            deep = de * 1.1
        if d <= 0.5:
            d = 0.5
        self.pos = (self.pos[0]-deep*(dis[0]/d)*other.mass/(2*(self.mass+other.mass)),
                    self.pos[1]-deep*(dis[1]/d)*other.mass/(2*(self.mass+other.mass)))
        other.pos = (other.pos[0]+deep*(dis[0]/d)*self.mass/(2*(self.mass+other.mass)),
                     other.pos[1]+deep*(dis[1]/d)*self.mass/(2*(self.mass+other.mass)))
        # 实现行星之间重置位置

    def update(self,player):
        self.pos = (self.pos[0] + self.verb[0]/60-player.verb[0]/60,
                    self.pos[1] + self.verb[1]/60-player.verb[1]/60)
        # 逐帧计算行星位置
        for row in self.co_just_now:
            if row[1] <= 0:
                self.co_just_now.remove(row)
            else:
                row = (row[0], row[1]-1/60)
        # 计时刚刚碰撞


def addStar(pos, verb, radium, stars):
    c = (random.randint(100, 255),
         random.randint(100, 255),
         random.randint(100, 255))
    star = Star(pos, verb, radium, c)
    stars.append(star)
    # 增加行星，用于命令行和ran_addStar


def ran_addStar(stars):
    radium = random.randint(20, 40)
    if random.randint(0, 1):
        verbx = random.randint(30, 200)
        verby = random.randint(int(verbx/10), 200)
        if random.randint(0, 1):
            pos = (0, random.randint(radium, HEIGHT-radium))
            verb = (verbx, verby)
        else:
            pos = (WIDTH, random.randint(radium, HEIGHT-radium))
            verb = (-1*verbx, verby)
    else:
        verby = random.randint(30, 200)
        verbx = random.randint(int(verby/10), 200)
        if random.randint(0, 1):
            pos = (random.randint(radium, WIDTH-radium), 0)
            verb = (verbx, verby)
        else:
            pos = (random.randint(radium, WIDTH-radium), HEIGHT)
            verb = (verbx, -1*verby)
    # 随机生成合理的位置和速度
    addStar(pos, verb, radium, stars)
    # 随机生成行星


# def reset_position(player, stars):
#     #feed_back = (abs(player.verb[0])+abs(player.verb[1]))/60
#     feed_back = (abs(player.verb[0])/60, abs(player.verb[1])/60)
#     if player.pos[0] < 0.4*WIDTH:
#         for star in stars:
#             star.pos = (star.pos[0]+feed_back[0], star.pos[1])
#         player.pos = (player.pos[0]+feed_back[0], player.pos[1])
#     if player.pos[0] > 0.6*WIDTH:
#         for star in stars:
#             star.pos = (star.pos[0]-feed_back[0], star.pos[1])
#         player.pos = (player.pos[0]-feed_back[0], player.pos[1])
#     if player.pos[1] < 0.4*HEIGHT:
#         for star in stars:
#             star.pos = (star.pos[0], star.pos[1]+feed_back[1])
#         player.pos = (player.pos[0], player.pos[1]+feed_back[1])
#     if player.pos[1] > 0.6*HEIGHT:
#         for star in stars:
#             star.pos = (star.pos[0], star.pos[1]-feed_back[1])
#         player.pos = (player.pos[0], player.pos[1]-feed_back[1])
#     # 用于使火箭处于大约中间


def play(file, loop):
    if os.path.realpath('')[-4:] == 'game':
        full_path = os.path.realpath('main\sounds\\'+file+'.mp3')
    else:
        full_path = os.path.realpath('sounds\\'+file+'.mp3')
    music.load(full_path)
    music.play(loop, 0.0)


def is_playing():
    return music.get_busy()
