import pygame
import os
import sys
import sqlite3


pygame.init()
size = width, height = 800, 800
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
pygame.display.set_caption('Kingdom Battles')


def change_move(player, mouse_pos):
    x, y = mouse_pos
    if x >= 0.85 * width and x <= width and y >= 0 and y <= 0.1 * height:
        conn = sqlite3.connect('plan.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE plan SET act_p = ? WHERE warrior = ?', (2, 'knight',))
        cursor.execute('UPDATE plan SET act_p = ? WHERE warrior = ?', (3, 'archer',))
        cursor.execute('UPDATE plan SET act_p = ? WHERE warrior = ?', (1, 'catapult',))
        conn.commit()
        conn.close()
        if player == 'red':
            return 'blue'
        return 'red'
    return player

def initialize_db():
    conn = sqlite3.connect('players_money.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS money (
            player TEXT NOT NULL,
            money TEXT NOT NULL
        )''')
    cursor.execute('INSERT INTO money (player, money) VALUES (?, ?)', ('red', 1750))
    cursor.execute('INSERT INTO money (player, money) VALUES (?, ?)', ('blue', 1750))
    conn.commit()
    conn.close()

def initialize_plan_db():
    conn = sqlite3.connect('plan.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plan (
            x TEXT NOT NULL,
            y TEXT NOT NULL,
            warrior TEXT NOT NULL,
            hp TEXT NOT NULL,
            act_p TEXT NOT NULL,
            state TEXT NOT NULL,
            player TEXT NOT NULL
        )''')
    for x in range(10):
        for y in range(10):
            cursor.execute('INSERT INTO plan (x, y, warrior, hp, act_p, state, player) VALUES (?, ?, ?, ?, ?, ?, ?)',
                           (x, y, 0, 0, 0, 0, 0))
    conn.commit()
    conn.close()

def get_money(player):
    conn = sqlite3.connect('players_money.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM money WHERE player = ?', (player,))
    m = cursor.fetchone()
    conn.close()
    return m

def money_changer(player, warrior):
    conn = sqlite3.connect('players_money.db')
    cursor = conn.cursor()

    cursor.execute('SELECT money FROM money WHERE player = ?', (player,))
    old_money = cursor.fetchone()

    if warrior == 'knight':
        value = -150
    elif warrior == 'archer':
        value = -200
    elif warrior == 'catapult':
        value = -300
    else:
        value = int(warrior)
    new_money = int(list(old_money)[0]) + value
    cursor.execute('UPDATE money SET money = ? WHERE player = ?', (new_money, player))

    conn.commit()
    conn.close()

def draw(left, top, width, height, player, cell_size):
    mm = min(left, top)
    font1 = pygame.font.Font(None, int(mm * 0.2))
    m1 = get_money(player)
    p1 = font1.render(m1[1], True, ('yellow'))
    screen.blit(p1, (mm * 0.35, height - mm * 0.35))
    AnimatedSprite(load_image('animated_knight_idle.png'), 4, 1, width / 2, height - b_top + 35, False, 0, cell_size * 4 / 3)
    AnimatedSprite(load_image('animated_archer_idle.png'), 4, 1, width / 2 + cell_size * 4 / 3, height - b_top + 35, False, 0,
                   cell_size * 4 / 3)
    AnimatedSprite(load_image('animated_catapult.png'), 5, 2, width / 2 + cell_size * 8 / 3, height - b_top + 35, False, -1,
                   cell_size * 4 / 3)
    intro_text = ['150', '200', '300']
    font = pygame.font.Font(None, int(0.2 * top))
    x, y = width / 2 + 1 / 4 * cell_size, height - 0.25 * top
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('yellow'))
        screen.blit(string_rendered, (x, y))
        x += cell_size * 4 / 3


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        if colorkey != 2:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

