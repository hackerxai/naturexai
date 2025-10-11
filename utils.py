import aiohttp
import asyncio
import base64
import io
from PIL import Image
import config
from telegram import InputMediaPhoto
import logging

# Словарь для отслеживания количества запросов пользователей
user_request_count = {}

# Кеш рабочих моделей для оптимизации fallback
working_models_cache = {}

async def recognize_with_fallback(image_data, prompt, task_type="plant"):
    """Универсальная функция распознавания с поддержкой множественных изображений"""
    
    for model_key in config.FALLBACK_MODELS:
        if model_key not in config.AVAILABLE_MODELS:
            continue
            
        model_name = config.AVAILABLE_MODELS[model_key]
        
        try:
            print(f"Пробуем модель: {model_name}")
            
            # Подготавливаем изображения
            content_parts = [{"type": "text", "text": prompt}]
            
            # Обрабатываем одно или несколько изображений
            if isinstance(image_data, list):
                # Множественные изображения
                for i, image_bytes in enumerate(image_data):
                    base64_image = await encode_image_to_base64(image_bytes)
                    if base64_image:
                        content_parts.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        })
                        print(f"  📸 Изображение {i+1}/{len(image_data)} обработано")
            else:
                # Одиночное изображение
                base64_image = await encode_image_to_base64(image_data)
                if base64_image:
                    content_parts.append({
                        "type": "image_url", 
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    })
            
            if len(content_parts) == 1:  # Только текст, нет изображений
                print(f"❌ Не удалось обработать изображения для модели {model_name}")
                continue
            
            # Формируем запрос к OpenRouter API
            headers = {
                "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/plant-recognition-bot",
                "X-Title": "Plant Recognition Bot - Expert Mode" if task_type == "expert" else "Plant Recognition Bot"
            }
            
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user", 
                        "content": content_parts
                    }
                ],
                "max_tokens": 1500 if task_type == "expert" else 1000,
                "temperature": 0.7
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(config.OPENROUTER_BASE_URL + "/chat/completions", 
                                      headers=headers, json=payload) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        if 'choices' in result and result['choices']:
                            recognition_text = result['choices'][0]['message']['content']
                            print(f"✅ Модель {model_name} сработала успешно!")
                            
                            # Сохраняем рабочую модель в кеш
                            working_models_cache[task_type] = model_key
                            
                            return recognition_text, None
                    else:
                        error_text = await response.text()
                        print(f"❌ Модель {model_name} вернула ошибку {response.status}: {error_text}")
                        
        except Exception as e:
            print(f"❌ Ошибка с моделью {model_name}: {str(e)}")
            continue
    
    return None, "Все доступные модели недоступны. Попробуйте позже."

# Словарь для отслеживания подписок на ежедневные уроки
biology_subscriptions = set()

# Индекс текущего урока для каждого пользователя
user_lesson_index = {}

# Словарь для отслеживания режима пользователя (plant/expert)
user_recognition_mode = {}

# Словарь для хранения данных экспертного режима (множественные фото + текст)
expert_mode_data = {}

async def encode_image_to_base64(image_bytes):
    """Кодирует изображение в base64 для отправки в API"""
    try:
        # Открываем изображение с помощью PIL
        image = Image.open(io.BytesIO(image_bytes))
        
        # Конвертируем в RGB если нужно
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Сохраняем в буфер
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        
        # Кодируем в base64
        encoded_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return encoded_string
    except Exception as e:
        print(f"Ошибка при кодировании изображения: {e}")
        return None

async def recognize_plant_with_qwen(image_bytes):
    """Распознает растение используя OpenRouter API с автоматическим fallback на резервные модели"""
    return await recognize_with_fallback(image_bytes, config.PLANT_RECOGNITION_PROMPT, "plant")

