#!/usr/bin/env python3
import hashlib
import os
import shutil
from pathlib import Path
from typing import Dict, List

from common import (
    DEFAULT_ITERATION_ID,
    CURRENT_DIR,
    DIFF_DIR,
    PENDING_PROMOTION_DIR,
    build_parser,
    changes_path,
    generate_merged,
    get_artifact_doc_path,
    implementations_root,
    implementations_container_root,
    pending_promotion_doc_path,
    iter_artifact_doc_paths,
    merged_path,
    normalize_iteration_id,
    now_iso,
    read_yaml,
    safe_main,
    sync_technology_selection_mirrors,
    app_manifest_path,
    bump_patch,
    write_split_merged,
    write_yaml,
)

APP_IDENTIFIER = 'app_main'
IMPLEMENTATION_ID = 'IMPLEMENTATION_01'
REQ_SET_ID = 'requirements-set'
BASE_VERSION = '1.0.0'
DEFAULT_TARGET_VERSION = '1.1.0'

REQUIREMENT_DOC_TYPES = {
    'functional_requirements': {'req_type': 'functional', 'bucket': 'functional'},
    'non_functional_requirements': {'req_type': 'non_functional', 'bucket': 'non_functional'},
    'acceptance_tests': {'req_type': 'acceptance_tests', 'bucket': 'acceptance_tests'},
    'acceptance_criteria': {'req_type': 'acceptance_criteria', 'bucket': 'acceptance_criteria'},
    'technology_selection': {'req_type': 'technology_selection', 'bucket': 'technology_selection'},
    'models_and_contracts': {'req_type': 'models_and_contracts', 'bucket': 'models_and_contracts'},
    'data_and_api_contracts': {'req_type': 'models_and_contracts', 'bucket': 'models_and_contracts'},
    'contracts_and_models': {'req_type': 'models_and_contracts', 'bucket': 'models_and_contracts'},
}


def make_requirement(
    requirement_id: str,
    title: str,
    description: str,
    req_type: str,
    artifact_type: str,
    created_on_version: str,
    updated_on_version: str,
) -> Dict:
    # Scope is global per implementation (scope.yaml); no globs in requirement traceability
    traceability = {}
    return {
        '$schema': 'http://internal.schemas.com/ai-requirement-draft-01',
        'requirement_id': requirement_id,
        'title': title,
        'description': description,
        'type': req_type,
        'artifact_type': artifact_type,
        'iteration_id': DEFAULT_ITERATION_ID,
        'status': 'active',
        'versioning': {'created_on_version': created_on_version, 'updated_on_version': updated_on_version},
        'traceability': traceability,
    }


def pick_bucket(req_type: str) -> str:
    if req_type == 'non_functional':
        return 'non_functional'
    if req_type == 'acceptance_tests':
        return 'acceptance_tests'
    if req_type == 'acceptance_criteria':
        return 'acceptance_criteria'
    if req_type == 'technology_selection':
        return 'technology_selection'
    return 'functional'


def infer_req_type(doc_type: str) -> str:
    return REQUIREMENT_DOC_TYPES[doc_type]['req_type']


