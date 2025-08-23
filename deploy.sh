#!/bin/bash

# 🚀 Скрипт развертывания бота распознавания растений
# Универсальный скрипт для развертывания на Linux серверах

set -e  # Останавливаем при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода заголовков
print_header() {
    echo -e "\n${BLUE}============================================${NC}"
    echo -e "${BLUE}🚀 $1${NC}"
    echo -e "${BLUE}============================================${NC}\n"
}

# Функция для вывода успеха
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Функция для вывода предупреждений
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Функция для вывода ошибок
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Проверка, что скрипт запущен не под root
check_user() {
    if [ "$EUID" -eq 0 ]; then
        print_error "Не запускайте скрипт под root!"
        print_warning "Создайте отдельного пользователя для бота"
        exit 1
    fi
}

# Установка системных зависимостей
install_system_deps() {
    print_header "УСТАНОВКА СИСТЕМНЫХ ЗАВИСИМОСТЕЙ"
    
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv git curl
        print_success "Зависимости установлены (Ubuntu/Debian)"
    elif command -v yum >/dev/null 2>&1; then
        sudo yum update -y
        sudo yum install -y python3 python3-pip python3-venv git curl
        print_success "Зависимости установлены (CentOS/RHEL)"
    else
        print_error "Неподдерживаемая система. Установите вручную: python3, pip, git, curl"
        exit 1
    fi
}

# Создание виртуального окружения
setup_venv() {
    print_header "СОЗДАНИЕ ВИРТУАЛЬНОГО ОКРУЖЕНИЯ"
    
    if [ -d "venv" ]; then
        print_warning "Виртуальное окружение уже существует"
        read -p "Пересоздать? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
        else
            print_success "Используем существующее окружение"
            return
        fi
    fi
    
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Виртуальное окружение создано"
}

# Проверка конфигурации
check_config() {
    print_header "ПРОВЕРКА КОНФИГУРАЦИИ"
    
    if [ ! -f ".env" ]; then
        print_warning ".env файл не найден. Создаем из примера..."
        if [ -f "env_example.txt" ]; then
            cp env_example.txt .env
            print_warning "Отредактируйте .env файл перед запуском!"
        else
            print_error "env_example.txt не найден!"
            exit 1
        fi
    else
        print_success ".env файл найден"
    fi
    
    # Активируем окружение для проверки
    source venv/bin/activate
    
    if python check_setup.py; then
        print_success "Конфигурация корректна"
    else
        print_error "Ошибки в конфигурации. Исправьте перед продолжением."
        exit 1
    fi
}

# Создание systemd сервиса
create_systemd_service() {
    print_header "СОЗДАНИЕ SYSTEMD СЕРВИСА"
    
    read -p "Создать systemd сервис для автозапуска? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        SERVICE_NAME="plant-recognition-bot"
        SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
        CURRENT_DIR=$(pwd)
        CURRENT_USER=$(whoami)
        
        sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Plant Recognition Telegram Bot
After=network.target

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${CURRENT_DIR}
Environment=PATH=${CURRENT_DIR}/venv/bin
ExecStart=${CURRENT_DIR}/venv/bin/python ${CURRENT_DIR}/main.py
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=plant-bot

[Install]
WantedBy=multi-user.target
EOF

        sudo systemctl daemon-reload
        sudo systemctl enable $SERVICE_NAME
        
        print_success "Systemd сервис создан: $SERVICE_NAME"
        print_warning "Команды управления:"
        echo "  sudo systemctl start $SERVICE_NAME     # Запуск"
        echo "  sudo systemctl stop $SERVICE_NAME      # Остановка"  
        echo "  sudo systemctl restart $SERVICE_NAME   # Перезапуск"
        echo "  sudo systemctl status $SERVICE_NAME    # Статус"
        echo "  journalctl -u $SERVICE_NAME -f         # Логи"
    fi
}

# Настройка логирования
setup_logging() {
    print_header "НАСТРОЙКА ЛОГИРОВАНИЯ"
    
    # Создаем директорию для логов
    mkdir -p logs
    
    # Настраиваем logrotate
    sudo tee /etc/logrotate.d/plant-bot > /dev/null <<EOF
$(pwd)/logs/*.log $(pwd)/bot.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF
    
    print_success "Логирование настроено"
}

# Настройка файрволла (опционально)
setup_firewall() {
    print_header "НАСТРОЙКА ФАЙРВОЛЛА"
    
    read -p "Настроить базовый файрволл? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v ufw >/dev/null 2>&1; then
            sudo ufw --force enable
            sudo ufw default deny incoming
            sudo ufw default allow outgoing
            sudo ufw allow ssh
            print_success "Файрволл настроен"
        else
            print_warning "ufw не найден, пропускаем настройку файрволла"
        fi
    fi
}

# Финальные инструкции
show_final_instructions() {
    print_header "РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
    
    echo -e "${GREEN}🎉 Бот готов к работе!${NC}\n"
    
    echo -e "${BLUE}📋 Следующие шаги:${NC}"
    echo "1. Отредактируйте .env файл (если еще не сделали)"
    echo "2. Проверьте конфигурацию: source venv/bin/activate && python check_setup.py"
    echo "3. Запустите бота:"
    echo "   • Интерактивно: source venv/bin/activate && python main.py"
    echo "   • Как сервис: sudo systemctl start plant-recognition-bot"
    echo ""
    
    echo -e "${BLUE}📊 Мониторинг:${NC}"
    echo "• Логи бота: tail -f bot.log"
    echo "• Логи сервиса: journalctl -u plant-recognition-bot -f"
    echo "• Статус сервиса: systemctl status plant-recognition-bot"
    echo ""
    
    echo -e "${BLUE}🔧 Обновления:${NC}"
    echo "• git pull"
    echo "• source venv/bin/activate"
    echo "• pip install -r requirements.txt"
    echo "• sudo systemctl restart plant-recognition-bot"
    echo ""
    
    print_success "Удачи с ботом! 🌱💚"
}

# Главная функция
main() {
    print_header "РАЗВЕРТЫВАНИЕ БОТА РАСПОЗНАВАНИЯ РАСТЕНИЙ"
    
    # Проверяем пользователя
    check_user
    
    # Устанавливаем системные зависимости
    install_system_deps
    
    # Создаем виртуальное окружение
    setup_venv
    
    # Проверяем конфигурацию
    check_config
    
    # Создаем systemd сервис
    create_systemd_service
    
    # Настраиваем логирование
    setup_logging
    
    # Настраиваем файрволл
    setup_firewall
    
    # Показываем финальные инструкции
    show_final_instructions
}

# Запуск основной функции
main "$@"
