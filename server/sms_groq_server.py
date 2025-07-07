#!/usr/bin/env python3
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import json
from datetime import datetime
import os
from groq import Groq

# Groq API настройки
GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'your-groq-api-key-here')
groq_client = Groq(api_key=GROQ_API_KEY)

# История сообщений
messages = []

# Переменная для хранения обработанных AI ответов
ai_responses = []

def process_with_groq(text, phone):
    """Обрабатывает текст через Groq AI"""
    try:
        print(f"🤖 Отправляем в Groq AI: {text}")
        
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Ты умный SMS ассистент. Отвечай кратко и по делу на русском языке. Максимум 160 символов."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            model="llama3-8b-8192",  # Используем быстрый Llama модель
            max_tokens=100,
            temperature=0.7
        )
        
        ai_response = chat_completion.choices[0].message.content.strip()
        
        # Сохраняем AI ответ в переменную
        ai_data = {
            'original_text': text,
            'ai_response': ai_response,
            'phone': phone,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'model': 'llama3-8b-8192'
        }
        ai_responses.append(ai_data)
        
        # Ограничиваем историю AI ответов 50 записями
        if len(ai_responses) > 50:
            ai_responses[:] = ai_responses[-50:]
        
        print(f"🤖 Ответ AI: {ai_response}")
        return ai_response
        
    except Exception as e:
        print(f"❌ Ошибка Groq AI: {e}")
        return f"Извините, AI временно недоступен. Ваше сообщение '{text}' получено."

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/webhook' or parsed_path.path == '/webhook/webhook':
            # Обработка webhook
            query_params = parse_qs(parsed_path.query)
            phone = query_params.get('phone', [''])[0]
            mes = query_params.get('mes', [''])[0]
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"📱 Запрос от: {self.client_address[0]}")
            print(f"📩 [{timestamp}] Телефон: {phone}, Сообщение: {mes}")
            
            # Сохраняем входящее сообщение
            global messages
            incoming_msg = {
                'phone': phone,
                'text': mes,
                'timestamp': timestamp,
                'type': 'incoming',
                'ip': self.client_address[0]
            }
            messages.append(incoming_msg)
            
            # Обрабатываем сообщение через Groq AI
            ai_reply = process_with_groq(mes, phone)
            
            # Сохраняем исходящее сообщение (AI ответ)
            outgoing_msg = {
                'phone': phone,
                'text': ai_reply,
                'timestamp': timestamp,
                'type': 'outgoing',
                'ip': self.client_address[0],
                'ai_processed': True
            }
            messages.append(outgoing_msg)
            
            # Ограничиваем историю 100 сообщениями
            if len(messages) > 100:
                messages[:] = messages[-100:]
            
            response = {
                'status': 'ok',
                'reply': ai_reply,
                'timestamp': timestamp,
                'ai_processed': True
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        elif parsed_path.path == '/ai-history':
            # API для получения истории AI ответов
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(ai_responses, ensure_ascii=False).encode('utf-8'))
            
        elif parsed_path.path == '/test':
            # Тестовая страница
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
            <html>
            <head><title>SMS Gateway AI Test</title></head>
            <body>
                <h1>🤖 SMS Gateway AI Test</h1>
                <p>Если вы видите эту страницу с телефона, то сеть в порядке.</p>
                <button onclick="test()">Тест AI webhook</button>
                <div id="result"></div>
                <script>
                function test() {
                    fetch('/webhook?phone=test&mes=Привет, как дела?')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('result').innerHTML = 
                            '<h3>Результат:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    });
                }
                </script>
            </body>
            </html>
            """.encode()
            self.wfile.write(html)
        else:
            # Главная страница с мониторингом
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # Генерируем HTML с историей сообщений
            messages_html = ''
            if messages:
                for msg in messages[-15:]:  # Последние 15 сообщений
                    msg_class = 'incoming' if msg['type'] == 'incoming' else 'outgoing'
                    icon = '📩' if msg['type'] == 'incoming' else '🤖' if msg.get('ai_processed') else '📤'
                    ai_badge = ' <span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">AI</span>' if msg.get('ai_processed') else ''
                    messages_html += f'''
                    <div class="message {msg_class}">
                        <div class="msg-header">{icon} {"От" if msg['type'] == 'incoming' else "AI Ответ"}: {msg['phone']} | IP: {msg['ip']}{ai_badge}</div>
                        <div class="msg-text">{msg['text']}</div>
                        <div class="msg-time">{msg['timestamp']}</div>
                    </div>
                    '''
            else:
                messages_html = '<p>Пока сообщений нет. Отправьте тестовое SMS!</p>'
            
            # AI статистика
            ai_count = len(ai_responses)
            
            html = f"""
            <html>
            <head>
                <title>🤖 SMS Gateway AI Monitor</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
                    .status {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                    .ai-status {{ background: #cce5ff; color: #004085; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
                    .message {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 8px; }}
                    .incoming {{ background: #e3f2fd; border-left: 4px solid #2196f3; }}
                    .outgoing {{ background: #e8f5e8; border-left: 4px solid #28a745; }}
                    .msg-header {{ font-weight: bold; margin-bottom: 5px; }}
                    .msg-text {{ margin: 8px 0; font-size: 16px; }}
                    .msg-time {{ font-size: 12px; color: #666; }}
                    h1 {{ color: #333; }}
                    .stats {{ display: flex; gap: 15px; margin: 20px 0; flex-wrap: wrap; }}
                    .stat {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; flex: 1; min-width: 120px; }}
                    .refresh {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
                    .ai-btn {{ background: #28a745; color: white; padding: 8px 15px; border: none; border-radius: 5px; cursor: pointer; margin-left: 10px; }}
                </style>
                <script>
                    // Автообновление каждые 5 секунд
                    setTimeout(() => location.reload(), 5000);
                    
                    function showAiHistory() {{
                        fetch('/ai-history')
                        .then(r => r.json())
                        .then(data => {{
                            let popup = window.open('', 'ai-history', 'width=800,height=600');
                            popup.document.write(`
                                <html>
                                <head><title>AI История</title></head>
                                <body style="font-family: Arial; padding: 20px;">
                                    <h2>🤖 История AI обработки</h2>
                                    <pre>${{JSON.stringify(data, null, 2)}}</pre>
                                </body>
                                </html>
                            `);
                        }});
                    }}
                </script>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 SMS Gateway AI Monitor</h1>
                    
                    <div class="status">
                        ✅ Сервер работает | Время: {datetime.now().strftime('%H:%M:%S')} | Всего сообщений: {len(messages)}
                    </div>
                    
                    <div class="ai-status">
                        🤖 Groq AI активен | Модель: llama3-8b-8192 | Обработано запросов: {ai_count}
                    </div>
                    
                    <div class="stats">
                        <div class="stat">
                            <div style="font-size: 24px; font-weight: bold;">{len([m for m in messages if m['type'] == 'incoming'])}</div>
                            <div>Входящих SMS</div>
                        </div>
                        <div class="stat">
                            <div style="font-size: 24px; font-weight: bold;">{len([m for m in messages if m['type'] == 'outgoing'])}</div>
                            <div>AI Ответов</div>
                        </div>
                        <div class="stat">
                            <div style="font-size: 24px; font-weight: bold;">{len(set([m['ip'] for m in messages]))}</div>
                            <div>Устройств</div>
                        </div>
                        <div class="stat">
                            <div style="font-size: 24px; font-weight: bold;">{ai_count}</div>
                            <div>AI Запросов</div>
                        </div>
                    </div>
                    
                    <h2>📋 Последние сообщения:</h2>
                    <div id="messages">
                        {messages_html}
                    </div>
                    
                    <div style="margin-top: 20px; text-align: center;">
                        <button class="refresh" onclick="location.reload()">🔄 Обновить</button>
                        <button class="ai-btn" onclick="showAiHistory()">🤖 AI История</button>
                        <a href="/test" style="margin-left: 10px;">🧪 Тест</a>
                    </div>
                </div>
            </body>
            </html>
            """.encode()
            self.wfile.write(html)

PORT = 8080
Handler = MyHandler

print("🚀 Запуск SMS Gateway с Groq AI интеграцией")
print(f"🌐 Веб-интерфейс: http://localhost:{PORT}")
print(f"📱 Для Android: http://192.168.0.121:{PORT}/webhook")
print(f"🤖 AI API: Groq (llama3-8b-8192)")
print(f"🧪 Тест: http://192.168.0.121:{PORT}/test")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"✅ Сервер с AI слушает на порту {PORT}")
    httpd.serve_forever()
