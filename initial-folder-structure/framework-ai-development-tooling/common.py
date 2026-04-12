import argparse
import datetime as dt
import glob
import os
import re
from pathlib import Path
from fnmatch import fnmatch
from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

import yaml

MANIFEST_REL_PATH = "manifests/requirements-manifest.yaml"
PENDING_PROMOTION_DIR = "01-pending-promotion"
DIFF_DIR = "02-diff"
CURRENT_DIR = "03-current"
IMPLEMENTATIONS_DIR = "02-implementation"
IMPLEMENTATIONS_CONTAINER_DIR = "01-implementations"
IMPLEMENTATION_MAPPINGS_DIRNAME = "02-implementation-mapping"
REQUIREMENTS_MANIFEST_REL_PATH = "manifest.yaml"

MERGED_REL_PATH = f"{CURRENT_DIR}/merged/merged_requirements.yaml"
DECISIONS_REL_PATH = f"{CURRENT_DIR}/decisions.yaml"
TECHNOLOGY_SELECTION_REL_PATH = f"{CURRENT_DIR}/technology_selection.yaml"
PENDING_TECH_SELECTIONS_DIR = f"{PENDING_PROMOTION_DIR}/technology_selection"
CURRENT_TECH_SELECTIONS_DIR = f"{CURRENT_DIR}/technology_selection"
CHANGES_REL_PATH = f"{PENDING_PROMOTION_DIR}/_control.yaml"
DEFAULT_ITERATION_ID = 1

CANONICAL_ARTIFACT_REL_PATHS = {
    "functional_requirements": f"{CURRENT_DIR}/functional_requirements.yaml",
    "non_functional_requirements": f"{CURRENT_DIR}/non_functional_requirements.yaml",
    "acceptance_tests": f"{CURRENT_DIR}/acceptance_tests.yaml",
    "acceptance_criteria": f"{CURRENT_DIR}/acceptance_criteria.yaml",
    "technology_selection": f"{CURRENT_DIR}/technology_selection.yaml",
    "ui_contracts": f"{CURRENT_DIR}/ui_contracts.yaml",
    "api_contracts": f"{CURRENT_DIR}/api_contracts.yaml",
    "data_and_api_contracts": f"{CURRENT_DIR}/data_and_api_contracts.yaml",
    "models_and_contracts": f"{CURRENT_DIR}/models_and_contracts.yaml",
    # Backward compatibility alias.
    "data_contracts": f"{CURRENT_DIR}/data_and_api_contracts.yaml",
    "contracts_and_models": f"{CURRENT_DIR}/models_and_contracts.yaml",
}

GROUPED_REQUIREMENT_REL_DIRS: Dict[str, str] = {}

DIFF_BUCKETS_BY_ARTIFACT_TYPE = {
    "functional_requirements": "functional",
    "non_functional_requirements": "non_functional",
    "acceptance_tests": "acceptance_tests",
    "acceptance_criteria": "acceptance_criteria",
    "technology_selection": "technology_selection",
    "models_and_contracts": "models_and_contracts",
    "data_and_api_contracts": "models_and_contracts",
    "contracts_and_models": "models_and_contracts",
}

REQUIREMENT_TYPE_TO_ARTIFACT = {
    "functional_requirements": "functional_requirements",
    "non_functional_requirements": "non_functional_requirements",
    "data_and_api_contracts": "data_and_api_contracts",
    "data_contracts": "data_and_api_contracts",
    "models_and_contracts": "models_and_contracts",
    "contracts_and_models": "models_and_contracts",
    "technology_selection": "technology_selection",
    "acceptance_criteria": "acceptance_criteria",
    "acceptance_tests": "acceptance_tests",
}


def normalize_iteration_id(value: Any, default: int = DEFAULT_ITERATION_ID) -> int:
    if value is None:
        return int(default)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        s = value.strip()
        if s == "":
            return int(default)
        if s.isdigit():
            return int(s)
        m = re.fullmatch(r"ITER-(\d+)", s)
        if m:
            return int(m.group(1))
    raise ValueError(f"Invalid iteration_id value: {value!r}")


def now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-r", "--requirements-path", required=True)
    parser.add_argument("-a", "--app-path", default=None)
    parser.add_argument("--implementation-id", default=None)
    parser.add_argument("--all-implementations", action="store_true")
    return parser


def read_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def write_yaml(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=False)