async def recognize_plant_expert_mode(image_data, additional_text=""):
    """Экспертное распознавание растения с поддержкой множественных фото и дополнительного текста"""
    
    # Формируем расширенный промпт с учетом дополнительного текста
    expert_prompt = config.EXPERT_RECOGNITION_PROMPT
    
    if additional_text:
        expert_prompt += f"\n\n🗨️ ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ ОТ ПОЛЬЗОВАТЕЛЯ:\n{additional_text}\n\nОБЯЗАТЕЛЬНО учти эту информацию в анализе!"
    
    if isinstance(image_data, list) and len(image_data) > 1:
        expert_prompt += f"\n\n📸 ПОЛУЧЕНО {len(image_data)} ФОТОГРАФИЙ: Проанализируй все изображения в комплексе и сопоставь данные для максимально точного определения."
    
    return await recognize_with_fallback(image_data, expert_prompt, "expert")

def get_random_message(messages_list):
    """Возвращает случайное сообщение из списка"""
    import random
    return random.choice(messages_list)

def format_plant_response(plant_info):
    """Форматирует ответ о растении для красивого отображения"""
    if not plant_info:
        return "К сожалению, не удалось распознать растение. Попробуйте отправить более четкое фото! 📸"
    
    # Добавляем эмодзи в начало ответа
    formatted_response = f"🌿 **Результат распознавания:**\n\n{plant_info}\n\n💚 *Надеюсь, эта информация была полезной! Если у вас есть еще вопросов о растениях, я всегда готов помочь!*"
    
    return formatted_response

def format_expert_response(expert_info):
    """Форматирует экспертный ответ о растении"""
    if not expert_info:
        return "❌ Не удалось провести экспертный анализ. Попробуйте отправить более качественные фотографии или добавить дополнительную информацию."
    
    # Добавляем экспертную подпись
    expert_footer = """\n\n🔬 **ЭКСПЕРТНЫЙ АНАЛИЗ ЗАВЕРШЕН**
• Использованы научные методы систематики растений
• Проведен детальный морфологический анализ  
• Учтены экологические и географические факторы

📚 **Для более глубокого изучения рекомендуем:**
• Специализированные определители флоры вашего региона
• Консультации с профессиональными ботаниками
• Полевые исследования с экспертами-систематиками

🧬 *Наука открывает тайны природы!*"""
    
    formatted_response = f"🧬 **Экспертное определение растения:**\n\n{expert_info}{expert_footer}"
    
    return formatted_response

def get_admin_contact_link(message_type="support"):
    """Генерирует ссылку для связи с администратором с предзаполненным текстом"""
    
    # Предзаполненные тексты для разных типов обращений
    messages = {
        "support": "Привет! Пишу по поводу бота распознавания растений 🌱\n\nХочу обратиться в службу поддержки по следующему вопросу:\n\n[Опишите ваш вопрос здесь]",
        "feedback": "Привет! Пишу по поводу бота распознавания растений 🌱\n\nХочу оставить обратную связь:\n\n[Напишите ваш отзыв здесь]",
        "order_bot": "Привет! Пишу по поводу бота распознавания растений 🌱\n\nХочу заказать похожего бота для своих целей.\n\nМои требования:\n[Опишите ваши требования здесь]",
        "support_project": "Привет! Пишу по поводу бота распознавания растений 🌱\n\nХочу поддержать проект! Как я могу помочь?\n\n[Опишите как хотите помочь]"
    }
    
    # Получаем текст для конкретного типа обращения
    message_text = messages.get(message_type, messages["support"])
    
    # Создаем ссылку для написания админу (tg:// для мобильного приложения)
    admin_link = f"tg://user?id={config.ADMIN_ID}"
    
    return admin_link, message_text

def get_admin_username_link():
    """Возвращает ссылку на админа по username (если есть)"""
    # Если у админа есть username, можно использовать прямую ссылку
    admin_username = getattr(config, 'ADMIN_USERNAME', None)
    if admin_username:
        # Убираем @ если он есть в начале
        username = admin_username.lstrip('@')
        return f"https://t.me/{username}"
    else:
        # Используем ссылку по ID (откроется в приложении)
        return f"tg://user?id={config.ADMIN_ID}"

def get_admin_link_with_text(message_type="support"):
    """Возвращает ссылку и текст для связи с администратором"""
    admin_link, message_text = get_admin_contact_link(message_type)
    
    # Если есть username, используем более удобную ссылку
    if config.ADMIN_USERNAME:
        username = config.ADMIN_USERNAME.lstrip('@')
        return f"https://t.me/{username}", message_text
    else:
        return admin_link, message_text