def normalize_item(doc_type: str, item: Dict) -> Dict:
    rid = item.get('id')
    if not rid:
        body = str(item)
        rid = f"{doc_type.upper()}-{hashlib.sha1(body.encode('utf-8')).hexdigest()[:8]}"

    if item.get('text'):
        description = str(item.get('text'))
    elif item.get('description'):
        description = str(item.get('description'))
    elif item.get('term'):
        description = f"{item.get('term')}: {item.get('text','')}"
    else:
        description = str(item)

    section = item.get('section') or item.get('category')
    if not section:
        sp = item.get('section_path')
        if isinstance(sp, list) and sp:
            section = ' / '.join(str(x) for x in sp)
    entity = item.get('entity')
    if entity:
        section = f"{entity}{' / ' + section if section else ''}"

    title = str(item.get('capability') or item.get('name') or f"{(section or doc_type)}: {rid}")
    req_type = infer_req_type(doc_type)
    created_on_version = str(item.get('created_version') or BASE_VERSION)
    updated_on_version = str(item.get('updated_version') or created_on_version)
    req = make_requirement(
        str(rid),
        title,
        description,
        req_type,
        doc_type,
        created_on_version,
        updated_on_version,
    )
    if item.get('replaces_id'):
        req['replaces_id'] = str(item.get('replaces_id'))
    if item.get('acceptance_criteria'):
        req['acceptance_criteria'] = item.get('acceptance_criteria')
    if doc_type == 'technology_selection':
        for ts_field in ('capability', 'name', 'version', 'category', 'decision_ref', 'constraints'):
            if item.get(ts_field) is not None:
                req[ts_field] = item.get(ts_field)
    return req


def extract_requirements_from_yaml(path: str) -> List[Dict]:
    raw = read_yaml(path)
    doc_type = str(raw.get('type') or Path(path).stem)
    if doc_type not in REQUIREMENT_DOC_TYPES:
        return []
    out: List[Dict] = []

    items = raw.get('items', []) or raw.get('entries', []) or []
    for item in items:
        out.append(normalize_item(doc_type, item))

    for p in raw.get('paragraphs', []) or []:
        out.append(normalize_item(doc_type, p))

    return out


def sanitize_current_doc(doc: Dict) -> Dict:
    out = dict(doc or {})
    for key in ("source_path",):
        out.pop(key, None)
    for collection_key in ("items", "paragraphs"):
        items = out.get(collection_key)
        if not isinstance(items, list):
            continue
        cleaned = []
        for item in items:
            if not isinstance(item, dict):
                cleaned.append(item)
                continue
            c = dict(item)
            c.pop("implementation_id", None)
            c.pop("implementation_ids", None)
            c.pop("app_identifier", None)
            cleaned.append(c)
        out[collection_key] = cleaned
    return out


def discover_source_docs(req_root: str) -> Dict[str, Dict]:
    out: Dict[str, Dict] = {}
    roots = [
        os.path.join(req_root, CURRENT_DIR),
        os.path.join(req_root, "02-current"),
        os.path.join(req_root, "04-merged"),
        os.path.join(req_root, "yaml"),
    ]
    for root in roots:
        if not os.path.isdir(root):
            continue
        for fp in sorted(Path(root).rglob("*.yaml")):
            if fp.name == "requirements_index.yaml":
                continue
            if "pending-promotion" in fp.parts or "merged" in fp.parts:
                continue
            raw = read_yaml(str(fp))
            if not isinstance(raw, dict):
                continue
            doc_type = str(raw.get("type") or fp.stem)
            if doc_type in out:
                continue
            out[doc_type] = sanitize_current_doc(raw)
    return out


def discover_mapping_docs(req_root: str) -> Dict[str, Dict]:
    out: Dict[str, Dict] = {}
    impl_root = implementations_root(req_root)
    roots = [
        os.path.join(impl_root, "02-implementation-mapping"),
        os.path.join(impl_root, "implementation_mappings"),
        os.path.join(req_root, "05-implementation-mappings"),
        os.path.join(req_root, "implementation_mappings"),
    ]
    for root in roots:
        if not os.path.isdir(root):
            continue
        for fp in sorted(Path(root).glob("*.yaml")):
            raw = read_yaml(str(fp))
            if not isinstance(raw, dict):
                continue
            req_type = str(raw.get("requirement_type") or fp.stem)
            if not req_type:
                continue
            out[req_type] = raw
        if out:
            return out
    return out


def write_diff_file(fp: str, req: Dict):
    write_yaml(
        fp,
        {
            'requirement_id': req['requirement_id'],
            'diffs': [
                {
                    'seq': 1,
                    'op': 'create',
                    'version': (req.get('versioning') or {}).get('updated_on_version'),
                    'at': now_iso(),
                    'requirement': req,
                }
            ],
        },
    )


