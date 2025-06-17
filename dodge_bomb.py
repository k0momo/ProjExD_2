import os
import sys
import pygame as pg
import random
import time
import math


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

#追加機能1
def game_over(screen: pg.Surface, bg: pg.Surface, kk_gameover: pg.Surface) -> None:
    """画面を半透明で暗転し、泣き顔こうかとんと
    “Game Over” を5秒間表示して終了する。"""
    ovl = pg.Surface((WIDTH, HEIGHT))
    ovl.set_alpha(150)
    ovl.fill((0, 0, 0))
    screen.blit(bg, (0, 0))
    screen.blit(ovl, (0, 0))

    g_rct = kk_gameover.get_rect(center=(WIDTH//2, HEIGHT//2-40))
    screen.blit(kk_gameover, g_rct)

    font = pg.font.SysFont(None, 120)
    txt = font.render("Game Over", True, (255, 0, 0))
    txt_rct = txt.get_rect(center=(WIDTH//2, HEIGHT//2+120))
    screen.blit(txt, txt_rct)
    pg.display.update()
    time.sleep(5)
    
#追加機能2
def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """半径10→55 の10段階爆弾 Surface と速度テーブルを返す"""
    imgs, accs = [], []
    for i in range(10):
        r = 10 + 5*i                
        img = pg.Surface((r*2, r*2))
        pg.draw.circle(img, (255, 0, 0), (r, r), r)
        img.set_colorkey((0, 0, 0))
        imgs.append(img)
        accs.append(5 + i)           
    return imgs, accs

# 追加機能3
def load_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    base = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    dct: dict[tuple[int, int], pg.Surface] = {(0, 0): base}
    for ang, vec in zip((90, -90, 180, 45, -45, 135, -135),
                        [(-5, 0), (5, 0), (0, 5), (-5, -5),
                         (5, -5), (-5, 5), (5, 5)]):
        dct[vec] = pg.transform.rotate(base, ang)
    return dct

def get_kk_img(mv: tuple[int, int],
               dct: dict[tuple[int, int], pg.Surface]
              ) -> pg.Surface | None:
    if mv == (0, 0):
        return None
    best = max(dct.keys(), key=lambda v: v[0]*mv[0] + v[1]*mv[1])
    return dct[best]    

#追加機能４
def calc_orientation(org: pg.Rect, dst: pg.Rect,
                     cur_v: tuple[int, int] = (0, 0)
                    ) -> tuple[int, int]:
    """
    org(爆弾)→dst(こうかとん) への差ベクトルを長さ √50 に正規化。
    距離が 300 未満なら cur_v をそのまま返し慣性を持たせる。
    """
    dx, dy = dst.centerx - org.centerx, dst.centery - org.centery
    dist = math.hypot(dx, dy)
    if dist < 300 or dist == 0:
        return cur_v
    scale = (50 ** 0.5) / dist
    return (int(dx * scale), int(dy * scale))

#独自機能１
def title_screen(screen: pg.Surface, bg: pg.Surface) -> None:
    """
    起動時にタイトルを表示し、SPACE キーが押されるまで待機する。
    """
    font = pg.font.SysFont(None, 100)
    msg  = font.render("Press SPACE to Start", True, (0, 0, 255))
    msg_r = msg.get_rect(center=(WIDTH//2, HEIGHT//2))
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit(); sys.exit()
            if e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                return                     
        screen.blit(bg, (0, 0))
        screen.blit(msg, msg_r)
        pg.display.update()

def main() -> None:
    """ゲーム本体ループ。初期化後、60FPSで更新を続ける。"""
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")  
    
    #独自機能１
    title_screen(screen, bg_img)
    
    #追加機能３
    kk_imgs = load_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
      
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    #練習2
    #追加機能２
    bb_imgs, bb_accs = init_bb_imgs()
    bb_idx = 0
    bb_img = bb_imgs[bb_idx]                    
    bb_rct = bb_img.get_rect(
        center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
    vx, vy = +5, +5
    
    # 追加機能1
    kk_cry = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9) 
    
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
        if not yoko: 
            kk_rct.move_ip(-sum_mv[0], 0)
        if not tate: 
            kk_rct.move_ip(0, -sum_mv[1])
            
        # 追加機能3
        new_img = get_kk_img(tuple(sum_mv), kk_imgs)
        if new_img:
            kk_img = new_img
            
        # 追加機能4
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))    
        
        #練習2
        bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko: 
            vx *= -1
        if not tate: 
            vy *= -1
        
        #追加機能２
        bb_idx = min(tmr // 500, 9)          
        bb_img = bb_imgs[bb_idx]
        speed  = bb_accs[bb_idx]

        if vx or vy:
            scale = speed / math.hypot(vx, vy)
            vx, vy = int(vx*scale), int(vy*scale)
            
        bb_rct = bb_img.get_rect(center=bb_rct.center)
        
        # 練習4
        if kk_rct.colliderect(bb_rct):
            # 追加機能1
            game_over(screen, bg_img, kk_cry)
            return
        
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
