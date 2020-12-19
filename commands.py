import pgzrun
import random
import math
import time
from game_objects import Player, Star, addStar, reset_position, ran_addStar
from config import WIDTH, HEIGHT, G
'''
此文档用于写调试代码
调试方法：在游戏中摁'`'键，然后输入命令
'''


def check_commands(command, stars, mouse_position):
    c_l = command.split(' ')
    if c_l[0] == 'addStar' or c_l[0] == 'addstar':
        try:
            radium = c_l[3]
        except IndexError:
            radium = 25
        try:
            verb = c_l[2]
        except IndexError:
            verb = (0, 0)
        try:
            pos = c_l[1]
        except IndexError:
            pos = mouse_position
        addStar(pos, verb, radium, stars)
        return 1
    elif c_l[0] == 'quit' or c_l[0] == 'q':
        return 1
    else:
        return 0
