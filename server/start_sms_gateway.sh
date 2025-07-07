#!/bin/bash

# Запуск SMS Gateway сервера с Groq AI интеграцией

# Переменные
PORT=8080
LOG_FILE="groq_server.log"

# Проверяем наличие API ключа Groq
if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  GROQ_API_KEY не установлен!"
    echo "Установите переменную окружения:"
    echo "export GROQ_API_KEY='your-groq-api-key'"
    echo "Или создайте файл .env с:"
    echo "GROQ_API_KEY=your-groq-api-key"
    
    # Пытаемся загрузить из .env файла
    if [ -f ".env" ]; then
        echo "📁 Загружаем .env файл..."
        export $(cat .env | xargs)
    else
        echo "❌ Создайте .env файл или установите GROQ_API_KEY"
        exit 1
    fi
fi

# Убедимся, что ngrok установлен
if ! command -v ngrok &> /dev/null
then
    echo "ngrok не установлен. Установите ngrok перед запуском."
    exit 1
fi

# Убиваем процессы, связанных с портом 8080
lsof -ti:$PORT | xargs kill -9 &> /dev/null

# Запускаем сервер с AI интеграцией
nohup python3 sms_groq_server.py > $LOG_FILE 2>&1 &
echo "🚀 Запущен AI сервер на порту $PORT с логированием в $LOG_FILE"

# Запускаем ngrok
nohup ngrok http $PORT --log=stdout > ngrok.log 2>&1 &
echo "🌐 Ngrok туннель активирован"

# Открываем веб-интерфейс
open http://localhost:$PORT

echo "✅ Проект запущен. Проверьте http://localhost:$PORT для доступа к интерфейсу."
