from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
import config

def get_main_keyboard():
    """Главная клавиатура бота"""
    keyboard = [
        [KeyboardButton("🌿 Распознать растение"), KeyboardButton("🧬 Экспертный режим")],
        [KeyboardButton("ℹ️ О боте"), KeyboardButton("🌱 Уроки биологии")],
        [KeyboardButton("🌸 Цветочный тест Люшера"), KeyboardButton("❓ Помощь")],
        [KeyboardButton("💚 Обратная связь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_help_keyboard():
    """Клавиатура помощи"""
    keyboard = [
        [InlineKeyboardButton("📸 Как отправить фото", callback_data="help_photo")],
        [InlineKeyboardButton("🌱 Советы по фото", callback_data="help_tips")],
        [InlineKeyboardButton("🔍 Что я умею", callback_data="help_features")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_about_keyboard():
    """Клавиатура информации о боте"""
    keyboard = [
        [InlineKeyboardButton("🌟 Возможности", callback_data="about_features")],
        [InlineKeyboardButton("🔧 Технологии", callback_data="about_tech")],
        [InlineKeyboardButton("💡 Примеры", callback_data="about_examples")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_feedback_keyboard():
    """Клавиатура обратной связи"""
    # Получаем ссылку на администратора
    if config.ADMIN_USERNAME:
        admin_url = f"https://t.me/{config.ADMIN_USERNAME.lstrip('@')}"
    else:
        admin_url = f"tg://user?id={config.ADMIN_ID}"
    
    keyboard = [
        [InlineKeyboardButton("⭐ Оценить бота", url=admin_url)],
        [InlineKeyboardButton("💬 Предложить улучшение", url=admin_url)],
        [InlineKeyboardButton("🐛 Сообщить об ошибке", url=admin_url)],
        [InlineKeyboardButton("👨‍💼 Связаться с администратором", url=admin_url)],
        [InlineKeyboardButton("🤝 Заказать бота", url=admin_url)],
        [InlineKeyboardButton("💝 Поддержать проект", url=admin_url)],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_photo_tips_keyboard():
    """Клавиатура с советами по фото"""
    keyboard = [
        [InlineKeyboardButton("📱 Сделать новое фото", callback_data="new_photo")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu_inline():
    """Инлайн кнопка возврата в главное меню"""
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)

def get_expert_mode_keyboard():
    """Клавиатура для экспертного режима"""
    keyboard = [
        [InlineKeyboardButton("🔬 Начать экспертный анализ", callback_data="start_expert_analysis")],
        [InlineKeyboardButton("ℹ️ Что такое экспертный режим?", callback_data="expert_info")],
        [InlineKeyboardButton("🏠 Назад в главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_keyboard_inline():
    """Главная инлайн клавиатура для callback'ов"""
    keyboard = [
        [InlineKeyboardButton("🌿 Распознать растение", callback_data="new_photo_plant"), 
         InlineKeyboardButton("🧬 Экспертный режим", callback_data="expert_mode")],
        [InlineKeyboardButton("🧬 Уроки биологии", callback_data="lessons_menu")],
        [InlineKeyboardButton("🌸 Цветочный тест Люшера", callback_data="flower_test")],
        [InlineKeyboardButton("ℹ️ О боте", callback_data="about_features"), InlineKeyboardButton("❓ Помощь", callback_data="help_features")],
        [InlineKeyboardButton("💚 Обратная связь", callback_data="feedback_suggest")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_restart_keyboard():
    """Клавиатура для перезапуска бота"""
    keyboard = [
        [InlineKeyboardButton("🔄 Начать заново", callback_data="restart")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_flower_test_keyboard():
    """Клавиатура для цветочного теста Люшера"""
    keyboard = [
        [InlineKeyboardButton("🌸 Начать тест", web_app=WebAppInfo("https://flowerxai.vercel.app"))],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_lessons_unsubscribed_keyboard():
    """Клавиатура для неподписанных пользователей на уроки биологии"""
    keyboard = [
        [InlineKeyboardButton("✅ Подписаться на уроки", callback_data="subscribe_lessons")],
        [InlineKeyboardButton("🔬 Попробовать урок", callback_data="sample_lesson")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_lessons_subscribed_keyboard():
    """Клавиатура для подписанных пользователей на уроки биологии"""
    keyboard = [
        [InlineKeyboardButton("🔬 Получить урок сейчас", callback_data="sample_lesson")],
        [InlineKeyboardButton("❌ Отписаться", callback_data="unsubscribe_lessons")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_lessons_after_sample_keyboard(is_subscribed):
    """Клавиатура после получения пробного урока"""
    if is_subscribed:
        keyboard = [
            [InlineKeyboardButton("🔬 Еще урок", callback_data="sample_lesson")],
            [InlineKeyboardButton("⚙️ Управление подпиской", callback_data="lessons_menu")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("✅ Подписаться на ежедневные уроки", callback_data="subscribe_lessons")],
            [InlineKeyboardButton("🔬 Еще урок", callback_data="sample_lesson")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
    return InlineKeyboardMarkup(keyboard)
