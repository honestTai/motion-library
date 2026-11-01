---
name: motion-library
description: 开发时检索和接入本地动效库（video-shotcraft-cards）：按需求选卡、读配方、定位 Remotion TSX 源码及其依赖、把动效接入或移植到工程，也用于给库新增卡片和导入库的更新版本。当用户要做或改视频动效、镜头、转场、字卡、数据动画、Remotion 组件，提到动效库、镜头卡、卡名（如 card-stack、blur-slide），或说"给这段配个动效""把这个动效接进工程""动效库更新了"时使用。
---

# 动效库开发

这个 skill 只放用法，不放动效内容。库会持续更新，所以卡片数量、卡名和路径一律以工具的实时结果为准，不要凭记忆或写死。

工具会自动向上查找 `video-shotcraft-cards` 目录。找不到时设置 `MOTION_LIBRARY_ROOT`。下面的 `motion_lib.py` 都指本 skill 的 `scripts/motion_lib.py`，用 `python3 -I` 运行：

```bash
python3 -I scripts/motion_lib.py stats                        # 库的当前规模
python3 -I scripts/motion_lib.py search "数字跳动 强调增长" [--category data] [--limit 8]
python3 -I scripts/motion_lib.py show card-stack [--json]     # 配方、实现、依赖、资源、样片
python3 -I scripts/motion_lib.py copy card-stack --to <工程> --dry-run
python3 -I scripts/motion_lib.py doctor                       # 校验全库
```

分类：`opening` `typography` `ui-entrance` `camera` `data` `interaction` `transition` `rhythm` `effects` `outro`。

## 接入一个动效

1. **选卡**：用户给了卡名就直接用。否则用 `search` 取几个候选，读它们的"适用"和"能量"，按这段内容要表达什么来选。用户要看效果时，给出 `show` 列出的样片路径，或让用户打开库里的 `打开动效画廊.html`。
2. **读配方全文**：打开 `show` 给出的配方，至少读 `意图`、`动效核心`、`参数表`、`已知坑`。很多卡是一卡多式（有"两式选型"等章节），先按章节选定样式，再找对应实现。
3. **读准确的源码**：读 `show` 列出的 TSX，不要只看卡名就重写一个相似效果。这些实现的时序和缓动都调校过。
4. **接入**：先看目标工程的技术栈和现有约定。
   - Remotion 工程：先 `copy --dry-run`，确认后再执行。一卡多实现时用 `--demo <文件名片段>` 只取需要的。
   - 其它渲染方案（HyperFrames、GSAP、Three 等）：TSX 不能直接运行，按 [development.md](references/development.md) 的移植方法处理。
5. **换内容后回验**：配方的参数是在占位素材上调的。换文案或素材后，按该卡的 `已知坑` 重调，再抽帧检查入场、运动高峰、落定和退场。检查项见 development.md。
6. **交付时写明**：卡名、样式、配方和源码路径、改动位置，方便之后继续改。

写代码、改时序或换画幅之前，先读 [references/development.md](references/development.md)。

## 维护这个库

给库新增卡片，或导入新版本时，按 [references/updating.md](references/updating.md) 操作。结束时都要跑 `doctor`。

## 边界

- 这个库是配方、示例和样片，不含完整宣传片模板、音乐音效库和剪映导出。`demos/README.md` 里提到的 `template/`、`assets/scripts/smoke-render-demos.py`、`pr-checks.yml` 属于上游完整仓库，这里没有。
- 移植到工程时不要修改库里的原文件，除非用户明确要改库本身。
- 用真实素材替换占位内容。部分卡的手法来自公开作品的研究（见 `references/shots/ATTRIBUTION.md`），不要复刻原片的画面、文案或品牌元素。分发时保留 `LICENSE` 和该来源说明。
