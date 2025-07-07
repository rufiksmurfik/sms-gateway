# 🤖 SMS Gateway с AI

<div align="center">

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![Groq AI](https://img.shields.io/badge/Groq-AI-green.svg)
![Android](https://img.shields.io/badge/android-5.0+-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Умный SMS Gateway с искусственным интеллектом**

*Перехватывайте SMS на Android и получайте интеллектуальные ответы через Groq AI*

</div>

---

## ✨ Возможности

- 🤖 **AI-powered ответы** через Groq (Llama 3.1)
- 📱 **Перехват входящих SMS** на Android
- 🌐 **Веб-интерфейс** для мониторинга в реальном времени
- 🔒 **Ngrok туннель** для безопасного подключения
- 📊 **Статистика и история** всех сообщений
- ⚡ **Автоматический запуск** одним скриптом

## 🚀 Быстрый старт

### 1. 📱 Скачайте APK
Перейдите в [Releases](../../releases) и скачайте `sms-gateway.apk`

### 2. 🔧 Установите приложение
- Разрешите установку из неизвестных источников
- Установите APK на телефон с SIM-картой
- Дайте все разрешения (SMS, интернет)

### 3. 🔑 Настройте Groq AI API ключ
```bash
cd server
cp .env.example .env
# Отредактируйте .env файл и вставьте ваш API ключ от Groq
```

Или установите переменную окружения:
```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

**Как получить API ключ:**
1. Зарегистрируйтесь на [Groq Console](https://console.groq.com/keys)
2. Создайте новый API ключ
3. Скопируйте ключ в .env файл

### 4. 🖥️ Запустите сервер
```bash
cd server
chmod +x start_sms_gateway.sh
./start_sms_gateway.sh
```

### 5. 📡 Получите URL для Android
После запуска скрипта:
```bash
curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url'] + '/webhook')"
```

### 6. 🔗 Настройте подключение
- В приложении вставьте полученный URL
- Нажмите "ТЕСТ" для проверки соединения
- Статус должен показать "Подключено к серверу"

### 7. 🎉 Тестируйте!
- Отправьте SMS на телефон с приложением
- Откройте http://localhost:8080 для мониторинга
- Получайте умные ответы от AI!

## 📁 Структура проекта

```
├── server/           # Python сервер
│   ├── sms_server.py # Основной сервер
│   └── requirements.txt
├── android/          # Android приложение
│   └── app/
└── .github/workflows/ # Автоматическая сборка
```

## 🛠 Что это делает

1. **Android приложение** перехватывает входящие SMS
2. **Отправляет их на Python сервер** через HTTP
3. **Сервер генерирует ответ** (эхо сообщения)
4. **Веб-интерфейс** показывает все сообщения в реальном времени

## 💡 Возможности

- ✅ Перехват всех входящих SMS
- ✅ Веб-интерфейс для мониторинга
- ✅ Автоматические ответы
- ✅ Простая настройка
- ✅ Работает в локальной сети
- ✅ Бесплатно!

## 🔧 Разработка

Для сборки Android приложения:
```bash
cd android
./gradlew assembleDebug
```

APK будет в `android/app/build/outputs/apk/debug/`

## 📱 Системные требования

- **Android:** 5.0+ (API 21+)
- **Python:** 3.6+
- **Сеть:** WiFi (телефон и сервер в одной сети)

## 🤝 Поддержка

Если что-то не работает:
1. Проверьте разрешения в Android приложении
2. Убедитесь, что сервер запущен
3. Проверьте IP адрес и сетевое подключение
4. Откройте Issues в этом репозитории

---

**Лицензия:** MIT  
**Автор:** SMS Gateway Team
