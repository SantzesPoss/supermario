import asyncio
import math
import random
import pygame

# Original platform adventure, inspired by classic side-scrolling games.
pygame.init()
W, H = 960, 540
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption('Pixel Jump Adventure')
clock = pygame.time.Clock()
FONT = pygame.font.Font(None, 32)
BIG = pygame.font.Font(None, 72)
SMALL = pygame.font.Font(None, 23)
SKY = (123, 206, 245)
GROUND = (91, 174, 78)
BROWN = (151, 91, 55)

levels = [
    dict(width=2300, platforms=[(260,390,170,24),(570,330,170,24),(900,380,190,24),(1270,315,190,24),(1610,365,200,24)],
         gaps=[(740,850),(1490,1590)], coins=[(310,345),(620,285),(950,335),(1320,270),(1690,320),(1980,415)], enemies=[(470,448),(1130,448),(1830,448)]),
    dict(width=2750, platforms=[(230,390,150,24),(510,325,170,24),(810,275,160,24),(1110,365,200,24),(1480,310,190,24),(1860,345,200,24),(2250,300,180,24)],
         gaps=[(700,800),(1360,1460),(2100,2200)], coins=[(280,345),(570,280),(860,230),(1160,320),(1540,265),(1910,300),(2300,255)], enemies=[(420,448),(1000,448),(1750,448),(2470,448)]),
    dict(width=3100, platforms=[(240,380,170,24),(540,310,180,24),(870,360,180,24),(1190,280,170,24),(1530,350,200,24),(1900,290,170,24),(2230,370,200,24),(2630,305,180,24)],
         gaps=[(750,850),(1400,1510),(2110,2210),(2470,2570)], coins=[(290,335),(590,265),(920,315),(1240,235),(1580,305),(1950,245),(2280,325),(2680,260)], enemies=[(440,448),(1080,448),(1800,448),(2390,448),(2880,448)])
]

level_index = 0
score = 0
lives = 3
state = 'menu'
pressed = {'left':False, 'right':False, 'jump':False}
player = pygame.Rect(75, 380, 34, 44)
vy = 0
on_ground = False
camera = 0
coins_left = []
enemies = []
invuln = 0
jump_lock = False


def reset_level():
    global player, vy, camera, coins_left, enemies, invuln, on_ground, jump_lock
    player = pygame.Rect(75, 380, 34, 44)
    vy = 0
    camera = 0
    on_ground = False
    jump_lock = False
    invuln = 70
    d = levels[level_index]
    coins_left = [pygame.Rect(x, y, 22, 22) for x,y in d['coins']]
    enemies = [{'rect':pygame.Rect(x,y,34,32), 'x':float(x), 'dir':1 if i%2 else -1, 'start':x} for i,(x,y) in enumerate(d['enemies'])]


def restart():
    global level_index, score, lives, state
    level_index, score, lives, state = 0, 0, 3, 'play'
    reset_level()


def ground_rects():
    d = levels[level_index]
    gaps = sorted(d['gaps'])
    start = 0
    result = []
    for a,b in gaps:
        if a>start: result.append(pygame.Rect(start,480,a-start,60))
        start = b
    if start < d['width']: result.append(pygame.Rect(start,480,d['width']-start,60))
    result += [pygame.Rect(*r) for r in d['platforms']]
    return result


def hurt():
    global lives, state
    lives -= 1
    if lives <= 0: state = 'lost'
    else: reset_level()