def increment_user_requests(user_id):
    """Увеличивает счетчик запросов пользователя и возвращает текущее количество"""
    global user_request_count
    user_request_count[user_id] = user_request_count.get(user_id, 0) + 1
    return user_request_count[user_id]

async def check_and_send_promo(update, context, user_id):
    """Проверяет количество запросов и отправляет промо-сообщение после 3-го запроса"""
    request_count = increment_user_requests(user_id)
    
    if request_count == 3:
        try:
            # Промо-сообщение (можно кастомизировать под свои нужды)
            promo_text = """🔥 **Спасибо за использование бота!** 🔥

Надеюсь, бот распознавания растений вам понравился! 🌱

🌟 **Что еще можно попробовать:**
• Изучите больше растений с помощью фото
• Подпишитесь на ежедневные уроки биологии
• Поделитесь ботом с друзьями

💚 Если бот полезен - оставьте обратную связь!

Продолжайте изучать удивительный мир растений! 🌿✨"""

            # Сначала отправляем картинку cv.jpg
            with open('cv.jpg', 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=promo_text,
                    parse_mode='Markdown'
                )
            
            print(f"Промо-сообщение отправлено пользователю {user_id}")
            
        except Exception as e:
            print(f"Ошибка при отправке промо-сообщения пользователю {user_id}: {e}")
            # Если не удалось отправить с картинкой, отправляем просто текст
            try:
                await update.message.reply_text(
                    promo_text,
                    parse_mode='Markdown'
                )
            except Exception as e2:
                print(f"Ошибка при отправке текстового промо пользователю {user_id}: {e2}")

def subscribe_to_biology_lessons(user_id):
    """Подписывает пользователя на ежедневные уроки биологии"""
    global biology_subscriptions
    biology_subscriptions.add(user_id)
    # Инициализируем индекс урока для нового пользователя
    if user_id not in user_lesson_index:
        user_lesson_index[user_id] = 0
    return True

def unsubscribe_from_biology_lessons(user_id):
    """Отписывает пользователя от ежедневных уроков биологии"""
    global biology_subscriptions
    biology_subscriptions.discard(user_id)
    return True

def is_subscribed_to_biology_lessons(user_id):
    """Проверяет подписан ли пользователь на уроки биологии"""
    return user_id in biology_subscriptions

def get_subscribed_users():
    """Возвращает список всех подписанных пользователей"""
    return list(biology_subscriptions)

def get_next_lesson_for_user(user_id):
    """Возвращает следующий урок для пользователя"""
    if user_id not in user_lesson_index:
        user_lesson_index[user_id] = 0
    
    # Импортируем уроки здесь, чтобы избежать циклических импортов
    from config import BIOLOGY_LESSONS
    
    current_index = user_lesson_index[user_id]
    lesson = BIOLOGY_LESSONS[current_index % len(BIOLOGY_LESSONS)]
    
    # Увеличиваем индекс для следующего раза
    user_lesson_index[user_id] = (current_index + 1) % len(BIOLOGY_LESSONS)
    
    return lesson

def format_biology_lesson(lesson):
    """Форматирует урок биологии для отправки"""
    formatted_lesson = f"""🧬 **Ежедневный урок биологии**

📚 **{lesson['title']}**

{lesson['content']}

💡 **Интересный факт:**
{lesson['fact']}

🔬 **Подумай над этим:**
{lesson['question']}

---
💚 *Надеюсь, урок был интересным! Завтра тебя ждет новая тема!*

🔕 Чтобы отписаться от уроков, используй команду /lessons"""
    
    return formatted_lesson

def set_user_recognition_mode(user_id, mode):
    """Устанавливает режим распознавания для пользователя (plant/expert)"""
    global user_recognition_mode
    user_recognition_mode[user_id] = mode
    
    # Инициализация данных экспертного режима
    if mode == "expert":
        expert_mode_data[user_id] = {
            'photos': [],
            'additional_text': '',
            'waiting_for_text': False,
            'waiting_for_photos': True
        }