def get_artifact_doc_path(requirements_path: str, requirement_type: str, create_dirs: bool = False) -> str:
    canonical_rel = CANONICAL_ARTIFACT_REL_PATHS.get(
        requirement_type, f"{CURRENT_DIR}/{requirement_type}.yaml"
    )
    canonical_abs = os.path.join(requirements_path, canonical_rel)
    if create_dirs:
        os.makedirs(os.path.dirname(canonical_abs), exist_ok=True)
        return canonical_abs
    return canonical_abs


def iter_artifact_doc_paths(requirements_path: str) -> List[str]:
    current_root = os.path.join(requirements_path, CURRENT_DIR)
    out: List[str] = []
    if os.path.isdir(current_root):
        for fp in sorted(Path(current_root).rglob("*.yaml")):
            if fp.name == "requirements_index.yaml":
                continue
            if "merged" in fp.parts:
                continue
            out.append(str(fp))
    return out


def grouped_rel_dir_for_requirement_type(requirement_type: str) -> str:
    return GROUPED_REQUIREMENT_REL_DIRS.get(requirement_type, requirement_type)


def pending_promotion_doc_path(
    requirements_path: str, requirement_type: str, create_dirs: bool = False
) -> str:
    out = os.path.join(
        requirements_path, PENDING_PROMOTION_DIR, f"{requirement_type}.yaml"
    )
    if create_dirs:
        os.makedirs(os.path.dirname(out), exist_ok=True)
    return out


def iter_pending_promotion_doc_paths(requirements_path: str) -> List[str]:
    root = os.path.join(requirements_path, PENDING_PROMOTION_DIR)
    out: List[str] = []
    if not os.path.isdir(root):
        return out
    for fp in sorted(Path(root).rglob("*.yaml")):
        if fp.name in {"_control.yaml", "structured-diff.yaml"}:
            continue
        out.append(str(fp))
    return out


def implementation_dir(requirements_path: str, implementation_id: str, create_dirs: bool = False) -> str:
    out = os.path.join(implementations_container_root(requirements_path), implementation_id)
    if create_dirs:
        os.makedirs(out, exist_ok=True)
    return out


def implementation_manifest_path(requirements_path: str, implementation_id: str, create_dirs: bool = False) -> str:
    root = implementation_dir(requirements_path, implementation_id, create_dirs=create_dirs)
    return os.path.join(root, f"{implementation_id}.manifest.yaml")


def implementation_delta_path(requirements_path: str, implementation_id: str, create_dirs: bool = False) -> str:
    """Current delta document path; stored in 02-delta-history so 01-delta-current/ holds only structured-diff.yaml."""
    root = implementation_dir(requirements_path, implementation_id, create_dirs=create_dirs)
    out_dir = os.path.join(root, "02-delta-history")
    if create_dirs:
        os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, "01-delta-current.yaml")


def implementation_structured_diff_path(
    requirements_path: str, implementation_id: str, create_dirs: bool = False
) -> str:
    """Only artifact under 01-delta-current/ is structured-diff.yaml."""
    root = implementation_dir(requirements_path, implementation_id, create_dirs=create_dirs)
    out_dir = os.path.join(root, "01-delta-current")
    if create_dirs:
        os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, "structured-diff.yaml")


def implementation_delta_history_dir(requirements_path: str, implementation_id: str, create_dirs: bool = False) -> str:
    root = implementation_dir(requirements_path, implementation_id, create_dirs=create_dirs)
    out = os.path.join(root, "02-delta-history")
    if create_dirs:
        os.makedirs(out, exist_ok=True)
    return out


def implementation_plan_history_dir(requirements_path: str, implementation_id: str, create_dirs: bool = False) -> str:
    root = implementation_dir(requirements_path, implementation_id, create_dirs=create_dirs)
    out = os.path.join(root, "04-ai-plan-history")
    if create_dirs:
        os.makedirs(out, exist_ok=True)
    return out


def implementation_plan_current_dir(requirements_path: str, implementation_id: str, create_dirs: bool = False) -> str:
    root = implementation_dir(requirements_path, implementation_id, create_dirs=create_dirs)
    out = os.path.join(root, "03-ai-plan-current")
    if create_dirs:
        os.makedirs(out, exist_ok=True)
    return out


def implementation_plan_dir(requirements_path: str, implementation_id: str, create_dirs: bool = False) -> str:
    root = implementation_dir(requirements_path, implementation_id, create_dirs=create_dirs)
    out = os.path.join(root, "05-ai-plan")
    if create_dirs:
        os.makedirs(out, exist_ok=True)
    return out


def app_manifest_path(app_path: str) -> str:
    return os.path.join(app_path, MANIFEST_REL_PATH)


