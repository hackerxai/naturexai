#!/bin/bash

echo "🌱 Установка зависимостей для бота распознавания растений..."
echo

echo "📦 Обновление pip..."
python3 -m pip install --upgrade pip

echo
echo "📦 Установка зависимостей..."
pip3 install -r requirements.txt

echo
echo "✅ Установка завершена!"
echo
echo "🚀 Для запуска проверки выполните:"
echo "   python3 check_setup.py"
echo
echo "🚀 Для запуска бота выполните:"
echo "   python3 main.py"
echo
