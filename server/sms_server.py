#!/usr/bin/env python3
"""
Простой SMS Gateway сервер
Принимает SMS от Android приложения и отвечает
"""

from flask import Flask, request, jsonify
import time
from datetime import datetime
import json

app = Flask(__name__)

# История сообщений
messages = []

@app.route('/')
def index():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SMS Gateway</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
            .status {{ background: #d4edda; color: #155724; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
            .message {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
            .incoming {{ background: #e3f2fd; }}
            .outgoing {{ background: #f3e5f5; }}
            .timestamp {{ font-size: 12px; color: #666; }}
            h1 {{ color: #333; }}
            .endpoint {{ background: #f8f9fa; padding: 10px; border-left: 4px solid #007bff; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📱 SMS Gateway Server</h1>
            
            <div class="status">
                ✅ Сервер работает | Сообщений: <span id="count">{len(messages)}</span> | 
                Время: {datetime.now().strftime('%H:%M:%S')}
            </div>
            
            <div class="endpoint">
                <strong>URL для Android приложения:</strong><br>
                <code>http://ваш-ip:5000/webhook</code>
            </div>
            
            <h2>📋 Последние сообщения:</h2>
            <div id="messages">
                {''.join([f'<div class="message {msg["type"]}"><strong>{"От" if msg["type"] == "incoming" else "Кому"}:</strong> {msg["phone"]}<br><strong>Текст:</strong> {msg["text"]}<br><span class="timestamp">{msg["timestamp"]}</span></div>' for msg in messages[-10:]])}
            </div>
            
            <h2>🔧 API Endpoints:</h2>
            <ul>
                <li><code>GET /</code> - Эта страница</li>
                <li><code>GET /webhook</code> - Получение SMS от приложения</li>
                <li><code>GET /status</code> - JSON статус</li>
                <li><code>GET /clear</code> - Очистить историю</li>
            </ul>
        </div>
        
        <script>
            // Автообновление каждые 3 секунды
            setInterval(() => location.reload(), 3000);
        </script>
    </body>
    </html>
    """

@app.route('/webhook')
def receive_sms():
    """Получение SMS от Android приложения"""
    phone = request.args.get('phone', '').strip()
    text = request.args.get('mes', '').strip()
    sms_id = request.args.get('id', str(int(time.time())))
    
    if not phone or not text:
        return jsonify({'error': 'Нужны параметры phone и mes'}), 400
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Сохраняем входящее сообщение
    incoming_msg = {
        'phone': phone,
        'text': text,
        'timestamp': timestamp,
        'id': sms_id,
        'type': 'incoming'
    }
    messages.append(incoming_msg)
    
    print(f"📩 [{timestamp}] SMS от {phone}: {text}")
    
    # Генерируем ответ
    reply_text = f"Эхо: {text} (получено в {timestamp.split(' ')[1]})"
    
    # Сохраняем исходящее сообщение
    outgoing_msg = {
        'phone': phone,
        'text': reply_text,
        'timestamp': timestamp,
        'id': f"reply_{int(time.time())}",
        'type': 'outgoing'
    }
    messages.append(outgoing_msg)
    
    print(f"📤 [{timestamp}] Ответ для {phone}: {reply_text}")
    
    # Ограничиваем историю 100 сообщениями
    if len(messages) > 100:
        messages[:] = messages[-100:]
    
    return jsonify({
        'status': 'ok',
        'reply': reply_text,
        'timestamp': timestamp
    })

@app.route('/status')
def status():
    """JSON статус сервера"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'total_messages': len(messages),
        'last_message': messages[-1] if messages else None
    })

@app.route('/clear')
def clear():
    """Очистка истории сообщений"""
    global messages
    messages = []
    print("🗑️ История сообщений очищена")
    return jsonify({'status': 'cleared', 'message': 'История очищена'})

if __name__ == '__main__':
    print("🚀 Запуск SMS Gateway сервера...")
    print(f"🌐 Web интерфейс: http://localhost:5000")
    print(f"📱 Для Android: http://ваш-ip:5000/webhook")
    print(f"🔧 Узнать IP: ifconfig | grep 'inet ' | grep -v 127.0.0.1")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