def merged_path(requirements_path: str) -> str:
    return os.path.join(requirements_path, MERGED_REL_PATH)


def decisions_path(requirements_path: str) -> str:
    return os.path.join(requirements_path, DECISIONS_REL_PATH)


def get_decisions(requirements_path: str) -> Dict[str, Any]:
    """Load decisions from 03-current/decisions.yaml if present; else return empty structure."""
    fp = decisions_path(requirements_path)
    if not os.path.exists(fp):
        return {"schema_version": 1, "type": "decisions", "items": []}
    return read_yaml(fp) or {"schema_version": 1, "type": "decisions", "items": []}


def technology_selection_path(requirements_path: str) -> str:
    return os.path.join(requirements_path, TECHNOLOGY_SELECTION_REL_PATH)


def stage_technology_selection_path(requirements_path: str, stage_dir: str) -> str:
    return os.path.join(requirements_path, stage_dir, "technology_selection.yaml")


def technology_selection_mirror_path(
    requirements_path: str,
    stage_dir: str,
    implementation_id: str,
    create_dirs: bool = False,
) -> str:
    fp = os.path.join(
        requirements_path,
        stage_dir,
        "technology_selection",
        f"technology_selections_{implementation_id}.yaml",
    )
    if create_dirs:
        os.makedirs(os.path.dirname(fp), exist_ok=True)
    return fp


def _technology_entry_matches(entry: Dict[str, Any], implementation_id: str) -> bool:
    """True if this entry applies to the given implementation_id.

    Reads ``implementation_ids`` (array).  Falls back to the legacy scalar
    ``implementation_id`` for backward compatibility.  When neither is present
    the entry matches all implementations (wildcard default).
    """
    impl_ids = entry.get("implementation_ids")
    if impl_ids is None:
        legacy = entry.get("implementation_id")
        impl_ids = [str(legacy)] if legacy is not None else ["*"]
    try:
        str_ids = [str(x) for x in impl_ids]
    except (TypeError, ValueError):
        return False
    if "*" in str_ids:
        return True
    return any(
        fnmatch(implementation_id, pat) if "*" in pat else pat == implementation_id
        for pat in str_ids
    )


def get_technology_selection_raw(requirements_path: str) -> Dict[str, Any]:
    """Load full technology-selection.yaml (all entries, no filtering)."""
    fp = technology_selection_path(requirements_path)
    if not os.path.exists(fp):
        return {"schema_version": 1, "type": "technology_selection", "entries": []}
    return read_yaml(fp) or {"schema_version": 1, "type": "technology_selection", "entries": []}


def get_stage_technology_selection_raw(requirements_path: str, stage_dir: str) -> Dict[str, Any]:
    fp = stage_technology_selection_path(requirements_path, stage_dir)
    if not os.path.exists(fp):
        return {"schema_version": 1, "type": "technology_selection", "entries": []}
    return read_yaml(fp) or {"schema_version": 1, "type": "technology_selection", "entries": []}


_TS_STRIP_KEYS = {"implementation_id", "implementation_ids"}


def get_technology_selection(
    requirements_path: str, implementation_id: str
) -> Dict[str, Any]:
    """Load technology-selection.yaml and return entries filtered by implementation_id."""
    fp = technology_selection_path(requirements_path)
    default = {
        "schema_version": 1,
        "type": "technology_selection",
        "implementation_id": implementation_id,
        "entries": [],
    }
    if not os.path.exists(fp):
        return default
    doc = read_yaml(fp) or {}
    raw_entries = doc.get("entries")
    if not isinstance(raw_entries, list):
        return default
    filtered = [
        {k: v for k, v in e.items() if k not in _TS_STRIP_KEYS}
        for e in raw_entries
        if isinstance(e, dict) and _technology_entry_matches(e, implementation_id)
    ]
    return {
        "schema_version": doc.get("schema_version", 1),
        "type": doc.get("type", "technology_selection"),
        "implementation_id": implementation_id,
        "entries": filtered,
    }


def get_stage_technology_selection(
    requirements_path: str, stage_dir: str, implementation_id: str
) -> Dict[str, Any]:
    fp = stage_technology_selection_path(requirements_path, stage_dir)
    default = {
        "schema_version": 1,
        "type": "technology_selection",
        "implementation_id": implementation_id,
        "entries": [],
    }
    if not os.path.exists(fp):
        return default
    doc = read_yaml(fp) or {}
    raw_entries = doc.get("entries")
    if not isinstance(raw_entries, list):
        return default
    filtered = [
        {k: v for k, v in e.items() if k not in _TS_STRIP_KEYS}
        for e in raw_entries
        if isinstance(e, dict) and _technology_entry_matches(e, implementation_id)
    ]
    return {
        "schema_version": doc.get("schema_version", 1),
        "type": doc.get("type", "technology_selection"),
        "generated_at": doc.get("generated_at"),
        "implementation_id": implementation_id,
        "entries": filtered,
    }


