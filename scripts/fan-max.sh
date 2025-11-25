#!/bin/bash
# Script para controlar ventiladores HP en Linux

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para encontrar el path correcto del ventilador
find_fan_path() {
    FAN_PATH=$(grep -l hp /sys/class/hwmon/hwmon*/name 2>/dev/null | sed 's/name$/pwm1_enable/')
    if [ -z "$FAN_PATH" ]; then
        echo -e "${RED}Error: No se encontró el control de ventiladores HP${NC}"
        exit 1
    fi
    echo "$FAN_PATH"
}

# Función para mostrar RPM actual
show_rpm() {
    FAN_DIR=$(dirname "$1")
    FAN1=$(cat "$FAN_DIR/fan1_input" 2>/dev/null)
    FAN2=$(cat "$FAN_DIR/fan2_input" 2>/dev/null)
    echo -e "${YELLOW}Fan 1: ${FAN1} RPM${NC}"
    echo -e "${YELLOW}Fan 2: ${FAN2} RPM${NC}"
}

# Encontrar path
FAN_PATH=$(find_fan_path)

# Verificar modo actual
CURRENT_MODE=$(cat "$FAN_PATH" 2>/dev/null)

case "$1" in
    max|MAX|0)
        echo 0 | sudo tee "$FAN_PATH" > /dev/null
        echo -e "${GREEN}✓ Ventiladores configurados al MÁXIMO${NC}"
        sleep 2
        show_rpm "$FAN_PATH"
        ;;
    auto|AUTO|2)
        echo 2 | sudo tee "$FAN_PATH" > /dev/null
        echo -e "${GREEN}✓ Ventiladores en modo AUTOMÁTICO${NC}"
        sleep 1
        show_rpm "$FAN_PATH"
        ;;
    status|"")
        echo -e "${YELLOW}Estado actual:${NC}"
        case "$CURRENT_MODE" in
            0) echo "Modo: MÁXIMO (0)" ;;
            1) echo "Modo: MANUAL (1)" ;;
            2) echo "Modo: AUTOMÁTICO (2)" ;;
            *) echo "Modo: Desconocido ($CURRENT_MODE)" ;;
        esac
        show_rpm "$FAN_PATH"
        ;;
    *)
        echo "Uso: $0 [max|auto|status]"
        echo ""
        echo "  max    - Ventiladores al máximo (4700+ RPM)"
        echo "  auto   - Modo automático (control por BIOS)"
        echo "  status - Mostrar estado actual"
        echo ""
        exit 1
        ;;
esac