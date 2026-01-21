#!/usr/bin/env bash
# dbs_upgrade_nodeJs.sh
# Purpose: Install or upgrade Node.js in user-space without root, matching the
#          desired version for this project. Provides rollback on failure and
#          ensures PATH is configured in ~/.bashrc.
# Notes:
# - Installs to "$HOME/nodejs" using official Node.js tarballs.
# - Safe to re-run; it will upgrade/downgrade to the target version.
# - Requires curl or wget, tar, and a POSIX shell.

set -euo pipefail

TARGET_VERSION="v22.21.1"
FALLBACK_VERSION="v16.20.2"
NODE_DIR="${HOME}/nodejs"
TMP_DIR="$(mktemp -d)"
ARCHIVE="node-${TARGET_VERSION}-linux-x64.tar.xz"
URL="https://nodejs.org/dist/${TARGET_VERSION}/${ARCHIVE}"
BACKUP_DIR=""

cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

log() {
  printf '%s\n' "$*"
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

current_version() {
  if [ -x "${NODE_DIR}/bin/node" ]; then
    "${NODE_DIR}/bin/node" -v 2>/dev/null || true
  fi
}

glibc_version() {
  ldd --version 2>/dev/null | head -n 1 | awk '{print $NF}'
}

version_lt() {
  [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n 1)" != "$2" ]
}

backup_existing() {
  if [ -d "${NODE_DIR}" ]; then
    BACKUP_DIR="${NODE_DIR}.bak.$(date +%Y%m%d_%H%M%S)"
    mv "${NODE_DIR}" "${BACKUP_DIR}"
  fi
}

restore_backup() {
  if [ -n "${BACKUP_DIR}" ] && [ -d "${BACKUP_DIR}" ]; then
    rm -rf "${NODE_DIR}"
    mv "${BACKUP_DIR}" "${NODE_DIR}"
    log "Restored previous Node.js from ${BACKUP_DIR}."
  fi
}

ensure_bashrc_path() {
  local path_line='export PATH=$HOME/nodejs/bin:$PATH'
  local bashrc="${HOME}/.bashrc"
  if [ ! -f "${bashrc}" ]; then
    touch "${bashrc}"
  fi
  if ! grep -Fq "${path_line}" "${bashrc}"; then
    printf '\n%s\n' "${path_line}" >> "${bashrc}"
    log "Added PATH update to ${bashrc}."
  fi
}

download_archive() {
  if command -v curl >/dev/null 2>&1; then
    curl -fsSLo "${TMP_DIR}/${ARCHIVE}" "${URL}"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "${TMP_DIR}/${ARCHIVE}" "${URL}"
  else
    fail "Neither curl nor wget is available to download Node.js."
  fi
}

verify_candidate() {
  local candidate="${1}"
  local output
  output="$("${candidate}" -v 2>&1)" || {
    log "Install verification failed: ${output}"
    return 1
  }
  if [ "${output}" != "${TARGET_VERSION}" ]; then
    log "Install verification failed: expected ${TARGET_VERSION}, got ${output}"
    return 1
  fi
  return 0
}

main() {
  local before
  local glibc
  local selected_version
  before="$(current_version || true)"
  glibc="$(glibc_version || true)"
  selected_version="${TARGET_VERSION}"
  if [ -n "${glibc}" ] && version_lt "${glibc}" "2.28"; then
    selected_version="${FALLBACK_VERSION}"
    ARCHIVE="node-${selected_version}-linux-x64.tar.xz"
    URL="https://nodejs.org/dist/${selected_version}/${ARCHIVE}"
  fi

  log "Target Node.js version: ${selected_version}"
  if [ -n "${glibc}" ]; then
    log "Detected glibc version: ${glibc}"
  fi
  if [ -n "${before}" ]; then
    log "Current Node.js version: ${before}"
  else
    log "No existing Node.js found at ${NODE_DIR}."
  fi

  log "Downloading ${URL}..."
  download_archive

  log "Preparing Node.js..."
  tar -xJf "${TMP_DIR}/${ARCHIVE}" -C "${TMP_DIR}"
  if ! verify_candidate "${TMP_DIR}/node-${selected_version}-linux-x64/bin/node"; then
    fail "New Node.js binary could not run on this server. Try an older version."
  fi

  log "Installing Node.js..."
  backup_existing
  if ! mv "${TMP_DIR}/node-${selected_version}-linux-x64" "${NODE_DIR}"; then
    log "Install failed. Attempting rollback..."
    restore_backup
    fail "Install failed and rollback attempted."
  fi

  ensure_bashrc_path

  local after
  after="$("${NODE_DIR}/bin/node" -v 2>&1 || true)"
  if [ "${after}" != "${selected_version}" ]; then
    log "Install verification failed: ${after}"
    log "Attempting rollback..."
    restore_backup
    fail "Expected ${selected_version}, but found ${after:-unknown}."
  fi

  log "Node.js install complete: ${after}"
  if [ -n "${before}" ] && [ "${before}" != "${after}" ]; then
    log "Upgraded from ${before} to ${after}."
  fi
}

main "$@"
