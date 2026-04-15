#!/usr/bin/env python3
import argparse
import json
import os
import re
from pathlib import Path

import yaml

SOURCE_EXTS = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'}

BUILTIN = {
    'assert', 'buffer', 'child_process', 'cluster', 'console', 'constants', 'crypto',
    'dgram', 'diagnostics_channel', 'dns', 'domain', 'events', 'fs', 'http', 'http2',
    'https', 'inspector', 'module', 'net', 'os', 'path', 'perf_hooks', 'process',
    'punycode', 'querystring', 'readline', 'repl', 'stream', 'string_decoder', 'sys',
    'timers', 'tls', 'trace_events', 'tty', 'url', 'util', 'v8', 'vm', 'wasi',
    'worker_threads', 'zlib'
}
BUILTIN |= {f'node:{b}' for b in BUILTIN}

RE_FROM = re.compile(r"from\s+['\"]([^'\"]+)['\"]")
RE_REQ = re.compile(r"require\(\s*['\"]([^'\"]+)['\"]\s*\)")
RE_DYN = re.compile(r"import\(\s*['\"]([^'\"]+)['\"]\s*\)")


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def norm(spec: str):
    if not spec or spec.startswith('.') or spec.startswith('/'):
        return None
    if spec in BUILTIN or spec.startswith('node:'):
        return None
    if spec.startswith('@'):
        parts = spec.split('/')
        return '/'.join(parts[:2]) if len(parts) >= 2 else spec
    return spec.split('/')[0]


def walk(root: Path):
    for base, dirs, files in os.walk(root):
        if os.path.basename(base) in {'node_modules', '.git', 'dist', 'build', '.angular', '.next', 'coverage'}:
            dirs[:] = []
            continue
        for f in files:
            p = Path(base) / f
            if p.suffix in SOURCE_EXTS:
                yield p


def read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return None


def resolve_dts(project_root: Path, pkg: str):
    pkg_dir = project_root / 'node_modules' / pkg
    pj = read_json(pkg_dir / 'package.json')
    if not pj:
        return None

    candidates = []
    for k in ('types', 'typings'):
        v = pj.get(k)
        if isinstance(v, str):
            candidates.append(v)

    ex = pj.get('exports')
    stack = [ex]
    while stack:
        v = stack.pop()
        if isinstance(v, str):
            if v.endswith('.d.ts') or v.endswith('.d.mts'):
                candidates.append(v)
        elif isinstance(v, dict):
            for k in ('types', 'typings'):
                vv = v.get(k)
                if isinstance(vv, str):
                    candidates.append(vv)
            stack.extend(v.values())

    m = pj.get('main')
    if isinstance(m, str):
        candidates.append(re.sub(r'\.js$', '.d.ts', m))
    candidates += ['index.d.ts', 'index.d.mts']

    seen = set()
    for c in candidates:
        if not c:
            continue
        c = c.replace('./', '')
        if c in seen:
            continue
        seen.add(c)
        p = pkg_dir / c
        if p.exists() and p.is_file():
            return p
    return None


def collect_dts_files(project_root: Path, pkg: str):
    pkg_dir = project_root / 'node_modules' / pkg
    files = []
    primary = resolve_dts(project_root, pkg)
    if primary and primary.exists():
        files.append(primary)

    runtime_dir = pkg_dir / 'runtime'
    if runtime_dir.exists() and runtime_dir.is_dir():
        for p in runtime_dir.rglob('*'):
            if p.is_file() and (p.name.endswith('.d.ts') or p.name.endswith('.d.mts')):
                files.append(p)

    seen = set()
    out = []
    for p in files:
        s = str(p)
        if s in seen:
            continue
        seen.add(s)
        out.append(p)
    return out


