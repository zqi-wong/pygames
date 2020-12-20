import pgzrun
import random
import math
import time
from game_objects import Player, Star, addStar, reset_position, ran_addStar
from commands import check_commands
from config import WIDTH, HEIGHT, G


game_stop = 0
flag_gravity = False
debug_mode = False
stars = []
mouse_position = ()
timer = 0
player = Player('rocket', pos=(600, 400))


def draw():
    global flag_gravity
    screen.clear()
    screen.fill((30, 30, 30))
    screen.draw.text('next jet:{:.2f}'.format(player.timer), (800, 100))
    for star in stars:
        screen.draw.filled_circle(star.pos, star.radium, star.color)
    player.draw()
    # 画行星和火箭

    if mouse_position:
        screen.draw.line(player.pos, mouse_position, (204, 204, 204))
    # 画喷气线

    if game_stop == 1:
        msg = "                WAIT!!!!\n" +\
              "        Is  that  too  easy  to  you?\n" +\
              "Now  somethings  challenging  is  coming!"
        screen.draw.text(msg, (400, 300))
    elif game_stop == 2:
        msg = "Here  comes  the  GRAVITY!"
        screen.draw.text(msg, (400, 300))
    elif game_stop == 3:
        msg = "GAME  OVER\npress 'c' to exit\npress 'r' to restart"
        screen.draw.text(msg, (400, 300))
    elif debug_mode:
        msg = "Debuging……"
        screen.draw.text(msg, (400, 300))
    # 一些特殊停止记号


def update():
    global timer, flag_gravity, game_stop, debug_mode
    if keyboard.BACKQUOTE:
        debug_mode = 1
        while True:
            command = input("input your command\ninput 'quit' to quit\n")
            if check_commands(command, stars, mouse_position):
                break
    if keyboard.Z:
        debug_mode = 0
    # 命令行

    if keyboard.C and game_stop == 3:
        exit()
    if keyboard.R and game_stop == 3:
        restart()
    # 退出游戏

    if game_stop or debug_mode:
        return None
    # 特殊停止

    timer += 1/60
    reset_position(player, stars)
    # 调节大致处于屏幕中央

    if random.randint(0, 240-int(math.atan(timer)*(360/math.pi))) == 0:
        ran_addStar(stars)
    # 随机生成星体

    for star in stars:
        star.update()
        if any((star.pos[0] <= -3*WIDTH, star.pos[0] >= 4*WIDTH,
                star.pos[1] <= -3*HEIGHT, star.pos[1] >= 4*HEIGHT)):
            stars.remove(star)
    a = (player.pos[0]-mouse_position[0],
         player.pos[1]-mouse_position[1])
    le = math.sqrt(a[0]**2+a[1]**2)
    if le <= 0.1:
        le = 0.1
    rel = (a[0]/le, a[1]/le)  # 以鼠标方向为喷气方向
    player.update_verb(stars, flag_gravity, rel)
    player.update_pos()
    # 计算位置和速度

    for i in range(len(stars)):
        for j in range(len(stars)):
            if i == j:
                continue
            dis = (stars[j].pos[0]-stars[i].pos[0],
                   stars[j].pos[1]-stars[i].pos[1])
            d = math.sqrt(dis[0]**2+dis[1]**2)
            if d <= stars[i].radium+stars[j].radium:
                stars[i].collide(stars[j])
    for star in stars:
        if player.is_collide(star):
            player.crush()
            game_stop = 3
    # 检测碰撞

    if keyboard.SPACE:
        player.jet()
    if player.timer > 0:
        player.timer -= 1/60
    elif player.timer < 0:
        player.timer = 0
    # 检测喷火

    if flag_gravity == False and timer >= 30:
        flag_gravity = True
        game_stop = 1
        clock.schedule(set_game_stop2, 4.0)
    # 增加重力


def set_game_stop2():
    global game_stop
    game_stop = 2
    clock.schedule(set_game_stop0, 2.0)


def set_game_stop0():
    global game_stop
    game_stop = 0
    # 以上两个函数用于增加重力


def on_mouse_move(pos):
    global mouse_position
    mouse_position = pos


def restart():
    global game_stop, flag_gravity, debug_mode, stars, mouse_position, player, timer
    game_stop = 0
    flag_gravity = False
    debug_mode = False
    stars = []
    timer = 0
    player = Player('rocket', pos=(600, 400))


# def on_key_down(key):
#     print(key)


pgzrun.go()
