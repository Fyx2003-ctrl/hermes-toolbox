"""内置简笔画角色生成器：根据关键词生成二次元风格简笔画 (RGBA 透明底)。

用法:
    from character_gen import generate_character
    img = generate_character("miku")          # 初音未来风格
    img = generate_character("kurumi")        # 时崎狂三风格
    img = generate_character("blonde", hair=(255, 220, 90))  # 自定义发色

预设角色:
    miku    初音未来: 青色双马尾 + 蓝色大眼睛
    kurumi  时崎狂三: 黑发+红色双马尾 + 红金异色瞳
    blonde  金发双马尾: 金发 + 蓝色眼睛 (默认)
    sakura  粉发少女: 粉色长发 + 绿色眼睛
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw

SKIN = (255, 224, 214)      # 肤色
WHITE = (255, 255, 255, 255)

PRESETS = {
    "miku":   dict(hair=(0, 200, 200), hair2=(0, 230, 230), eye=(40, 160, 255),
                   eye2=(40, 160, 255), ribbon=(255, 120, 150), top=(40, 40, 60)),
    "kurumi": dict(hair=(30, 30, 40), hair2=(200, 40, 60), eye=(255, 80, 60),
                   eye2=(255, 200, 60), ribbon=(20, 20, 30), top=(60, 20, 30)),
    "blonde": dict(hair=(255, 215, 110), hair2=(255, 230, 160), eye=(60, 140, 255),
                   eye2=(60, 140, 255), ribbon=(255, 100, 140), top=(80, 120, 200)),
    "sakura": dict(hair=(255, 170, 200), hair2=(255, 200, 225), eye=(90, 220, 150),
                   eye2=(90, 220, 150), ribbon=(255, 120, 170), top=(255, 190, 210)),
}


def _ellipse(d: ImageDraw.ImageDraw, cx, cy, rx, ry, fill, outline=None, width=1):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill, outline=outline, width=width)


def generate_character(name: str = "miku", size: int = 320) -> Image.Image:
    """生成一个简笔画少女角色，返回 RGBA 图片 (宽约 size, 高约 size*1.35)。"""
    name = (name or "blonde").strip().lower()
    # 支持 "初音未来" / "miku" / "miku.png" 等写法
    for key in PRESETS:
        if key in name or name in key:
            name = key
            break
    else:
        name = "blonde"
    p = PRESETS[name]

    W = size
    H = int(size * 1.35)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    cx = W / 2
    # ---- 头发后层 (长发/双马尾, 在身体后面) ----
    twin = (name == "miku" or name == "kurumi")   # 双马尾
    # 后发 (头后大块)
    d.polygon([(cx - 78, 70), (cx - 60, 205), (cx + 60, 205), (cx + 78, 70)], fill=p["hair"] + (255,))
    if twin:
        # 双马尾: 左右两条大飘带
        _ellipse(d, cx - 95, 150, 42, 105, p["hair"] + (255,))
        _ellipse(d, cx + 95, 150, 42, 105, p["hair2"] + (255,))
        # 马尾尾端蝴蝶结
        _ellipse(d, cx - 95, 245, 16, 10, p["ribbon"] + (255,))
        _ellipse(d, cx + 95, 245, 16, 10, p["ribbon"] + (255,))
    else:
        # 长直发: 两侧长发
        _ellipse(d, cx - 80, 150, 34, 95, p["hair"] + (255,))
        _ellipse(d, cx + 80, 150, 34, 95, p["hair2"] + (255,))

    # ---- 身体/衣服 ----
    d.polygon([(cx - 62, 208), (cx - 52, H - 8), (cx + 52, H - 8), (cx + 62, 208)], fill=p["top"] + (255,))
    # 领口
    d.polygon([(cx - 30, 208), (cx, 242), (cx + 30, 208)], fill=WHITE)
    d.line([(cx - 30, 208), (cx, 242), (cx + 30, 208)], fill=(0, 0, 0, 60), width=3)
    # 蝴蝶结 (胸前)
    _ellipse(d, cx - 16, 255, 15, 9, p["ribbon"] + (255,))
    _ellipse(d, cx + 16, 255, 15, 9, p["ribbon"] + (255,))
    _ellipse(d, cx, 255, 8, 8, (240, 60, 110, 255))

    # ---- 头 ----
    _ellipse(d, cx, 88, 62, 58, SKIN + (255,))           # 脸
    # 脖子
    d.rectangle([cx - 10, 140, cx + 10, 172], fill=SKIN + (255,))
    # ---- 刘海/前发 ----
    d.pieslice([cx - 70, 30, cx + 70, 130], 180, 360, fill=p["hair"] + (255,))  # 头顶
    # 刘海锯齿
    d.polygon([(cx - 62, 52), (cx - 40, 96), (cx - 24, 55)], fill=p["hair"] + (255,))
    d.polygon([(cx - 30, 55), (cx - 6, 100), (cx + 8, 55)], fill=p["hair"] + (255,))
    d.polygon([(cx + 2, 55), (cx + 26, 96), (cx + 44, 52)], fill=p["hair"] + (255,))
    # 侧发
    d.rectangle([cx - 66, 80, cx - 46, 118], fill=p["hair"] + (255,))
    d.rectangle([cx + 46, 80, cx + 66, 118], fill=p["hair2"] + (255,))
    # 头顶呆毛
    d.arc([cx - 14, 18, cx + 14, 42], 200, 340, fill=p["hair"] + (255,), width=7)

    # ---- 眼睛 (大眼睛) ----
    _ellipse(d, cx - 26, 92, 16, 19, WHITE)
    _ellipse(d, cx + 26, 92, 16, 19, WHITE)
    _ellipse(d, cx - 26, 95, 12, 15, p["eye"] + (255,))
    _ellipse(d, cx + 26, 95, 12, 15, p["eye2"] + (255,))
    _ellipse(d, cx - 24, 93, 5, 7, (20, 20, 30, 255))    # 瞳孔
    _ellipse(d, cx + 28, 93, 5, 7, (20, 20, 30, 255))
    _ellipse(d, cx - 29, 89, 5, 4, WHITE)                # 高光
    _ellipse(d, cx + 23, 89, 5, 4, WHITE)
    # 眉毛
    d.arc([cx - 44, 72, cx - 10, 92], 200, 340, fill=(90, 60, 60, 255), width=4)
    d.arc([cx + 10, 72, cx + 44, 92], 200, 340, fill=(90, 60, 60, 255), width=4)
    # 腮红
    _ellipse(d, cx - 46, 108, 12, 6, (255, 130, 150, 120))
    _ellipse(d, cx + 46, 108, 12, 6, (255, 130, 150, 120))
    # 嘴
    d.arc([cx - 8, 104, cx + 8, 118], 20, 160, fill=(180, 80, 90, 255), width=3)

    return img


def save_character(name: str, path: str, size: int = 320) -> str:
    img = generate_character(name, size)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    img.save(path)
    return path


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "miku"
    out = sys.argv[2] if len(sys.argv) > 2 else f"assets/{target}.png"
    save_character(target, out)
    print(f"saved {out}")
