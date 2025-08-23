#!/usr/bin/env python3
"""
Тестовый скрипт для проверки основных функций бота
Запускается без подключения к Telegram API
"""

import asyncio
import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_config():
    """Тестирует загрузку конфигурации"""
    print("🔧 Тестирование конфигурации...")
    
    try:
        import config
        print("✅ config.py загружен успешно")
        
        # Проверяем основные настройки
        if hasattr(config, 'EMOJIS'):
            print(f"✅ Эмодзи настроены: {len(config.EMOJIS)} шт.")
        
        if hasattr(config, 'WELCOME_MESSAGES'):
            print(f"✅ Приветственные сообщения: {len(config.WELCOME_MESSAGES)} шт.")
        
        if hasattr(config, 'PHOTO_MESSAGES'):
            print(f"✅ Сообщения о фото: {len(config.PHOTO_MESSAGES)} шт.")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в config.py: {e}")
        return False

async def test_utils():
    """Тестирует утилиты"""
    print("\n🔧 Тестирование утилит...")
    
    try:
        import utils
        
        # Тестируем функцию получения случайного сообщения
        from config import WELCOME_MESSAGES
        random_msg = utils.get_random_message(WELCOME_MESSAGES)
        print(f"✅ get_random_message работает: {random_msg[:50]}...")
        
        # Тестируем форматирование ответа
        test_response = utils.format_plant_response("Это тестовое растение")
        print(f"✅ format_plant_response работает: {test_response[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в utils.py: {e}")
        return False

async def test_keyboards():
    """Тестирует клавиатуры"""
    print("\n🔧 Тестирование клавиатур...")
    
    try:
        import keyboards
        
        # Тестируем создание клавиатур
        main_kb = keyboards.get_main_keyboard()
        print("✅ Главная клавиатура создана")
        
        help_kb = keyboards.get_help_keyboard()
        print("✅ Клавиатура помощи создана")
        
        about_kb = keyboards.get_about_keyboard()
        print("✅ Клавиатура информации создана")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в keyboards.py: {e}")
        return False

async def test_handlers():
    """Тестирует хендлеры (без Telegram API)"""
    print("\n🔧 Тестирование хендлеров...")
    
    try:
        import handlers
        print("✅ handlers.py загружен успешно")
        
        # Проверяем наличие основных функций
        if hasattr(handlers, 'start_command'):
            print("✅ start_command найден")
        
        if hasattr(handlers, 'handle_photo'):
            print("✅ handle_photo найден")
        
        if hasattr(handlers, 'handle_text'):
            print("✅ handle_text найден")
        
        if hasattr(handlers, 'handle_callback'):
            print("✅ handle_callback найден")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в handlers.py: {e}")
        return False

async def test_imports():
    """Тестирует импорты всех модулей"""
    print("\n🔧 Тестирование импортов...")
    
    try:
        # Тестируем импорт всех основных модулей
        import config
        import handlers
        import keyboards
        import utils
        
        print("✅ Все модули импортируются успешно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

async def main():
    """Главная функция тестирования"""
    print("🌱 Тестирование бота распознавания растений")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_utils,
        test_keyboards,
        test_handlers
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Результаты тестирования: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Бот готов к работе!")
        print("\n🚀 Следующие шаги:")
        print("1. Создайте файл .env с вашими настройками")
        print("2. Запустите: python check_setup.py")
        print("3. Запустите бота: python main.py")
    else:
        print("❌ Некоторые тесты не пройдены. Проверьте ошибки выше.")
        print("\n🔧 Возможные решения:")
        print("1. Установите зависимости: pip install -r requirements.txt")
        print("2. Проверьте синтаксис Python файлов")
        print("3. Убедитесь, что все файлы на месте")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Критическая ошибка: {e}")
        sys.exit(1)
