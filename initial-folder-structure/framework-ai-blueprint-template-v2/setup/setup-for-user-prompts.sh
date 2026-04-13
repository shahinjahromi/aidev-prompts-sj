#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Blueprint Setup Script (v2, user-prompts mode)
# Generates a new app-specific specs repository from this template.
#
# Usage:
#   ./setup/setup-for-user-prompts.sh --output-dir /path/to/workspace --app-slug my-app [OPTIONS]
#
# Required:
#   --output-dir DIR          Absolute path to an existing base directory
#                             (blueprint and app folders are created under it)
#   --app-slug SLUG           Kebab-case slug (e.g. "my-app"); used as requirement_set_id
#
# Optional:
#   --app-repo-dir DIR        Application repo directory name (default: implementation ID)
#   --specs-repo-dir DIR      Specs repo directory name (default: slug-ai-blueprint)
#   --impl-suffix SUFFIX      Prompted if omitted; appended to app slug
#                             (final implementation ID: slug-suffix)
#   --impl-id ID              Legacy full implementation ID; must equal slug-suffix
#   --core-stack STACK        Core technology stack (e.g. go, node, python).
#                             When provided and preset files exist, seeds NFR and TS
#                             presets into 01-pending-promotion/ for this implementation.
#   --add-impl                Add a new implementation to an existing blueprint.
#                             Blueprint must already exist; only the new impl dir
#                             and app repo are created. Existing content is unchanged.
#   --workspace-root DIR      Workspace root path (default: output-dir)
#   --startup-script PATH     App startup script relative path (default: scripts/local-dev.sh)
#   --e2e-reports-dir DIR     E2E reports dir name relative to workspace (default: slug-test-results)
#   --db-contract-id ID       DB contract logical ID (default: CONTRACT-APP-DB-SCHEMA)
#   --db-contract-enabled     Enable DB contract alignment (default: false)
#   --secrets-path PATH       Secrets instructions file path (default: placeholder)
#   --timezone TZ             Timezone (default: America/Denver)
#   --email-fixed EMAIL       Fixed test email (default: placeholder)
#   --email-domain DOMAIN     Random email domain (default: placeholder)
#   -h, --help                Show this help message
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_YAML_SRC="${TEMPLATE_ROOT}/.instructions/config.yaml"

OUTPUT_DIR=""
APP_SLUG=""
APP_REPO_DIR=""
SPECS_REPO_DIR=""
IMPL_SUFFIX=""
IMPL_ID=""
CORE_STACK=""
ADD_IMPL="false"
WORKSPACE_ROOT=""
STARTUP_SCRIPT="scripts/local-dev.sh"
E2E_REPORTS_DIR=""
DB_CONTRACT_ID="CONTRACT-APP-DB-SCHEMA"
DB_CONTRACT_ENABLED="false"
SECRETS_PATH=""
TIMEZONE="America/Denver"
EMAIL_FIXED=""
EMAIL_DOMAIN=""

usage() {
  sed -n '/^# Usage:/,/^# =====/p' "$0" | sed 's/^# //' | sed 's/^#//'
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir)         OUTPUT_DIR="$2"; shift 2 ;;
    --app-slug)           APP_SLUG="$2"; shift 2 ;;
    --app-repo-dir)       APP_REPO_DIR="$2"; shift 2 ;;
    --specs-repo-dir)     SPECS_REPO_DIR="$2"; shift 2 ;;
    --impl-suffix)        IMPL_SUFFIX="$2"; shift 2 ;;
    --impl-id)            IMPL_ID="$2"; shift 2 ;;
    --core-stack)         CORE_STACK="$2"; shift 2 ;;
    --add-impl)           ADD_IMPL="true"; shift ;;
    --workspace-root)     WORKSPACE_ROOT="$2"; shift 2 ;;
    --startup-script)     STARTUP_SCRIPT="$2"; shift 2 ;;
    --e2e-reports-dir)    E2E_REPORTS_DIR="$2"; shift 2 ;;
    --db-contract-id)     DB_CONTRACT_ID="$2"; shift 2 ;;
    --db-contract-enabled) DB_CONTRACT_ENABLED="true"; shift ;;
    --secrets-path)       SECRETS_PATH="$2"; shift 2 ;;
    --timezone)           TIMEZONE="$2"; shift 2 ;;
    --email-fixed)        EMAIL_FIXED="$2"; shift 2 ;;
    --email-domain)       EMAIL_DOMAIN="$2"; shift 2 ;;
    -h|--help)            usage ;;
    *) echo "ERROR: Unknown option: $1"; echo "Run with -h for usage."; exit 1 ;;
  esac
