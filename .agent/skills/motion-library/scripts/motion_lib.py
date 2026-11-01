#!/usr/bin/env python3
"""Live query tool for the motion library. It scans the library on every run and
keeps no cache, so added or edited cards are visible immediately.

  motion_lib.py stats
  motion_lib.py search "三个步骤依次出现" [--category ui-entrance] [--limit 8]
  motion_lib.py show card-stack [--json]
  motion_lib.py copy card-stack --to /path/to/remotion-project [--demo CardStack] [--dry-run] [--force]
  motion_lib.py doctor
"""
import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

LIB_DIRNAME = 'video-shotcraft-cards'
REQUIRED_SECTIONS = ('意图', '参数表', '已知坑', '参考实现')
REQUIRED_FIELDS = ('name', '一句话', '适用', '时长', '能量')


def find_root():
    env = os.environ.get('MOTION_LIBRARY_ROOT')
    if env:
        root = Path(env).expanduser().resolve()
        if (root / 'references' / 'shots').is_dir():
            return root
        sys.exit(f'MOTION_LIBRARY_ROOT has no references/shots: {root}')
    for parent in Path(__file__).resolve().parents:
        if (parent / LIB_DIRNAME / 'references' / 'shots').is_dir():
            return parent / LIB_DIRNAME
    sys.exit(f'Library not found. Set MOTION_LIBRARY_ROOT to the {LIB_DIRNAME} folder.')


ROOT = find_root()
SHOTS = ROOT / 'references' / 'shots'
DEMOS = ROOT / 'demos'


def rel(path):
    return path.relative_to(ROOT).as_posix()


def parse_card(path):
    text = path.read_text(encoding='utf-8')
    fields = {}
    body = text
    match = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if match:
        body = text[match.end():]
        for line in match.group(1).splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                fields[key.strip()] = value.strip()
    sections = {}
    parts = re.split(r'^## +(.+?)\s*$', body, flags=re.M)
    for title, content in zip(parts[1::2], parts[2::2]):
        sections[title] = content.strip()
    return {
        'name': path.stem,
        'category': path.parent.name,
        'path': path,
        'text': text,
        'fields': fields,
        'sections': sections,
    }


def load_cards():
    cards = [parse_card(p) for p in sorted(SHOTS.glob('*/*.md'))]
    return {c['name']: c for c in cards}


def find_by_basename(filename):
    return sorted(DEMOS.rglob(filename))


def demo_files(card):
    """Resolve the card's 参考实现 section into real source files.

    The section is free-form: a directory followed by file names, full paths,
    or bare names meaning "same directory". Returns (files, unresolved names).
    """
    section = card['sections'].get('参考实现', '')
    # Provenance notes such as "原 template/src/.../Scene.tsx" name upstream files not in this library.
    section = re.sub(r'[\w./\-]*template/[\w./\-]*', '', section)
    files, missing = [], []
    last_dir = None
    token = re.compile(r'(?:demos|assets/lib)/[\w./\-]+|[\w\-]+\.tsx?')
    for raw in token.findall(section):
        if raw.startswith(('demos/', 'assets/')):
            candidate = ROOT / raw.rstrip('/.')
            if candidate.is_dir():
                last_dir = candidate
                continue
            if candidate.is_file():
                files.append(candidate)
                last_dir = candidate.parent
                continue
            missing.append(raw)
            continue
        hit = last_dir / raw if last_dir and (last_dir / raw).is_file() else None
        if hit is None:
            same_name = find_by_basename(raw)
            hit = same_name[0] if len(same_name) == 1 else None
        if hit:
            files.append(hit)
        else:
            missing.append(raw)
    if not files and last_dir:
        files = sorted(last_dir.glob('*.tsx'))
    return list(dict.fromkeys(files)), missing


IMPORT_RE = re.compile(r"""(?:from\s+|import\s*\(\s*|import\s+|require\(\s*)['"]([^'"]+)['"]""")
STATIC_RE = re.compile(r"""staticFile\(\s*(?:'([^']+)'|"([^"]+)"|`([^`]+)`)\s*\)""")


