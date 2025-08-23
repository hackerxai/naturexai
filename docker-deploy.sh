#!/bin/bash

# 🐳 Скрипт развертывания бота через Docker
# Упрощенное развертывание с использованием Docker Compose

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}============================================${NC}"
    echo -e "${BLUE}🐳 $1${NC}"
    echo -e "${BLUE}============================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Проверка Docker
check_docker() {
    print_header "ПРОВЕРКА DOCKER"
    
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker не установлен!"
        echo "Установите Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_error "Docker Compose не установлен!"
        echo "Установите Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Проверяем, что Docker запущен
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker не запущен!"
        echo "Запустите Docker daemon"
        exit 1
    fi
    
    print_success "Docker и Docker Compose готовы"
}

# Подготовка .env файла
prepare_env() {
    print_header "ПОДГОТОВКА КОНФИГУРАЦИИ"
    
    if [ ! -f ".env" ]; then
        if [ -f "env_example.txt" ]; then
            cp env_example.txt .env
            print_warning ".env файл создан из примера"
            print_warning "ОБЯЗАТЕЛЬНО отредактируйте .env файл перед запуском!"
        else
            print_error "env_example.txt не найден!"
            exit 1
        fi
    else
        print_success ".env файл найден"
    fi
    
    # Проверяем, что переменные не пустые
    source .env
    if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "your_bot_token_here" ]; then
        print_error "BOT_TOKEN не настроен в .env файле!"
        exit 1
    fi
    
    if [ -z "$OPENROUTER_API_KEY" ] || [ "$OPENROUTER_API_KEY" = "your_openrouter_api_key_here" ]; then
        print_error "OPENROUTER_API_KEY не настроен в .env файле!"
        exit 1
    fi
    
    print_success "Конфигурация корректна"
}

# Создание директорий
create_dirs() {
    print_header "СОЗДАНИЕ ДИРЕКТОРИЙ"
    
    mkdir -p logs
    mkdir -p data
    
    print_success "Директории созданы"
}

# Сборка и запуск
build_and_run() {
    print_header "СБОРКА И ЗАПУСК КОНТЕЙНЕРА"
    
    echo "🔨 Сборка образа..."
    docker-compose build
    
    echo "🚀 Запуск контейнера..."
    docker-compose up -d
    
    print_success "Контейнер запущен"
}

# Проверка статуса
check_status() {
    print_header "ПРОВЕРКА СТАТУСА"
    
    sleep 5  # Ждем немного для запуска
    
    if docker-compose ps | grep -q "Up"; then
        print_success "Бот работает!"
    else
        print_error "Проблема с запуском бота"
        echo "Проверьте логи: docker-compose logs"
        exit 1
    fi
}

# Показать команды управления
show_management_commands() {
    print_header "КОМАНДЫ УПРАВЛЕНИЯ"
    
    echo -e "${BLUE}🔧 Основные команды:${NC}"
    echo "  docker-compose up -d          # Запуск в фоне"
    echo "  docker-compose down           # Остановка"
    echo "  docker-compose restart        # Перезапуск"
    echo "  docker-compose logs -f        # Просмотр логов"
    echo "  docker-compose ps             # Статус контейнеров"
    echo ""
    
    echo -e "${BLUE}🔄 Обновление:${NC}"
    echo "  git pull                      # Получить обновления"
    echo "  docker-compose down           # Остановить"
    echo "  docker-compose build          # Пересобрать"
    echo "  docker-compose up -d          # Запустить"
    echo ""
    
    echo -e "${BLUE}📊 Мониторинг:${NC}"
    echo "  docker-compose logs           # Все логи"
    echo "  docker stats                  # Использование ресурсов"
    echo "  docker system df              # Использование места"
    echo ""
}

# Финальные инструкции
show_final_instructions() {
    print_header "РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
    
    echo -e "${GREEN}🎉 Бот успешно развернут через Docker!${NC}\n"
    
    echo -e "${BLUE}📊 Проверка:${NC}"
    echo "• Статус: docker-compose ps"
    echo "• Логи: docker-compose logs -f"
    echo ""
    
    echo -e "${BLUE}🔗 Полезные ссылки:${NC}"
    echo "• Логи контейнера сохраняются в ./logs/"
    echo "• Конфигурация в .env файле"
    echo ""
    
    print_success "Бот готов к работе! 🤖🌱"
}

# Главная функция
main() {
    print_header "РАЗВЕРТЫВАНИЕ ЧЕРЕЗ DOCKER"
    
    # Проверяем Docker
    check_docker
    
    # Подготавливаем конфигурацию
    prepare_env
    
    # Создаем директории
    create_dirs
    
    # Собираем и запускаем
    build_and_run
    
    # Проверяем статус
    check_status
    
    # Показываем команды управления
    show_management_commands
    
    # Финальные инструкции
    show_final_instructions
}

# Обработка аргументов
case "${1:-}" in
    "stop")
        print_header "ОСТАНОВКА БОТА"
        docker-compose down
        print_success "Бот остановлен"
        ;;
    "restart")
        print_header "ПЕРЕЗАПУСК БОТА"
        docker-compose restart
        print_success "Бот перезапущен"
        ;;
    "logs")
        print_header "ПРОСМОТР ЛОГОВ"
        docker-compose logs -f
        ;;
    "status")
        print_header "СТАТУС БОТА"
        docker-compose ps
        ;;
    "update")
        print_header "ОБНОВЛЕНИЕ БОТА"
        git pull
        docker-compose down
        docker-compose build
        docker-compose up -d
        print_success "Бот обновлен и перезапущен"
        ;;
    *)
        main "$@"
        ;;
esac