done

# ─── Validate required arguments ────────────────────────────────
prompt_if_empty() {
  local varname="$1"
  local prompt_text="$2"
  local default_val="${3:-}"
  local current_val="${!varname}"
  if [[ -z "$current_val" ]]; then
    if [[ -n "$default_val" ]]; then
      read -rp "$prompt_text [$default_val]: " current_val
      current_val="${current_val:-$default_val}"
    else
      read -rp "$prompt_text: " current_val
    fi
    eval "$varname=\"$current_val\""
  fi
}

prompt_required() {
  local varname="$1"
  local prompt_text="$2"
  local current_val="${!varname}"

  if [[ -n "$current_val" ]]; then
    return
  fi

  if [[ ! -t 0 ]]; then
    echo "ERROR: Missing required value for ${varname}."
    echo "Provide it with the corresponding --flag or run interactively."
    echo "Run with -h for usage."
    exit 1
  fi

  while [[ -z "$current_val" ]]; do
    read -rp "$prompt_text: " current_val
    current_val="$(echo "$current_val" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  done

  eval "$varname=\"$current_val\""
}

prompt_required OUTPUT_DIR "Base directory (absolute path to existing workspace root)"
prompt_required APP_SLUG   "Application slug (kebab-case, e.g. my-app)"

if [[ "$OUTPUT_DIR" != /* ]]; then
  echo "ERROR: --output-dir must be an absolute path (received: ${OUTPUT_DIR})"
  exit 1
fi

if [[ ! -d "$OUTPUT_DIR" ]]; then
  echo "ERROR: Base directory does not exist: ${OUTPUT_DIR}"
  exit 1
fi

SPECS_REPO_DIR="${SPECS_REPO_DIR:-${APP_SLUG}-ai-blueprint}"

if [[ -n "$IMPL_ID" ]]; then
  if [[ "$IMPL_ID" != "${APP_SLUG}-"* ]]; then
    echo "ERROR: --impl-id must start with ${APP_SLUG}-"
    exit 1
  fi
  IMPL_SUFFIX="${IMPL_ID#${APP_SLUG}-}"
  if [[ -z "$IMPL_SUFFIX" ]]; then
    echo "ERROR: --impl-id must include a suffix after ${APP_SLUG}-"
    exit 1
  fi
fi

prompt_required IMPL_SUFFIX "Implementation suffix (final ID will be ${APP_SLUG}-<suffix>)"
IMPL_ID="${APP_SLUG}-${IMPL_SUFFIX}"

if [[ -z "$APP_REPO_DIR" ]]; then
  APP_REPO_DIR="$IMPL_ID"
fi

if [[ -z "$WORKSPACE_ROOT" ]]; then
  WORKSPACE_ROOT="$OUTPUT_DIR"
fi

# Resolve actual blueprint and app destinations under the base directory
BLUEPRINT_DIR="${OUTPUT_DIR}/${SPECS_REPO_DIR}"
APP_DIR="${OUTPUT_DIR}/${APP_REPO_DIR}"

if [[ "$ADD_IMPL" == "true" ]]; then
  if [[ ! -d "$BLUEPRINT_DIR" ]]; then
    echo "ERROR: --add-impl requires the blueprint to already exist: ${BLUEPRINT_DIR}"
    exit 1
  fi
else
  if [[ -d "$BLUEPRINT_DIR" ]]; then
    echo "ERROR: Blueprint directory already exists: ${BLUEPRINT_DIR}"
    echo "  Use --add-impl to add a new implementation to an existing blueprint."
    exit 1
  fi
fi
if [[ -d "$APP_DIR" ]]; then
  echo "ERROR: App directory already exists: ${APP_DIR}"
  exit 1
fi
if [[ -z "$E2E_REPORTS_DIR" ]]; then
  E2E_REPORTS_DIR="${APP_SLUG}-test-results"
fi
if [[ -z "$SECRETS_PATH" ]]; then
  SECRETS_PATH="${WORKSPACE_ROOT}/secrets/secrets-instructions.txt"
fi
if [[ -z "$EMAIL_FIXED" ]]; then
  EMAIL_FIXED="test@example.com"
fi
if [[ -z "$EMAIL_DOMAIN" ]]; then
  EMAIL_DOMAIN="example.com"
fi

TODAY="$(date +%Y-%m-%d)"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Blueprint Setup v2                                         ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  App Slug:          %-38s ║\n" "$APP_SLUG"
printf "║  App Repo Dir:      %-38s ║\n" "$APP_REPO_DIR"
printf "║  Specs Repo Dir:    %-38s ║\n" "$SPECS_REPO_DIR"
printf "║  Implementation Suffix: %-33s ║\n" "$IMPL_SUFFIX"
printf "║  Implementation ID: %-38s ║\n" "$IMPL_ID"
printf "║  Core Stack:        %-38s ║\n" "${CORE_STACK:-<none>}"
printf "║  Mode:              %-38s ║\n" "$([ "$ADD_IMPL" = "true" ] && echo "add-impl" || echo "new")"
printf "║  Workspace Root:    %-38s ║\n" "$WORKSPACE_ROOT"
printf "║  Base Dir:          %-38s ║\n" "$OUTPUT_DIR"
printf "║  Blueprint Dir:     %-38s ║\n" "$BLUEPRINT_DIR"
printf "║  Timezone:          %-38s ║\n" "$TIMEZONE"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ─── Copy template (new blueprint only) ──────────────────────────────────
if [[ "$ADD_IMPL" != "true" ]]; then
  echo "Copying template to ${BLUEPRINT_DIR}..."
  mkdir -p "$BLUEPRINT_DIR"
  cp -r "${TEMPLATE_ROOT}/." "$BLUEPRINT_DIR"

  # Remove setup folder from destination (it belongs to the template only)
  rm -rf "${BLUEPRINT_DIR}/setup"

  # Remove any stray root-level setup script from destination.
  rm -f "${BLUEPRINT_DIR}/setup.sh"

  # Remove any .git from destination so it starts as a fresh repo
  rm -rf "${BLUEPRINT_DIR}/.git"

  # ─── Replace <<PLACEHOLDER>> tokens in all text files ───────────
  echo "Replacing placeholders..."
  find "$BLUEPRINT_DIR" -type f \( \
    -name '*.yaml' -o -name '*.yml' -o -name '*.txt' -o -name '*.md' \
    -o -name '*.mdc' -o -name '*.sh' -o -name '*.json' -o -name '*.ts' \
  \) | while read -r file; do
    sed -i \
      -e "s|<<APP_SLUG>>|${APP_SLUG}|g" \
      -e "s|<<APP_REPO_DIR>>|${APP_REPO_DIR}|g" \
      -e "s|<<SPECS_REPO_DIR>>|${SPECS_REPO_DIR}|g" \
      -e "s|<<IMPLEMENTATION_ID>>|${IMPL_ID}|g" \
      -e "s|<<WORKSPACE_ROOT>>|${WORKSPACE_ROOT}|g" \
      -e "s|<<APP_STARTUP_SCRIPT>>|${STARTUP_SCRIPT}|g" \
      -e "s|<<E2E_REPORTS_DIR>>|${E2E_REPORTS_DIR}|g" \
      -e "s|<<DB_CONTRACT_LOGICAL_ID>>|${DB_CONTRACT_ID}|g" \
      -e "s|<<DB_CONTRACT_ENABLED>>|${DB_CONTRACT_ENABLED}|g" \
      -e "s|<<SECRETS_INSTRUCTIONS_PATH>>|${SECRETS_PATH}|g" \
      -e "s|<<TIMEZONE>>|${TIMEZONE}|g" \
      -e "s|<<EMAIL_FIXED>>|${EMAIL_FIXED}|g" \
      -e "s|<<EMAIL_RANDOM_DOMAIN>>|${EMAIL_DOMAIN}|g" \
      -e "s|<<DATE>>|${TODAY}|g" \
      "$file"
  done

  # ─── User-prompts mode cleanup ─────────────────────────────────────────
  # Remove all prompt files and instruction markdown files from generated blueprint.
  # Keep .instructions/config.yaml only.
  echo "Applying user-prompts mode cleanup..."
  find "$BLUEPRINT_DIR" -type f \( \
    -name '*.prompt.md' -o \
    -name '*.instructions.md' -o \
    -path '*/.instructions/*.md' -o \
    -path '*/instructions/*.md' \
  \) -delete

  # Ensure no generic instructions markdown survives in user-prompts mode.
  rm -f "${BLUEPRINT_DIR}/.instructions/instructions.md"

  if [[ ! -f "$CONFIG_YAML_SRC" ]]; then
    echo "ERROR: Missing required source file: ${CONFIG_YAML_SRC}"
    exit 1
  fi

  mkdir -p "${BLUEPRINT_DIR}/.instructions"
  cp "$CONFIG_YAML_SRC" "${BLUEPRINT_DIR}/.instructions/config.yaml"
  echo "  Ensured .instructions/config.yaml is copied"

  # ─── Rename __IMPL_ID__ directory to actual implementation ID ────
  echo "Renaming implementation directory..."
  IMPL_TEMPLATE_DIR="${BLUEPRINT_DIR}/02-implementation/01-implementations/__IMPL_ID__"
  if [[ -d "$IMPL_TEMPLATE_DIR" ]]; then
    IMPL_DEST_DIR="${BLUEPRINT_DIR}/02-implementation/01-implementations/${IMPL_ID}"
    mv "$IMPL_TEMPLATE_DIR" "$IMPL_DEST_DIR"
    echo "  Renamed __IMPL_ID__ → ${IMPL_ID}"
  fi

  # ─── Ensure type subfolders exist in pending and current ──────
  echo "Ensuring requirement type subfolders..."
  mkdir -p "${BLUEPRINT_DIR}/01-requirements/01-pending-promotion/nfr-and-global-cr"
  mkdir -p "${BLUEPRINT_DIR}/01-requirements/01-pending-promotion/technology-selection"
  mkdir -p "${BLUEPRINT_DIR}/01-requirements/03-current/nfr-and-global-cr"
  mkdir -p "${BLUEPRINT_DIR}/01-requirements/03-current/technology-selection"
  mkdir -p "${BLUEPRINT_DIR}/01-requirements/01-pending-promotion/models_and_contracts"
  mkdir -p "${BLUEPRINT_DIR}/01-requirements/03-current/models_and_contracts"
  for _dir in \
    "${BLUEPRINT_DIR}/01-requirements/01-pending-promotion/nfr-and-global-cr" \
    "${BLUEPRINT_DIR}/01-requirements/01-pending-promotion/technology-selection" \
    "${BLUEPRINT_DIR}/01-requirements/03-current/nfr-and-global-cr" \
    "${BLUEPRINT_DIR}/01-requirements/03-current/technology-selection" \
    "${BLUEPRINT_DIR}/01-requirements/01-pending-promotion/models_and_contracts" \
    "${BLUEPRINT_DIR}/01-requirements/03-current/models_and_contracts"; do
    if [[ -z "$(ls -A "${_dir}" 2>/dev/null)" ]]; then
      touch "${_dir}/.gitkeep"
    fi
  done

  # ─── Create E2E test-results directory ──────────────────────────
  echo "Creating test-results directory..."
  mkdir -p "${BLUEPRINT_DIR}/03-test-results/${IMPL_ID}"

  # ─── Make scripts executable ────────────────────────────────────
  chmod +x "${BLUEPRINT_DIR}/scripts/"*.sh 2>/dev/null || true

  # ─── Initialize git repo ────────────────────────────────────────
  echo ""
  echo "Initializing git repository..."
  cd "$BLUEPRINT_DIR" && git init -q && git add -A && git commit -q -m "Initial blueprint from template v2"
  echo "Git repository initialized with initial commit."
else
  # ─── --add-impl mode: create new impl dir in existing blueprint ───────
  echo "Adding new implementation ${IMPL_ID} to existing blueprint ${BLUEPRINT_DIR}..."
  IMPL_DEST_DIR="${BLUEPRINT_DIR}/02-implementation/01-implementations/${IMPL_ID}"
  if [[ -d "$IMPL_DEST_DIR" ]]; then
    echo "ERROR: Implementation directory already exists: ${IMPL_DEST_DIR}"
    exit 1
  fi
  # Copy implementation template directory structure
  IMPL_TEMPLATE_DIR="${TEMPLATE_ROOT}/02-implementation/01-implementations/__IMPL_ID__"
  if [[ -d "$IMPL_TEMPLATE_DIR" ]]; then
    cp -r "$IMPL_TEMPLATE_DIR" "$IMPL_DEST_DIR"
    echo "  Created implementation directory: ${IMPL_DEST_DIR}"
  else
    mkdir -p "$IMPL_DEST_DIR"
    echo "  Created implementation directory (no template): ${IMPL_DEST_DIR}"
  fi
  # Ensure type subfolders exist for new impl
  mkdir -p "${BLUEPRINT_DIR}/01-requirements/01-pending-promotion/nfr-and-global-cr"
  mkdir -p "${BLUEPRINT_DIR}/01-requirements/01-pending-promotion/technology-selection"
  mkdir -p "${BLUEPRINT_DIR}/01-requirements/03-current/nfr-and-global-cr"
  mkdir -p "${BLUEPRINT_DIR}/01-requirements/03-current/technology-selection"
  mkdir -p "${BLUEPRINT_DIR}/03-test-results/${IMPL_ID}"
fi

# ─── Create app directory with manifest ──────────────────────────
APP_MANIFEST_DIR="${APP_DIR}/manifests"
mkdir -p "$APP_MANIFEST_DIR"
if [[ ! -f "${APP_MANIFEST_DIR}/requirements-manifest.yaml" ]]; then
  cat > "${APP_MANIFEST_DIR}/requirements-manifest.yaml" <<MANIFEST
manifest_version: '1.0'
requirement_set_id: ${APP_SLUG}
app_identifier: ${APP_SLUG}
implementation_id: ${IMPL_ID}
iteration_id: 1
requirements_version_target: 1.0.0
requirements_version_implemented: 0.0.0
requirement_baseline: []
MANIFEST
  echo "Created app directory and manifest: ${APP_MANIFEST_DIR}/requirements-manifest.yaml"
else
  echo "App manifest already exists: ${APP_MANIFEST_DIR}/requirements-manifest.yaml"
fi

# ─── Seed core-stack presets into pending-promotion ──────────────
# Detect the user prompts folder relative to this script's location.
# The script ships inside the user prompts folder tree; walk up until we find
# the folder that contains aidev2-details/.
_PROMPTS_ROOT=""
_CANDIDATE="${SCRIPT_DIR}"
for _i in 1 2 3 4 5; do
  if [[ -d "${_CANDIDATE}/aidev2-details" ]]; then
    _PROMPTS_ROOT="$_CANDIDATE"
    break
  fi
  _CANDIDATE="$(dirname "$_CANDIDATE")"
done

if [[ -n "$CORE_STACK" && -n "$_PROMPTS_ROOT" ]]; then
  echo "Seeding ${CORE_STACK} presets for ${IMPL_ID}..."

  _NFR_PRESET="${_PROMPTS_ROOT}/aidev2-details/preset-requirements/nfr-and-global-cr-by-core-stack/${CORE_STACK}/nfr_and_global_cr-[implementation id].yaml"
  _TS_PRESET="${_PROMPTS_ROOT}/aidev2-details/preset-requirements/tech_selections_by-core-stack/${CORE_STACK}/technology_selection_[implementation_id].yaml"

  _NFR_DEST="${BLUEPRINT_DIR}/01-requirements/01-pending-promotion/nfr-and-global-cr/nfr_and_global_cr_${IMPL_ID}.yaml"
  _TS_DEST="${BLUEPRINT_DIR}/01-requirements/01-pending-promotion/technology-selection/technology_selection_${IMPL_ID}.yaml"

  if [[ -f "$_NFR_PRESET" ]]; then
    mkdir -p "$(dirname "$_NFR_DEST")"
    cp "$_NFR_PRESET" "$_NFR_DEST"
    # Replace placeholder implementation id in the file
    sed -i "s|\[implementation id\]|${IMPL_ID}|g" "$_NFR_DEST"
    echo "  Seeded NFR preset → ${_NFR_DEST}"
    # Register an impl-specific copy in the prompts preset folder
    _NFR_REGISTRY="${_PROMPTS_ROOT}/aidev2-details/preset-requirements/nfr-and-global-cr-by-core-stack/${CORE_STACK}/nfr_and_global_cr_${IMPL_ID}.yaml"
    cp "$_NFR_DEST" "$_NFR_REGISTRY"
    echo "  Registered NFR preset → ${_NFR_REGISTRY}"
  else
    echo "  No NFR preset found for stack '${CORE_STACK}' (skipping)"
  fi

  if [[ -f "$_TS_PRESET" ]]; then
    mkdir -p "$(dirname "$_TS_DEST")"
    cp "$_TS_PRESET" "$_TS_DEST"
    # Replace placeholder implementation id in the file
    sed -i "s|\[implementation_id\]|${IMPL_ID}|g" "$_TS_DEST"
    sed -i "s|implementation_id: .*|implementation_id: ${IMPL_ID}|g" "$_TS_DEST"
    echo "  Seeded TS preset → ${_TS_DEST}"
    # Register an impl-specific copy in the prompts preset folder
    _TS_REGISTRY="${_PROMPTS_ROOT}/aidev2-details/preset-requirements/tech_selections_by-core-stack/${CORE_STACK}/technology_selection_${IMPL_ID}.yaml"
    cp "$_TS_DEST" "$_TS_REGISTRY"
    echo "  Registered TS preset → ${_TS_REGISTRY}"
  else
    echo "  No TS preset found for stack '${CORE_STACK}' (skipping)"
  fi
elif [[ -n "$CORE_STACK" && -z "$_PROMPTS_ROOT" ]]; then
  echo "  WARNING: Could not locate user prompts root; skipping preset seeding."
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Done! Your specs repo is ready at:"
echo "    ${BLUEPRINT_DIR}"
echo ""
echo "  Next steps:"
echo "    1. Fill in .instructions/codebase-context.yaml with your project's tech stack"
echo "    2. Verify .instructions/config.yaml values for your environment"
echo "    3. Use your GitHub user prompts from ~/.config/Code/User/prompts"
echo "    4. Continue with your standard aidev2 pipeline steps"
echo "════════════════════════════════════════════════════════════════"