def resolve_import(base, spec):
    target = (base.parent / spec).resolve()
    options = [target, *(Path(f'{target}{ext}') for ext in ('.tsx', '.ts', '.jsx', '.js')),
               target / 'index.tsx', target / 'index.ts']
    return next((o for o in options if o.is_file()), None)


def closure(entries):
    """Follow relative imports. Returns local files, npm packages, staticFile refs, broken imports."""
    seen, npm, static, broken = {}, set(), set(), []
    stack = list(entries)
    while stack:
        current = stack.pop().resolve()
        if current in seen:
            continue
        seen[current] = True
        if current.suffix not in ('.tsx', '.ts', '.jsx', '.js'):
            continue
        source = current.read_text(encoding='utf-8')
        for spec in IMPORT_RE.findall(source):
            if spec.startswith('.'):
                hit = resolve_import(current, spec)
                if hit:
                    stack.append(hit)
                else:
                    broken.append((rel(current), spec))
            else:
                parts = spec.split('/')
                npm.add('/'.join(parts[:2]) if spec.startswith('@') else parts[0])
        for groups in STATIC_RE.findall(source):
            static.add(next(g for g in groups if g))
    return sorted(seen), sorted(npm), sorted(static), broken


def static_sources(ref):
    """Map a staticFile() argument to files in demos/_textures. Template refs may match several."""
    name = ref.rsplit('/', 1)[-1]
    textures = DEMOS / '_textures'
    if '${' in name:
        pattern = re.sub(r'\$\{[^}]*\}', '*', name)
        return sorted(textures.glob(pattern))
    hit = textures / name
    return [hit] if hit.is_file() else []


def load_gallery():
    path = ROOT / 'gallery' / 'api' / 'library.json'
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    return {c['name']: c for c in data.get('cards', [])}


def media_paths(entry):
    out = []
    for style in (entry or {}).get('styles', []):
        url = style.get('media', {}).get('url', '')
        if url:
            out.append({
                'key': style.get('key'),
                'label': style.get('label'),
                'path': (ROOT / 'gallery' / url.split('?')[0]).resolve(),
            })
    return out


def describe(card, gallery):
    files, missing = demo_files(card)
    local, npm, static, broken = closure(files)
    joined = '\n'.join(p.read_text(encoding='utf-8') for p in files)
    durations = sorted(set(re.findall(r'export const (\w+_DUR(?:ATION)?)\s*=\s*([^;\n]+)', joined)))
    return {
        'name': card['name'],
        'category': card['category'],
        'summary': card['fields'].get('一句话', ''),
        'use': card['fields'].get('适用', ''),
        'duration': card['fields'].get('时长', ''),
        'energy': card['fields'].get('能量', ''),
        'recipe': rel(card['path']),
        'demos': [rel(p) for p in files],
        'missing_refs': missing,
        'dependencies': [rel(p) for p in local if p not in [f.resolve() for f in files]],
        'npm': npm,
        'static_files': [
            {'ref': ref, 'sources': [rel(s) for s in static_sources(ref)]} for ref in static
        ],
        'broken_imports': broken,
        'design_stage': 'DesignStage' in joined,
        'duration_exports': [{'name': n, 'value': v.strip()} for n, v in durations],
        'media': [
            {'key': m['key'], 'label': m['label'], 'path': rel(m['path']), 'exists': m['path'].is_file()}
            for m in media_paths(gallery.get(card['name']))
        ],
    }


def query_terms(query):
    """Split into latin words plus Chinese runs and their bigrams, so natural phrases match."""
    terms = []
    for chunk in re.findall(r'[A-Za-z0-9\-]+|[一-鿿]+', query.lower()):
        terms.append(chunk)
        if re.match(r'[一-鿿]', chunk) and len(chunk) > 2:
            terms += [chunk[i:i + 2] for i in range(len(chunk) - 1)]
    return list(dict.fromkeys(terms))


def score(card, terms):
    weighted = [
        (8, card['name'].lower()),
        (4, card['fields'].get('一句话', '').lower()),
        (4, card['fields'].get('适用', '').lower()),
        (2, card['sections'].get('意图', '').lower()),
        (1, card['text'].lower()),
    ]
    return sum(weight * min(field.count(term), 3) for term in terms for weight, field in weighted)