def check(mouse_pos, width, height, cell_size, player, b_top):
    x, y = mouse_pos
    current_money = int(get_money(player)[1])
    if x >= width / 2 and x <= width / 2 + cell_size * 4 / 3 and y >= height - b_top + 35 and y <= height:
        if current_money >= 150:
            return 'knight'
        else:
            return 0
    elif x >= width / 2 + cell_size * 4 / 3 and x <= width / 2 + cell_size * 8 / 3 and y >= height - b_top + 35 and y <= height:
        if current_money >= 200:
            return 'archer'
        else:
            return 0
    elif x >= width / 2 + cell_size * 8 / 3 and x <= width / 2 + cell_size * 12 / 3 and y >= height - b_top + 35 and y <= height:
        if current_money >= 300:
            return'catapult'
        else:
            return 0
    else:
        return 0


class Plan():

    def __init__(self):
        self.sp = [[0] * 10 for _ in range(10)]
        self.sp2 = [[0] * 10 for _ in range(10)]

    def set_value(self, warrior, cell_size, left, top, player, t):
        self.t = t
        self.cell_size = cell_size
        sz = self.cell_size
        self.left = left
        self.top = top
        self.warrior = warrior
        self.player = player

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if self.on_click(cell):
            return True
        return False

    def get_cell(self, mouse_pos):
        sz = self.cell_size
        x1, y1 = mouse_pos
        if x1 <= self.left or x1 >= self.left + 10 * sz or y1 <= self.top or y1 >= self.top + 10 * sz:
            return [-1, -1]
        else:
            for x in range(10):
                for y in range(10):
                    if x1 <= self.left + x * sz + sz and x1 >= self.left + x * sz and y1 <= self.top + y * sz + sz and y1 >= self.top + y * sz:
                        return [x, y]

    def on_click(self, n):
        conn = sqlite3.connect('plan.db')
        cursor = conn.cursor()
        x, y = n[0], n[1]
        if n != [-1, -1]:
            cursor.execute('SELECT warrior FROM plan WHERE x = ? AND y = ?', (str(x), str(y)))
            m = cursor.fetchone()
            if m[0] == '0':
                if self.warrior == 'knight':
                    self.hp = 30
                elif self.warrior == 'archer':
                    self.hp = 20
                elif self.warrior == 'catapult':
                    self.hp = 40
                if self.player == 'blue' and x >= 7 and x < 10:
                    cursor.execute('UPDATE plan SET warrior = ?, hp = ?, state = ?, player = ? WHERE x = ? AND y = ?',
                                   (self.warrior, self.hp, 'idle', 'blue', x, y))
                    self.t = 0
                    money_changer(self.player, self.warrior)
                    conn.commit()
                    conn.close()
                    return True
                elif self.player == 'red' and x >= 0 and x < 3:
                    cursor.execute('UPDATE plan SET warrior = ?, hp = ?, state = ?, player = ? WHERE x = ? AND y = ?',
                                   (self.warrior, self.hp, 'idle', 'red', x, y))
                    self.t = 0
                    money_changer(self.player, self.warrior)
                    conn.commit()
                    conn.close()
                    return True
                else:
                    conn.commit()
                    conn.close()
                    return False
        conn.commit()
        conn.close()
        return False

    def update(self, screen):
        conn = sqlite3.connect('plan.db')
        cursor = conn.cursor()
        sz = self.cell_size
        if self.t == 1:
            for x in range(10):
                for y in range(10):
                    cursor.execute('SELECT warrior FROM plan WHERE x = ? AND y = ?', (x, y,))
                    m1 = cursor.fetchone()
                    if m1[0] == '0':
                        if self.player == 'blue' and x >= 7:
                            pygame.draw.rect(screen, (0, 255, 0), (sz * x + self.left + 1, sz * y + self.top + 1, sz - 2, sz - 2), 0)
                        elif self.player == 'red' and x < 3:
                            pygame.draw.rect(screen, (0, 255, 0), (sz * x + self.left + 1, sz * y + self.top + 1, sz - 2, sz - 2), 0)

        cursor.execute('SELECT warrior, x, y, player, state FROM plan')
        m = cursor.fetchall()
        for warrior, x, y, player, state in m:
            x, y = int(x), int(y)
            if warrior == 'knight':
                if state == 'idle':
                    if player == 'blue':
                        if self.sp[y][x] >= 4:
                            self.sp[y][x] = 0
                        AnimatedSprite(load_image('animated_knight_idle.png'), 4, 1, sz * x + self.left,
                                       sz * y + self.top, True, self.sp[y][x], self.cell_size)
                        self.sp[y][x] += 1
                    else:
                        if self.sp[y][x] >= 4:
                            self.sp[y][x] = 0
                        AnimatedSprite(load_image('animated_knight_idle.png'), 4, 1, sz * x + self.left,
                                       sz * y + self.top, False, self.sp[y][x], self.cell_size)
                        self.sp[y][x] += 1
                elif state == 'attack':
                    if player == 'blue':
                        if self.sp2[y][x] >= 5:
                            self.sp2[y][x] = 0
                            cursor.execute('UPDATE plan SET state = ? WHERE x = ? and y = ?', ('idle', x, y,))
                        AnimatedSprite(load_image('animated_knight_attack.png'), 5, 1, sz * x + self.left,
                                       sz * y + self.top, True, self.sp2[y][x], self.cell_size)
                        self.sp2[y][x] += 1
                    else:
                        if self.sp2[y][x] >= 5:
                            self.sp2[y][x] = 0
                            cursor.execute('UPDATE plan SET state = ? WHERE x = ? and y = ?', ('idle', x, y,))
                        AnimatedSprite(load_image('animated_knight_attack.png'), 5, 1, sz * x + self.left,
                                       sz * y + self.top, False, self.sp2[y][x], self.cell_size)
                        self.sp2[y][x] += 1

                    self.sp[y][x] += 1
            elif warrior == 'archer':
                if player == 'blue':
                    if self.sp[y][x] >= 4:
                        self.sp[y][x] = 0
                    AnimatedSprite(load_image('animated_archer_idle.png'), 4, 1, sz * x + self.left, sz * y + self.top,
                                   False, self.sp[y][x], self.cell_size)
                    self.sp[y][x] += 1
                else:
                    if self.sp[y][x] >= 4:
                        self.sp[y][x] = 0
                    AnimatedSprite(load_image('animated_archer_idle.png'), 4, 1, sz * x + self.left, sz * y + self.top,
                                   True, self.sp[y][x], self.cell_size)
                    self.sp[y][x] += 1
            elif warrior == 'catapult':
                if state == 'idle':
                    if player == 'blue':
                        AnimatedSprite(load_image('animated_catapult.png'), 5, 2, sz * x + self.left, sz * y + self.top,
                                    True, -1, self.cell_size)
                    else:
                        AnimatedSprite(load_image('animated_catapult.png'), 5, 2, sz * x + self.left, sz * y + self.top,
                                    False, -1, self.cell_size)
                elif state == 'attack':
                    if player == 'blue':
                        if self.sp2[y][x] >= 10:
                            self.sp2[y][x] = 0
                            cursor.execute('UPDATE plan SET state = ? WHERE x = ? and y = ?', ('idle', x, y,))
                        AnimatedSprite(load_image('animated_catapult.png'), 5, 2, sz * x + self.left,
                                       sz * y + self.top, True, self.sp2[y][x], self.cell_size)
                        self.sp2[y][x] += 1
                    else:
                        if self.sp2[y][x] >= 10:
                            self.sp2[y][x] = 0
                            cursor.execute('UPDATE plan SET state = ? WHERE x = ? and y = ?', ('idle', x, y,))
                        AnimatedSprite(load_image('animated_catapult.png'), 5, 2, sz * x + self.left,
                                       sz * y + self.top, False, self.sp2[y][x], self.cell_size)
                        self.sp2[y][x] += 1
        conn.commit()
        conn.close()


