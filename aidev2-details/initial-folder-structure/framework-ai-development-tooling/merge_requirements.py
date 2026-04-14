#!/usr/bin/env python3
from common import build_parser, generate_merged, merged_path, resolve_target_implementations, validate_target_for_app, write_split_merged, write_yaml


def main() -> None:
    parser = build_parser('Merge requirement diffs into merged/requirements.yaml')
    args = parser.parse_args()
    targets = resolve_target_implementations(args.requirements_path, args.app_path, args.implementation_id, args.all_implementations)
    req_set = None
    for t in targets:
        req_set, _ = validate_target_for_app(t, args.requirements_path)
    merged = generate_merged(args.requirements_path, req_set)
    out = merged_path(args.requirements_path)
    write_yaml(out, merged)
    write_split_merged(args.requirements_path)
    print(f'Merged requirements written to {out}')


if __name__ == '__main__':
    main()