def add_expert_photo(user_id, photo_bytes):
    """Добавляет фото в экспертный режим"""
    if user_id not in expert_mode_data:
        expert_mode_data[user_id] = {
            'photos': [],
            'additional_text': '',
            'waiting_for_text': False,
            'waiting_for_photos': True
        }
    
    expert_mode_data[user_id]['photos'].append(photo_bytes)
    return len(expert_mode_data[user_id]['photos'])

def set_expert_additional_text(user_id, text):
    """Устанавливает дополнительный текст для экспертного анализа"""
    if user_id in expert_mode_data:
        expert_mode_data[user_id]['additional_text'] = text

def get_expert_data(user_id):
    """Получает данные экспертного режима"""
    return expert_mode_data.get(user_id, None)

def clear_expert_data(user_id):
    """Очищает данные экспертного режима"""
    if user_id in expert_mode_data:
        del expert_mode_data[user_id]

def set_expert_waiting_state(user_id, waiting_for_text=False, waiting_for_photos=False):
    """Устанавливает состояние ожидания в экспертном режиме"""
    if user_id in expert_mode_data:
        expert_mode_data[user_id]['waiting_for_text'] = waiting_for_text
        expert_mode_data[user_id]['waiting_for_photos'] = waiting_for_photos

def get_user_recognition_mode(user_id):
    """Получает текущий режим распознавания пользователя"""
    return user_recognition_mode.get(user_id, "plant")

def clear_user_recognition_mode(user_id):
    """Очищает режим распознавания пользователя"""
    global user_recognition_mode
    user_recognition_mode.pop(user_id, None)

# Настройка логирования для дублирования
logger = logging.getLogger(__name__)

async def duplicate_request_to_admin(context, user, request_type, content=None, photo_data=None):
    """Дублирует запрос пользователя администратору
    
    Args:
        context: Контекст бота
        user: Объект пользователя
        request_type: Тип запроса ('photo', 'text', 'callback')
        content: Текстовое содержимое (для текста и callback)
        photo_data: Данные фото (для фото)
    """
    # Проверяем, включено ли дублирование
    if not config.DUPLICATE_REQUESTS:
        return
        
    try:
        # Формируем сообщение для администратора
        admin_message = f"📋 **Дублирование запроса**\n\n"
        admin_message += f"👤 **Пользователь:** {user.first_name}"
        if user.username:
            admin_message += f" (@{user.username})"
        admin_message += f"\n🆔 **ID:** {user.id}\n"
        admin_message += f"📝 **Тип запроса:** {request_type}\n"
        
        if request_type == 'photo':
            admin_message += f"📸 **Фото:** Распознавание растения"
            if photo_data:
                # Отправляем фото администратору
                await context.bot.send_photo(
                    chat_id=config.ADMIN_ID,
                    photo=photo_data,
                    caption=admin_message,
                    parse_mode='Markdown'
                )
            else:
                await context.bot.send_message(
                    chat_id=config.ADMIN_ID,
                    text=admin_message,
                    parse_mode='Markdown'
                )
        
        elif request_type == 'text':
            admin_message += f"💬 **Сообщение:** {content}"
            await context.bot.send_message(
                chat_id=config.ADMIN_ID,
                text=admin_message,
                parse_mode='Markdown'
            )
        
        elif request_type == 'callback':
            admin_message += f"🔘 **Callback:** {content}"
            await context.bot.send_message(
                chat_id=config.ADMIN_ID,
                text=admin_message,
                parse_mode='Markdown'
            )
        
        logger.info(f"Запрос пользователя {user.id} продублирован администратору")
        
    except Exception as e:
        logger.error(f"Ошибка дублирования запроса администратору: {e}")

async def duplicate_photo_request(context, user, photo_data):
    """Дублирует фото запрос администратору"""
    await duplicate_request_to_admin(context, user, 'photo', photo_data=photo_data)

async def duplicate_text_request(context, user, text):
    """Дублирует текстовый запрос администратору"""
    await duplicate_request_to_admin(context, user, 'text', content=text)

async def duplicate_callback_request(context, user, callback_data):
    """Дублирует callback запрос администратору"""
    await duplicate_request_to_admin(context, user, 'callback', content=callback_data)
