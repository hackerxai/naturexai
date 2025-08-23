import asyncio
import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import config
from handlers import *

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Главная функция запуска бота"""
    logger.info("Запуск бота распознавания растений...")
    
    # Проверяем наличие токена
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        return
    
    if not config.OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY не найден в переменных окружения!")
        return
    
    # Создаем приложение
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Добавляем хендлеры команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("lessons", lessons_command))
    
    # Добавляем хендлеры сообщений
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Добавляем хендлер callback запросов
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Создаем и настраиваем планировщик для ежедневных уроков
    scheduler = AsyncIOScheduler()
    
    # Создаем контекст для планировщика
    from telegram.ext import CallbackContext
    context_for_scheduler = CallbackContext(application=application)
    
    # Добавляем задачу отправки уроков каждый день в 10:00
    scheduler.add_job(
        send_daily_lessons,
        trigger=CronTrigger(hour=10, minute=0),
        args=[context_for_scheduler],
        id='daily_biology_lessons',
        name='Ежедневные уроки биологии',
        replace_existing=True
    )
    
    # Запускаем планировщик
    scheduler.start()
    
    logger.info("Бот успешно запущен!")
    logger.info(f"Используется модель: {config.VISION_MODEL}")
    logger.info("Планировщик ежедневных уроков биологии активирован (10:00 каждый день)")
    
    # Запускаем бота
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    try:
        # Для Windows исправляем проблему с event loop
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        main()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        logger.exception("Полный traceback ошибки:")
