# 开发约定

## 库的结构

| 路径 | 内容 |
|------|------|
| `references/shots/<分类>/<卡名>.md` | 配方卡，内容的权威来源 |
| `demos/<分类>/<目录>/*.tsx` | Remotion 参考实现，目录名不一定等于卡名，以配方的 `参考实现` 为准 |
| `demos/_fixtures/` | 共享件：`Fixtures.tsx`、`Motion.tsx`、`PageCam2D.tsx` |
| `demos/_textures/` | 真实素材版 demo 用的截图和 `live-layout.json` |
| `assets/lib/` | 可复用组件：`ClipCard`、`PageCam`、`Caption`、`DigitRoll`、`FlashCut`、`FlatPanel`、`VerticalTicker`、`helpers/` |
| `gallery/media/*.mp4` | 样片，只作效果参考 |
| `gallery/api/library.json` | 画廊索引，由配方同步而来 |

基准是 30fps、1920×1080。依赖版本快照见 `demos/upstream-render-dependencies.json`（remotion 4.0.484、react 19）。只补目标工程缺少的依赖，不要为了对齐版本去升降工程已有的依赖。

## 三类 demo

先看 demo 的 import，判断它属于哪一类。

**Motion 系**（依赖 `_fixtures/Motion.tsx`）
- 用 `useT()` 取归一化时间 t，用 `seg(t, t0, t1, ease)` 切分阶段，用 `E` 缓动表和 `lerp` 计算。
- 在 `<DesignStage>` 的 480×270 设计坐标里作画，再等比放大。参数表数值都在这个坐标系下，改合成分辨率时不用动参数。
- 文字密集时用 `raster="zoom"`，小字更清晰。
- 因为时间是归一化的，改总时长会让所有阶段等比伸缩。只想延长停留时，要改时间窗。

**Fixtures 系**（依赖 `_fixtures/Fixtures.tsx`）
- 用灰阶假 UI 场景件，坐标是合成像素。
- 接入时要把 FakeDashboard、Card 等占位件换成真实内容。

**真实纹理系**（依赖 `PageCam2D` 和 `_textures/`）
- 把整页截图当平面做相机巡游，相机关键帧是页面坐标。
- 换截图后，如果宽高比变了（比如换竖屏），要重新标定相机表。
- 资源路径写的是 `staticFile('textures/live/xxx.png')`，要放到工程的 `public/textures/live/`。`copy` 命令会按引用路径放好。

## 组件约定

- 每个 demo 导出 `XXX_DURATION` 或 `XXX_DUR`（30fps 帧数）。注册 Composition 时直接用它，不要另写时长。
- `copy` 默认保留库的相对目录，放在 `src/motion/` 下，所以 import 不用改：

```tsx
import { BlurSlide, BLUR_SLIDE_DURATION } from './motion/demos/typography/blur-slide/BlurSlide';

<Composition id="BlurSlide" component={BlurSlide}
  durationInFrames={BLUR_SLIDE_DURATION} fps={30} width={1920} height={1080} />
```

- 真实视频用 `assets/lib/ClipCard.tsx` 承载，务必传 `durationInFrames`。素材短于镜头时传 `loopDurationInFrames`。参数和坑见 `demos/README.md`。
- 用到 `@remotion/motion-blur` 的 demo 需要单独安装，`show` 的 npm 一行会列出来。
- `assets/lib/helpers/camera.tsx` 依赖 three 和 @react-three/fiber，`assets/lib/FlatPanel.tsx` 依赖 three，用到时才装。

## 必须遵守

- **逐帧确定**：所有动画都由帧号或 t 计算。禁用 `Math.random`、`Date.now` 和按帧累积的状态。随机用固定种子，比如 Motion 的 `rand(seed)` 或 Remotion 的 `random(seed)`。
- **同一元素的多个通道共用一个进度**：比如 blur-slide 的位移、模糊和透明度共用一个 `p`，分开写就会错位。
- **保留完整动作链**：蓄力或入场、主体运动、落定、阅读停留、退场。不要只抄高潮段。
- **改数量要连带改时序**：错峰总长 = 间隔 × 数量。加卡片或加词后，后面的时间窗要一起后移，否则两段动作会撞车。
- **测量文字的组件有字体风险**：`glass-pill-dictation-typing`、`chip-grid-single-select-blackout`、`pill-chip-slot-cycle-handled` 用 `useLayoutEffect` 量文字宽度，字体回退时布局会漂移。必要时把测量值写死。

## 换中文

- 中文字宽约是英文的两倍。很多 demo 写死了容器宽度或 `nowrap`，换文案后要查溢出，并调字号或容器。
- `split(' ')` 对中文得到一整块。按语义手动切成 3–5 段，不要退化成逐字入场。
- 换文案前先查这张卡的 `已知坑`，不少卡写了词数和宽度的上限。

## 换画幅或帧率

- 竖屏（1080×1920）：Motion 系的 `DesignStage` 是 16:9，要先调整舞台和布局，不能只改 Composition 尺寸。像素坐标的 demo 要重排，相机类要重标定。
- 帧率：配方里的 `f` 都按 30fps 算。写死帧数的 demo 换帧率时要按比例换算。归一化时间的 demo 只需换算总时长。

## 移植到非 Remotion 工程

不要重新发明效果，从配方和源码里提取这些内容，再用目标工程的方式实现：

1. 时间轴：把 `seg` 的每个时间窗换算成 秒 = t × 总帧数 / 30。
2. 缓动：`E` 表的公式都是纯函数，可以直接复制。不要用"看起来差不多"的预设曲线代替，`E.spring` 尤其如此。
3. 空间：transform、`transform-origin`、perspective、zIndex 原样保留。
4. 确定性：动画必须由渲染时间线驱动，不能依赖实时计时器。
5. 对照：抽同样时间点的帧，和 `gallery/media/` 的样片比较。

## 回验清单

用目标工程能用的方式渲染或抽帧（Remotion 用 `remotion still --frame=N`），至少看入场、运动高峰、落定、退场四个时间点：

- 文字没有遮挡、裁切或溢出，落定后的停留够读完
- 没有组件或资源丢失（`staticFile` 的 404 很常见）
- 动作之间没有撞车，节奏和口播或字幕对得上
- 需要看连贯运动时，渲染一小段视频，不要只看单帧

如实报告没检查到的部分。
