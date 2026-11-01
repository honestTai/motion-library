# Motion Library 动效库

给视频开发用的本地动效库，附带一个 AI agent skill。每个动效都有配方卡、可运行的 Remotion 源码和样片，可以让 agent 按需求选卡，并接入你的视频工程。

## 赞助商

本项目由 [hrouter.net](https://hrouter.net/) 赞助。

## 内容

- 152 张配方卡：用途、动作结构、时长、参数和已知坑
- 209 种样式，每种都有 MP4 样片
- 216 个 Remotion TSX 文件，以及可复用的组件和纹理素材
- 离线画廊：不用安装依赖，也不用启动服务
- `motion-library` skill：供 Claude Code、Codex 等 agent 查卡和接入

分类包括开场与品牌、文字与字卡、界面登场与陈列、运镜与空间、数据与指标、交互与功能演示、转场、节奏与蒙太奇、光效与强调、收尾。

## 快速开始

### 浏览动效

克隆仓库后，双击 [`video-shotcraft-cards/打开动效画廊.html`](video-shotcraft-cards/打开动效画廊.html)，就可以搜索、筛选和播放样片。也可以看[中文目录](video-shotcraft-cards/动效卡片目录.md)。

### 安装 skill

用软链接安装，这样仓库更新后 skill 也会同步。在仓库根目录运行：

```bash
ln -s "$PWD/.agent/skills/motion-library" ~/.claude/skills/motion-library
```

```bash
ln -s "$PWD/.agent/skills/motion-library" ~/.codex/skills/motion-library
```

然后开一个新会话，直接描述需求：

```text
这一段讲三个步骤：准备素材、安排画面、检查导出。用动效库选一个合适的动效，接进当前的 Remotion 工程。
```

### 命令行工具

工具只需要 Python 3，每次运行都会实时扫描库，没有索引要维护。

```bash
python3 .agent/skills/motion-library/scripts/motion_lib.py search "数字跳动 强调增长"
```

```bash
python3 .agent/skills/motion-library/scripts/motion_lib.py show card-stack
```

```bash
python3 .agent/skills/motion-library/scripts/motion_lib.py copy card-stack --to /path/to/remotion-project --dry-run
```

```bash
python3 .agent/skills/motion-library/scripts/motion_lib.py doctor
```

| 命令 | 作用 |
|---|---|
| `stats` | 查看库的当前规模 |
| `search` | 用中文或英文描述找卡 |
| `show` | 列出配方、源码、依赖、资源和样片路径 |
| `copy` | 把动效和依赖复制进工程，import 不用改，文件有冲突时会停下 |
| `doctor` | 校验配方、源码、依赖、样片和画廊索引是否一致 |

## 目录结构

```text
.agent/skills/motion-library/   agent skill 和命令行工具
video-shotcraft-cards/
├── references/shots/           配方卡，按分类存放
├── demos/                      Remotion 实现、共享件和纹理
├── assets/lib/                 可复用组件
├── gallery/                    离线画廊和样片
├── 动效卡片目录.md / .csv       中文目录
└── 打开动效画廊.html            画廊入口
```

## 在工程中使用

示例基于 Remotion，默认 30fps、1920×1080。依赖版本见 [`upstream-render-dependencies.json`](video-shotcraft-cards/demos/upstream-render-dependencies.json)，这个仓库不含完整宣传片模板和音乐音效库。

- [开发约定](.agent/skills/motion-library/references/development.md)：demo 类型、换中文、换画幅、移植到非 Remotion 工程
- [更新动效库](.agent/skills/motion-library/references/updating.md)：新增卡片、导入新版本、同步画廊
- [源码说明](video-shotcraft-cards/demos/README.md)：共享件、纹理和 ClipCard 的用法

`demos/README.md` 来自上游，其中提到的 `template/` 和测试脚本不在本仓库中。

## 来源与许可

动效内容提取自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)，按 [Apache License 2.0](video-shotcraft-cards/LICENSE) 分发。

本仓库相对上游的改动：提取动效卡片部分，新增离线画廊、中文目录、`motion-library` skill 和命令行工具，并删除了上游站点相关文件。

部分卡片的手法研究自公开发布的作品，实现均为重写，来源和边界见 [ATTRIBUTION.md](video-shotcraft-cards/references/shots/ATTRIBUTION.md)。使用时不要复刻原作的画面、文案或品牌元素。
