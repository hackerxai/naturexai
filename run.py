#!/usr/bin/env python3
"""
🚀 Скрипт запуска бота с проверками

Этот скрипт автоматически проверяет готовность и запускает бота.
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def signal_handler(sig, frame):
    """Обработчик сигнала завершения"""
    print("\n🛑 Получен сигнал завершения. Останавливаем бота...")
    sys.exit(0)

def check_files():
    """Проверяет наличие необходимых файлов"""
    required_files = [
        'main.py', 'config.py', 'handlers.py', 'utils.py', 
        'keyboards.py', 'requirements.txt', '.env'
    ]
    
    print("📁 Проверка файлов...")
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Отсутствуют файлы: {', '.join(missing_files)}")
        if '.env' in missing_files:
            print("💡 Подсказка: Запустите 'python setup.py' для создания .env файла")
        return False
    
    return True

def run_setup_check():
    """Запускает проверку готовности"""
    print("\n🔍 Запуск проверки готовности...")
    try:
        result = subprocess.run([sys.executable, "check_setup.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Все проверки пройдены успешно!")
            return True
        else:
            print("❌ Проверки показали ошибки:")
            print(result.stdout)
            if result.stderr:
                print("Ошибки:", result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ Файл check_setup.py не найден!")
        return False

def start_bot():
    """Запускает бота"""
    print("\n🤖 Запуск бота...")
    print("📝 Логи будут сохранены в bot.log")
    print("🛑 Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    try:
        # Запускаем основной скрипт бота
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка запуска бота: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
        return True
    
    return True

def show_status():
    """Показывает статус и полезную информацию"""
    print("\n" + "="*60)
    print("🤖 ЗАПУСК БОТА РАСПОЗНАВАНИЯ РАСТЕНИЙ")
    print("="*60)
    
    # Показываем время
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"🕒 Время запуска: {current_time}")
    
    # Показываем версию Python
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Показываем рабочую директорию
    print(f"📂 Директория: {os.getcwd()}")
    
def main():
    """Главная функция"""
    # Устанавливаем обработчик сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    show_status()
    
    # Проверяем файлы
    if not check_files():
        print("\n💡 Рекомендации:")
        print("   1. Убедитесь, что вы в правильной директории")
        print("   2. Запустите 'python setup.py' для настройки")
        return 1
    
    # Проверяем готовность
    if not run_setup_check():
        print("\n💡 Рекомендации:")
        print("   1. Проверьте файл .env")
        print("   2. Убедитесь, что все токены настроены")
        print("   3. Запустите 'python check_setup.py' для диагностики")
        return 1
    
    # Запускаем бота
    if not start_bot():
        return 1
    
    print("\n✅ Бот завершил работу корректно")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        print("💡 Проверьте логи и конфигурацию")
        sys.exit(1)