class Grass(pygame.sprite.Sprite):
    grass = load_image("grass.jpg", 2)

    def __init__(self, x, y,  *group):
        super().__init__(*group)
        self.image = Grass.grass
        self.rect = self.image.get_rect()
        self.rect.x = self.rect[2] * x
        self.rect.y = self.rect[3] * y


class Money(pygame.sprite.Sprite):
    money = load_image('mainmoney.png', -1)

    def __init__(self, left, top, width, height, *group):
        super().__init__(*group)
        self.image = Money.money
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = height - min(left, top)
        self.mid = min(left, top)
        self.image = pygame.transform.scale(self.image, (self.mid, self.mid))


class Lowtab(pygame.sprite.Sprite):
    lowtab = load_image('прямоугольник.png', -1)

    def __init__(self, left, top, width, height, cell_size,  *group):
        super().__init__(*group)
        self.image = Lowtab.lowtab
        self.image = pygame.transform.rotate(self.image, 90)
        self.rect = self.image.get_rect()
        self.rect.x = width / 2 - cell_size * 5
        self.rect.y = height - min(left, top) + 15
        self.at = self.rect.h / self.rect.w
        self.image = pygame.transform.scale(self.image, (cell_size * 10, cell_size * 10 * self.at))


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30
        self.t1 = 0
        self.render_lowtab = False

    # настройка внешнего вида
    def set_view(self, left, top, cell_size, w, h):
        self.left = left
        self.top = top
        self.cell_size = cell_size
        self.screen_w = w
        self.screen_h = h

    def render(self, screen):
        sz = self.cell_size
        for x in range(self.width):
            for y in range(self.height):
                pygame.draw.rect(screen, (255, 255, 255), (sz * x + self.left, sz * y + self.top, sz, sz), 1)
                if self.t1 == 1:
                    conn = sqlite3.connect('plan.db')
                    cursor = conn.cursor()
                    cursor.execute('SELECT warrior, player FROM plan WHERE x = ? AND y = ?', (x, y,))
                    cell_state2 = cursor.fetchone()
                    if cell_state2[0] == '0' and abs(self.x - x) + abs(self.y - y) <= self.act_p:
                        pygame.draw.rect(screen, (0, 255, 0),
                                         (sz * x + self.left + 1, sz * y + self.top + 1, sz - 2, sz - 2), 0)
                    elif cell_state2[0] != '0' and self.player_now != cell_state2[1] and self.act_p >= 1:
                        if self.warrior == 'knight' and abs(self.x - x) + abs(self.y - y) <= self.act_p:
                            pygame.draw.rect(screen, (255, 0, 0),
                                         (sz * x + self.left + 1, sz * y + self.top + 1, sz - 2, sz - 2), 0)
                        elif self.warrior == 'catapult' and abs(self.x - x) + abs(self.y - y) <= self.act_p + 2:
                            pygame.draw.rect(screen, (255, 0, 0),
                                             (sz * x + self.left + 1, sz * y + self.top + 1, sz - 2, sz - 2), 0)
                        elif self.warrior == 'archer' and abs(self.x - x) + abs(self.y - y) <= self.act_p + 1:
                            pygame.draw.rect(screen, (255, 0, 0),
                                             (sz * x + self.left + 1, sz * y + self.top + 1, sz - 2, sz - 2), 0)
                    conn.commit()
                    conn.close()


        if self.render_lowtab:
            self.heart = load_image('pixel_heart.png')
            self.sword = load_image('pixel_sword.png')
            self.boots = load_image('pixel_boots.png')
            font1 = pygame.font.Font(None, int(self.cell_size * 1.2))
            sz = min(self.top * 0.8 // 3, self.cell_size * 1.25)
            sz_pic = min(self.top * 0.8, self.cell_size * 2)
            self.heart = pygame.transform.scale(self.heart, (sz, sz))
            self.sword = pygame.transform.scale(self.sword, (sz, sz))
            self.boots = pygame.transform.scale(self.boots, (sz, sz))
            if self.cell_state_lowtab[2] == 'knight':
                AnimatedSprite(load_image('animated_knight_idle.png'), 4, 1, self.screen_w / 2 - self.cell_size * 4.5,
                               self.screen_h - self.top * 0.8, False, 0, sz_pic)
                p2 = font1.render('10', True, ('white'))
            elif self.cell_state_lowtab[2] == 'archer':
                AnimatedSprite(load_image('animated_archer_idle.png'), 4, 1, self.screen_w / 2 - self.cell_size * 4.5,
                               self.screen_h - self.top * 0.8, False, 0, sz_pic)
                p2 = font1.render('15', True, ('white'))
            elif self.cell_state_lowtab[2] == 'catapult':
                AnimatedSprite(load_image('animated_catapult.png'), 5, 2, self.screen_w / 2 - self.cell_size * 4.5,
                               self.screen_h - self.top * 0.8, False, -1, sz_pic)
                p2 = font1.render('10', True, ('white'))
            screen.blit(self.heart, (self.screen_w / 2 - self.cell_size * 2.5, self.screen_h - self.top * 0.8))
            screen.blit(self.sword, (self.screen_w / 2 - self.cell_size * 2.5, self.screen_h - self.top * 0.8 * 2 / 3))
            screen.blit(self.boots, (self.screen_w / 2 - self.cell_size * 2.5, self.screen_h - self.top * 0.8 * 1 / 3))
            p1 = font1.render(self.cell_state_lowtab[3], True, ('white'))
            p3 = font1.render(self.cell_state_lowtab[4], True, ('white'))
            screen.blit(p1, (self.screen_w / 2 - self.cell_size * 1.25, self.screen_h - self.top * 0.8))
            screen.blit(p2, (self.screen_w / 2 - self.cell_size * 1.25, self.screen_h - self.top * 0.8 * 2 / 3))
            screen.blit(p3, (self.screen_w / 2 - self.cell_size * 1.25, self.screen_h - self.top * 0.8 * 1 / 3))

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if self.on_click(cell):
            return True
        else:
            return False

    def set_t1(self, t1, player):
        self.t1, self.player = t1, player

    def get_cell(self, mouse_pos):
        sz = self.cell_size
        x1, y1 = mouse_pos
        if x1 <= self.left or x1 >= self.left + self.width * sz or y1 <= self.top or y1 >= self.top + self.height * sz:
            return [-1, -1]
        else:
            for x in range(self.width):
                for y in range(self.height):
                    if x1 <= self.left + x * sz + sz and x1 >= self.left + x * sz and y1 <= self.top + y * sz + sz and y1 >= self.top + y * sz:
                        return [x, y]

    def on_click(self, n):
        conn = sqlite3.connect('plan.db')
        cursor = conn.cursor()
        x, y = n[0], n[1]

        if n != [-1, -1]:
            cursor.execute('SELECT * FROM plan WHERE x = ? AND y = ?', (x, y,))
            cell_state = cursor.fetchone()

            if cell_state[2] != '0':
                self.render_lowtab = True
                self.cell_state_lowtab = cell_state
            else:
                self.render_lowtab = False

            if cell_state[2] != '0' and cell_state[6] == self.player:
                self.act_p = int(cell_state[4])
                self.x, self.y, self.player_now, self.warrior = x, y, cell_state[6], cell_state[2]
                conn.commit()
                conn.close()
                return True

            elif self.t1 == 1:
                if cell_state[2] == '0' and abs(self.x - x) + abs(self.y - y) <= self.act_p:
                    cursor.execute('SELECT * FROM plan WHERE x = ? AND y = ?', (self.x, self.y,))
                    cell_state3 = cursor.fetchone()
                    cell_state3 = list(cell_state3)
                    cell_state3[4] = self.act_p - (abs(self.x - x) + abs(self.y - y))
                    cell_state3 = tuple(cell_state3)
                    cursor.execute('UPDATE plan SET warrior = ?, hp = ?, act_p = ?, state = ?,'
                                   ' player = ? WHERE x = ? AND y = ?', (cell_state3[2], cell_state3[3], cell_state3[4], cell_state3[5], cell_state3[6], x, y))
                    cursor.execute('UPDATE plan SET warrior = ?, hp = ?, act_p = ?, state = ?,'
                                   ' player = ? WHERE x = ? AND y = ?', (0, 0, 0, 0, 0, self.x, self.y))
                    conn.commit()
                    conn.close()
                    return False

                elif cell_state[2] != '0' and self.player_now != cell_state[6] and self.act_p >= 1:
                    cursor.execute('SELECT * FROM plan WHERE x = ? AND y = ?', (self.x, self.y,))
                    cell_state3 = cursor.fetchone()
                    cell_state3 = list(cell_state3)
                    cell_state3[4] = 0
                    cell_state3 = tuple(cell_state3)
                    if cell_state3[2] == 'knight' and abs(self.x - x) + abs(self.y - y) == 1:
                        new_hp = int(cell_state[3]) - 10
                        if new_hp <= 0:
                            if cell_state[2] == 'knight':
                                money_changer(self.player_now, 75)
                            elif cell_state[2] == 'archer':
                                money_changer(self.player_now, 100)
                            elif cell_state[2] == 'catapult':
                                money_changer(self.player_now, 150)
                            cursor.execute('UPDATE plan SET warrior = ?, hp = ?, act_p = ?, state = ?,'
                                           ' player = ? WHERE x = ? AND y = ?', (
                                           cell_state3[2], cell_state3[3], cell_state3[4], 'attack',
                                           cell_state3[6], x, y))
                            cursor.execute('UPDATE plan SET warrior = ?, hp = ?, act_p = ?, state = ?,'
                                           ' player = ? WHERE x = ? AND y = ?', (0, 0, 0, 0, 0, self.x, self.y))
                        else:
                            cursor.execute('UPDATE plan SET hp = ? WHERE x = ? and y = ?', (new_hp, x, y))
                            cursor.execute('UPDATE plan SET act_p = ?, state = ? WHERE x = ? and y = ?', (cell_state3[4], 'attack', self.x, self.y))

                    elif cell_state3[2] == 'archer' and abs(self.x - x) + abs(self.y - y) <= 2:
                        new_hp = int(cell_state[3]) - 15
                        if new_hp <= 0:
                            if cell_state[2] == 'knight':
                                money_changer(self.player_now, 75)
                            elif cell_state[2] == 'archer':
                                money_changer(self.player_now, 100)
                            elif cell_state[2] == 'catapult':
                                money_changer(self.player_now, 150)
                            cursor.execute('UPDATE plan SET warrior = ?, hp = ?, act_p = ?, state = ?,'
                                           ' player = ? WHERE x = ? AND y = ?', (0, 0, 0, 0, 0, x, y))
                        else:
                            cursor.execute('UPDATE plan SET hp = ? WHERE x = ? and y = ?', (new_hp, x, y))
                        cursor.execute('UPDATE plan SET act_p = ? WHERE x = ? and y = ?', (cell_state3[4], self.x, self.y))

                    elif cell_state3[2] == 'catapult' and abs(self.x - x) + abs(self.y - y) <= 3:
                        new_hp = int(cell_state[3]) - 10
                        if new_hp <= 0:
                            if cell_state[2] == 'knight':
                                money_changer(self.player_now, 75)
                            elif cell_state[2] == 'archer':
                                money_changer(self.player_now, 100)
                            elif cell_state[2] == 'catapult':
                                money_changer(self.player_now, 150)
                            cursor.execute('UPDATE plan SET warrior = ?, hp = ?, act_p = ?, state = ?,'
                                           ' player = ? WHERE x = ? AND y = ?', (0, 0, 0, 0, 0, x, y))
                        else:
                            cursor.execute('UPDATE plan SET hp = ? WHERE x = ? and y = ?', (new_hp, x, y))
                        cursor.execute('UPDATE plan SET act_p = ?, state = ? WHERE x = ? and y = ?', (cell_state3[4], 'attack', self.x, self.y))

                    conn.commit()
                    conn.close()
                    return False

            else:
                conn.commit()
                conn.close()
                return False
        else:
            self.render_lowtab = False
            conn.commit()
            conn.close()
            return False


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, reverse, frame, size):
        super().__init__(all_sprites2)
        self.frames = []
        self.size = size
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = frame
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.reverse = reverse
        if self.reverse == True:
            self.image = pygame.transform.flip(self.image, True, False)
        self.image = pygame.transform.scale(self.image, (self.size, self.size))

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.flip(self.image, True, False)

    def check(self):
        if self.frames[self.cur_frame] == self.frames[-1]:
            return False
        return True