def split_params(s: str):
    s = s.strip()
    if not s:
        return []
    out, cur, depth = [], [], 0
    for ch in s:
        if ch in '(<[{':
            depth += 1
        elif ch in ')>]}' and depth > 0:
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(''.join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        out.append(''.join(cur).strip())

    parsed = []
    for p in out:
        if ':' in p:
            n, t = p.split(':', 1)
            parsed.append({'name': n.strip(), 'type': t.strip()})
        else:
            parsed.append({'name': p.strip(), 'type': 'unknown'})
    return parsed


def prune_empty(node):
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            pv = prune_empty(v)
            if pv in ({}, [], None, ''):
                continue
            out[k] = pv
        return out
    if isinstance(node, list):
        out = [prune_empty(v) for v in node]
        return [v for v in out if v not in ({}, [], None, '')]
    return node


def parse_api(text: str):
    lines = text.splitlines()
    result = {'class': {}, 'struct': {}, 'interface': {}, 'type': {}, 'alias': {}, 'enum': {}, 'object': {}}

    i = 0
    while i < len(lines):
        line = lines[i]
        cm = re.match(r"\s*(?:export\s+)?(?:declare\s+)?class\s+([A-Za-z_$][\w$]*)", line)
        im = re.match(r"\s*(?:export\s+)?(?:declare\s+)?interface\s+([A-Za-z_$][\w$]*)", line)
        em = re.match(r"\s*(?:export\s+)?(?:declare\s+)?enum\s+([A-Za-z_$][\w$]*)", line)
        tm = re.match(r"\s*(?:export\s+)?(?:declare\s+)?type\s+([A-Za-z_$][\w$]*)\s*=\s*(\{)?", line)

        if em:
            result['enum'][em.group(1)] = {'kind': 'enum'}
            i += 1
            continue

        if tm:
            name = tm.group(1)
            has_brace = bool(tm.group(2))
            obj = {'methods': [], 'public_properties': []}
            if has_brace:
                depth = line.count('{') - line.count('}')
                i += 1
                while i < len(lines):
                    l = lines[i]
                    pm = re.match(r"\s*([A-Za-z_$][\w$]*)\??\s*:\s*([^;{}]+);", l)
                    if pm:
                        obj['public_properties'].append({'name': pm.group(1), 'type': pm.group(2).strip()})
                    depth += l.count('{') - l.count('}')
                    i += 1
                    if depth <= 0:
                        break
                result['object'][name] = prune_empty(obj)
                continue

            target = line.split('=', 1)[1].strip() if '=' in line else 'unknown'
            result['alias'][name] = {'target': target}
            i += 1
            continue

        if not cm and not im:
            i += 1
            continue

        kind = 'class' if cm else 'interface'
        name = (cm or im).group(1)
        obj = {'methods': [], 'public_properties': []}
        depth = line.count('{') - line.count('}')
        i += 1
        while i < len(lines):
            l = lines[i]
            if re.search(r"\b(private|protected)\b", l):
                depth += l.count('{') - l.count('}')
                i += 1
                if depth <= 0:
                    break
                continue

            mm = re.match(r"\s*(?:public\s+)?(?:static\s+)?([A-Za-z_$][\w$]*)\s*\(([^;{}]*)\)\s*:\s*([^;{}]+);", l)
            if mm:
                m = {'name': mm.group(1), 'return_type': mm.group(3).strip()}
                params = split_params(mm.group(2))
                if params:
                    m['parameters'] = params
                obj['methods'].append(m)

            pm = re.match(r"\s*(?:public\s+)?([A-Za-z_$][\w$]*)\??\s*:\s*([^;{}]+);", l)
            if pm and '(' not in l:
                obj['public_properties'].append({'name': pm.group(1), 'type': pm.group(2).strip()})

            depth += l.count('{') - l.count('}')
            i += 1
            if depth <= 0:
                break

        result[kind][name] = prune_empty(obj)

    return prune_empty(result)


def merge_type_maps(dst, src):
    for section in ('class', 'struct', 'interface', 'type', 'alias', 'enum', 'object'):
        if section not in src:
            continue
        if section not in dst:
            dst[section] = {}
        for name, body in src[section].items():
            dst[section][name] = body
    return dst


def run(project_root: Path, output_path: Path, source_dirs):
    libs = set()
    for area in source_dirs:
        root = project_root / area
        if not root.exists():
            continue
        for fp in walk(root):
            try:
                txt = fp.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            for rx in (RE_FROM, RE_REQ, RE_DYN):
                for m in rx.finditer(txt):
                    n = norm(m.group(1))
                    if n:
                        libs.add(n)

    out = {
        'metadata': {
            'source_root': str(project_root),
            'libraries_scanned': 0,
            'notes': 'Public classes or similar and public method signatures extracted from referenced local libraries, omitting empty collection properties.'
        },
        'libraries': []
    }

    for lib in sorted(libs):
        dts_files = collect_dts_files(project_root, lib)
        entry = {'name': lib, 'types_file': str(dts_files[0]) if dts_files else None}
        merged = {'class': {}, 'struct': {}, 'interface': {}, 'type': {}, 'alias': {}, 'enum': {}, 'object': {}}
        for dts in dts_files:
            try:
                parsed = parse_api(dts.read_text(encoding='utf-8', errors='ignore'))
                merge_type_maps(merged, parsed)
            except Exception:
                continue
        merged = prune_empty(merged)
        if merged:
            entry['type1'] = merged
        out['libraries'].append(prune_empty(entry))

    out['metadata']['libraries_scanned'] = len(out['libraries'])
    out = prune_empty(out)

    rendered = yaml.dump(
        out,
        Dumper=NoAliasDumper,
        sort_keys=False,
        allow_unicode=False,
        default_flow_style=False,
        indent=2
    )
    output_path.write_text(rendered, encoding='utf-8')
    print(f'Wrote {output_path}')
    print(f"Libraries scanned: {len(out['libraries'])}")


def parse_args():
    p = argparse.ArgumentParser(description='Extract Node.js library interfaces/method signatures from referenced local libraries.')
    p.add_argument('--project-root', required=True, help='Path to target Node.js app root (contains node_modules).')
    p.add_argument('--output', required=True, help='Output YAML file path.')
    p.add_argument('--source-dirs', default='server,client,scripts', help='Comma-separated source dirs relative to project root.')
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    output = Path(args.output).resolve()
    source_dirs = [s.strip() for s in args.source_dirs.split(',') if s.strip()]
    run(project_root, output, source_dirs)
