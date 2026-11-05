<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/hero.zh-CN.svg">
  <img src="docs/assets/hero.zh-CN-light.svg" alt="Motion Library">
</picture>

### 给视频开发用的动效库

**每个动效都有配方、源码和样片。看样片、搜用途、复制卡名，让 agent 接进你的视频工程。**

[![配方卡](https://img.shields.io/badge/配方卡-152-E0451A?style=flat-square)](video-shotcraft-cards/动效卡片目录.md)
[![样片](https://img.shields.io/badge/动态样片-209-E0451A?style=flat-square)](video-shotcraft-cards/打开动效画廊.html)
[![Remotion](https://img.shields.io/badge/Remotion-4-1C1A16?style=flat-square)](https://www.remotion.dev/)
[![Agent Skill](https://img.shields.io/badge/Agent_Skill-Claude_Code_%7C_Codex-1C1A16?style=flat-square)](.agent/skills/motion-library/SKILL.md)
[![License](https://img.shields.io/badge/License-Apache_2.0-6D695F?style=flat-square)](video-shotcraft-cards/LICENSE)

**[快速开始](#-快速开始) · [动效分类](#️-动效分类) · [开发文档](#-开发文档) · [来源与许可](#-来源与许可)**

[English](README.md) · **简体中文**

</div>

## ❤️ 赞助商

| 赞助商 | 简介 |
| :--- | :--- |
| [![HRouter](docs/assets/hrouter-sponsor.svg)](https://hrouter.net/home) | **[HRouter](https://hrouter.net/home)**：面向 AI 编程与应用开发的模型接入、API Key 管理与用量统计，也由作者运营。 |

## 🚀 快速开始

### 1. 浏览动效

```bash
git clone https://github.com/honestTai/motion-library.git
```

打开 [`video-shotcraft-cards/打开动效画廊.html`](video-shotcraft-cards/打开动效画廊.html)。也可以直接看[中文目录](video-shotcraft-cards/动效卡片目录.md)。

### 2. 安装 skill

用软链接安装，仓库更新后 skill 也会同步。在仓库根目录运行：

```bash
ln -s "$PWD/.agent/skills/motion-library" ~/.claude/skills/motion-library
```

```bash
ln -s "$PWD/.agent/skills/motion-library" ~/.codex/skills/motion-library
```

### 3. 开一个新会话，描述需求

```text
这一段讲三个步骤：准备素材、安排画面、检查导出。
用动效库选一个合适的动效，接进当前的 Remotion 工程。
```

## 🎞️ 动效分类

| 分类 | 卡片数 | 代表动效 |
|:---|:---:|:---|
| 开场与品牌 | 10 | [`spotlight-hero-card`](video-shotcraft-cards/references/shots/opening/spotlight-hero-card.md) |
| 文字与字卡 | 25 | [`blur-slide`](video-shotcraft-cards/references/shots/typography/blur-slide.md) |
| 界面登场与陈列 | 27 | [`card-stack`](video-shotcraft-cards/references/shots/ui-entrance/card-stack.md) |
| 运镜与空间 | 10 | [`crash-zoom-punch`](video-shotcraft-cards/references/shots/camera/crash-zoom-punch.md) |
| 数据与指标 | 11 | [`odometer-digit-roll`](video-shotcraft-cards/references/shots/data/odometer-digit-roll.md) |
| 交互与功能演示 | 15 | [`ai-stream-response`](video-shotcraft-cards/references/shots/interaction/ai-stream-response.md) |
| 转场 | 19 | [`shot-transitions`](video-shotcraft-cards/references/shots/transition/shot-transitions.md) |
| 节奏与蒙太奇 | 11 | [`beat-cut-moves`](video-shotcraft-cards/references/shots/rhythm/beat-cut-moves.md) |
| 光效与强调 | 17 | [`impact-feedback`](video-shotcraft-cards/references/shots/effects/impact-feedback.md) |
| 收尾 | 7 | [`outro-group-photo-launch`](video-shotcraft-cards/references/shots/outro/outro-group-photo-launch.md) |

## 📚 开发文档

示例基于 Remotion，默认 30fps、1920×1080。依赖版本见 [`upstream-render-dependencies.json`](video-shotcraft-cards/demos/upstream-render-dependencies.json)。

- [开发约定](.agent/skills/motion-library/references/development.md)：demo 类型、换中文、换画幅、移植到非 Remotion 工程
- [更新动效库](.agent/skills/motion-library/references/updating.md)：新增卡片、导入新版本、同步画廊
- [源码说明](video-shotcraft-cards/demos/README.md)：共享件、纹理和 ClipCard 的用法。这份说明来自上游，其中提到的 `template/` 和测试脚本不在本仓库中

## 📄 来源与许可

动效内容提取自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)，按 [Apache License 2.0](video-shotcraft-cards/LICENSE) 分发。

本仓库相对上游的改动：提取动效卡片部分，新增并重新设计离线画廊，新增中文目录、`motion-library` skill 和命令行工具，并删除了上游站点相关文件。这个仓库不含完整宣传片模板和音乐音效库。

部分卡片的手法研究自公开发布的作品，实现均为重写，来源和边界见 [ATTRIBUTION.md](video-shotcraft-cards/references/shots/ATTRIBUTION.md)。使用时不要复刻原作的画面、文案或品牌元素。

## 📈 Star history

<a href="https://www.star-history.com/#honestTai/motion-library&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=honestTai/motion-library&type=Date&theme=dark">
    <img src="https://api.star-history.com/svg?repos=honestTai/motion-library&type=Date" alt="motion-library 的 Star 历史">
  </picture>
</a>

---

<div align="center">

Made by **[honestTai](https://github.com/honestTai)** · [HRouter](https://hrouter.net/home) · [More projects](https://github.com/honestTai)

</div>
