# 更新动效库

工具每次运行都直接扫描库文件，没有缓存，所以库更新后 skill 不用重新生成。只有约定本身变了（比如新增一类共享件、配方格式变化）才需要改这个 skill 的文档。

## 导入新版本压缩包

1. 解压到一个空的临时目录，先检查内容，不运行里面的脚本。
2. 和现有库比较，弄清增加、修改、删除了什么：

```bash
diff -rq <临时目录>/video-shotcraft-cards <库根目录>
```

3. 先向用户说明差异。现有库里有用户自己改过或新增的内容时，不要直接覆盖，先确认保留哪边。
4. 确认后再合并，然后跑 `doctor`，并报告卡片数量的变化。

新压缩包里可能带有本仓库已清理掉的打包和上游站点文件（`PACKAGE-MANIFEST.json`、库内 `SKILL.md`、`agents/`、`gallery/index.html`、`gallery/library.html`、`gallery/app.js`、`gallery/build-seo.py`、`gallery/fetch-media.sh`、`llms.txt`、`robots.txt`、`sitemap.xml`、`og-image.jpg`）。合并时不要带回来。

画廊界面和品牌信息已经按本仓库重新设计。`gallery/library-offline.html`、`styles.css`、`app-offline.js`、`logo-mark.svg` 不要被新包覆盖，`translations.js` 只合并新卡的翻译，保留界面文案。根目录 `README.md` 和 `docs/assets/` 也属于本仓库。

## 新增一张卡

1. 新建 `references/shots/<分类>/<卡名>.md`。卡名用 kebab-case，文件名必须和 front matter 的 `name` 一致：

```markdown
---
name: my-card
一句话: 一句话讲清画面发生了什么
适用: 什么内容、什么段落用它
时长: 约 4.0s（120f@30fps）
能量: 中（为什么是这个能量）
标签: data, effects
---

## 意图
为什么这样设计，观众先看到什么、后看到什么。

## 动效核心
可复现的公式、时间窗和缓动。

## 参数表
| 参数 | 典型值 | 调节手感 |
|------|--------|----------|

## 已知坑
换内容时会出什么问题，上限是多少。

## 参考实现
demos/<分类>/my-card/
（MyCard.tsx）
```

`标签` 可选，值必须是分类目录名。分类目录也要是现有分类之一，否则同步脚本会报错。新增分类时要改 `gallery/sync-from-cards.py` 里的 `CATEGORIES`。

2. 新建 `demos/<分类>/my-card/MyCard.tsx`：导出组件和 `MY_CARD_DURATION`，优先用 `_fixtures/Motion.tsx` 的工具，逐帧确定，能过 `tsc --noEmit --strict`。占位内容用中性文案，不带品牌元素。
3. 把样片放到 `gallery/media/my-card.mp4`。
4. 更新画廊，见下一节。
5. 跑 `doctor`，并手动把卡加进 `动效卡片目录.md` 和 `.csv`（这两个文件没有生成脚本）。

## 更新画廊

`gallery/sync-from-cards.py` 只做两件事：把配方复制到 `gallery/source/`，并刷新 `library.json` 里**已有**卡片的文字字段。要注意：

- **它不会添加新卡**。新卡要先手动在 `gallery/api/library.json` 的 `cards` 里加一条（`name`、`source`、`category`、`styles[].key/label/media`），再运行脚本。可以照抄一张现有的卡。
- **它不更新离线画廊**。`打开动效画廊.html` 读的是 `gallery/library-offline-data.js`，内容是 `window.OFFLINE_SHOTCRAFT_LIBRARY = <library.json 内容>;`，这里没有生成脚本，要在同步后重新写入。

```bash
python3 -I gallery/sync-from-cards.py    # 在库根目录运行
```

`doctor` 会提示离线画廊和 `library.json` 的卡片不一致。运行前库里有未备份的改动时，注意这个脚本会删除已没有对应配方的 `gallery/source` 副本，并改写 `library.json`。

## doctor 的结果

- **ERROR**：缺字段或章节、参考实现路径失效、import 解析不了、样片缺失、索引和配方对不上。要修。
- **WARN**：源码没有被任何卡引用、资源不在 `_textures`、画廊副本或离线数据过期。逐条判断。目前已知 `demos/ui-entrance/clipcard-looping/ClipCardLooping.tsx` 没有被卡引用，它是 ClipCard 的回归 demo，属于正常情况。
