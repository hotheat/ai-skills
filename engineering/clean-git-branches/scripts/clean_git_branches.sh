#!/usr/bin/env bash
set -euo pipefail

REMOTE="origin"
MONTHS="3"
EXECUTE="false"

log_info() {
  printf '[INFO] %s\n' "$*"
}

log_warn() {
  printf '[WARN] %s\n' "$*" >&2
}

usage() {
  cat <<'EOF'
Usage: clean_git_branches.sh [--remote origin] [--months 3] [--execute]

Default mode is dry-run. Pass --execute to delete branches.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote)
      REMOTE="${2:-}"
      shift 2
      ;;
    --months)
      MONTHS="${2:-}"
      shift 2
      ;;
    --execute)
      EXECUTE="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      log_warn "Unknown argument: $1"
      usage
      exit 2
      ;;
  esac
done

if ! [[ "$MONTHS" =~ ^[0-9]+$ ]] || [[ "$MONTHS" -lt 1 ]]; then
  log_warn "--months must be a positive integer"
  exit 2
fi

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$repo_root" ]]; then
  log_warn "Not inside a Git repository"
  exit 1
fi

cd "$repo_root"

now_epoch="$(date +%s)"
cutoff_epoch="$(date -v-"${MONTHS}"m +%s 2>/dev/null || date -d "${MONTHS} months ago" +%s)"
current_branch="$(git branch --show-current)"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

local_plan="$tmp_dir/local_plan.tsv"
remote_plan="$tmp_dir/remote_plan.tsv"
merged_pr_branches="$tmp_dir/merged_pr_branches.txt"
: > "$local_plan"
: > "$remote_plan"
: > "$merged_pr_branches"

is_protected_branch() {
  local branch="$1"
  case "$branch" in
    main|master|develop|dev|release|staging|production|release/*|hotfix/*|prod/*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

branch_tip_epoch() {
  local ref="$1"
  git log -1 --format=%ct "$ref" 2>/dev/null || printf '0'
}

date_from_epoch() {
  local epoch="$1"
  if ! [[ "$epoch" =~ ^[0-9]+$ ]] || [[ "$epoch" -le 0 ]]; then
    printf 'unknown'
    return 0
  fi
  date -r "$epoch" '+%Y-%m-%d %H:%M:%S %z' 2>/dev/null || date -d "@$epoch" '+%Y-%m-%d %H:%M:%S %z'
}

current_repo_slug() {
  local url slug
  url="$(git remote get-url "$REMOTE" 2>/dev/null || true)"
  slug="$(printf '%s\n' "$url" | sed -E 's#^git@github.com:##; s#^https://github.com/##; s#^ssh://git@github.com/##; s#\.git$##')"
  if [[ "$slug" == */* ]]; then
    printf '%s' "$slug"
  fi
}

local_branch_age_epoch() {
  local branch="$1"
  local first_reflog
  first_reflog="$(git reflog show --date=unix --format='%gd %cd' "$branch" 2>/dev/null | awk 'END {print $2}')"
  if [[ -n "$first_reflog" && "$first_reflog" =~ ^[0-9]+$ ]]; then
    printf '%s' "$first_reflog"
  else
    branch_tip_epoch "$branch"
  fi
}

mark_local_delete() {
  local branch="$1"
  local reason="$2"
  local created_epoch="$3"
  if [[ "$branch" == "$current_branch" ]]; then
    return 0
  fi
  if is_protected_branch "$branch"; then
    return 0
  fi
  printf '%s\t%s\t%s\n' "$branch" "$reason" "$created_epoch" >> "$local_plan"
}

mark_remote_delete() {
  local branch="$1"
  local reason="$2"
  local created_epoch="$3"
  if [[ "$branch" == "$current_branch" ]]; then
    return 0
  fi
  if is_protected_branch "$branch"; then
    return 0
  fi
  printf '%s\t%s\t%s\n' "$branch" "$reason" "$created_epoch" >> "$remote_plan"
}

has_merged_pr_branch() {
  local branch="$1"
  grep -Fxq "$branch" "$merged_pr_branches"
}

log_info "步骤1：检查仓库状态"
if [[ -n "$(git status --short)" ]]; then
  log_warn "Working tree is not clean. Commit, stash, or discard changes before branch cleanup."
  exit 1
fi
log_info "步骤1完成：工作区干净"

log_info "步骤2：同步远程引用"
git fetch --all --prune
log_info "步骤2完成：远程引用已同步"

log_info "步骤3：读取已合入 PR 的分支"
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  pr_rows="$tmp_dir/merged_pr_rows.tsv"
  current_repo="$(current_repo_slug)"
  : > "$pr_rows"
  (
    gh pr list --state merged --limit 200 --json headRefName,headRepositoryOwner,headRepository \
      --jq '.[] | [.headRefName, (.headRepositoryOwner.login // ""), (.headRepository.name // "")] | @tsv' \
      > "$pr_rows"
  ) 2>/dev/null &
  gh_pid="$!"
  gh_waited=0
  while kill -0 "$gh_pid" 2>/dev/null; do
    if [[ "$gh_waited" -ge 20 ]]; then
      kill "$gh_pid" 2>/dev/null || true
      wait "$gh_pid" 2>/dev/null || true
      log_warn "Timed out reading merged PRs; skip merged PR detection"
      : > "$pr_rows"
      break
    fi
    sleep 1
    gh_waited=$((gh_waited + 1))
  done
  wait "$gh_pid" 2>/dev/null || true

  while IFS=$'\t' read -r head_ref head_repo_owner head_repo_name; do
    [[ -z "$head_ref" ]] && continue
    if [[ -z "$head_repo_owner" || -z "$head_repo_name" ]]; then
      printf '%s\n' "$head_ref" >> "$merged_pr_branches"
      continue
    fi
    if [[ "$head_repo_owner/$head_repo_name" == "$current_repo" ]]; then
      printf '%s\n' "$head_ref" >> "$merged_pr_branches"
    fi
  done < "$pr_rows"
  sort -u "$merged_pr_branches" -o "$merged_pr_branches"