def cmd_search(args):
    cards = load_cards().values()
    terms = query_terms(args.query)
    ranked = [(score(c, terms), c) for c in cards if not args.category or c['category'] == args.category]
    ranked = sorted((r for r in ranked if r[0] > 0), key=lambda r: -r[0])[:args.limit]
    if not ranked:
        print('No match. Try broader words or a --category.')
    for value, card in ranked:
        print(f"{card['name']}  [{card['category']}]  score={value}")
        print(f"  效果: {card['fields'].get('一句话', '')}")
        print(f"  适用: {card['fields'].get('适用', '')}")
        print(f"  时长: {card['fields'].get('时长', '')} | 能量: {card['fields'].get('能量', '')}")


def get_card(name):
    cards = load_cards()
    if name in cards:
        return cards[name]
    close = [n for n in cards if name.lower() in n.lower()]
    sys.exit(f'Card not found: {name}' + (f'. Did you mean: {", ".join(close[:8])}' if close else ''))


def cmd_show(args):
    info = describe(get_card(args.card), load_gallery())
    if args.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return
    print(f"{info['name']}  [{info['category']}]")
    print(f"效果: {info['summary']}\n适用: {info['use']}\n时长: {info['duration']} | 能量: {info['energy']}")
    print(f'库根目录: {ROOT}')
    print(f"配方: {info['recipe']}")
    print('实现:', *(f'  {d}' for d in info['demos']), sep='\n')
    print('共享依赖:', *(f'  {d}' for d in info['dependencies'] or ['(无)']), sep='\n')
    print('npm:', ', '.join(info['npm']) or '(无)')
    print('坐标系:', 'DesignStage 480×270 设计坐标' if info['design_stage'] else '合成像素坐标（默认 1920×1080）')
    for item in info['duration_exports']:
        print(f"时长导出: {item['name']} = {item['value']}")
    for item in info['static_files']:
        print(f"静态资源: staticFile({item['ref']}) ← {', '.join(item['sources']) or '库内没有，需自备'}")
    for item in info['media']:
        print(f"样片: {item['path']}{'' if item['exists'] else '  (缺失)'}  [{item['label']}]")
    for problem in info['missing_refs']:
        print(f'警告: 参考实现指向不存在的文件 {problem}')
    for source, spec in info['broken_imports']:
        print(f'警告: {source} 的 import 无法解析: {spec}')


def cmd_copy(args):
    card = get_card(args.card)
    files, _ = demo_files(card)
    if args.demo:
        files = [f for f in files if args.demo in f.stem]
    if not files:
        sys.exit(f'No matching demo for {card["name"]}. Run show to list them.')
    local, npm, static, broken = closure(files)
    target = Path(args.to).expanduser().resolve()
    if not target.is_dir():
        sys.exit(f'Target project does not exist: {target}')
    # Keeping the library's relative layout means the demos' imports need no rewriting.
    plan = [(p, target / args.src_dir / rel(p)) for p in local]
    unmatched = []
    for ref in static:
        sources = static_sources(ref)
        if not sources:
            unmatched.append(ref)
        folder = ref.rsplit('/', 1)[0] if '/' in ref else ''
        plan += [(s, target / 'public' / folder / s.name) for s in sources]
    conflicts = [d for s, d in plan if d.exists() and d.read_bytes() != s.read_bytes()]
    if conflicts and not args.force:
        print('Stopped: these files already exist with different content (use --force to overwrite):')
        print(*(f'  {c}' for c in conflicts), sep='\n')
        sys.exit(1)
    for source, dest in plan:
        print(f"{'would copy' if args.dry_run else 'copy'} {rel(source)} -> {dest}")
        if not args.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
    print('npm packages needed:', ', '.join(npm) or '(none)')
    for ref in unmatched:
        print(f'Not in library, supply it yourself: public/{ref}')
    for source, spec in broken:
        print(f'Broken import to fix by hand: {source}: {spec}')


def cmd_stats(_args):
    cards = load_cards()
    gallery = load_gallery()
    print(f'库根目录: {ROOT}')
    print(f'配方卡: {len(cards)} | 样式: {sum(len(c.get("styles", [])) for c in gallery.values())}'
          f' | TSX: {len(list(DEMOS.rglob("*.tsx")))}'
          f' | 样片: {len(list((ROOT / "gallery" / "media").rglob("*.mp4")))}')
    counts = {}
    for card in cards.values():
        counts[card['category']] = counts.get(card['category'], 0) + 1
    for name, count in sorted(counts.items()):
        print(f'  {name}: {count}')