def sync_technology_selection_mirror(
    requirements_path: str,
    stage_dir: str,
    implementation_id: str,
) -> str:
    doc = get_stage_technology_selection(requirements_path, stage_dir, implementation_id)
    out = {
        "schema_version": doc.get("schema_version", 1),
        "type": doc.get("type", "technology_selection"),
        "entries": doc.get("entries", []),
    }
    if doc.get("generated_at") is not None:
        out["generated_at"] = doc.get("generated_at")
    fp = technology_selection_mirror_path(
        requirements_path, stage_dir, implementation_id, create_dirs=True
    )
    write_yaml(fp, out)
    return fp


def sync_technology_selection_mirrors(
    requirements_path: str,
    stage_dir: str,
    implementation_ids: List[str],
) -> List[str]:
    written: List[str] = []
    for implementation_id in sorted({str(x) for x in implementation_ids if x}):
        written.append(sync_technology_selection_mirror(requirements_path, stage_dir, implementation_id))
    return written


def changes_path(requirements_path: str) -> str:
    return os.path.join(requirements_path, CHANGES_REL_PATH)


def requirements_manifest_path(requirements_path: str) -> str:
    return os.path.join(requirements_path, REQUIREMENTS_MANIFEST_REL_PATH)


def implementations_root(requirements_path: str) -> str:
    return os.path.join(os.path.dirname(requirements_path), IMPLEMENTATIONS_DIR)


def implementations_container_root(requirements_path: str) -> str:
    return os.path.join(implementations_root(requirements_path), IMPLEMENTATIONS_CONTAINER_DIR)


def get_app_manifest(app_path: str) -> Dict[str, Any]:
    return read_yaml(app_manifest_path(app_path))


def get_app_requirement_set_id(app_path: str) -> str:
    rid = get_app_manifest(app_path).get("requirement_set_id")
    if not rid:
        raise ValueError(f"App manifest missing requirement_set_id: {app_manifest_path(app_path)}")
    return str(rid)


def get_app_identifier(app_path: str) -> str:
    aid = get_app_manifest(app_path).get("app_identifier")
    if not aid:
        raise ValueError(f"App manifest missing app_identifier: {app_manifest_path(app_path)}")
    return str(aid)


def get_app_iteration_id(app_path: str) -> int:
    it = get_app_manifest(app_path).get("iteration_id")
    if not it:
        raise ValueError(f"App manifest missing iteration_id: {app_manifest_path(app_path)}")
    return normalize_iteration_id(it)


def get_app_requirements_version_target(app_path: str) -> str:
    v = get_app_manifest(app_path).get("requirements_version_target")
    if not v:
        raise ValueError(f"App manifest missing requirements_version_target: {app_manifest_path(app_path)}")
    return str(v)


def get_app_requirements_version_implemented(app_path: str) -> str:
    v = get_app_manifest(app_path).get("requirements_version_implemented")
    if not v:
        raise ValueError(f"App manifest missing requirements_version_implemented: {app_manifest_path(app_path)}")
    return str(v)


def get_app_baseline_requirement_ids(app_path: str) -> List[str]:
    """Return requirement IDs from app manifest requirement_baseline only (versioned source of truth)."""
    manifest = get_app_manifest(app_path)
    out: List[str] = []
    for entry in manifest.get("requirement_baseline", []) or []:
        if isinstance(entry, dict) and entry.get("requirement_id"):
            out.append(str(entry.get("requirement_id")))
    return sorted(set(out))


def get_app_implementation_id(app_path: str) -> str:
    manifest = get_app_manifest(app_path)
    iid = manifest.get("implementation_id")
    if not iid:
        raise ValueError(f"App manifest missing implementation_id: {app_manifest_path(app_path)}")
    return str(iid)


def get_requirements_requirement_set_id(requirements_path: str) -> Optional[str]:
    for fp in [requirements_manifest_path(requirements_path), merged_path(requirements_path), changes_path(requirements_path)]:
        if os.path.exists(fp):
            rid = read_yaml(fp).get("requirement_set_id")
            if rid:
                return str(rid)
    return None


