import logging
from telegram import Update
from telegram.ext import ContextTypes
import config
import utils
from keyboards import *

async def handle_expert_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, photo):
    """Обработчик фотографий в экспертном режиме"""
    user = update.effective_user
    
    # Скачиваем фото
    file = await context.bot.get_file(photo.file_id)
    image_bytes = await file.download_as_bytearray()
    
    # Добавляем фото к данным пользователя
    photo_count = utils.add_expert_photo(user.id, image_bytes)
    
    # Создаем клавиатуру для управления экспертным режимом
    keyboard = [
        [InlineKeyboardButton("📸 Добавить еще фото", callback_data="add_more_photos")],
        [InlineKeyboardButton("✍️ Добавить описание", callback_data="add_description")],
        [InlineKeyboardButton("🧬 Начать анализ", callback_data="start_expert_analysis_now")],
        [InlineKeyboardButton("🗑️ Очистить все", callback_data="clear_expert_data")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    expert_keyboard = InlineKeyboardMarkup(keyboard)
    
    expert_data = utils.get_expert_data(user.id)
    additional_text_status = "✅ Есть описание" if expert_data and expert_data['additional_text'] else "❌ Нет описания"
    
    await update.message.reply_text(
        f"🧬 **Экспертный режим активен!**\n\n"
        f"📸 **Фотографий собрано:** {photo_count}\n"
        f"✍️ **Дополнительное описание:** {additional_text_status}\n\n"
        f"Вы можете:\n"
        f"• Добавить еще фотографии для более точного анализа\n"
        f"• Добавить текстовое описание (место находки, особенности и т.д.)\n"
        f"• Начать экспертный анализ с имеющимися данными\n\n"
        f"💡 **Совет:** Больше фото и дополнительная информация = точнее результат!",
        reply_markup=expert_keyboard,
        parse_mode='Markdown'
    )

async def handle_expert_analysis(query):
    """Обработка запуска экспертного анализа"""
    user_id = query.from_user.id
    expert_data = utils.get_expert_data(user_id)
    
    if not expert_data or not expert_data['photos']:
        await query.edit_message_text(
            "❌ **Нет фотографий для анализа**\n\n"
            "Сначала загрузите хотя бы одно фото растения!",
            reply_markup=get_expert_mode_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    # Показываем статус анализа
    await query.edit_message_text(
        f"🧬 **Начинаю экспертный анализ...**\n\n"
        f"📊 **Данные для анализа:**\n"
        f"📸 Фотографий: {len(expert_data['photos'])}\n"
        f"✍️ Описание: {'✅ Есть' if expert_data['additional_text'] else '❌ Нет'}\n\n"
        f"🔬 Выполняю научную идентификацию...\n"
        f"⏳ Это может занять некоторое время...",
        parse_mode='Markdown'
    )
    
    try:
        # Запускаем экспертный анализ
        recognition_info, error = await utils.recognize_plant_expert_mode(
            expert_data['photos'], 
            expert_data['additional_text']
        )
        
        if recognition_info:
            # Форматируем и отправляем результат
            formatted_response = utils.format_expert_response(recognition_info)
            
            await query.edit_message_text(
                formatted_response,
                parse_mode='Markdown'
            )
            
            # Очищаем данные после успешного анализа
            utils.clear_expert_data(user_id)
            
            # Отправляем клавиатуру для нового анализа
            await query.message.reply_text(
                "🎯 **Анализ завершен!**\n\n"
                "Хотите провести новый экспертный анализ?",
                reply_markup=get_main_keyboard()
            )
        else:
            await query.edit_message_text(
                f"❌ **Ошибка анализа**\n\n{error}\n\n"
                "Попробуйте:\n"
                "• Добавить больше качественных фотографий\n"
                "• Указать дополнительную информацию\n"
                "• Повторить анализ позже",
                reply_markup=get_expert_mode_keyboard(),
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Ошибка экспертного анализа для пользователя {user_id}: {e}")
        await query.edit_message_text(
            "❌ **Техническая ошибка**\n\n"
            "Произошла ошибка при анализе. Попробуйте еще раз!",
            reply_markup=get_expert_mode_keyboard(),
            parse_mode='Markdown'
        )

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    welcome_message = utils.get_random_message(config.WELCOME_MESSAGES)
    
    full_message = f"{welcome_message}\n\nПривет, {user.first_name}! 👋\n\nЯ - твой дружелюбный помощник по растениям! 🌱\n\nОтправь мне фотографию любого растения, и я расскажу тебе о нем все самое интересное! 📸\n\nИспользуй кнопки ниже для навигации:"
    
    await update.message.reply_text(
        full_message,
        reply_markup=get_main_keyboard(),
        parse_mode='Markdown'
    )
    
    # Проверяем количество запросов и отправляем промо при необходимости
    await utils.check_and_send_promo(update, context, user.id)
    
    logger.info(f"Пользователь {user.id} ({user.username}) запустил бота")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """❓ **Как я могу помочь?**

Я - эксперт по растениям! Вот что я умею:

🌿 **Распознавать растения** по фотографиям
💡 **Рассказывать интересные факты** о каждом растении
🌍 **Объяснять**, где растет растение
🌸 **Информировать** о периоде цветения
🏠 **Давать советы** по выращиванию дома

**Как использовать:**
1. 📸 Отправь мне фотографию растения
2. 🔍 Я проанализирую изображение
3. 🌱 Получи подробную информацию!

Выбери, что тебя интересует:"""
    
    await update.message.reply_text(
        help_text,
        reply_markup=get_help_keyboard(),
        parse_mode='Markdown'
    )
    
    # Проверяем количество запросов и отправляем промо при необходимости
    user = update.effective_user
    await utils.check_and_send_promo(update, context, user.id)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /about"""
    about_text = """ℹ️ **О боте "Растения-Эксперт"**

Я создан, чтобы помочь тебе узнать больше о мире растений! 🌱

**Мои возможности:**
• 🔍 Точное распознавание растений по фото
• 📚 Обширная база знаний о растениях
• 💡 Интересные факты и советы
• 🌍 Информация о местах произрастания
• 🏠 Рекомендации по домашнему выращиванию

**Технологии:**
• 🤖 Искусственный интеллект Qwen
• 📸 Анализ изображений
• 🌐 OpenRouter API

Выбери, что хочешь узнать подробнее:"""
    
    await update.message.reply_text(
        about_text,
        reply_markup=get_about_keyboard(),
        parse_mode='Markdown'
    )
    
    # Проверяем количество запросов и отправляем промо при необходимости
    user = update.effective_user
    await utils.check_and_send_promo(update, context, user.id)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик фотографий растений и экспертного режима"""
    user = update.effective_user
    
    # Определяем режим распознавания
    recognition_mode = utils.get_user_recognition_mode(user.id)
    
    # Получаем фото с лучшим качеством
    photo = update.message.photo[-1]
    
    if recognition_mode == "expert":
        # Экспертный режим - обрабатываем множественные фото
        await handle_expert_photo(update, context, photo)
        return
    
    # Обычный режим распознавания растений
    processing_message = utils.get_random_message(config.PHOTO_MESSAGES)
    
    status_message = await update.message.reply_text(
        f"{processing_message}\n\n⏳ Обрабатываю изображение...",
        reply_markup=get_main_menu_inline()
    )
    
    try:
        # Скачиваем фото
        file = await context.bot.get_file(photo.file_id)
        image_bytes = await file.download_as_bytearray()
        
        # Распознаем растение
        recognition_info, error = await utils.recognize_plant_with_qwen(image_bytes)
        formatted_response = utils.format_plant_response(recognition_info) if recognition_info else None
        log_message = "растение"
        
        if recognition_info:
            # Отправляем результат
            await update.message.reply_text(
                formatted_response,
                reply_markup=get_main_keyboard(),
                parse_mode='Markdown'
            )
            
            # Проверяем количество запросов и отправляем промо при необходимости
            await utils.check_and_send_promo(update, context, user.id)
            
            logger.info(f"Пользователь {user.id} успешно распознал {log_message}")
        else:
            # Отправляем сообщение об ошибке
            error_message = f"❌ {error}\n\nПопробуйте отправить более четкое фото растения! 📸"
            
            await update.message.reply_text(
                error_message,
                reply_markup=get_restart_keyboard()
            )
            
            logger.warning(f"Ошибка распознавания {log_message} для пользователя {user.id}: {error}")
        
        # Очищаем режим после обработки фото
        utils.clear_user_recognition_mode(user.id)
    
    except Exception as e:
        logger.error(f"Ошибка при обработке фото пользователя {user.id}: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при обработке фото. Попробуйте еще раз! 🔄",
            reply_markup=get_restart_keyboard()
        )
        # Очищаем режим при ошибке
        utils.clear_user_recognition_mode(user.id)
    
    finally:
        # Удаляем статусное сообщение
        try:
            await status_message.delete()
        except:
            pass

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user = update.effective_user
    text = update.message.text.lower()
    
    # Проверяем, ожидается ли текст в экспертном режиме
    expert_data = utils.get_expert_data(user.id)
    if expert_data and expert_data.get('waiting_for_text'):
        # Сохраняем дополнительное описание
        utils.set_expert_additional_text(user.id, update.message.text)
        utils.set_expert_waiting_state(user.id, waiting_for_text=False)
        
        # Создаем клавиатуру для продолжения
        keyboard = [
            [InlineKeyboardButton("📸 Добавить еще фото", callback_data="add_more_photos")],
            [InlineKeyboardButton("✍️ Изменить описание", callback_data="add_description")], 
            [InlineKeyboardButton("🧬 Начать анализ", callback_data="start_expert_analysis_now")],
            [InlineKeyboardButton("🗑️ Очистить все", callback_data="clear_expert_data")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        expert_keyboard = InlineKeyboardMarkup(keyboard)
        
        photo_count = len(expert_data['photos'])
        await update.message.reply_text(
            f"✅ **Описание сохранено!**\n\n"
            f"📸 **Фотографий:** {photo_count}\n"
            f"✍️ **Описание:** ✅ Есть\n\n"
            f"📝 **Ваше описание:**\n_{update.message.text}_\n\n"
            f"Теперь можете добавить еще фото или начать анализ!",
            reply_markup=expert_keyboard,
            parse_mode='Markdown'
        )
        return
    
    if "распознать растение" in text or "растение" in text:
        utils.set_user_recognition_mode(user.id, "plant")
        await update.message.reply_text(
            "🌿 Отлично! Отправь мне фотографию растения, и я его распознаю!\n\n📸 Просто сделай фото или выбери из галереи.",
            reply_markup=get_main_menu_inline()
        )
        # Проверяем количество запросов и отправляем промо при необходимости
        await utils.check_and_send_promo(update, context, user.id)
    
    elif "экспертный режим" in text or "экспертный" in text:
        # Показываем информацию об экспертном режиме
        expert_info_text = """🧬 **Экспертный режим распознавания**

🎯 **Возможности экспертного режима:**

• 📸 **Множественные фотографии** - отправьте несколько ракурсов растения
• ✍️ **Дополнительная информация** - добавьте описание места находки, особенности
• 🔬 **Научный анализ** - детальная морфологическая диагностика  
• 📊 **Варианты определения** - получите несколько возможных видов с вероятностями
• 🧠 **Экспертные рассуждения** - увидите логику определения

**Преимущества:**
• Значительно выше точность определения
• Систематический подход к анализу
• Учет экологических факторов
• Профессиональные рекомендации

Готовы к научному подходу? 🔬"""

        await update.message.reply_text(
            expert_info_text,
            reply_markup=get_expert_mode_keyboard(),
            parse_mode='Markdown'
        )
        # Проверяем количество запросов и отправляем промо при необходимости
        await utils.check_and_send_promo(update, context, user.id)
    
    elif "цветочный тест люшера" in text or "цветочный тест" in text:
        flower_test_text = """🌸 **Цветочный тест Люшера**

Ого! Узнал что за цветочек на фото, а хочешь узнать что за цветочек ты сам? 😉

🌺 Этот психологический тест поможет тебе:
• Узнать о своих скрытых качествах
• Понять свое эмоциональное состояние
• Открыть новые стороны личности

Тест основан на выборе цветов, которые тебе больше всего нравятся. Каждый цвет расскажет что-то важное о тебе!

Готов узнать, какой ты цветочек? 🌸"""
        
        await update.message.reply_text(
            flower_test_text,
            reply_markup=get_flower_test_keyboard(),
            parse_mode='Markdown'
        )
        # Проверяем количество запросов и отправляем промо при необходимости
        await utils.check_and_send_promo(update, context, user.id)
    
    elif "о боте" in text or "информация" in text:
        await about_command(update, context)
        # Проверяем количество запросов и отправляем промо при необходимости
        await utils.check_and_send_promo(update, context, user.id)
    
    elif "помощь" in text or "help" in text:
        await help_command(update, context)
        # Проверяем количество запросов и отправляем промо при необходимости
        await utils.check_and_send_promo(update, context, user.id)
    
    elif "обратная связь" in text or "отзыв" in text:
        feedback_text = """💚 **Обратная связь**

Мне очень важно твое мнение! Расскажи, как я работаю:

• ⭐ Оцени мою работу
• 💬 Предложи улучшения
• 🐛 Сообщи об ошибках
• 👨‍💼 Связаться с администратором
• 🤝 Заказать похожего бота
• 💝 Поддержать проект

Выбери, что хочешь сделать:"""
        
        await update.message.reply_text(
            feedback_text,
            reply_markup=get_feedback_keyboard(),
            parse_mode='Markdown'
        )
        # Проверяем количество запросов и отправляем промо при необходимости
        await utils.check_and_send_promo(update, context, user.id)
    
    elif any(word in text for word in ["поддержка", "админ", "администратор", "связаться", "помощь с ботом"]):
        admin_link, message_text = utils.get_admin_link_with_text("support")
        contact_text = f"""👨‍💼 **Связь с администратором**

🔗 **Нажми на ссылку**, чтобы написать админу:
[Написать администратору]({admin_link})

📝 **Готовый текст:**
```
{message_text}
```

💬 Скопируй текст и отправь администратору!"""
        
        await update.message.reply_text(
            contact_text,
            reply_markup=get_feedback_keyboard(),
            parse_mode='Markdown'
        )
        # Проверяем количество запросов и отправляем промо при необходимости
        await utils.check_and_send_promo(update, context, user.id)
    
    elif any(word in text for word in ["заказать бота", "создать бота", "разработка", "бизнес"]):
        admin_link, message_text = utils.get_admin_link_with_text("order_bot")
        order_text = f"""🤝 **Заказ бота**

Хотите похожего бота? Обратитесь к разработчику!

🔗 **Написать о заказе:**
[Связаться с администратором]({admin_link})

📝 **Готовый текст:**
```
{message_text}
```

🚀 Давайте обсудим ваш проект!"""
        
        await update.message.reply_text(
            order_text,
            reply_markup=get_feedback_keyboard(),
            parse_mode='Markdown'
        )
        # Проверяем количество запросов и отправляем промо при необходимости
        await utils.check_and_send_promo(update, context, user.id)
    
    elif any(word in text for word in ["поддержать", "донат", "спасибо", "благодарность"]):
        admin_link, message_text = utils.get_admin_link_with_text("support_project")
        support_text = f"""💝 **Поддержка проекта**

Благодарим за желание поддержать проект! 🙏

🔗 **Связаться с создателем:**
[Написать администратору]({admin_link})

📝 **Готовый текст:**
```
{message_text}
```

Ваша поддержка помогает развивать проект! 💚"""
        
        await update.message.reply_text(
            support_text,
            reply_markup=get_feedback_keyboard(),
            parse_mode='Markdown'
        )
        # Проверяем количество запросов и отправляем промо при необходимости
        await utils.check_and_send_promo(update, context, user.id)
    
    elif any(word in text for word in ["уроки биологии", "уроки", "биология", "ежедневные уроки"]):
        await lessons_command(update, context)
    
    else:
        await update.message.reply_text(
            "🤔 Не совсем понимаю, что ты хочешь.\n\nОтправь мне фотографию растения для распознавания, или используй кнопки меню! 🌿",
            reply_markup=get_main_keyboard()
        )
        # Проверяем количество запросов и отправляем промо при необходимости
        await utils.check_and_send_promo(update, context, user.id)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback запросов от инлайн кнопок"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "main_menu":
        welcome_message = utils.get_random_message(config.WELCOME_MESSAGES)
        user = update.effective_user
        
        full_message = f"{welcome_message}\n\nПривет, {user.first_name}! 👋\n\nЯ - твой дружелюбный помощник по растениям! 🌱\n\nОтправь мне фотографию любого растения, и я расскажу тебе о нем все самое интересное! 📸\n\nВыбери что тебя интересует:"
        
        await query.edit_message_text(
            full_message,
            reply_markup=get_main_keyboard_inline(),
            parse_mode='Markdown'
        )
    
    elif query.data == "help_photo":
        help_photo_text = """📸 **Как отправить фото растения:**

1. **Сделай новое фото:**
   • Нажми на скрепку 📎
   • Выбери "Камера" 📱
   • Сфотографируй растение
   • Отправь фото

2. **Выбери из галереи:**
   • Нажми на скрепку 📎
   • Выбери "Галерея" 🖼️
   • Найди фото растения
   • Отправь фото

**Советы для лучшего распознавания:**
• 📱 Фото должно быть четким
• 🌿 Растение должно занимать большую часть кадра
• ☀️ Хорошее освещение
• 🔍 Фокус на растении, а не на фоне"""
        
        await query.edit_message_text(
            help_photo_text,
            reply_markup=get_photo_tips_keyboard(),
            parse_mode='Markdown'
        )
    
    elif query.data == "help_tips":
        tips_text = """🌱 **Советы по фотографированию растений:**

**Для лучшего распознавания:**

📸 **Качество фото:**
• Используй хорошее освещение ☀️
• Фото должно быть четким и не размытым
• Избегай теней и бликов

🌿 **Композиция:**
• Растение должно занимать 70-80% кадра
• Покажи листья, цветы, стебель
• Убери отвлекающие предметы с фона

🔍 **Детали:**
• Сфотографируй характерные части растения
• Если есть цветы - обязательно включи их
• Покажи форму листьев

**Примеры хороших фото:**
• Крупный план листа или цветка
• Общий вид растения на нейтральном фоне
• Фото в естественном освещении"""
        
        await query.edit_message_text(
            tips_text,
            reply_markup=get_photo_tips_keyboard(),
            parse_mode='Markdown'
        )
    
    elif query.data == "help_features":
        features_text = """🔍 **Что я умею:**

🌿 **Распознавание растений:**
• Определяю название растения
• Описываю внешний вид
• Рассказываю интересные факты

🌍 **Географическая информация:**
• Где растет растение в природе
• Климатические условия
• Тип почвы и среды обитания

🌸 **Биологические особенности:**
• Период цветения
• Сезонность роста
• Особенности ухода

🏠 **Домашнее выращивание:**
• Можно ли выращивать дома
• Требования к уходу
• Советы по содержанию

💡 **Дополнительные возможности:**
• Работаю с любыми растениями
• Понимаю фото на разных языках
• Даю дружелюбные ответы с эмодзи"""
        
        await query.edit_message_text(
            features_text,
            reply_markup=get_help_keyboard(),
            parse_mode='Markdown'
        )
    
    elif query.data == "about_features":
        about_features_text = """🌟 **Мои возможности:**

🌿 **Точное распознавание:**
• Определяю более 10,000 видов растений
• Работаю с цветами, деревьями, травами
• Распознаю даже редкие экземпляры

📚 **Обширные знания:**
• Научные названия растений
• Народные названия и легенды
• Интересные факты и истории

🌍 **Географическая информация:**
• Континенты и страны произрастания
• Климатические зоны
• Типы экосистем

🏠 **Практические советы:**
• Условия выращивания дома
• Требования к поливу и свету
• Советы по уходу

💚 **Дружелюбность:**
• Простые объяснения
• Красивые эмодзи
• Позитивный настрой"""
        
        await query.edit_message_text(
            about_features_text,
            reply_markup=get_about_keyboard(),
            parse_mode='Markdown'
        )
    
    elif query.data == "about_tech":
        tech_text = """🔧 **Технологии:**

🤖 **Искусственный интеллект:**
• Модель Qwen 2.5 7B Instruct
• Обучена на миллионах изображений растений
• Понимает контекст и детали

📸 **Обработка изображений:**
• Анализ качества фото
• Оптимизация для API
• Поддержка различных форматов

🌐 **API интеграция:**
• OpenRouter для доступа к AI моделям
• Быстрая обработка запросов
• Надежная доставка ответов

💻 **Архитектура:**
• Асинхронная обработка
• Обработка ошибок
• Логирование действий

🔒 **Безопасность:**
• Защищенные API ключи
• Валидация входных данных
• Приватность пользователей"""
        
        await query.edit_message_text(
            tech_text,
            reply_markup=get_about_keyboard(),
            parse_mode='Markdown'
        )
    
    elif query.data == "about_examples":
        examples_text = """💡 **Примеры работы:**

🌹 **Роза:**
• Название: Роза (Rosa)
• Описание: Красивый цветок с ароматными лепестками
• Факт: Розы выращивают более 5000 лет
• Где растет: Сады, парки, дикая природа
• Цветение: Весна-осень
• Дома: Отлично подходит для выращивания

🌵 **Кактус:**
• Название: Кактус (Cactaceae)
• Описание: Суккулент с колючками
• Факт: Могут жить без воды месяцами
• Где растет: Пустыни, засушливые регионы
• Цветение: Различное время года
• Дома: Очень неприхотлив в уходе

🌻 **Подсолнух:**
• Название: Подсолнечник (Helianthus)
• Описание: Высокое растение с желтыми цветами
• Факт: Цветы поворачиваются к солнцу
• Где растет: Поля, сады, обочины дорог
• Цветение: Лето-осень
• Дома: Можно выращивать на балконе"""
        
        await query.edit_message_text(
            examples_text,
            reply_markup=get_about_keyboard(),
            parse_mode='Markdown'
        )
    

    
    elif query.data == "new_photo" or query.data == "new_photo_plant":
        utils.set_user_recognition_mode(query.from_user.id, "plant")
        await query.edit_message_text(
            "📱 **Новое фото растения:**\n\nОтлично! Готов к новому распознаванию! 🌿\n\nОтправь мне фотографию растения, и я его изучу! 📸\n\nПомни советы:\n• Четкое фото\n• Хорошее освещение\n• Растение в центре кадра\n\nЖду твое фото! 💚",
            reply_markup=get_main_menu_inline(),
            parse_mode='Markdown'
        )
    
    elif query.data == "expert_mode":
        # Показываем информацию об экспертном режиме
        expert_info_text = """🧬 **Экспертный режим распознавания**

🎯 **Возможности экспертного режима:**

• 📸 **Множественные фотографии** - отправьте несколько ракурсов растения
• ✍️ **Дополнительная информация** - добавьте описание места находки, особенности
• 🔬 **Научный анализ** - детальная морфологическая диагностика  
• 📊 **Варианты определения** - получите несколько возможных видов с вероятностями
• 🧠 **Экспертные рассуждения** - увидите логику определения

**Преимущества:**
• Значительно выше точность определения
• Систематический подход к анализу
• Учет экологических факторов
• Профессиональные рекомендации

Готовы к научному подходу? 🔬"""

        await query.edit_message_text(
            expert_info_text,
            reply_markup=get_expert_mode_keyboard(),
            parse_mode='Markdown'
        )
    
    elif query.data == "start_expert_analysis":
        utils.set_user_recognition_mode(query.from_user.id, "expert")
        await query.edit_message_text(
            "🧬 **Экспертный режим активирован!**\n\n"
            "📸 **Шаг 1:** Отправьте первое фото растения\n\n"
            "💡 **Рекомендации для максимальной точности:**\n"
            "• Общий вид растения (габитус)\n"
            "• Крупный план листьев\n" 
            "• Цветки/соцветия (если есть)\n"
            "• Плоды/семена (если есть)\n"
            "• Место произрастания\n\n"
            "После загрузки фото вы сможете:\n"
            "✍️ Добавить описание находки\n"
            "📸 Загрузить дополнительные фотографии\n"
            "🔬 Начать научный анализ\n\n"
            "🎯 Начинайте загрузку фотографий!",
            reply_markup=get_main_menu_inline(),
            parse_mode='Markdown'
        )
    
    elif query.data == "flower_test":
        flower_test_text = """🌸 **Цветочный тест Люшера**

Ого! Узнал что за цветочек на фото, а хочешь узнать что за цветочек ты сам? 😉

🌺 Этот психологический тест поможет тебе:
• Узнать о своих скрытых качествах
• Понять свое эмоциональное состояние
• Открыть новые стороны личности

Тест основан на выборе цветов, которые тебе больше всего нравятся. Каждый цвет расскажет что-то важное о тебе!

Готов узнать, какой ты цветочек? 🌸"""
        
        await query.edit_message_text(
            flower_test_text,
            reply_markup=get_flower_test_keyboard(),
            parse_mode='Markdown'
        )
    
    # Обработчики экспертного режима
    elif query.data == "add_more_photos":
        await query.edit_message_text(
            "📸 **Добавление фотографий**\n\n"
            "Отправьте дополнительные фотографии растения.\n\n"
            "💡 **Полезные ракурсы:**\n"
            "• Разные части растения (листья, стебель, цветы)\n"
            "• Детальные снимки характерных признаков\n"
            "• Место произрастания (биотоп)\n\n"
            "Каждое новое фото будет автоматически добавлено к анализу!",
            reply_markup=get_main_menu_inline(),
            parse_mode='Markdown'
        )
    
    elif query.data == "add_description":
        utils.set_expert_waiting_state(query.from_user.id, waiting_for_text=True)
        await query.edit_message_text(
            "✍️ **Дополнительное описание**\n\n"
            "Отправьте текстовое сообщение с дополнительной информацией:\n\n"
            "📝 **Что указать:**\n"
            "• Место находки (лес, поле, сад, болото)\n"
            "• Время года и условия\n"
            "• Размеры растения\n"
            "• Особые признаки или запах\n"
            "• Любые другие наблюдения\n\n"
            "Напишите ваше описание следующим сообщением 👇",
            reply_markup=get_main_menu_inline(),
            parse_mode='Markdown'
        )
    
    elif query.data == "start_expert_analysis_now":
        await handle_expert_analysis(query)
    
    elif query.data == "clear_expert_data":
        utils.clear_expert_data(query.from_user.id)
        await query.edit_message_text(
            "🗑️ **Данные очищены**\n\n"
            "Все фотографии и описания удалены.\n"
            "Можете начать заново!",
            reply_markup=get_expert_mode_keyboard(),
            parse_mode='Markdown'
        )
    
    elif query.data == "expert_info":
        expert_help_text = """🧬 **Что такое экспертный режим?**

🎯 **Это продвинутый режим** для максимально точного определения растений с использованием научных методов ботаники.

**🔬 Научный подход:**
• Морфологический анализ всех органов
• Систематическая классификация
• Учет экологических факторов
• Сравнение с ботаническими базами данных

**📸 Множественные фото помогают:**
• Увидеть растение под разными углами
• Рассмотреть детали строения
• Определить размеры и пропорции
• Оценить условия произрастания

**✍️ Текстовое описание дает:**
• Информацию о биотопе
• Данные о размерах
• Особенности, не видные на фото
• Дополнительный контекст

**💡 Результат:** Значительно более точное и научно обоснованное определение!"""

        await query.edit_message_text(
            expert_help_text,
            reply_markup=get_expert_mode_keyboard(),
            parse_mode='Markdown'
        )
    
    elif query.data == "restart":
        welcome_message = utils.get_random_message(config.WELCOME_MESSAGES)
        user = update.effective_user
        
        full_message = f"{welcome_message}\n\nПривет, {user.first_name}! 👋\n\nЯ - твой дружелюбный помощник по растениям! 🌱\n\nОтправь мне фотографию любого растения, и я расскажу тебе о нем все самое интересное! 📸\n\nИспользуй кнопки ниже для навигации:"
        
        await query.edit_message_text(
            full_message,
            reply_markup=get_main_keyboard_inline(),
            parse_mode='Markdown'
        )
    

    
    elif query.data == "subscribe_lessons":
        # Для callback запросов нужно обработать подписку напрямую
        user = query.from_user
        user_id = user.id
        
        # Подписываем пользователя
        utils.subscribe_to_biology_lessons(user_id)
        
        success_text = """✅ **Подписка активирована!**

🎉 Поздравляю! Теперь ты будешь получать ежедневные мини-уроки по биологии!

📅 **Что дальше:**
• Первый урок придет завтра в 10:00
• Каждый день новая тема
• Уроки будут интересными и простыми

🔬 А пока можешь получить пробный урок прямо сейчас! 👇"""
        
        await query.edit_message_text(
            success_text,
            reply_markup=get_lessons_subscribed_keyboard(),
            parse_mode='Markdown'
        )
        
        logger.info(f"Пользователь {user_id} подписался на уроки биологии через callback")
    
    elif query.data == "unsubscribe_lessons":
        # Для callback запросов нужно обработать отписку напрямую
        user = query.from_user
        user_id = user.id
        
        # Отписываем пользователя
        utils.unsubscribe_from_biology_lessons(user_id)
        
        unsubscribe_text = """❌ **Подписка отменена**

Жаль, что ты решил отписаться от уроков биологии! 😢

🔄 **В любое время ты можешь:**
• Снова подписаться на уроки
• Получить разовый урок
• Изучать растения через фотографии

Буду рад видеть тебя снова! 💚"""
        
        await query.edit_message_text(
            unsubscribe_text,
            reply_markup=get_lessons_unsubscribed_keyboard(),
            parse_mode='Markdown'
        )
        
        logger.info(f"Пользователь {user_id} отписался от уроков биологии через callback")
    
    elif query.data == "sample_lesson":
        # Для callback запросов нужно обработать получение урока напрямую
        user = query.from_user
        user_id = user.id
        
        # Получаем следующий урок для пользователя
        lesson = utils.get_next_lesson_for_user(user_id)
        formatted_lesson = utils.format_biology_lesson(lesson)
        
        await query.edit_message_text(
            formatted_lesson,
            reply_markup=get_lessons_after_sample_keyboard(utils.is_subscribed_to_biology_lessons(user_id)),
            parse_mode='Markdown'
        )
        
        logger.info(f"Пользователь {user_id} получил пробный урок биологии через callback")
    
    elif query.data == "lessons_menu":
        # Для callback запросов нужно показать меню уроков напрямую
        user = query.from_user
        user_id = user.id
        
        # Проверяем статус подписки
        is_subscribed = utils.is_subscribed_to_biology_lessons(user_id)
        
        if is_subscribed:
            lessons_text = """🧬 **Ежедневные уроки биологии**

✅ Ты подписан на ежедневные мини-уроки!

📅 **Как это работает:**
• Каждый день в 10:00 ты получаешь новый урок
• Уроки простые и интересные
• Каждый урок с фактами и вопросами для размышления

🎯 **Что можно сделать:**"""
            
            await query.edit_message_text(
                lessons_text,
                reply_markup=get_lessons_subscribed_keyboard(),
                parse_mode='Markdown'
            )
        else:
            lessons_text = """🧬 **Ежедневные уроки биологии**

Хочешь каждый день узнавать что-то новое о мире биологии? 🌱

📚 **Что ты получишь:**
• Короткие и понятные уроки
• Интересные факты о живой природе
• Вопросы для размышления
• Дружелюбный и простой язык

⏰ **Время отправки:** каждый день в 10:00

Присоединяйся к изучению удивительного мира биологии! 🔬"""
            
            await query.edit_message_text(
                lessons_text,
                reply_markup=get_lessons_unsubscribed_keyboard(),
                parse_mode='Markdown'
            )
        
        logger.info(f"Пользователь {user_id} открыл меню уроков биологии через callback")

async def lessons_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /lessons - управление ежедневными уроками биологии"""
    user = update.effective_user
    user_id = user.id
    
    # Проверяем статус подписки
    is_subscribed = utils.is_subscribed_to_biology_lessons(user_id)
    
    if is_subscribed:
        lessons_text = """🧬 **Ежедневные уроки биологии**

✅ Ты подписан на ежедневные мини-уроки!

📅 **Как это работает:**
• Каждый день в 10:00 ты получаешь новый урок
• Уроки простые и интересные
• Каждый урок с фактами и вопросами для размышления

🎯 **Что можно сделать:**"""
        
        await update.message.reply_text(
            lessons_text,
            reply_markup=get_lessons_subscribed_keyboard(),
            parse_mode='Markdown'
        )
    else:
        lessons_text = """🧬 **Ежедневные уроки биологии**

Хочешь каждый день узнавать что-то новое о мире биологии? 🌱

📚 **Что ты получишь:**
• Короткие и понятные уроки
• Интересные факты о живой природе
• Вопросы для размышления
• Дружелюбный и простой язык

⏰ **Время отправки:** каждый день в 10:00

Присоединяйся к изучению удивительного мира биологии! 🔬"""
        
        await update.message.reply_text(
            lessons_text,
            reply_markup=get_lessons_unsubscribed_keyboard(),
            parse_mode='Markdown'
        )
    
    # Проверяем количество запросов и отправляем промо при необходимости
    await utils.check_and_send_promo(update, context, user_id)
    
    logger.info(f"Пользователь {user_id} открыл меню уроков биологии")

async def subscribe_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подписка на ежедневные уроки биологии"""
    user = update.effective_user
    user_id = user.id
    
    # Подписываем пользователя
    utils.subscribe_to_biology_lessons(user_id)
    
    success_text = """✅ **Подписка активирована!**

🎉 Поздравляю! Теперь ты будешь получать ежедневные мини-уроки по биологии!

📅 **Что дальше:**
• Первый урок придет завтра в 10:00
• Каждый день новая тема
• Уроки будут интересными и простыми

🔬 А пока можешь получить пробный урок прямо сейчас! 👇"""
    
    await update.message.reply_text(
        success_text,
        reply_markup=get_lessons_subscribed_keyboard(),
        parse_mode='Markdown'
    )
    
    logger.info(f"Пользователь {user_id} подписался на уроки биологии")

async def unsubscribe_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отписка от ежедневных уроков биологии"""
    user = update.effective_user
    user_id = user.id
    
    # Отписываем пользователя
    utils.unsubscribe_from_biology_lessons(user_id)
    
    unsubscribe_text = """❌ **Подписка отменена**

Жаль, что ты решил отписаться от уроков биологии! 😢

🔄 **В любое время ты можешь:**
• Снова подписаться на уроки
• Получить разовый урок
• Изучать растения через фотографии

Буду рад видеть тебя снова! 💚"""
    
    await update.message.reply_text(
        unsubscribe_text,
        reply_markup=get_lessons_unsubscribed_keyboard(),
        parse_mode='Markdown'
    )
    
    logger.info(f"Пользователь {user_id} отписался от уроков биологии")

async def get_sample_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет пробный урок биологии"""
    user = update.effective_user
    user_id = user.id
    
    # Получаем следующий урок для пользователя
    lesson = utils.get_next_lesson_for_user(user_id)
    formatted_lesson = utils.format_biology_lesson(lesson)
    
    await update.message.reply_text(
        formatted_lesson,
        reply_markup=get_lessons_after_sample_keyboard(utils.is_subscribed_to_biology_lessons(user_id)),
        parse_mode='Markdown'
    )
    
    # Проверяем количество запросов и отправляем промо при необходимости
    await utils.check_and_send_promo(update, context, user_id)
    
    logger.info(f"Пользователь {user_id} получил пробный урок биологии")

async def send_daily_lessons(context: ContextTypes.DEFAULT_TYPE):
    """Отправляет ежедневные уроки всем подписанным пользователям"""
    subscribed_users = utils.get_subscribed_users()
    
    if not subscribed_users:
        logger.info("Нет подписанных пользователей для отправки уроков")
        return
    
    logger.info(f"Отправка ежедневных уроков {len(subscribed_users)} пользователям")
    
    for user_id in subscribed_users:
        try:
            # Получаем следующий урок для пользователя
            lesson = utils.get_next_lesson_for_user(user_id)
            formatted_lesson = utils.format_biology_lesson(lesson)
            
            # Отправляем урок
            await context.bot.send_message(
                chat_id=user_id,
                text=formatted_lesson,
                parse_mode='Markdown'
            )
            
            logger.info(f"Урок отправлен пользователю {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки урока пользователю {user_id}: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка в боте: {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Произошла непредвиденная ошибка. Попробуйте еще раз или начните заново! 🔄",
            reply_markup=get_restart_keyboard()
        )
