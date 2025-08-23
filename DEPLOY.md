# 🚀 Деплой бота распознавания растений

## 🌐 Доступные платформы

### 1️⃣ Локальный запуск (Windows/Linux/Mac)
### 2️⃣ Облачные платформы (Heroku, Railway, Render)
### 3️⃣ VPS серверы
### 4️⃣ Docker контейнеры

## 💻 Локальный запуск

### Windows
```bash
# Установка зависимостей
install.bat

# Проверка готовности
python check_setup.py

# Запуск бота
python main.py
```

### Linux/Mac
```bash
# Установка зависимостей
chmod +x install.sh
./install.sh

# Проверка готовности
python3 check_setup.py

# Запуск бота
python3 main.py
```

## ☁️ Облачные платформы

### Heroku

1. **Создайте аккаунт** на [Heroku](https://heroku.com/)
2. **Установите Heroku CLI**
3. **Создайте приложение:**
```bash
heroku create your-plant-bot
```

4. **Добавьте переменные окружения:**
```bash
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set ADMIN_ID=your_admin_id
heroku config:set OPENROUTER_API_KEY=your_api_key
```

5. **Деплой:**
```bash
git add .
git commit -m "Initial commit"
git push heroku main
```

6. **Запуск:**
```bash
heroku ps:scale worker=1
```

### Railway

1. **Подключите GitHub** репозиторий
2. **Создайте проект** на [Railway](https://railway.app/)
3. **Добавьте переменные окружения** в Variables
4. **Railway автоматически** развернет бота

### Render

1. **Создайте аккаунт** на [Render](https://render.com/)
2. **Создайте Web Service**
3. **Подключите GitHub** репозиторий
4. **Настройте переменные окружения**
5. **Укажите команду запуска:** `python main.py`

## 🖥️ VPS серверы

### Ubuntu/Debian

1. **Подключитесь к серверу:**
```bash
ssh user@your-server-ip
```

2. **Обновите систему:**
```bash
sudo apt update && sudo apt upgrade -y
```

3. **Установите Python:**
```bash
sudo apt install python3 python3-pip python3-venv -y
```

4. **Создайте виртуальное окружение:**
```bash
python3 -m venv plant-bot
source plant-bot/bin/activate
```

5. **Клонируйте проект:**
```bash
git clone https://github.com/hackerxai/naturexai.git
cd plant-recognition-bot
```

6. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

7. **Создайте .env файл:**
```bash
nano .env
# Добавьте ваши переменные окружения
```

8. **Запустите бота:**
```bash
python main.py
```

### CentOS/RHEL

1. **Установите Python:**
```bash
sudo yum install python3 python3-pip -y
```

2. **Следуйте шагам** как для Ubuntu

### Настройка автозапуска (systemd)

1. **Создайте сервис файл:**
```bash
sudo nano /etc/systemd/system/plant-bot.service
```

2. **Добавьте содержимое:**
```ini
[Unit]
Description=Plant Recognition Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/plant-recognition-bot
Environment=PATH=/home/your-username/plant-bot/bin
ExecStart=/home/your-username/plant-bot/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Активируйте сервис:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable plant-bot
sudo systemctl start plant-bot
```

4. **Проверьте статус:**
```bash
sudo systemctl status plant-bot
```

## 🐳 Docker

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements и установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash bot
USER bot

# Запуск бота
CMD ["python", "main.py"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  plant-bot:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_ID=${ADMIN_ID}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

### Запуск Docker
```bash
# Сборка образа
docker build -t plant-bot .

# Запуск контейнера
docker run -d --name plant-bot \
  -e BOT_TOKEN=your_token \
  -e ADMIN_ID=your_id \
  -e OPENROUTER_API_KEY=your_key \
  plant-bot

# Или с Docker Compose
docker-compose up -d
```

## 🔧 Настройка для продакшена

### Логирование
```python
# В main.py добавьте:
import logging
from logging.handlers import RotatingFileHandler

# Настройка ротации логов
handler = RotatingFileHandler(
    'bot.log', 
    maxBytes=1024*1024,  # 1MB
    backupCount=5
)
logging.getLogger().addHandler(handler)
```

### Мониторинг
```python
# Добавьте health check
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time() - start_time
    }
```

### Безопасность
1. **Используйте HTTPS** для API запросов
2. **Ограничьте доступ** к API ключам
3. **Настройте firewall** на VPS
4. **Регулярно обновляйте** зависимости

## 📊 Мониторинг и поддержка

### Логи
```bash
# Просмотр логов в реальном времени
tail -f bot.log

# Поиск ошибок
grep "ERROR" bot.log

# Статистика использования
grep "Пользователь" bot.log | wc -l
```

### Статус бота
```bash
# Проверка процесса
ps aux | grep python

# Проверка портов
netstat -tlnp | grep python

# Проверка логов systemd
sudo journalctl -u plant-bot -f
```

### Резервное копирование
```bash
# Создание бэкапа
tar -czf plant-bot-backup-$(date +%Y%m%d).tar.gz \
  --exclude=__pycache__ \
  --exclude=*.log \
  .

# Автоматический бэкап (cron)
0 2 * * * tar -czf /backups/plant-bot-$(date +\%Y\%m\%d).tar.gz /path/to/bot
```

## 🚨 Устранение неполадок

### Бот не запускается
1. Проверьте логи: `tail -f bot.log`
2. Проверьте переменные окружения
3. Убедитесь, что все зависимости установлены
4. Проверьте права доступа к файлам

### Ошибки API
1. Проверьте API ключ OpenRouter
2. Убедитесь в наличии средств на балансе
3. Проверьте лимиты API
4. Проверьте доступность сервиса

### Проблемы с производительностью
1. Мониторьте использование CPU и RAM
2. Проверьте скорость интернет-соединения
3. Оптимизируйте размер изображений
4. Настройте кэширование

## 📈 Масштабирование

### Горизонтальное масштабирование
1. **Несколько экземпляров** бота
2. **Балансировщик нагрузки** для API
3. **Кэш Redis** для общих данных
4. **База данных** для пользователей

### Вертикальное масштабирование
1. **Увеличение ресурсов** сервера
2. **Оптимизация кода** Python
3. **Асинхронная обработка** изображений
4. **Сжатие изображений** перед отправкой

---

**🚀 Успешного деплоя! Ваш бот готов покорять мир растений! 🌱**