def cmd_doctor(_args):
    cards = load_cards()
    gallery = load_gallery()
    errors, warnings = [], []
    referenced = set()
    for card in cards.values():
        name = card['name']
        declared = card['fields'].get('name')
        if declared != name:
            errors.append(f'{name}: front matter name is {declared!r}')
        for field in REQUIRED_FIELDS:
            if field not in card['fields']:
                errors.append(f'{name}: missing field {field}')
        for section in REQUIRED_SECTIONS:
            if section not in card['sections']:
                errors.append(f'{name}: missing section {section}')
        files, missing = demo_files(card)
        if missing:
            errors.append(f'{name}: 参考实现 points to missing {missing}')
        if not files:
            errors.append(f'{name}: no demo source resolved')
        local, _, static, broken = closure(files)
        referenced.update(local)
        for source, spec in broken:
            errors.append(f'{name}: unresolved import in {source}: {spec}')
        for ref in static:
            if not static_sources(ref):
                warnings.append(f'{name}: staticFile({ref}) is not in demos/_textures')
        if name not in gallery:
            errors.append(f'{name}: not in gallery/api/library.json')
        for media in media_paths(gallery.get(name)):
            if not media['path'].is_file():
                errors.append(f'{name}: missing sample {rel(media["path"])}')
        copy = ROOT / 'gallery' / 'source' / f'{name}.md'
        if copy.is_file() and copy.read_bytes() != card['path'].read_bytes():
            warnings.append(f'{name}: gallery/source copy differs from the recipe')
    for name in gallery:
        if name not in cards:
            errors.append(f'{name}: in library.json but has no recipe')
    tsx = {p.resolve() for p in DEMOS.rglob('*.tsx') if '_fixtures' not in p.parts}
    for orphan in sorted(tsx - set(referenced)):
        warnings.append(f'{rel(orphan)}: no card references this demo')
    offline = ROOT / 'gallery' / 'library-offline-data.js'
    if offline.is_file():
        payload = offline.read_text(encoding='utf-8').split('=', 1)[1].strip().rstrip(';')
        offline_names = {c['name'] for c in json.loads(payload).get('cards', [])}
        if offline_names != set(gallery):
            warnings.append('gallery/library-offline-data.js is out of sync with library.json')
    manifest = ROOT / 'PACKAGE-MANIFEST.json'
    if manifest.is_file():
        listed = {f['path'] for f in json.loads(manifest.read_text(encoding='utf-8')).get('files', [])}
        absent = [p for p in listed if not (ROOT / p).is_file()]
        if absent:
            warnings.append(f'{len(absent)} files in PACKAGE-MANIFEST.json no longer exist (normal after an update)')
    print(f'Checked {len(cards)} cards in {ROOT}')
    print(*(f'ERROR {e}' for e in errors), sep='\n') if errors else None
    print(*(f'WARN  {w}' for w in warnings), sep='\n') if warnings else None
    print(f'{len(errors)} errors, {len(warnings)} warnings')
    sys.exit(1 if errors else 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('stats').set_defaults(run=cmd_stats)
    sub.add_parser('doctor').set_defaults(run=cmd_doctor)
    search = sub.add_parser('search')
    search.add_argument('query')
    search.add_argument('--category')
    search.add_argument('--limit', type=int, default=8)
    search.set_defaults(run=cmd_search)
    show = sub.add_parser('show')
    show.add_argument('card')
    show.add_argument('--json', action='store_true')
    show.set_defaults(run=cmd_show)
    copy = sub.add_parser('copy')
    copy.add_argument('card')
    copy.add_argument('--to', required=True)
    copy.add_argument('--src-dir', default='src/motion')
    copy.add_argument('--demo', help='only copy demos whose file name contains this text')
    copy.add_argument('--dry-run', action='store_true')
    copy.add_argument('--force', action='store_true')
    copy.set_defaults(run=cmd_copy)
    args = parser.parse_args()
    args.run(args)


if __name__ == '__main__':
    main()
