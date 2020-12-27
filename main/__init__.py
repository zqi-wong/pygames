import pgzrun
import random
import math
import time
from game_objects import Player, Star, addStar, ran_addStar, Boss, play, is_playing
from commands import check_commands
from config import WIDTH, HEIGHT, G, upgrade_bin, boss_score, gravity_score


def bg_restart():
    bg_center = Actor('background')
    bg_up = Actor('background')
    bg_down = Actor('background')
    bg_left = Actor('background')
    bg_right = Actor('background')
    bg_lu = Actor('background')
    bg_ru = Actor('background')
    bg_ld = Actor('background')
    bg_rd = Actor('background')
    bgs = [bg_lu, bg_up, bg_ru, bg_left,
           bg_center, bg_right, bg_ld, bg_down, bg_rd]
    bg_center.bgpos = [WIDTH/2, HEIGHT/2]
    bg_up.bgpos = [WIDTH/2, HEIGHT/2+bg_center.height]
    bg_down.bgpos = [WIDTH/2, HEIGHT/2-bg_center.height]
    bg_left.bgpos = [WIDTH/2-bg_center.width, HEIGHT/2]
    bg_right.bgpos = [WIDTH/2+bg_center.width, HEIGHT/2]
    bg_lu.bgpos = [WIDTH/2-bg_center.width, HEIGHT/2+bg_center.height]
    bg_ld.bgpos = [WIDTH/2-bg_center.width, HEIGHT/2-bg_center.height]
    bg_ru.bgpos = [WIDTH/2+bg_center.width, HEIGHT/2+bg_center.height]
    bg_rd.bgpos = [WIDTH/2+bg_center.width, HEIGHT/2-bg_center.height]
    return bgs


def restart():
    global game_stop, flag_gravity, debug_mode, upgrading_timer, stars, mouse_position, player, timer, boss_mode, intro, bgs
    game_stop = 0
    flag_gravity = False
    debug_mode = False
    boss_mode = False
    intro = False
    stars = []
    timer = 0
    upgrading_timer = upgrade_bin
    player = Player('rocket', pos=(WIDTH/2, HEIGHT/2))
    play('deepspacetravels', -1)
    bgs = bg_restart()
    # 用于重新开始


restart()


def draw():
    global flag_gravity
    screen.clear()
    for bg in bgs:
        bg.pos = bg.bgpos[0], bg.bgpos[1]
        bg.draw()
    screen.draw.text('next jet:{:.2f}\nscore:{:.1f}'.format(
        player.timer, player.score), (2*WIDTH/3, 100))
    for star in stars:
        screen.draw.filled_circle(star.pos, star.radium, star.color)
    player.draw()
    if boss_mode:
        boss.draw()
        screen.draw.text(' '.join(list(map(str, boss.li))), boss.pos)
    # 画行星和火箭

    if mouse_position:
        screen.draw.line(player.pos, mouse_position, (204, 204, 204))
    # 画喷气线

    if game_stop == 1:
        msg = "                WAIT!!!!\n" +\
              "        Is  that  too  easy  to  you?\n" +\
              "Now  somethings  challenging  is  coming!"
        screen.draw.text(msg, (WIDTH/2-100, HEIGHT/2-100))
    elif debug_mode:
        msg = "Debuging……"
        screen.draw.text(msg, (WIDTH/2-100, HEIGHT/2-100))
    elif game_stop == 2:
        msg = "Here  comes  the  GRAVITY!"
        screen.draw.text(msg, (WIDTH/2-100, HEIGHT/2-100))
    elif game_stop == 3:
        msg = "GAME  OVER\nyour score is {:.1f}\n".format(player.score)
        msg += "press 'c' to exit\npress 'r' to restart"
        screen.draw.text(msg, (WIDTH/2-100, HEIGHT/2-100))
    elif game_stop == 4:
        msg = "Now you can upgrade one of you skill:\n"
        msg += "press SPACE to stronger your jet\n"
        msg += "press X to shooter the cd of shooting"
        screen.draw.text(msg, (WIDTH/2-100, HEIGHT/2-100))
    elif game_stop == 5:
        msg = "Press SPACE to jet\nPress X to shoot"
        screen.draw.text(msg, (WIDTH/2-100, HEIGHT/2-100))
    # 一些特殊停止记号


