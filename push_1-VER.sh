#!/bin/bash
# Отправить ветку 1-VER в https://github.com/Aleksandr22012000/VKR_HUMAN-RIGHTS
set -euo pipefail
cd "$(dirname "$0")"

REMOTE="${REMOTE:-origin}"
BRANCH="${BRANCH:-1-VER}"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "Ошибка: запустите скрипт из корня репозитория VKR_HUMAN-RIGHTS."
  exit 1
fi

current="$(git branch --show-current)"
if [[ "$current" != "$BRANCH" ]]; then
  echo "Переключение на ветку $BRANCH (было: $current)"
  git checkout "$BRANCH" 2>/dev/null || git checkout -b "$BRANCH"
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Внимание: есть незакоммиченные изменения:"
  git status -s
  echo ""
  read -r -p "Закоммитить всё и продолжить? [y/N] " ans
  if [[ "${ans,,}" == "y" || "${ans,,}" == "yes" || "${ans,,}" == "д" ]]; then
    git add -A
    git commit -m "Обновление материалов ВКР и md-to-docx"
  else
    echo "Сначала закоммитьте изменения: git add … && git commit -m \"…\""
    exit 1
  fi
fi

echo "Ветка: $(git branch --show-current)"
echo "Коммит: $(git log -1 --oneline)"
echo "Remote: $REMOTE → $BRANCH"
echo ""

git -c core.hooksPath=/dev/null push -u "$REMOTE" "$BRANCH"

echo ""
echo "Готово: https://github.com/Aleksandr22012000/VKR_HUMAN-RIGHTS/tree/$BRANCH"
