#!/usr/bin/env bash

set -euo pipefail

SCRIPT_NAME="$(basename "$0")"

print_help() {
  cat <<EOF
Uso:
  ./$SCRIPT_NAME               (Modo interactivo con menú)
  ./$SCRIPT_NAME status        (Muestra el estado del repositorio)
  ./$SCRIPT_NAME pull          (Hace pull con rebase)
  ./$SCRIPT_NAME commit "msg"  (Agrega cambios y crea commit)
  ./$SCRIPT_NAME push          (Hace push de la rama actual)
  ./$SCRIPT_NAME sync "msg"    (Pull + Add + Commit + Push)

Comandos:
  status, s           Muestra el estado del repositorio.
  pull, pl            Hace pull con rebase en la rama actual.
  commit, c "mensaje" Agrega cambios (git add -A) y crea commit.
  push, p             Hace push de la rama actual.
  sync, all, a "msg"  Hace pull + add + commit + push completo.
EOF
}

ensure_git_repo() {
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "❌ Error: Este directorio no es un repositorio Git."
    exit 1
  fi
}

ensure_origin_remote() {
  if ! git remote get-url origin >/dev/null 2>&1; then
    echo "❌ Error: No existe el remote 'origin' configurado en Git."
    exit 1
  fi
}

current_branch() {
  git rev-parse --abbrev-ref HEAD
}

pull_current_branch() {
  local branch
  branch="$(current_branch)"
  echo "⬇️ Haciendo pull (--rebase --autostash) de origin/$branch..."
  git pull --rebase --autostash origin "$branch"
  echo "✅ Pull completado."
}

commit_all_changes() {
  local message="${1:-}"
  if [[ -z "$message" ]]; then
    read -rp "💬 Ingresa el mensaje del commit: " message
  fi

  if [[ -z "$message" ]]; then
    echo "⚠️ El mensaje del commit no puede estar vacío."
    return 1
  fi

  echo "📦 Agregando todos los cambios (git add -A)..."
  git add -A

  if git diff --cached --quiet; then
    echo "ℹ️ No hay cambios para crear un commit."
    return 0
  fi

  echo "💾 Creando commit: '$message'..."
  git commit -m "$message"
  echo "✅ Commit creado con éxito."
}

push_current_branch() {
  local branch
  branch="$(current_branch)"
  echo "⬆️ Haciendo push a origin/$branch..."
  git push origin "$branch"
  echo "✅ Push completado."
}

sync_all() {
  local message="${1:-}"
  if [[ -z "$message" ]]; then
    read -rp "💬 Ingresa el mensaje del commit para sincronizar: " message
  fi
  pull_current_branch
  commit_all_changes "$message"
  push_current_branch
  echo "🚀 Sincronización completa finalizada exitosamente."
}

interactive_menu() {
  local branch
  branch="$(current_branch)"
  echo "=========================================="
  echo "   ⚡ GIT AUTOMÁTICO (Rama: $branch) ⚡"
  echo "=========================================="
  echo "1) 🚀 Sincronizar todo (Pull + Commit + Push)"
  echo "2) ⬇️ Pull (Traer cambios del servidor)"
  echo "3) 💾 Commit (Guardar cambios locales)"
  echo "4) ⬆️ Push (Subir cambios al servidor)"
  echo "5) 🔍 Status (Ver estado actual)"
  echo "6) ❌ Salir"
  echo "------------------------------------------"
  read -rp "Selecciona una opción [1-6]: " opt
  echo ""

  case "$opt" in
    1) sync_all ;;
    2) pull_current_branch ;;
    3) commit_all_changes "" ;;
    4) push_current_branch ;;
    5) git status -sb ;;
    6) echo "¡Hasta luego!"; exit 0 ;;
    *) echo "⚠️ Opción no válida." ;;
  esac
}

main() {
  ensure_git_repo
  ensure_origin_remote

  if [[ $# -eq 0 ]]; then
    interactive_menu
    exit 0
  fi

  local cmd="$1"

  case "$cmd" in
    status|s)
      git status -sb
      ;;
    pull|pl)
      pull_current_branch
      ;;
    commit|c)
      commit_all_changes "${2:-}"
      ;;
    push|p)
      push_current_branch
      ;;
    sync|all|a)
      sync_all "${2:-}"
      ;;
    help|-h|--help)
      print_help
      ;;
    *)
      echo "⚠️ Comando no reconocido: $cmd"
      print_help
      exit 1
      ;;
  esac
}

main "$@"