def del_db():
    conn = sqlite3.connect('plan.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM plan')
    conn.commit()
    conn.close()
    conn = sqlite3.connect('players_money.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM money')
    conn.commit()
    conn.close()

def start_screen(width, height):
    intro_text = 'Kingdom Battles'

    fon = pygame.transform.scale(load_image('Title_image.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, int(height * 0.0875))
    string_rendered = font.render(intro_text, 1, pygame.Color('black'))
    screen.blit(string_rendered, (width * 0.25, height * 0.1))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                del_db()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return True
        if screen.get_size() != (width, height):
            width, height = screen.get_size()
            fon = pygame.transform.scale(load_image('Title_image.png'), (width, height))
            screen.blit(fon, (0, 0))
            font = pygame.font.Font(None, int(height * 0.0875))
            string_rendered = font.render(intro_text, 1, pygame.Color('black'))
            screen.blit(string_rendered, (width * 0.25, height * 0.1))
        pygame.display.flip()

def end_screen(width, height, text):
    intro_text = text
    another_txt = ['Нажмите Q, чтобы выйти из игры', 'Нажмите W, чтобы начать игру заново']

    fon = pygame.transform.scale(load_image('end_screen.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, int(height * 0.0875))
    string_rendered = font.render(intro_text, 1, pygame.Color('white'))
    screen.blit(string_rendered, (0.05 * width, height * 0.1))
    x, y = width * 0.15, height * 0.9
    font1 = pygame.font.Font(None, int(height * 0.05))

    for line in another_txt:
        string_rendered = font1.render(line, 1, pygame.Color('white'))
        screen.blit(string_rendered, (x, y))
        y += 0.05 * height


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                del_db()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == 113:
                    del_db()
                    pygame.quit()
                    sys.exit()
                if event.key == 119:
                    del_db()
                    initialize_db()
                    initialize_plan_db()
                    return 0
        if screen.get_size() != (width, height):
            width, height = screen.get_size()
            fon = pygame.transform.scale(load_image('end_screen.png'), (width, height))
            screen.blit(fon, (0, 0))
            font = pygame.font.Font(None, int(height * 0.0875))
            string_rendered = font.render(intro_text, 1, pygame.Color('white'))
            screen.blit(string_rendered, (0.05 * width, height * 0.1))
            x, y = width * 0.15, height * 0.9
            font1 = pygame.font.Font(None, int(height * 0.05))

            for line in another_txt:
                string_rendered = font1.render(line, 1, pygame.Color('white'))
                screen.blit(string_rendered, (x, y))
                y += 0.05 * height
        pygame.display.flip()


if __name__ == '__main__':
    initialize_db()
    initialize_plan_db()
    clock = pygame.time.Clock()

    cell_size = 0.0625 * min(width, height)
    b_left = (width / 2) - cell_size * 5
    b_top = (height / 2) - cell_size * 5

    board = Board(10, 10)
    board.set_view(b_left, b_top, cell_size, width, height)

    all_sprites = pygame.sprite.Group()
    for x in range(int(width / 400) + 1):
        for y in range(int(height / 400) + 1):
            Grass(x, y, all_sprites)

    all_money = pygame.sprite.Group()
    Money(b_left, b_top, width, height, all_money)

    low_tab = pygame.sprite.Group()
    Lowtab(b_left, b_top, width, height, cell_size, low_tab)

    card1 = load_image('прямоугольник.png', -1)
    card2 = load_image('прямоугольник.png', -1)
    card3 = load_image('прямоугольник.png', -1)
    card1 = pygame.transform.scale(card1, (cell_size * 4 / 3, b_top - 35))
    card2 = pygame.transform.scale(card2, (cell_size * 4 / 3, b_top - 35))
    card3 = pygame.transform.scale(card3, (cell_size * 4 / 3, b_top - 35))

    player = 'blue'
    turn = load_image('turn.png', -1)
    turn = pygame.transform.scale(turn, (0.15 * width, 0.1 * height))

    warrior, t, t1 = 0, 0, 0
    plan = Plan()
    plan.set_value(warrior, cell_size, b_left, b_top, player, t)
    board.set_t1(t1, player)

    pygame.mixer.music.load('music_for_game.mp3')
    pygame.mixer.music.play(-1)
    volume = 0.5
    pygame.mixer.music.set_volume(volume)
    sound1 = pygame.mixer.Sound('Meep-Merp-Sound-Effect.mp3')

    all_sprites2 = pygame.sprite.Group()

    turn_n = 0

    running = start_screen(width, height)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                del_db()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                p1 = player
                player = change_move(player, event.pos)
                if p1 != player:
                    t, warrior, t1 = 0, 0, 0
                    board.set_t1(t1, player)
                    plan.set_value(warrior, cell_size, b_left, b_top, player, t)
                    turn_n += 1
                if t == 1:
                    if plan.get_click(event.pos):
                        t = 0
                if board.get_click(event.pos):
                    t1 = 1
                    board.set_t1(t1, player)
                else:
                    t1 = 0
                    board.set_t1(t1, player)
                warrior = check(event.pos, width, height, cell_size, player, b_top)
                if warrior != 0:
                    t, t1 = 1, 0
                    board.set_t1(t1, player)
                    plan.set_value(warrior, cell_size, b_left, b_top, player, t)
                if warrior == 0 and t == 0 and t1 == 0 and player == change_move(player, event.pos):
                    sound1.play()
            if event.type == pygame.KEYDOWN:
                if event.key == 49:
                    volume -= 0.1
                    pygame.mixer.music.set_volume(volume)
                elif event.key == 50:
                    volume += 0.1
                    pygame.mixer.music.set_volume(volume)
                elif event.key == 51:
                    if volume != 0:
                        volume = 0
                    else:
                        volume = 0.5
                    pygame.mixer.music.set_volume(volume)

        if screen.get_size() != (width, height):
            all_sprites2 = pygame.sprite.Group()
            width, height = screen.get_size()
            cell_size = 0.0625 * min(width, height)
            b_left = (width / 2) - cell_size * 5
            b_top = (height / 2) - cell_size * 5
            board.set_view(b_left, b_top, cell_size, width, height)

            for x in range(int(width / 400) + 1):
                for y in range(int(height / 400) + 1):
                    Grass(x, y, all_sprites)

            all_money = pygame.sprite.Group()
            Money(b_left, b_top, width, height, all_money)

            low_tab = pygame.sprite.Group()
            Lowtab(b_left, b_top, width, height, cell_size, low_tab)

            card1 = pygame.transform.scale(card1, (cell_size * 4 / 3, b_top - 35))
            card2 = pygame.transform.scale(card2, (cell_size * 4 / 3, b_top - 35))
            card3 = pygame.transform.scale(card3, (cell_size * 4 / 3, b_top - 35))

            turn = pygame.transform.scale(turn, (0.15 * width, 0.1 * height))

            plan.set_value(warrior, cell_size, b_left, b_top, player, t)

        screen.fill((0, 0, 0))
        all_sprites2 = pygame.sprite.Group()
        all_sprites.draw(screen)
        all_money.draw(screen)
        low_tab.draw(screen)
        screen.blit(turn, (width * 0.85, 0))
        pygame.draw.rect(screen, player, (0, 0, 0.1 * width, 0.05 * height))
        plan.update(screen)
        screen.blit(card1, (width / 2, height - b_top + 35))
        screen.blit(card2, (width / 2 + cell_size * 4 / 3, height - b_top + 35))
        screen.blit(card3, (width / 2 + cell_size * 4 / 3 * 2, height - b_top + 35))
        draw(b_left, b_top, width, height, player, cell_size)
        board.render(screen)
        clock.tick(6)
        all_sprites2.draw(screen)

        if turn_n >= 2:
            conn = sqlite3.connect('plan.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM plan WHERE player = ?', ('blue',))
            bl = cursor.fetchall()
            cursor.execute('SELECT * FROM plan WHERE player = ?', ('red',))
            rd = cursor.fetchall()
            if rd == [] and bl == []:
                txt = 'Ничья'
                t1, t, turn_n, player = 0, 0, 0, 'blue'
                end_screen(width, height, txt)
            elif bl == []:
                txt = 'Победили Красные'
                t1, t, turn_n, player = 0, 0, 0, 'blue'
                end_screen(width, height, txt)
            elif rd == []:
                txt = 'Победили Синие'
                t1, t, turn_n, player = 0, 0, 0, 'blue'
                end_screen(width, height, txt)
        pygame.display.flip()