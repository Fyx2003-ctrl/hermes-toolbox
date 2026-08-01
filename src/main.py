"""二次元角色粒子系统 — 粒子汇聚成角色 + 呼吸/流光 + 鼠标交互 + 爆炸消散。

用法:
    python main.py                          # 默认角色: 初音未来
    python main.py --character kurumi       # 时崎狂三
    python main.py --image 某图片.png        # 任意图片 → 粒子角色
    python main.py --particles 20000        # 粒子数量
    python main.py --fullscreen             # 全屏
    python main.py --demo                   # 无头自动演示 (输出截图到 shots/, 用于验证)

操作:
    移动鼠标    — 粒子被推开 (波纹涟漪)
    左键点击    — 角色爆炸成满天粒子, 再自动重组
    右键点击    — 立即重组
    ESC         — 退出
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import time

import numpy as np
import pygame

from character_gen import generate_character

# ---------------- 状态 ----------------
ASSEMBLE = 0      # 汇聚
IDLE = 1          # 成型 (呼吸/流光)
BURST = 2         # 爆炸消散

# ---------------- 图片预处理 ----------------
def auto_clean(img, tolerance=48):
    """自动去除纯色背景(角落色)并紧致裁剪, 返回 RGBA 图。"""
    from PIL import Image
    img = img.convert("RGBA")
    arr = np.array(img)
    h, w = arr.shape[:2]
    # 角落颜色 = 背景参考
    corners = np.concatenate([
        arr[:4, :4, :3].reshape(-1, 3), arr[:4, -4:, :3].reshape(-1, 3),
        arr[-4:, :4, :3].reshape(-1, 3), arr[-4:, -4:, :3].reshape(-1, 3)])
    bg = corners.mean(axis=0)
    rgb = arr[..., :3].astype(np.int16)
    dist = np.abs(rgb - bg).sum(axis=2)
    arr[..., 3][dist < tolerance] = 0          # 背景 → 透明
    img = Image.fromarray(arr)
    bbox = img.getbbox()                        # 紧致裁剪掉空白边缘
    if bbox:
        img = img.crop(bbox)
    return img

# ---------------- 粒子系统 ----------------
class ParticleField:
    def __init__(self, img, screen, max_particles=18000):
        self.screen = screen
        self.sw, self.sh = screen.get_size()
        self.max_particles = max_particles

        # ---- 采样图片 -> 粒子目标位置与颜色 ----
        xs, ys, colors, sw_, sh_ = self._sample(img, max_particles)
        self.n = len(xs)

        # 角色居中, 高度占屏幕 72% (注意: 用采样后的尺寸!)
        target_h = self.sh * 0.72
        scale = target_h / max(sh_, 1)
        ox = (self.sw - sw_ * scale) / 2
        oy = (self.sh - sh_ * scale) / 2

        self.tx = xs.astype(np.float32) * scale + ox      # 目标 x
        self.ty = ys.astype(np.float32) * scale + oy      # 目标 y
        self.colors = colors.astype(np.float32)           # (n,3)

        # 粒子大小: 由图片面积 / 粒子数决定, 限制在 1.5~4
        area = sw_ * sh_ * scale * scale
        self.base_size = float(np.clip(math.sqrt(area / max(self.n, 1)) * 0.9, 1.5, 4.0))

        # 动态状态
        rng = np.random.default_rng()
        self.x = rng.uniform(0, self.sw, self.n).astype(np.float32)
        self.y = rng.uniform(0, self.sh, self.n).astype(np.float32)
        self.vx = np.zeros(self.n, dtype=np.float32)
        self.vy = np.zeros(self.n, dtype=np.float32)
        self.phase = rng.uniform(0, 2 * math.pi, self.n).astype(np.float32)   # 每粒子随机相位
        self.delay = (rng.uniform(0, 1, self.n) ** 1.5).astype(np.float32)    # 汇聚延迟 (波浪式)

        self.state = ASSEMBLE
        self.t = 0.0            # 状态内计时
        self.burst_time = 0.0

        # 中心点 (用于呼吸/流光相位)
        self.cx = self.tx.mean()
        self.cy = self.ty.mean()

    # ---------- 采样 ----------
    @staticmethod
    def _sample(img, max_particles):
        img = img.convert("RGBA")
        w, h = img.size
        # 压缩到合理宽度, 保证粒子数可控
        scale = min(1.0, 340 / max(w, 1))
        if scale < 1.0:
            img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))))
        arr = np.asarray(img)
        alpha = arr[..., 3] > 40
        ys, xs = np.nonzero(alpha)
        if len(xs) == 0:                      # 空图兜底: 中心画一个点
            xs, ys = np.array([w // 2]), np.array([h // 2])
        if len(xs) > max_particles:           # 太多则随机抽样
            idx = np.random.default_rng().choice(len(xs), max_particles, replace=False)
            xs, ys = xs[idx], ys[idx]
        colors = arr[ys, xs, :3].astype(np.float32)
        return xs, ys, colors, img.size[0], img.size[1]

    # ---------- 交互 ----------
    def mouse_force(self, mx, my, radius=150.0, strength=2600.0):
        """鼠标斥力: 粒子被推开, 移开后弹回。"""
        dx = self.x - mx
        dy = self.y - my
        d2 = dx * dx + dy * dy
        mask = d2 < radius * radius
        if not mask.any():
            return
        d = np.sqrt(d2[mask]) + 1e-5
        f = strength * (1.0 - d / radius) / d          # 越近越强
        self.vx[mask] += (dx[mask] / d) * f
        self.vy[mask] += (dy[mask] / d) * f

    def burst(self):
        """爆炸: 给粒子随机速度 + 重力, 之后自动重组。"""
        if self.state == BURST:
            return
        self.state = BURST
        self.burst_time = 0.0
        rng = np.random.default_rng()
        ang = rng.uniform(0, 2 * math.pi, self.n)
        spd = rng.uniform(120, 720, self.n)
        self.vx = np.cos(ang) * spd
        self.vy = np.sin(ang) * spd - 200.0           # 向上爆开 + 随后下落

    def reassemble(self):
        self.state = ASSEMBLE
        self.t = 0.0

    # ---------- 更新 ----------
    def update(self, dt, mx=None, my=None):
        self.t += dt
        n = self.n
        T = self.t

        if self.state == BURST:
            self.burst_time += dt
            # 重力 + 阻尼
            self.vy += 500.0 * dt
            self.vx *= (1 - 1.6 * dt)
            self.vy *= (1 - 1.6 * dt)
            self.x += self.vx * dt
            self.y += self.vy * dt
            # 落地轻微反弹
            floor = self.sh + 20
            down = self.y > floor
            self.y[down] = floor
            self.vy[down] *= -0.35
            if self.burst_time > 2.6:
                self.reassemble()
            return

        if self.state == ASSEMBLE:
            # 波浪式汇聚: 每粒子有延迟, ease-out 缓动
            k = 1 - math.exp(-3.2 * dt)
            active = self.delay <= T
            if active.any():
                self.x[active] += (self.tx[active] - self.x[active]) * k
                self.y[active] += (self.ty[active] - self.y[active]) * k
                self.vx[active] *= (1 - 2.0 * dt)
                self.vy[active] *= (1 - 2.0 * dt)
                self.x[active] += self.vx[active] * dt
                self.y[active] += self.vy[active] * dt
            if T > self.delay.max() + 1.2:
                self.state = IDLE
                self.t = 0.0
            return

        # IDLE: 成型状态
        # 位置微浮动 (呼吸)
        wob = 1.6 * math.sin(T * 1.8) * 0.9
        self.x = self.tx + np.sin(T * 1.2 + self.phase) * wob
        self.y = self.ty + np.cos(T * 1.35 + self.phase * 1.3) * wob
        # 鼠标斥力
        if mx is not None and my is not None:
            self.mouse_force(mx, my)
            self.x += self.vx * dt
            self.y += self.vy * dt
            self.vx *= (1 - 4.0 * dt)     # 弹性复位
            self.vy *= (1 - 4.0 * dt)

    # ---------- 绘制 ----------
    def draw(self):
        s = self.base_size
        n = self.n
        T = self.t

        if self.state == BURST:
            # 爆炸: 粒子变小变暗
            f = max(0.0, 1.0 - self.burst_time / 3.0)
            size = np.full(n, max(s * 0.7, 1.5))
            col = self.colors * f
        elif self.state == ASSEMBLE:
            # 汇聚中: 亮度随到达进度提升
            prog = np.clip(T / (self.delay.max() + 1.2), 0.05, 1.0)
            size = np.full(n, s * (0.4 + 0.6 * prog))
            col = self.colors * (0.35 + 0.65 * prog)
        else:
            # 呼吸: 大小周期波动 (以角色中心距离为相位, 形成波浪)
            dist = np.sqrt((self.x - self.cx) ** 2 + (self.y - self.cy) ** 2)
            breath = 1.0 + 0.28 * np.sin(T * 2.0 + dist * 0.02)
            size = np.full(n, s) * breath
            # 流光: RGB 三通道不同相位的正弦, 沿对角方向流动
            wave = T * 3.0 + (self.x + self.y) * 0.012
            lum = np.empty((n, 3), dtype=np.float32)
            lum[:, 0] = 1.0 + 0.14 * np.sin(wave)
            lum[:, 1] = 1.0 + 0.14 * np.sin(wave + 2.1)
            lum[:, 2] = 1.0 + 0.14 * np.sin(wave + 4.2)
            col = self.colors * lum

        col = np.clip(col, 0, 255).astype(np.uint8)
        # 绘制 (2x2 方块, 速度快)
        rects = []
        for i in range(n):
            xi = int(self.x[i] - s)
            yi = int(self.y[i] - s)
            if -2 <= xi < self.sw and -2 <= yi < self.sh:
                rects.append((self.screen, col[i], (xi, yi, int(s), int(s))))
        if rects:
            pygame.draw.rect(rects[0][0], rects[0][1], rects[0][2])
            # 批量: 同一 surface 上逐条画
            for surf, c, r in rects[1:]:
                pygame.draw.rect(surf, c, r)


# ---------------- 主程序 ----------------
def load_image(args):
    if args.image and os.path.exists(args.image):
        from PIL import Image
        return auto_clean(Image.open(args.image))
    return generate_character(args.character)


def main():
    ap = argparse.ArgumentParser(description="二次元角色粒子系统")
    ap.add_argument("--image", help="输入图片路径 (任意图片)")
    ap.add_argument("--character", default="miku",
                    help="内置角色: miku / kurumi / blonde / sakura (可写中文: 初音/狂三/金发/粉发)")
    ap.add_argument("--particles", type=int, default=18000)
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--fullscreen", action="store_true")
    ap.add_argument("--demo", action="store_true", help="无头自动演示, 截图到 shots/")
    args = ap.parse_args()

    if args.demo:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    pygame.init()
    flags = pygame.FULLSCREEN if args.fullscreen else 0
    screen = pygame.display.set_mode((args.width, args.height), flags)
    pygame.display.set_caption("二次元粒子系统 — 移动鼠标互动 | 左键爆炸 | ESC退出")

    img = load_image(args)
    field = ParticleField(img, screen, max_particles=args.particles)
    clock = pygame.time.Clock()
    running = True
    t0 = time.time()
    shots_dir = "shots"
    if args.demo:
        os.makedirs(shots_dir, exist_ok=True)

    def save_shot(tag):
        pygame.image.save(screen, os.path.join(shots_dir, f"{tag}.png"))

    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        mx, my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    field.burst()
                elif e.button == 3:
                    field.reassemble()

        field.update(dt, mx, my)

        screen.fill((8, 10, 18))
        field.draw()

        if args.demo:
            el = time.time() - t0
            # 时间线: 汇聚(0-3s) -> 成型(3-6s) -> 爆炸(6s) -> 重组(9s+) -> 结束
            if el < 0.1:
                save_shot("0_start")
            if 2.4 < el < 2.6:
                save_shot("1_assembled")
            if 4.9 < el < 5.1:
                save_shot("2_idle_breath")
            if 6.0 < el < 6.2 and field.state != BURST:
                field.burst()
            if 6.7 < el < 6.9:
                save_shot("3_burst")
            if 11.5 < el < 11.7:
                save_shot("4_reassembled")
            if el > 12.0:
                print(f"demo done: {field.n} particles, base_size={field.base_size:.2f}")
                running = False
        else:
            # 屏幕角落提示
            font = pygame.font.SysFont("simsun,arial", 18)
            hint = font.render("左键: 爆炸  右键: 重组  ESC: 退出", True, (140, 150, 170))
            screen.blit(hint, (16, 12))
            info = font.render(f"粒子数: {field.n}  状态: "
                               + {ASSEMBLE: "汇聚中", IDLE: "成型", BURST: "爆炸"}[field.state],
                               True, (140, 150, 170))
            screen.blit(info, (16, 36))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
