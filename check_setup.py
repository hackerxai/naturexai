#!/usr/bin/env python3
"""
Скрипт проверки готовности бота к запуску
Проверяет наличие всех необходимых файлов и переменных окружения
"""

import os
import sys
from dotenv import load_dotenv

# Безопасная функция печати для Windows (обрабатывает эмодзи)
def safe_print(text):
    """Безопасная печать с обработкой Unicode для Windows"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Заменяем эмодзи на ASCII символы для Windows
        replacements = {
            '🌱': '[*]',
            '🔍': '[?]',
            '✅': '[+]',
            '❌': '[X]',
            '📦': '[PKG]',
            '🌍': '[ENV]',
            '⚙️': '[CFG]', 
            '🎉': '[OK]',
            '🚀': '>>',
            '🔧': '[FIX]'
        }
        for emoji, replacement in replacements.items():
            text = text.replace(emoji, replacement)
        print(text)

def check_files():
    """Проверяет наличие всех необходимых файлов"""
    required_files = [
        'main.py',
        'utils.py', 
        'config.py',
        'handlers.py',
        'keyboards.py',
        'requirements.txt',
        '.env'
    ]
    
    safe_print("🔍 Проверка файлов...")
    all_found = True
    
    for file in required_files:
        if os.path.exists(file):
            safe_print(f"✅ {file}")
        else:
            safe_print(f"❌ {file} - НЕ НАЙДЕН!")
            all_found = False
    
    return all_found

def check_dependencies():
    """Проверяет установку необходимых зависимостей"""
    safe_print("\n📦 Проверка зависимостей...")
    all_installed = True
    
    try:
        import telegram
        safe_print(f"✅ python-telegram-bot {telegram.__version__}")
    except ImportError:
        safe_print("❌ python-telegram-bot - НЕ УСТАНОВЛЕН!")
        all_installed = False
    
    try:
        import requests
        safe_print(f"✅ requests {requests.__version__}")
    except ImportError:
        safe_print("❌ requests - НЕ УСТАНОВЛЕН!")
        all_installed = False
    
    try:
        import dotenv
        safe_print("✅ python-dotenv установлен")
    except ImportError:
        safe_print("❌ python-dotenv - НЕ УСТАНОВЛЕН!")
        all_installed = False
    
    try:
        import PIL
        safe_print("✅ Pillow установлен")
    except ImportError:
        safe_print("❌ Pillow - НЕ УСТАНОВЛЕН!")
        all_installed = False
    
    try:
        import aiohttp
        safe_print(f"✅ aiohttp {aiohttp.__version__}")
    except ImportError:
        safe_print("❌ aiohttp - НЕ УСТАНОВЛЕН!")
        all_installed = False
    
    return all_installed

def check_environment():
    """Проверяет переменные окружения"""
    safe_print("\n🌍 Проверка переменных окружения...")
    
    load_dotenv()
    env_ok = True
    
    # Проверка BOT_TOKEN
    bot_token = os.getenv('BOT_TOKEN')
    if bot_token and bot_token != 'your_bot_token_here':
        safe_print("✅ BOT_TOKEN настроен")
    else:
        safe_print("❌ BOT_TOKEN не настроен или имеет значение по умолчанию")
        env_ok = False
    
    # Проверка ADMIN_ID
    admin_id = os.getenv('ADMIN_ID')
    if admin_id and admin_id != '0':
        safe_print("✅ ADMIN_ID настроен")
    else:
        safe_print("❌ ADMIN_ID не настроен или имеет значение по умолчанию")
        env_ok = False
    
    # Проверка OPENROUTER_API_KEY
    api_key = os.getenv('OPENROUTER_API_KEY')
    if api_key and api_key != 'your_openrouter_api_key':
        safe_print("✅ OPENROUTER_API_KEY настроен")
    else:
        safe_print("❌ OPENROUTER_API_KEY не настроен или имеет значение по умолчанию")
        env_ok = False
    
    return env_ok

def check_config():
    """Проверяет корректность config.py"""
    safe_print("\n⚙️ Проверка конфигурации...")
    
    try:
        import config
        safe_print("✅ config.py загружается без ошибок")
        
        if hasattr(config, 'BOT_TOKEN'):
            safe_print("✅ BOT_TOKEN доступен в конфиге")
        if hasattr(config, 'OPENROUTER_API_KEY'):
            safe_print("✅ OPENROUTER_API_KEY доступен в конфиге")
        if hasattr(config, 'VISION_MODEL'):
            safe_print(f"✅ Модель: {config.VISION_MODEL}")
        if hasattr(config, 'EMOJIS'):
            safe_print(f"✅ Эмодзи настроены: {len(config.EMOJIS)} шт.")
        
        return True
    except Exception as e:
        safe_print(f"❌ Ошибка в config.py: {e}")
        return False
    
    return True

def main():
    """Главная функция проверки"""
    safe_print("🌱 Проверка готовности бота распознавания растений")
    safe_print("=" * 50)
    
    all_checks_passed = True
    
    # Проверяем файлы
    if not check_files():
        all_checks_passed = False
    
    # Проверяем зависимости
    if not check_dependencies():
        all_checks_passed = False
    
    # Проверяем переменные окружения
    if not check_environment():
        all_checks_passed = False
    
    # Проверяем конфигурацию
    if not check_config():
        all_checks_passed = False
    
    # Результат
    safe_print("\n" + "=" * 50)
    if all_checks_passed:
        safe_print("🎉 Все проверки пройдены! Бот готов к запуску!")
        safe_print("\n🚀 Для запуска выполните:")
        safe_print("python run.py")
        return True
    else:
        safe_print("❌ Обнаружены проблемы! Исправьте их перед запуском.")
        safe_print("\n🔧 Что нужно сделать:")
        safe_print("  1. Проверьте файл .env")
        safe_print("  2. Убедитесь, что все токены настроены")
        safe_print("  3. Запустите 'python check_setup.py' для диагностики")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        safe_print("\n⏹️ Проверка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        safe_print(f"\n❌ Проверки показали ошибки:")
        safe_print(f"\nОшибки: {e}")
        safe_print(f"\n💡 Рекомендации:")
        safe_print(f"  1. Проверьте файл .env")
        safe_print(f"  2. Убедитесь, что все токены настроены")
        safe_print(f"  3. Запустите 'python check_setup.py' для диагностики")
        sys.exit(1)