else
  log_warn "gh is unavailable or unauthenticated; skip merged PR detection"
fi
log_info "步骤3完成：已读取 merged PR 分支"

log_info "步骤4：计算本地分支清理计划"
while IFS= read -r branch; do
  [[ -z "$branch" ]] && continue
  branch_epoch="$(local_branch_age_epoch "$branch")"

  if has_merged_pr_branch "$branch"; then
    mark_local_delete "$branch" "merged PR" "$branch_epoch"
  fi

  if ! git show-ref --verify --quiet "refs/remotes/${REMOTE}/${branch}"; then
    mark_local_delete "$branch" "remote branch missing" "$branch_epoch"
  fi

  if [[ "$branch_epoch" =~ ^[0-9]+$ && "$branch_epoch" -gt 0 && "$branch_epoch" -lt "$cutoff_epoch" ]]; then
    mark_local_delete "$branch" "older than ${MONTHS} months" "$branch_epoch"
  fi
done < <(git for-each-ref --format='%(refname:short)' refs/heads)
log_info "步骤4完成：本地分支清理计划已生成"

log_info "步骤5：计算远程分支清理计划"
while IFS= read -r remote_ref; do
  branch="${remote_ref#${REMOTE}/}"
  [[ "$branch" == "HEAD" || -z "$branch" ]] && continue
  branch_epoch="$(branch_tip_epoch "refs/remotes/${REMOTE}/${branch}")"

  if has_merged_pr_branch "$branch"; then
    mark_remote_delete "$branch" "merged PR" "$branch_epoch"
  fi

  if [[ "$branch_epoch" =~ ^[0-9]+$ && "$branch_epoch" -gt 0 && "$branch_epoch" -lt "$cutoff_epoch" ]]; then
    mark_remote_delete "$branch" "older than ${MONTHS} months" "$branch_epoch"
  fi
done < <(git for-each-ref --format='%(refname:short)' "refs/remotes/${REMOTE}")
log_info "步骤5完成：远程分支清理计划已生成"

log_info "步骤6：输出清理计划"
local_summary="$tmp_dir/local_summary.tsv"
remote_summary="$tmp_dir/remote_summary.tsv"

awk -F '\t' '
  NF >= 3 {
    if ($1 in reasons) {
      reasons[$1] = reasons[$1] "; " $2
    } else {
      reasons[$1] = $2
    }
    if (!($1 in epochs) || ($3 ~ /^[0-9]+$/ && $3 < epochs[$1])) {
      epochs[$1] = $3
    }
  }
  END {
    for (branch in reasons) {
      print branch "\t" epochs[branch] "\t" reasons[branch]
    }
  }
' "$local_plan" | sort > "$local_summary"

awk -F '\t' '
  NF >= 3 {
    if ($1 in reasons) {
      reasons[$1] = reasons[$1] "; " $2
    } else {
      reasons[$1] = $2
    }
    if (!($1 in epochs) || ($3 ~ /^[0-9]+$/ && $3 < epochs[$1])) {
      epochs[$1] = $3
    }
  }
  END {
    for (branch in reasons) {
      print branch "\t" epochs[branch] "\t" reasons[branch]
    }
  }
' "$remote_plan" | sort > "$remote_summary"

if [[ ! -s "$local_summary" && ! -s "$remote_summary" ]]; then
  log_info "No branches selected for deletion"
  exit 0
fi

while IFS=$'\t' read -r branch created_epoch reason; do
  [[ -z "$branch" ]] && continue
  printf 'LOCAL\t%s\tcreated_at=%s\t%s\n' "$branch" "$(date_from_epoch "$created_epoch")" "$reason"
done < "$local_summary"

while IFS=$'\t' read -r branch created_epoch reason; do
  [[ -z "$branch" ]] && continue
  printf 'REMOTE\t%s/%s\tcreated_at=%s\t%s\n' "$REMOTE" "$branch" "$(date_from_epoch "$created_epoch")" "$reason"
done < "$remote_summary"
log_info "步骤6完成：清理计划已输出"

if [[ "$EXECUTE" != "true" ]]; then
  log_info "Dry run only. Re-run with --execute to delete selected branches."
  exit 0
fi

printf '\nType 确认删除 to delete the branches listed above: '
if ! IFS= read -r confirmation; then
  log_warn "No confirmation received. Abort deletion."
  exit 1
fi

if [[ "$confirmation" != "确认删除" ]]; then
  log_warn "Confirmation did not match. Abort deletion."
  exit 1
fi

log_info "步骤7：执行分支删除"
while IFS=$'\t' read -r branch created_epoch reason; do
  [[ -z "$branch" ]] && continue
  log_info "Deleting local branch: ${branch} (${reason})"
  git branch -D "$branch"
done < "$local_summary"

while IFS=$'\t' read -r branch created_epoch reason; do
  [[ -z "$branch" ]] && continue
  log_info "Deleting remote branch: ${REMOTE}/${branch} (${reason})"
  git push "$REMOTE" --delete "$branch"
done < "$remote_summary"
log_info "步骤7完成：分支删除已执行"
