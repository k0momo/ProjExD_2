import os
import sys
import pygame as pg
import random


WIDTH, HEIGHT = 1100, 650
# 練習1
DELTA = {pg.K_UP:(0, -5), pg.K_DOWN:(0,5), pg.K_LEFT:(-5,0), pg.K_RIGHT:(5,0)}

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 練習3
def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：obj_rct ...こうかとんRect または 爆弾Rect
    戻り値：（横方向が画面内か、縦方向が画面内か）
    """
    yoko = 0 <= obj_rct.left and obj_rct.right <= WIDTH
    tate = 0 <= obj_rct.top and obj_rct.bottom <= HEIGHT
    return yoko, tate 

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    #練習2
    bb_img = pg.Surface((20, 20))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)   
    bb_img.set_colorkey((0, 0, 0))                      
    bb_rct = bb_img.get_rect(
        center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
    vx, vy = +5, +5
    
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
            
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        #練習1
        for k, mv in DELTA.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        kk_rct.move_ip(sum_mv)
        # 練習3
        yoko, tate = check_bound(kk_rct)
        if not yoko: kk_rct.move_ip(-sum_mv[0], 0)
        if not tate: kk_rct.move_ip(0, -sum_mv[1])
        
        #練習2
        bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko: vx *= -1
        if not tate: vy *= -1
        
        screen.blit(kk_img, kk_rct)
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
