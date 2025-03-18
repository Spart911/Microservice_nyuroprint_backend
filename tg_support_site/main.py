import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv
from telegram.error import TelegramError
from telethon import TelegramClient, functions, events



# Получаем переменные из окружения
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')


# Инициализация клиента Telegram
client = TelegramClient('session_name', api_id, api_hash)

# Настройка FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nyuroprint.vercel.app", "https://nyuroprint.ru"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Логирование
logging.basicConfig(level=logging.INFO)

# Словарь для хранения активных соединений
active_connections = {}


@app.get("/api/chat-history")
async def get_chat_history(chat_id: str = Query(..., description="Chat ID for fetching history")):
    try:
        # Получаем историю сообщений с чата
        messages = await get_chat_history_tg(chat_id)

        return JSONResponse(content={"history": messages})

    except TelegramError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chat history: {str(e)}")


# Подписка на новые сообщения в Telegram-чате
@client.on(events.NewMessage())
async def new_message_listener(event):
    try:
        chat_id = event.chat_id
        message_text = event.text
        logging.info(f"Received new message from chat {chat_id}: {message_text}")

        # Отправка сообщения через WebSocket
        for ws in active_connections.values():
            if ws.client_state:
                logging.info("Sending message to frontend via WebSocket")
                await ws.send_text(json.dumps({'text': message_text}))
                logging.info(f"Message from chat {chat_id} sent to the frontend: {message_text}")
            else:
                logging.error("WebSocket connection not established. Message not sent.")
    except Exception as e:
        logging.error(f"Error while processing new message: {e}", exc_info=True)


async def get_chat_history_tg(chat_id, limit=100):
    """Загрузка истории чата из Telegram."""
    try:
        # Проверка, подключён ли клиент
        if not client.is_connected():
            await client.connect()

        # Получаем сообщения из чата
        messages = await client.get_messages(int(chat_id), limit=limit)
        return [f"{message.text}" for message in messages][::-1]
    except Exception as e:
        logging.error(f"Ошибка при загрузке истории чата {chat_id}: {e}")
        return []


async def create_channel(title):
    """Создание канала в Telegram."""
    await client.start(phone_number)

    about = '____SUPPORT____'

    try:
        result = await client(functions.channels.CreateChannelRequest(
            title=title,
            about=about,
            broadcast=True,  # Канал
            megagroup=False  # Не супер-группа
        ))
        logging.info(f"Создан канал: {result.chats[0].id}")
        return result.chats[0].id
    except Exception as e:
        logging.error(f"Ошибка при создании канала: {e}")
        return None


async def send_message_to_telegram(chat_id, text):
    try:
        # Авторизация клиента, если она еще не выполнена
        if not client.is_connected():
            await client.connect()

        # Проверка авторизации
        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            await client.sign_in(phone_number, input('Введите код: '))

        # Отправка сообщения
        await client.send_message(chat_id, text)
        print(f"Сообщение отправлено в чат {chat_id}: {text}")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(ws: WebSocket, client_id: str):
    await ws.accept()
    print(f"WebSocket-соединение установлено с {ws.client.host}:{ws.client.port}, client_id: {client_id}")

    # Сохраняем соединение для данного клиента
    active_connections[client_id] = ws

    try:
        while True:
            message = await ws.receive_text()
            print(f"Получено сообщение от {client_id}: {message}")
            data = json.loads(message)
            uid = data.get('uid')
            text = data.get('text')

            if not uid or not text:
                print("Неверный формат сообщения. Ожидались ключи 'uid' и 'text'.")
                await ws.send_text(json.dumps({'error': 'Invalid message format'}))
                continue

            # Отправка запроса на фронт с UID для получения chat_id
            await ws.send_text(json.dumps({'uid': uid}))

            # Ожидание ответа с chat_id от клиента
            response = await ws.receive_text()
            data = json.loads(response)

            # Получаем chat_id из ответа
            chat_id = int(data.get('chat_id', 0))
            print(f"Получен chat_id: {chat_id} для UID: {uid}")

            if chat_id:
                # Отправляем сообщение в Telegram
                await send_message_to_telegram(chat_id, "Пользователь сайта: " + text)
            else:
                print(f"Не удалось получить chat_id для UID: {uid}")
                print(f"Создание нового чата для UID: {uid}")
                chat_id = await create_channel(uid)

                print(f"Созданный чат: {chat_id}")
                # Отправка chat_id обратно на фронт
                await ws.send_text(json.dumps({'chat_id': chat_id}))

                # Отправка нового сообщения
                await send_message_to_telegram(chat_id, "Пользователь сайта: " + text)

    except WebSocketDisconnect as e:
        print(f"WebSocket-соединение с {client_id} закрыто: {e.code}")
        # Удаляем соединение при отключении
        del active_connections[client_id]
    except Exception as e:
        print(f"Ошибка в процессе обработки WebSocket-сообщения: {e}")
        try:
            await ws.send_text(json.dumps({'error': 'Internal server error'}))
        except WebSocketDisconnect:
            print("Не удалось отправить сообщение из-за закрытия соединения")



def check_ssl_certificates(key_path='ssl/certificate.key.pem', cert_path='ssl/certificate.crt.pem'):
    key_exists = os.path.isfile(key_path)
    cert_exists = os.path.isfile(cert_path)

    if key_exists and cert_exists:
        print("Сертификаты найдены. Все в порядке.")
    else:
        if not key_exists:
            print(f"Файл ключа отсутствует: {key_path}")
        if not cert_exists:
            print(f"Файл сертификата отсутствует: {cert_path}")






