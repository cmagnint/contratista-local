#!/bin/bash
# ----------------------------------------------------------
# Script para hacer commit y push automático
# Autor: devt_terrasoft
# Uso: ./scripts/git-auto-push.sh
# ----------------------------------------------------------

cd "$(dirname "$0")/.." || exit 1

if git diff-index --quiet HEAD --; then
    echo "✅ No hay cambios para commitear."
    exit 0
fi

FECHA=$(date '+%Y-%m-%d')

echo "📝 Ingresa el mensaje del commit:"
read -r COMMIT_MSG

# Si está vacío, usar mensaje por defecto
if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG=":hammer: Update FIRST ${FECHA}"
fi

echo "📦 Agregando archivos..."
git add .

echo "📝 Creando commit con mensaje: '$COMMIT_MSG'"
git commit -m "$COMMIT_MSG"

echo "🚀 Haciendo push al repositorio..."
git push -u origin main

echo "✅ Commit y push completados con éxito."