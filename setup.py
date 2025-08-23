#!/usr/bin/env python3
"""
🚀 Скрипт быстрой настройки бота распознавания растений

Этот скрипт поможет вам быстро настроить и запустить бота.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Выводит заголовок скрипта"""
    print("\n" + "="*60)
    print("🌱 БЫСТРАЯ НАСТРОЙКА БОТА РАСПОЗНАВАНИЯ РАСТЕНИЙ")
    print("="*60)
    print("Добро пожаловать! Этот скрипт поможет настроить бота.\n")

def check_python_version():
    """Проверяет версию Python"""
    print("🐍 Проверка версии Python...")
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше!")
        print(f"   Текущая версия: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def install_dependencies():
    """Устанавливает зависимости"""
    print("\n📦 Установка зависимостей...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Зависимости установлены успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        return False

def setup_env_file():
    """Создает .env файл на основе env_example.txt"""
    print("\n⚙️  Настройка переменных окружения...")
    
    if os.path.exists('.env'):
        response = input("Файл .env уже существует. Перезаписать? (y/N): ")
        if response.lower() != 'y':
            print("Пропускаем создание .env файла")
            return True
    
    if not os.path.exists('env_example.txt'):
        print("❌ Файл env_example.txt не найден!")
        return False
    
    # Копируем пример как основу
    shutil.copy('env_example.txt', '.env')
    
    print("✅ Файл .env создан на основе env_example.txt")
    print("\n📝 ВАЖНО: Теперь вам нужно отредактировать .env файл:")
    print("   1. Получите BOT_TOKEN у @BotFather в Telegram")
    print("   2. Узнайте ваш ADMIN_ID у @userinfobot")
    print("   3. Получите OPENROUTER_API_KEY на https://openrouter.ai/")
    print("   4. Замените значения в .env файле на реальные")
    
    return True

def run_check():
    """Запускает проверку готовности"""
    print("\n🔍 Запуск проверки готовности...")
    try:
        subprocess.run([sys.executable, "check_setup.py"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Проверка показала ошибки. Исправьте их перед запуском.")
        return False
    except FileNotFoundError:
        print("❌ Файл check_setup.py не найден!")
        return False

def final_instructions():
    """Выводит финальные инструкции"""
    print("\n" + "="*60)
    print("🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
    print("="*60)
    print("\n📋 Следующие шаги:")
    print("   1. Отредактируйте .env файл (замените примеры на реальные значения)")
    print("   2. Запустите: python check_setup.py")
    print("   3. Если всё OK, запустите: python main.py")
    print("\n🐳 Альтернативно, для Docker:")
    print("   1. docker-compose up --build")
    print("\n📚 Документация:")
    print("   - README.md - полная документация")
    print("   - QUICK_START.md - быстрый старт")
    print("   - DEPLOY.md - деплой на серверы")
    print("\n💬 Поддержка:")
    print("   - Проверьте логи в bot.log")
    print("   - Используйте check_setup.py для диагностики")
    print("\n🌱 Удачи с ботом! 💚")

def main():
    """Главная функция"""
    print_header()
    
    # Проверяем Python
    if not check_python_version():
        return 1
    
    # Устанавливаем зависимости
    if not install_dependencies():
        return 1
    
    # Настраиваем .env
    if not setup_env_file():
        return 1
    
    # Финальные инструкции
    final_instructions()
    
    # Предлагаем запустить проверку
    response = input("\nЗапустить проверку готовности сейчас? (Y/n): ")
    if response.lower() != 'n':
        run_check()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Настройка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)