def get_requirements_app_identifier(requirements_path: str) -> Optional[str]:
    fp = requirements_manifest_path(requirements_path)
    if not os.path.exists(fp):
        return None
    doc = read_yaml(fp)
    aid = doc.get("app_identifier") or doc.get("app_id")
    if aid:
        return str(aid)
    return None


def load_implementations(requirements_path: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    root = implementations_container_root(requirements_path)
    if not os.path.isdir(root):
        return out
    for fp in sorted(Path(root).glob("*/" + "*.manifest.yaml")):
        doc = read_yaml(str(fp))
        impl_id = doc.get("implementation_id")
        if not impl_id:
            impl_id = fp.parent.name
        out.append(
            {
                "implementation_id": str(impl_id),
                "app_identifier": str(doc.get("app_identifier") or ""),
                "app_path": doc.get("app_path"),
                "manifest_path": str(fp),
            }
        )
    return out


def resolve_target_implementations(requirements_path: str, app_path: Optional[str], implementation_id: Optional[str], all_implementations: bool) -> List[Dict[str, Any]]:
    impls = load_implementations(requirements_path)
    if all_implementations:
        if not impls:
            raise ValueError("--all-implementations requested but no implementation manifests were found")
        missing = [x.get("implementation_id") for x in impls if not x.get("app_path")]
        if missing:
            raise ValueError(f"Implementation manifest missing app_path for: {', '.join(str(x) for x in missing)}")
        return impls
    if app_path:
        resolved_impl = implementation_id or get_app_implementation_id(app_path)
        return [{"implementation_id": resolved_impl, "app_identifier": get_app_identifier(app_path), "app_path": app_path}]
    if implementation_id:
        out = [i for i in impls if i.get("implementation_id") == implementation_id]
        if not out:
            raise ValueError(f"implementation_id not found: {implementation_id}")
        return out
    raise ValueError("Specify --app-path, or --implementation-id, or --all-implementations")


def validate_target_for_app(target: Dict[str, Any], requirements_path: str) -> Tuple[str, str]:
    app_path = target.get("app_path")
    if not app_path:
        raise ValueError("Target missing app_path")

    app_req = get_app_requirement_set_id(app_path)
    req_req = get_requirements_requirement_set_id(requirements_path)
    if req_req is None:
        raise ValueError("Requirements data missing requirement_set_id")
    if app_req != req_req:
        raise ValueError(f"requirement_set_id mismatch: app='{app_req}' requirements='{req_req}'")

    app_id = get_app_identifier(app_path)
    req_app_id = get_requirements_app_identifier(requirements_path)
    if not req_app_id:
        raise ValueError(
            f"Requirements manifest missing app_identifier: {requirements_manifest_path(requirements_path)}"
        )
    if req_app_id != app_id:
        raise ValueError(
            f"app_identifier mismatch: app manifest='{app_id}' requirements manifest='{req_app_id}'"
        )

    app_impl_id = get_app_implementation_id(app_path)
    tgt_id = target.get("app_identifier")
    if tgt_id and str(tgt_id) != app_id:
        raise ValueError(f"app_identifier mismatch: target='{tgt_id}' manifest='{app_id}'")
    tgt_impl = target.get("implementation_id")
    if tgt_impl and str(tgt_impl) != app_impl_id:
        raise ValueError(f"implementation_id mismatch: target='{tgt_impl}' manifest='{app_impl_id}'")

    # enforce manifest iteration + requirement version fields exist
    _ = get_app_iteration_id(app_path)
    target_v = get_app_requirements_version_target(app_path)
    implemented_v = get_app_requirements_version_implemented(app_path)
    if compare_versions(target_v, implemented_v) < 0:
        raise ValueError(
            f"requirements version mismatch: implemented='{implemented_v}' cannot be greater than target='{target_v}'"
        )

    return req_req, app_id


def parse_new_value(raw: Any) -> Any:
    if not isinstance(raw, str):
        return raw
    s = raw.strip()
    if s == "":
        return ""
    try:
        return yaml.safe_load(s)
    except Exception:
        return raw


def set_dot_path(obj: Dict[str, Any], path: str, value: Any) -> None:
    keys = path.split('.')
    cur = obj
    for key in keys[:-1]:
        if key not in cur or not isinstance(cur[key], dict):
            cur[key] = {}
        cur = cur[key]
    cur[keys[-1]] = value


def get_diff_files(requirements_path: str) -> List[str]:
    out = []
    for pat in [
        os.path.join(requirements_path, DIFF_DIR, "functional", "*.yaml"),
        os.path.join(requirements_path, DIFF_DIR, "non_functional", "*.yaml"),
        os.path.join(requirements_path, DIFF_DIR, "acceptance_tests", "*.yaml"),
        os.path.join(requirements_path, DIFF_DIR, "acceptance_criteria", "*.yaml"),
        os.path.join(requirements_path, DIFF_DIR, "technology_selection", "*.yaml"),
        os.path.join(requirements_path, DIFF_DIR, "models_and_contracts", "*.yaml"),
    ]:
        out.extend(glob.glob(pat))
    return sorted(out)


def apply_diff_sequence(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    current = None
    for d in sorted(item.get('diffs', []), key=lambda x: x.get('seq', 0)):
        op = d.get('op')
        if op == 'create':
            current = deepcopy(d.get('requirement') or {})
        elif op == 'update' and current is not None:
            for ch in d.get('changes', []):
                field = ch.get('field')
                if field:
                    set_dot_path(current, field, parse_new_value(ch.get('new')))
        elif op == 'remove':
            current = None
    return current


def scope_entry_from_dict(entry: Any) -> Dict[str, List[str]]:
    """Parse scope from an implementation scope.yaml entry only. Do not use for requirement traceability."""
    if not isinstance(entry, dict):
        return {"globs": [], "exclude_globs": []}

    def _norm_list(v: Any) -> List[str]:
        out: List[str] = []
        if not isinstance(v, list):
            return out
        for x in v:
            if isinstance(x, str):
                out.append(x)
        return sorted(set(out))

    return {
        "globs": _norm_list(entry.get("globs")),
        "exclude_globs": _norm_list(entry.get("exclude_globs")),
    }


def has_any_scope(scope: Dict[str, List[str]]) -> bool:
    return bool(scope.get("globs") or [])


def load_global_scope_mappings(requirements_path: str) -> List[Dict[str, Any]]:
    fp = os.path.join(implementation_mappings_dir(requirements_path), "scope.yaml")
    if not os.path.exists(fp):
        return []
    doc = read_yaml(fp)
    entries = doc.get("global_scopes")
    if not isinstance(entries, list):
        return []
    out: List[Dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        impl_id = str(e.get("implementation_id") or "*")
        s = scope_entry_from_dict(e)
        out.append(
            {
                "implementation_id": impl_id,
                "globs": s["globs"],
                "exclude_globs": s["exclude_globs"],
            }
        )
    return out


def get_global_scope_for_implementation(requirements_path: str, implementation_id: str) -> Dict[str, List[str]]:
    mappings = load_global_scope_mappings(requirements_path)
    exact = [m for m in mappings if m.get("implementation_id") == implementation_id]
    wildcard = [
        m
        for m in mappings
        if m.get("implementation_id")
        and "*" in str(m.get("implementation_id"))
        and fnmatch(implementation_id, str(m.get("implementation_id")))
    ]

    exact_non_empty = [m for m in exact if has_any_scope(m)]
    wildcard_non_empty = [m for m in wildcard if has_any_scope(m)]

    if exact_non_empty:
        return merge_scopes(exact_non_empty)
    if wildcard_non_empty:
        return merge_scopes(wildcard_non_empty)
    if exact or wildcard:
        return {"globs": [], "exclude_globs": []}
    return {"globs": [], "exclude_globs": []}


def resolve_scope_for_requirement(
    requirements_path: str, implementation_id: str, _traceability: Any = None
) -> Dict[str, List[str]]:
    """Scope is taken only from implementation folder (scope.yaml). Requirement traceability is not used."""
    return get_global_scope_for_implementation(requirements_path, implementation_id)


def merge_scopes(scopes: List[Dict[str, List[str]]]) -> Dict[str, List[str]]:
    out = {"globs": set(), "exclude_globs": set()}
    for s in scopes:
        if not isinstance(s, dict):
            continue
        for k in ["globs", "exclude_globs"]:
            for v in (s.get(k) or []):
                out[k].add(str(v))
    return {k: sorted(v) for k, v in out.items()}


def strip_requirement_traceability_globs(req: Dict[str, Any]) -> None:
    """Remove globs/exclude_globs from requirement traceability; scope is implementation-only."""
    t = req.get("traceability")
    if isinstance(t, dict):
        t.pop("globs", None)
        t.pop("exclude_globs", None)
        if not t:
            req.pop("traceability", None)


def _load_contracts_doc(requirements_path: str, rel_path: str) -> Dict[str, Any]:
    path = os.path.join(requirements_path, rel_path)
    if not os.path.isfile(path):
        return {}
    return read_yaml(path)


# Requirement type used in merged "requirements" list vs 03-current artifact key.
_CURRENT_ARTIFACT_TO_REQ_TYPE = {
    "functional_requirements": "functional",
    "non_functional_requirements": "non_functional",
    "acceptance_tests": "acceptance_tests",
    "acceptance_criteria": "acceptance_criteria",
    "technology_selection": "technology_selection",
    "api_contracts": "api_contracts",
    "ui_contracts": "ui_contracts",
    "data_and_api_contracts": "data_and_api_contracts",
    "data_contracts": "data_and_api_contracts",
    "models_and_contracts": "models_and_contracts",
    "contracts_and_models": "models_and_contracts",
}


def _normalize_artifact_item_to_requirement(item: Dict[str, Any], req_type: str) -> Dict[str, Any]:
    """Turn a 03-current artifact item (id, text, section/...) into a merged-requirement shape."""
    rid = item.get("id")
    if not rid:
        return {}
    out: Dict[str, Any] = {
        "requirement_id": str(rid),
        "type": req_type,
        "title": str(item.get("title") or item.get("capability") or item.get("name") or item.get("id") or rid),
        "description": str(item.get("text") or item.get("description") or ""),
        "section": item.get("section") or item.get("category"),
        "section_path": item.get("section_path"),
    }
    if item.get("replaces_id") is not None:
        out["replaces_id"] = str(item.get("replaces_id"))
    if item.get("entity") is not None:
        out["entity"] = item.get("entity")
    if item.get("subsection") is not None:
        out["subsection"] = item.get("subsection")
    if item.get("acceptance_criteria") is not None:
        out["acceptance_criteria"] = item.get("acceptance_criteria")
    if req_type == "technology_selection":
        for ts_field in ("capability", "name", "version", "category", "decision_ref", "constraints"):
            if item.get(ts_field) is not None:
                out[ts_field] = item.get(ts_field)
    return out


def _load_current_artifact_requirements(
    requirements_path: str, artifact_key: str
) -> List[Dict[str, Any]]:
    """Load all requirements from a single 03-current artifact (e.g. non_functional_requirements)."""
    rel = CANONICAL_ARTIFACT_REL_PATHS.get(artifact_key)
    if not rel:
        return []
    path = os.path.join(requirements_path, rel)
    if not os.path.isfile(path):
        return []
    doc = read_yaml(path)
    items = doc.get("items") or doc.get("entries") or []
    req_type = _CURRENT_ARTIFACT_TO_REQ_TYPE.get(artifact_key, artifact_key)
    out: List[Dict[str, Any]] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        req = _normalize_artifact_item_to_requirement(it, req_type)
        if req:
            out.append(req)
    return out


def generate_merged(requirements_path: str, requirement_set_id: str) -> Dict[str, Any]:
    reqs = []
    for fp in get_diff_files(requirements_path):
        cur = apply_diff_sequence(read_yaml(fp))
        if cur:
            strip_requirement_traceability_globs(cur)
            reqs.append(cur)
    # Set of requirement_ids already in reqs (from 02-diff).
    existing_ids = {str(r.get("requirement_id") or "") for r in reqs if r.get("requirement_id")}
    # Include every requirement from 03-current artifacts so the diff vs app manifest is complete.
    for artifact_key in [
        "functional_requirements",
        "non_functional_requirements",
        "acceptance_tests",
        "acceptance_criteria",
        "technology_selection",
        "models_and_contracts",
    ]:
        for r in _load_current_artifact_requirements(requirements_path, artifact_key):
            rid = r.get("requirement_id")
            if rid and rid not in existing_ids:
                existing_ids.add(rid)
                reqs.append(r)
    api_contracts = _load_contracts_doc(requirements_path, CANONICAL_ARTIFACT_REL_PATHS["api_contracts"])
    ui_contracts = _load_contracts_doc(requirements_path, CANONICAL_ARTIFACT_REL_PATHS["ui_contracts"])
    for r in _load_current_artifact_requirements(requirements_path, "api_contracts"):
        rid = r.get("requirement_id")
        if rid and rid not in existing_ids:
            existing_ids.add(rid)
            reqs.append(r)
    for r in _load_current_artifact_requirements(requirements_path, "ui_contracts"):
        rid = r.get("requirement_id")
        if rid and rid not in existing_ids:
            existing_ids.add(rid)
            reqs.append(r)
    data_and_api_contracts = _load_contracts_doc(
        requirements_path, CANONICAL_ARTIFACT_REL_PATHS["data_and_api_contracts"]
    )
    if data_and_api_contracts and "version" not in data_and_api_contracts:
        data_and_api_contracts["version"] = "1.0.0"
    for r in _load_current_artifact_requirements(requirements_path, "data_and_api_contracts"):
        rid = r.get("requirement_id")
        if rid and rid not in existing_ids:
            existing_ids.add(rid)
            reqs.append(r)
    reqs.sort(key=lambda x: str(x.get('requirement_id', '')))
    technology_selection = get_technology_selection_raw(requirements_path)
    models_and_contracts = _load_contracts_doc(
        requirements_path, CANONICAL_ARTIFACT_REL_PATHS.get("models_and_contracts", f"{CURRENT_DIR}/models_and_contracts.yaml")
    )
    if models_and_contracts and "version" not in models_and_contracts:
        models_and_contracts["version"] = "1.0.0"
    return {
        'requirement_set_id': requirement_set_id,
        'iteration_id': get_current_iteration_id(requirements_path),
        'requirements_version': get_current_requirements_version(requirements_path),
        'merged_at': now_iso(),
        'technology_selection': technology_selection,
        'api_contracts': api_contracts,
        'ui_contracts': ui_contracts,
        'data_and_api_contracts': data_and_api_contracts,
        'models_and_contracts': models_and_contracts,
        # Backward compatibility field for older consumers.
        'data_contracts': data_and_api_contracts,
        'requirements': reqs,
    }


def get_current_iteration_id(requirements_path: str) -> int:
    cp = changes_path(requirements_path)
    if os.path.exists(cp):
        doc = read_yaml(cp)
        it = doc.get("iteration_id")
        if it is not None:
            return normalize_iteration_id(it)
    return int(DEFAULT_ITERATION_ID)


def get_current_requirements_version(requirements_path: str) -> str:
    cp = changes_path(requirements_path)
    if os.path.exists(cp):
        doc = read_yaml(cp)
        v = doc.get("current_version")
        if v:
            return str(v)
    return "1.0.0"


def implementation_mappings_dir(requirements_path: str) -> str:
    return os.path.join(implementations_root(requirements_path), IMPLEMENTATION_MAPPINGS_DIRNAME)


def load_implementation_mappings(requirements_path: str) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    mdir = implementation_mappings_dir(requirements_path)
    if not os.path.isdir(mdir):
        return out
    for fp in sorted(glob.glob(os.path.join(mdir, "*.yaml"))):
        doc = read_yaml(fp)
        req_type = str(doc.get("requirement_type") or os.path.splitext(os.path.basename(fp))[0])
        default_ids = doc.get("default_implementation_ids")
        if not isinstance(default_ids, list) or not default_ids:
            default_ids = ["*"]
        entries: Dict[str, List[str]] = {}
        for m in doc.get("mappings", []) or []:
            if not isinstance(m, dict):
                continue
            rid = m.get("requirement_id")
            ids = m.get("implementation_ids")
            if not rid:
                continue
            if not isinstance(ids, list) or not ids:
                ids = ["*"]
            entries[str(rid)] = [str(x) for x in ids]
        out[req_type] = {
            "default_implementation_ids": [str(x) for x in default_ids],
            "mappings": entries,
        }
    return out


def applies_to_implementation(
    mappings_by_type: Dict[str, Dict[str, Any]],
    requirement_type: str,
    requirement_id: str,
    implementation_id: str,
) -> bool:
    cfg = mappings_by_type.get(requirement_type)
    if not cfg:
        return True
    explicit = (cfg.get("mappings") or {}).get(requirement_id)
    candidates = explicit if explicit else cfg.get("default_implementation_ids") or ["*"]
    for c in candidates:
        if c == "*" or fnmatch(implementation_id, str(c)):
            return True
    return False


def write_split_merged(requirements_path: str) -> None:
    """Ensure merged/ exists. The single merged requirements list is written to merged/merged_requirements.yaml by callers (promote, merge)."""
    out_dir = os.path.join(requirements_path, CURRENT_DIR, "merged")
    os.makedirs(out_dir, exist_ok=True)


def bump_patch(version: str) -> str:
    p = version.split('.')
    if len(p) == 3 and all(x.isdigit() for x in p):
        return f"{p[0]}.{p[1]}.{int(p[2]) + 1}"
    return version


def compare_versions(a: str, b: str) -> int:
    def parse(v: str) -> List[int]:
        parts = str(v).split(".")
        if len(parts) != 3:
            return [0, 0, 0]
        out = []
        for p in parts:
            out.append(int(p) if p.isdigit() else 0)
        return out

    av = parse(a)
    bv = parse(b)
    if av < bv:
        return -1
    if av > bv:
        return 1
    return 0
