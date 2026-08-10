# 🧰 个人工具箱 (Windows + WSL2)

收集日常实用的自动化脚本与工具，全部在 Windows 11 + WSL2 (Ubuntu-24.04) 环境实测可用。

## 📁 结构

```
toolbox/
├── particle-anime/        # 🎨 二次元粒子系统 (独立项目)
│   ├── src/               #   PC 版 (Python + Pygame)
│   ├── web/               #   手机网页版 (单文件 HTML, 图片内嵌)
│   ├── build.bat          #   Windows 一键打包 EXE
│   └── README.md          #   使用说明
├── scripts/               # 🛠️ Windows 批处理工具
│   ├── C盘一键清理.bat    #   9 项安全清理 (缓存/回收站/更新)
│   ├── 数据路径迁移D盘.bat #   下载/文档/图片默认保存到 D 盘 (源头方案)
│   ├── WSL迁移到D盘.bat   #   WSL 发行版迁移 D 盘 (自动备份可回滚)
│   └── Hermes技能更新.bat #   Hermes 技能库与本体更新
├── tools/                 # 🐍 Python 自动化工具
│   ├── update_projects.py #   GitHub 开源项目周检 (更新 Excel)
│   └── cron_update.sh     #   cron 包装脚本
├── AI-创作工具链.md       # 🎨 AI公众号+漫画自动化管线 (见下方)
└── github_projects.xlsx   # 📊 开源项目汇总表 (已复现/未复现/待验证)
```

## 🎨 AI 创作工具链 (2026-08 新增)

详见 [`AI-创作工具链.md`](AI-创作工具链.md) — 公众号自动生成(热搜→深挖→三遍工序) + AI漫画(古籍→分镜→参考图锁定生图→排版)。

## 🛠️ 脚本说明

### scripts/C盘一键清理.bat
安全清理：用户/系统临时文件、Windows 更新缓存、Edge 缓存、WPS 组件池、微信插件缓存、剪映缓存、回收站。
```bat
双击运行即可 (无需管理员)
```

### scripts/数据路径迁移D盘.bat
从源头解决 C 盘膨胀：创建 `D:\UserData` 并把系统默认保存位置 (下载/文档/图片/视频/音乐) 改到 D 盘。
```bat
双击运行 (一次性, 重启资源管理器生效)
```

### scripts/WSL迁移到D盘.bat
将 WSL 发行版整个迁移到 D 盘 (释放 ~6.6GB)。自动备份 tar → 迁移 → 设置默认用户，失败自动回滚。
```bat
双击运行 (迁移期间 WSL 关闭 5-10 分钟)
```

### scripts/Hermes技能更新.bat
更新 Hermes 技能库与本体：
```bat
双击运行
```

## 🐍 工具说明

### tools/update_projects.py
每周检索 GitHub 热门开源项目 (6 大分类)，合并更新 `github_projects.xlsx`：
- 已有项目保留状态 (已复现/未复现/待验证)
- 新项目自动追加为"待验证"
- 支持 GitHub Token (环境变量 `GH_TOKEN`) 提升 API 限额

```bash
python3 update_projects.py
# 或配置 cron: 每周一 9:00 自动执行
```

### 配合 Hermes cron 使用
```bash
# ~/.hermes/scripts/gh_projects_weekly.sh 已配置
# cron: 0 9 * * 1 (每周一 9:00)
```

## ✅ 环境要求

- Windows 10/11 + WSL2 (Ubuntu)
- Python 3.9+ (工具脚本)
- bat 脚本为 GBK 编码 (中文 Windows cmd 直接运行, 勿转为 UTF-8)

## 📜 许可

MIT — 自由使用修改
