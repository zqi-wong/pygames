import pgzrun
from pgzero.actor import Actor
from pgzero.clock import clock
from pgzero.game import exit
import math
import random
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
        self.cd_shoot = 6
        self.crusharea = ((9, 0), (28, 2.747), (28, -2.474))
        # 极坐标下的碰撞监测点
        self.WHOSYOURDADDY = False

    def update_verb(self, stars, flag_gravity, rel):
        fx = 13*((self.jet_strength*self.timer)**2)*rel[0] if self.isjet else 0
        fy = 13*(self.timer**2)*rel[1] if self.isjet else 0  # 喷汽部分
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
        self.pos = (self.pos[0] + self.verb[0]/60,
                    self.pos[1] + self.verb[1]/60)
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

    def is_collide(self, star):
        ang_r = self.angle*(math.pi/180)
        check_points = [(self.pos[0]-math.sin(ang_r+self.crusharea[0][1])*self.crusharea[0][0],
                         self.pos[1]-math.cos(ang_r+self.crusharea[0][1])*self.crusharea[0][0]),
                        (self.pos[0]-math.sin(ang_r+self.crusharea[1][1])*self.crusharea[1][0],
                         self.pos[1]-math.cos(ang_r+self.crusharea[1][1])*self.crusharea[1][0]),
                        (self.pos[0]-math.sin(ang_r+self.crusharea[2][1])*self.crusharea[2][0],
                         self.pos[1]-math.cos(ang_r+self.crusharea[2][1])*self.crusharea[2][0])]
        dis = map(lambda x: (star.pos[0]-x[0], star.pos[1]-x[1]),
                  check_points)
        d = map(lambda x: math.sqrt(x[0]**2+x[1]**2), dis)
        return any((x <= star.radium for x in d))
        # 判断是否碰撞

    def crush(self):
        self.image = 'crushed_rocket'
        # 变成碰坏的形态


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

    def update(self):
        self.pos = (self.pos[0] + self.verb[0]/60,
                    self.pos[1] + self.verb[1]/60)
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


def reset_position(player, stars):
    feed_back = (abs(player.verb[0])+abs(player.verb[1]))/60
    if player.pos[0] < 0.15*WIDTH:
        for star in stars:
            star.pos = (star.pos[0]+feed_back, star.pos[1])
        player.pos = (player.pos[0]+feed_back, player.pos[1])
    if player.pos[0] > 0.85*WIDTH:
        for star in stars:
            star.pos = (star.pos[0]-feed_back, star.pos[1])
        player.pos = (player.pos[0]-feed_back, player.pos[1])
    if player.pos[1] < 0.15*HEIGHT:
        for star in stars:
            star.pos = (star.pos[0], star.pos[1]+feed_back)
        player.pos = (player.pos[0], player.pos[1]+feed_back)
    if player.pos[1] > 0.85*HEIGHT:
        for star in stars:
            star.pos = (star.pos[0], star.pos[1]-feed_back)
        player.pos = (player.pos[0], player.pos[1]-feed_back)
    # 用于使火箭处于大约中间
