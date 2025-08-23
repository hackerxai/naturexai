@echo off
echo 🌱 Установка зависимостей для бота распознавания растений...
echo.

echo 📦 Обновление pip...
python -m pip install --upgrade pip

echo.
echo 📦 Установка зависимостей...
pip install -r requirements.txt

echo.
echo ✅ Установка завершена!
echo.
echo 🚀 Для запуска проверки выполните:
echo    python check_setup.py
echo.
echo 🚀 Для запуска бота выполните:
echo    python main.py
echo.
pause