def main() -> None:
    parser = build_parser('Bootstrap requirements into diff/merged/changes model')
    args = parser.parse_args()
    req_root = args.requirements_path
    impl_root_parent = implementations_root(req_root)
    prev_control = read_yaml(changes_path(req_root)) if os.path.exists(changes_path(req_root)) else {}
    app_manifest = {}
    if args.app_path:
        ap = app_manifest_path(args.app_path)
        if os.path.exists(ap):
            app_manifest = read_yaml(ap)

    req_set_id = str(
        app_manifest.get("requirement_set_id")
        or prev_control.get("requirement_set_id")
        or REQ_SET_ID
    )
    app_identifier = str(
        app_manifest.get("app_identifier")
        or prev_control.get("app_identifier")
        or APP_IDENTIFIER
    )
    implementation_id = str(app_manifest.get("implementation_id") or IMPLEMENTATION_ID)
    # Requirements versioning is driven by control.yaml / requirements manifest only.
    # App manifest versions are never used as input for requirements versioning.
    base_version = str(
        prev_control.get("current_version")
        or BASE_VERSION
    )
    target_version = str(
        prev_control.get("next_version")
        or bump_patch(base_version)
        or DEFAULT_TARGET_VERSION
    )

    source_docs = discover_source_docs(req_root)
    mapping_docs = discover_mapping_docs(req_root)

    # full replace model
    for rel in [
        f'{DIFF_DIR}/functional',
        f'{DIFF_DIR}/non_functional',
        f'{DIFF_DIR}/acceptance_tests',
        f'{DIFF_DIR}/acceptance_criteria',
        f'{DIFF_DIR}/technology_selection',
        f'{DIFF_DIR}/history',
        CURRENT_DIR,
        f'{CURRENT_DIR}/merged',
        PENDING_PROMOTION_DIR,
        impl_root_parent,
    ]:
        p = os.path.join(req_root, rel)
        if os.path.exists(p):
            shutil.rmtree(p)
        os.makedirs(p, exist_ok=True)
    # Remove legacy pending layout if present.
    for legacy in [
        'changes',
        'changes/pending.yaml',
        'changes/structured-diff.yaml',
        # Legacy pending files are app-specific; clean any matching pattern.
        'changes/types',
        'changes/pending-promotion',
        'changes/pending-implementation',
        'diffs',
        'merged',
        'implementation_mappings',
        '01-pending-implementation',
        '02-current',
        '03-diff',
        '04-merged',
        '05-implementation-mappings',
        '06-implementation-plan',
        '07-implementation-plan-history',
        'agent-state',
    ]:
        lp = os.path.join(req_root, legacy)
        if os.path.isdir(lp):
            shutil.rmtree(lp)
        elif os.path.exists(lp):
            os.remove(lp)

    for doc_type, raw in sorted(source_docs.items()):
        canonical = get_artifact_doc_path(req_root, doc_type, create_dirs=True)
        write_yaml(canonical, raw)

    files = iter_artifact_doc_paths(req_root)

    seen = set()
    doc_types = set()
    included_docs = 0
    skipped_docs = 0
    for full_path in files:
        doc_type = str(read_yaml(full_path).get('type') or Path(full_path).stem)
        doc_types.add(doc_type)
        reqs = extract_requirements_from_yaml(full_path)
        if doc_type in REQUIREMENT_DOC_TYPES:
            included_docs += 1
        else:
            skipped_docs += 1
        for r in reqs:
            rid = r['requirement_id']
            if rid in seen:
                continue
            seen.add(rid)
            bucket = pick_bucket(r['type'])
            out = os.path.join(req_root, DIFF_DIR, bucket, f"{rid}.yaml")
            write_diff_file(out, r)

    write_yaml(
        changes_path(req_root),
        {
            'requirement_set_id': req_set_id,
            'app_identifier': app_identifier,
            'iteration_id': normalize_iteration_id(prev_control.get('iteration_id'), DEFAULT_ITERATION_ID),
            'current_version': base_version,
            'next_version': target_version,
        },
    )
    for dt in sorted(doc_types):
        src_path = get_artifact_doc_path(req_root, dt, create_dirs=False)
        src = read_yaml(src_path) if os.path.exists(src_path) else {}
        pending_doc = {
            'schema_version': src.get('schema_version', 1),
            'type': src.get('type', dt),
            'generated_at': src.get('generated_at', now_iso().split('T')[0]),
            'items': [],
        }
        if 'paragraphs' in src:
            pending_doc['paragraphs'] = []
        write_yaml(
            pending_promotion_doc_path(req_root, dt, create_dirs=True),
            pending_doc,
        )
    impls_root = implementations_container_root(req_root)
    os.makedirs(impls_root, exist_ok=True)
    write_yaml(
        os.path.join(impl_root_parent, "manifest.yaml"),
        {
            "requirement_set_id": req_set_id,
            "app_identifier": app_identifier,
            "implementations_root": "01-implementations",
            "implementation_mappings_root": "02-implementation-mapping",
        },
    )
    impl_root = os.path.join(impls_root, implementation_id)
    os.makedirs(os.path.join(impl_root, "01-delta-current"), exist_ok=True)
    os.makedirs(os.path.join(impl_root, "02-delta-history"), exist_ok=True)
    os.makedirs(os.path.join(impl_root, "03-ai-plan-current"), exist_ok=True)
    os.makedirs(os.path.join(impl_root, "04-ai-plan-history"), exist_ok=True)
    os.makedirs(os.path.join(impl_root, "05-ai-plan"), exist_ok=True)
    write_yaml(
        os.path.join(impl_root, f"{implementation_id}.manifest.yaml"),
        {
            "implementation_id": implementation_id,
            "app_path": args.app_path,
            "app_manifest_path": os.path.join(args.app_path or "", ".aidev/requirements/requirements-state.yaml"),
            "app_identifier": app_identifier,
            "delta_file": "02-delta-history/01-delta-current.yaml",
            "delta_history_dir": "02-delta-history",
            "plan_history_dir": "04-ai-plan-history",
            "plan_current_dir": "03-ai-plan-current",
            "plan_dir": "05-ai-plan",
        },
    )
    write_yaml(
        os.path.join(impl_root, "02-delta-history", "01-delta-current.yaml"),
        {
            "generated_at": now_iso(),
            "implementation_id": implementation_id,
            "summary": {"added": 0, "updated": 0, "removed": 0},
            "delta": {"added": [], "updated": [], "removed": []},
        },
    )
    mappings_root = os.path.join(impl_root_parent, "02-implementation-mapping")
    os.makedirs(mappings_root, exist_ok=True)
    if mapping_docs:
        for req_type, doc in sorted(mapping_docs.items()):
            write_yaml(os.path.join(mappings_root, f"{req_type}.yaml"), doc)
    else:
        for req_type in sorted(doc_types):
            write_yaml(
                os.path.join(mappings_root, f"{req_type}.yaml"),
                {
                    "requirement_type": req_type,
                    "default_implementation_ids": ["*"],
                    "mappings": [],
                },
            )
    write_yaml(merged_path(req_root), generate_merged(req_root, req_set_id))
    write_split_merged(req_root)
    sync_technology_selection_mirrors(req_root, PENDING_PROMOTION_DIR, [implementation_id])
    sync_technology_selection_mirrors(req_root, CURRENT_DIR, [implementation_id])
    print(
        'Bootstrapped requirements model '
        f'(full replace, docs considered: {len(files)}, included FR/NFR docs: {included_docs}, '
        f'skipped artifact docs: {skipped_docs}, requirements: {len(seen)})'
    )


if __name__ == '__main__':
    safe_main(main, 'bootstrap_core')