def update():
    global vy, on_ground, score, level_index, state, camera, invuln, jump_lock
    if state != 'play': return
    if invuln: invuln -= 1
    dx = (int(pressed['right'])-int(pressed['left']))*5
    player.x += dx
    player.x = max(0, min(player.x, levels[level_index]['width']-player.width))
    if pressed['jump'] and on_ground and not jump_lock:
        vy = -13.5
        on_ground = False
        jump_lock = True
    if not pressed['jump']: jump_lock = False
    prev_bottom = player.bottom
    vy = min(15, vy+0.65)
    player.y += round(vy)
    on_ground = False
    if vy >= 0:
        for platform in ground_rects():
            if player.colliderect(platform) and prev_bottom <= platform.top+10:
                player.bottom = platform.top
                vy = 0
                on_ground = True
                break
    if player.top > H+90:
        hurt()
        return
    for c in coins_left[:]:
        if player.colliderect(c):
            coins_left.remove(c)
            score += 10
    for enemy in enemies[:]:
        enemy['x'] += enemy['dir']*1.55
        if abs(enemy['x']-enemy['start'])>85: enemy['dir'] *= -1
        enemy['rect'].x = round(enemy['x'])
        if player.colliderect(enemy['rect']):
            if vy>1 and prev_bottom <= enemy['rect'].top+15:
                enemies.remove(enemy)
                vy = -9
                score += 25
            elif not invuln:
                hurt()
                return
    if player.right >= levels[level_index]['width']-70:
        score += 100
        if level_index == len(levels)-1:
            state = 'won'
        else:
            level_index += 1
            reset_level()
        return
    camera = max(0, min(levels[level_index]['width']-W, player.centerx-W//3))


def text(s, x, y, font=FONT, color=(255,255,255)):
    screen.blit(font.render(str(s), True, color), (x,y))


def draw():
    screen.fill(SKY)
    for i in range(9):
        x = (i*370-camera*.22)% (W+300)-130
        pygame.draw.ellipse(screen,(237,248,255),(x,85+(i%3)*37,120,38))
        pygame.draw.ellipse(screen,(237,248,255),(x+25,64+(i%3)*37,70,50))
    for i in range(12):
        x = (i*280-camera*.45)%(W+350)-180
        pygame.draw.ellipse(screen,(84,188,132),(x,375,310,175))
    if state in ('menu','lost','won'):
        title = {'menu':'PIXEL JUMP','lost':'GAME OVER','won':'YOU WIN!'}[state]
        text(title, W//2-BIG.size(title)[0]//2, 125, BIG, (35,65,92))
        subtitle = '3 levels  |  coins  |  enemies  |  checkpoints' if state=='menu' else f'Final score: {score}'
        text(subtitle,W//2-FONT.size(subtitle)[0]//2,215,FONT,(35,65,92))
        text('Press ENTER or tap START',W//2-155,285,FONT,(35,65,92))
        pygame.draw.rect(screen,(33,115,91),(W//2-105,340,210,65),border_radius=16)
        text('START',W//2-42,359)
        return
    for rect in ground_rects():
        r = rect.move(-camera,0)
        if r.right < 0 or r.left > W: continue
        pygame.draw.rect(screen,BROWN,r,border_radius=3)
        pygame.draw.rect(screen,GROUND,(r.x,r.y,r.width,11),border_radius=3)
        for x in range(r.x+12,r.right,36):
            pygame.draw.rect(screen,(177,113,70),(x,r.y+25,15,6),border_radius=3)
    for c in coins_left:
        x,y = c.centerx-camera,c.centery
        pygame.draw.circle(screen,(241,171,22),(x,y),12)
        pygame.draw.circle(screen,(255,232,80),(x,y),9)
        pygame.draw.line(screen,(230,155,15),(x,y-5),(x,y+5),3)
    for e in enemies:
        r=e['rect'].move(-camera,0)
        pygame.draw.ellipse(screen,(137,62,143),r)
        pygame.draw.circle(screen,(255,255,255),(r.x+11,r.y+12),5)
        pygame.draw.circle(screen,(255,255,255),(r.x+25,r.y+12),5)
        pygame.draw.circle(screen,(28,30,48),(r.x+12,r.y+12),2)
        pygame.draw.circle(screen,(28,30,48),(r.x+26,r.y+12),2)
    if invuln%8<5:
        p=player.move(-camera,0)
        pygame.draw.rect(screen,(30,82,175),(p.x+4,p.y+19,26,25),border_radius=5)
        pygame.draw.rect(screen,(245,173,106),(p.x+7,p.y+8,21,17),border_radius=6)
        pygame.draw.rect(screen,(221,66,55),(p.x+3,p.y+2,29,10),border_radius=4)
        pygame.draw.rect(screen,(250,250,250),(p.x+22,p.y+13,5,5))
    finish_x=levels[level_index]['width']-62-camera
    pygame.draw.line(screen,(60,64,76),(finish_x,290),(finish_x,480),6)
    pygame.draw.polygon(screen,(249,213,57),[(finish_x,292),(finish_x+65,311),(finish_x,334)])
    pygame.draw.rect(screen,(22,49,78),(0,0,W,58))
    text(f'LEVEL {level_index+1}/3',20,15)
    text(f'SCORE {score}',230,15)
    text(f'LIVES {lives}',430,15)
    text('MOVE: arrows/A D   JUMP: Space/W/Up',620,19,SMALL)
    # Touch controls: left, right, jump
    for rect,label in [(pygame.Rect(22,420,78,80),'◀'),(pygame.Rect(111,420,78,80),'▶'),(pygame.Rect(W-112,420,90,80),'JUMP')]:
        s=pygame.Surface(rect.size,pygame.SRCALPHA)
        pygame.draw.rect(s,(20,46,70,115),s.get_rect(),border_radius=17)
        screen.blit(s,rect.topleft)
        f=SMALL if label=='JUMP' else FONT
        text(label,rect.centerx-f.size(label)[0]//2,rect.centery-f.get_height()//2,f)


def touch(x,y,down):
    global state
    if state!='play':
        if down: restart()
        return
    if 22<=x<=100 and 420<=y<=500: pressed['left']=down
    if 111<=x<=189 and 420<=y<=500: pressed['right']=down
    if W-112<=x<=W-22 and 420<=y<=500: pressed['jump']=down


async def main():
    global state
    reset_level()
    running=True
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE: running=False
                if state!='play' and event.key in (pygame.K_RETURN,pygame.K_SPACE): restart()
                if event.key in (pygame.K_LEFT,pygame.K_a): pressed['left']=True
                if event.key in (pygame.K_RIGHT,pygame.K_d): pressed['right']=True
                if event.key in (pygame.K_UP,pygame.K_w,pygame.K_SPACE): pressed['jump']=True
            elif event.type==pygame.KEYUP:
                if event.key in (pygame.K_LEFT,pygame.K_a): pressed['left']=False
                if event.key in (pygame.K_RIGHT,pygame.K_d): pressed['right']=False
                if event.key in (pygame.K_UP,pygame.K_w,pygame.K_SPACE): pressed['jump']=False
            elif event.type==pygame.MOUSEBUTTONDOWN:
                touch(*event.pos,True)
            elif event.type==pygame.MOUSEBUTTONUP:
                pressed['left']=pressed['right']=pressed['jump']=False
            elif event.type==pygame.FINGERDOWN:
                touch(event.x*W,event.y*H,True)
            elif event.type==pygame.FINGERUP:
                pressed['left']=pressed['right']=pressed['jump']=False
        update()
        draw()
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    pygame.quit()

asyncio.run(main())
