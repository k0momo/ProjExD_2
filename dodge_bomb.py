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
    # 画面の境界を超えないかチェック
    yoko = 0 <= obj_rct.left and obj_rct.right <= WIDTH
    tate = 0 <= obj_rct.top and obj_rct.bottom <= HEIGHT
    return yoko, tate 

#追加機能1
# ゲームオーバー画面を表示する関数
def game_over(screen: pg.Surface, bg: pg.Surface, kk_gameover: pg.Surface) -> None:
    """画面を半透明で暗転し、泣き顔こうかとんと
    “Game Over” を5秒間表示して終了する。"""
    ovl = pg.Surface((WIDTH, HEIGHT))
    ovl.set_alpha(180)
    ovl.fill((0, 0, 0))
    screen.blit(bg, (0, 0))
    screen.blit(ovl, (0, 0))

    font = pg.font.SysFont(None, 64)
    txt  = font.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(txt, txt_rct)

    margin = 45                        
    y_pos  = txt_rct.centery            

    left_rct = kk_gameover.get_rect(center=(txt_rct.left - margin, y_pos))
    screen.blit(kk_gameover, left_rct)
    
    right_rct  = kk_gameover.get_rect(center=(txt_rct.right + margin, y_pos))
    screen.blit(kk_gameover, right_rct)
        
    pg.display.update()
    time.sleep(5)
    
#追加機能2
# 爆弾画像と速度テーブルを初期化する関数
def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """半径10→55 の10段階爆弾 Surface と速度テーブルを返す"""
    imgs, accs = [], []
    # 半径10から55まで5ずつ増やして画像を作成
    for i in range(10):
        r = 10 + 5*i                
        img = pg.Surface((r*2, r*2))
        pg.draw.circle(img, (255, 0, 0), (r, r), r)
        img.set_colorkey((0, 0, 0))
        imgs.append(img)
        # 速度は半径の2倍に設定
        accs.append(5 + i)           
    return imgs, accs

# 追加機能3
# こうかとん画像を8方向に対応させて辞書で返す関数
def load_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """8 方向ベクトルに対応するこうかとん画像 Surface を辞書で返す。"""
    base = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    dct: dict[tuple[int, int], pg.Surface] = {(0, 0): base}
    # このfor文は、8方向の角度とベクトルを対応させる。
    # 90度、-90度、180度、45度、-45度、135度、-135度の角度で回転させた画像を作成
    for ang, vec in zip((90, -90, 180, 45, -45, 135, -135),
                        [(-5, 0), (5, 0), (0, 5), (-5, -5),
                         (5, -5), (-5, 5), (5, 5)]):
        dct[vec] = pg.transform.rotate(base, ang)
    return dct

# 移動量 mv に最も近い方向のこうかとん画像を返す。
def get_kk_img(mv: tuple[int, int],
               dct: dict[tuple[int, int], pg.Surface]
              ) -> pg.Surface | None:
    """移動量 mv に最も近い方向画像を返す。mv が (0,0) なら None。"""
    if mv == (0, 0):
        return None
    # ベクトルの大きさを計算
    best = max(dct.keys(), key=lambda v: v[0]*mv[0] + v[1]*mv[1])
    return dct[best]    

#追加機能４
# 爆弾の向きを計算し、長さ √50 に正規化したベクトルを返す。
def calc_orientation(org: pg.Rect, dst: pg.Rect,
                     cur_v: tuple[int, int] = (0, 0)
                    ) -> tuple[int, int]:
    """
    org(爆弾)→dst(こうかとん) への差ベクトルを長さ √50 に正規化。
    距離が 300 未満なら cur_v をそのまま返し慣性を持たせる。
    """
    dx, dy = dst.centerx - org.centerx, dst.centery - org.centery
    dist = math.hypot(dx, dy) 
    # 距離が 300 未満なら慣性を持たせる
    if dist < 300 or dist == 0:
        return cur_v 
    # 距離が 300 以上なら、dx, dy を長さ √50 に正規化
    # 50 は爆弾の移動速度の基準値
    scale = (50 ** 0.5) / dist
    return (int(dx * scale), int(dy * scale))

#独自機能２
# 生存フレーム数を秒換算して右上に描画する関数
def draw_timer(screen: pg.Surface, tmr: int) -> None:
    """
    生存フレーム tmr を秒換算し、右上に “Time: xx” と描画する。
    tmr : int
        経過フレーム数（1 フレーム ≒ 0.02 秒）
    """
    font = pg.font.SysFont(None, 40)
    # フレーム数を秒に換算（50 フレームで 1 秒）
    sec  = tmr // 50                 
    # 秒数を描画
    txt  = font.render(f"Time: {sec}", True, (0, 0, 0))
    screen.blit(txt, (WIDTH - 150, 10))

#独自機能１
# タイトル画面を表示し、SPACE キーが押されるまで待機する関数
def title_screen(screen: pg.Surface, bg: pg.Surface) -> None:
    """
    起動時にタイトルを表示し、SPACE キーが押されるまで待機する。
    """
    font = pg.font.SysFont(None, 100)
    msg  = font.render("Mr. Fushimi, press the SPACE!!", True, (0, 0, 255))
    msg_r = msg.get_rect(center=(WIDTH//2, HEIGHT//2))
    # 背景画像を読み込み
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit(); sys.exit()
            # SPACE キーが押されたらループを抜ける    
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
      
    # こうかとんの初期位置を設定  
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
    # こうかとんの泣き顔画像を読み込み
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
            # キーが押されている場合、移動量を加算
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        kk_rct.move_ip(sum_mv)
        # 練習3
        # 画面外に出ないように調整
        yoko, tate = check_bound(kk_rct)
        if not yoko: 
            kk_rct.move_ip(-sum_mv[0], 0)
        if not tate: 
            kk_rct.move_ip(0, -sum_mv[1])
            
        # 追加機能3
        # 移動量に応じてこうかとんの画像を更新
        new_img = get_kk_img(tuple(sum_mv), kk_imgs)
        if new_img:
            kk_img = new_img
            
        # 追加機能4
        # 爆弾の向きを計算し、長さ √50 に正規化
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))    
        
        #練習2
        bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko: 
            vx *= -1
        if not tate: 
            vy *= -1
        
        #追加機能２
        # 爆弾の半径に応じて画像と速度を選択
        bb_idx = min(tmr // 500, 9)          
        bb_img = bb_imgs[bb_idx]
        speed  = bb_accs[bb_idx]

        # 爆弾の移動速度を正規化
        if vx or vy:
            scale = speed / math.hypot(vx, vy)
            vx, vy = int(vx*scale), int(vy*scale)
        # 爆弾の位置を更新    
        bb_rct = bb_img.get_rect(center=bb_rct.center)
        
        # 練習4
        # こうかとんと爆弾が衝突したらゲームオーバー
        if kk_rct.colliderect(bb_rct):
            # 追加機能1
            game_over(screen, bg_img, kk_cry)
            return
        
        screen.blit(kk_img, kk_rct)
        screen.blit(bb_img, bb_rct)
        
        #独自機能２
        # 生存フレーム数を秒換算して右上に描画
        draw_timer(screen, tmr)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
