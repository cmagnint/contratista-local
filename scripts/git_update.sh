#!/bin/bash
# ----------------------------------------------------------
# Script para hacer commit y push automático
# Autor: devt_terrasoft
# Uso: ./scripts/git-auto-push.sh
# ----------------------------------------------------------

# Ir a la carpeta raíz del repositorio
cd "$(dirname "$0")/.." || exit 1

# Verificar si hay cambios
if git diff-index --quiet HEAD --; then
    echo "✅ No hay cambios para commitear."
    exit 0
fi

# Generar fecha del día
FECHA=$(date '+%Y-%m-%d')

# Mensaje de commit fijo
COMMIT_MSG=":hammer: Update FIRST ${FECHA}"

echo "📦 Agregando archivos..."
git add .

echo "📝 Creando commit con mensaje: '$COMMIT_MSG'"
git commit -m "$COMMIT_MSG"

echo "🚀 Haciendo push al repositorio..."
git push -u origin main

echo "✅ Commit y push completados con éxito."