def update():
    global timer, flag_gravity, game_stop, debug_mode, upgrading_timer, boss_mode, boss, gravity_score, intro
    if not is_playing():
        if game_stop == 3:
            play('game_over', -1)
        else:
            play('deepspacetravels', -1)
    # 音乐相关

    if keyboard.BACKQUOTE:
        debug_mode = 1
        while True:
            command = input("input your command\ninput 'quit' to quit\n")
            ret = check_commands(command, stars, mouse_position, player)
            if ret == 1:
                break
            elif ret == 2:
                game_stop = 4
                break
    if keyboard.Z:
        debug_mode = 0
    # 命令行

    if keyboard.C and game_stop == 3:
        exit()
    if keyboard.R and game_stop == 3:
        restart()
    # 退出游戏

    if keyboard.X and game_stop == 4:
        player.cd_shoot = player.cd_shoot * \
            0.6 if player.cd_shoot >= 1.5 else 0.5*(player.cd_shoot+0.5)
        player.timer = 0.1
        game_stop = 0
    elif keyboard.SPACE and game_stop == 4:
        player.cd_jet = player.cd_jet-0.2 if player.cd_jet >= 2.1 else player.cd_jet
        player.jet_strength += 0.6
        player.timer = 0.1
        game_stop = 0
    if player.score >= upgrading_timer:
        game_stop = 4
        upgrading_timer += upgrade_bin
    # 实现升级

    if timer >= 1 and not intro:
        intro = True
        game_stop = 5
    if (keyboard.X or keyboard.SPACE) and game_stop == 5:
        game_stop = 0
    # 引入介绍

    if game_stop or debug_mode:
        return None
    # 特殊停止

    timer += 1/60
    player.score += 1/500
    # reset_position(player, stars)
    # 调节大致处于屏幕中央

    bg_move()
    # 移动背景

    if player.score >= boss_score and not boss_mode:
        boss = Boss('boss123', (WIDTH/2, 100))
        boss_mode = True
        animate(player,pos=(WIDTH/2, HEIGHT*0.7))
    # 生成boss

    n = (WIDTH+HEIGHT)/2000
    if random.randint(0, (240-int(math.atan(timer)*(400/math.pi)/n))) == 0:
        ran_addStar(stars, timer)
    # 随机生成星体

    for star in stars:
        star.update(player)
        if any((star.pos[0] <= -3*WIDTH, star.pos[0] >= 4*WIDTH,
                star.pos[1] <= -3*HEIGHT, star.pos[1] >= 4*HEIGHT)):
            stars.remove(star)
    rel = count_rel(player, mouse_position)
    player.update_verb(stars, flag_gravity, rel)
    player.update_pos()
    if boss_mode:  # boss相关
        boss.update()
        boss.attack(player, stars)
    # 计算位置和速度

    for bullet in [x for x in stars if x.bullet]:
        for star in stars:
            if star == bullet:
                continue
            dis = (bullet.pos[0]-star.pos[0],
                   bullet.pos[1]-star.pos[1])
            d = math.sqrt(dis[0]**2+dis[1]**2)
            if d <= star.radium+bullet.radium:
                stars.remove(bullet)
                stars.remove(star)
                player.score += 5-star.radium/10
        if boss_mode:  # boss相关
            if boss.is_co_bu(bullet):
                stars.remove(bullet)
    # 实现子弹功能 和 子弹攻击boss功能

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
        if player.is_collide(star) and (not player.WHOSYOURDADDY):
            player.crush()
            game_stop = 3
    if boss_mode:  # boss相关
        for star in [star for star in filter(lambda x: x.bullet == False, stars)]:
            if boss.is_co_star(star):
                stars.remove(star)
        if boss.is_co_player(player) and (not player.WHOSYOURDADDY):
            player.crush()
            game_stop = 3
    # 检测碰撞

    if keyboard.SPACE:
        player.jet()
    elif keyboard.X:
        mel = count_rel(player, mouse_position)
        player.shoot(mel, stars)
    if player.timer > 0:
        player.timer -= 1/60
    elif player.timer < 0:
        player.timer = 0
    # 检测喷火

    if flag_gravity == False and player.score >= gravity_score:
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
    player.timer = 0
    # 以上两个函数用于增加重力


def on_mouse_move(pos):
    global mouse_position
    mouse_position = pos


def count_rel(player, mouse_position):
    a = (player.pos[0]-mouse_position[0],
         player.pos[1]-mouse_position[1])
    le = math.sqrt(a[0]**2+a[1]**2)
    if le <= 0.1:
        le = 0.1
    rel = (a[0]/le, a[1]/le)  # 以鼠标方向为喷气方向
    return rel
    # 计算鼠标方向


def bg_move():
    # if player.pos[0] < 0.41*WIDTH or player.pos[0] > 0.59*WIDTH or player.pos[1] < 0.41*HEIGHT or player.pos[1] > 0.59*HEIGHT:
    #     for i in bgs:
    #         i.bgpos[0] -= player.verb[0]/40
    #         i.bgpos[1] -= player.verb[1]/40
    # else:
    #     for i in bgs:
    #         i.bgpos[0] -= player.verb[0]/120
    #         i.bgpos[1] -= player.verb[1]/120
    for i in bgs:
        i.bgpos[0] -= player.verb[0]/60
        i.bgpos[1] -= player.verb[1]/60
    if bgs[4].bgpos[0] > WIDTH/2+bgs[4].width:
        for i in bgs:
            i.bgpos[0] -= bgs[4].width
    if bgs[4].bgpos[0] < WIDTH/2-bgs[4].width:
        for i in bgs:
            i.bgpos[0] += bgs[4].width
    if bgs[4].bgpos[1] > HEIGHT/2+bgs[4].height:
        for i in bgs:
            i.bgpos[1] -= bgs[4].height
    if bgs[4].bgpos[1] < HEIGHT/2-bgs[4].height:
        for i in bgs:
            i.bgpos[1] += bgs[4].height


# def on_key_down(key):
#     print(key)


pgzrun.go()
