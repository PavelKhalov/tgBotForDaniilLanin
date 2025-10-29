import telebot
from dotenv import load_dotenv
import os
import json
from telebot import types
from datetime import datetime

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# Папка для хранения данных пользователей
USERS_DATA_DIR = "users_data"
ADMIN_ID  = int(os.getenv("ADMIN_ID"))

# Создаем папку если ее нет
if not os.path.exists(USERS_DATA_DIR):
    os.makedirs(USERS_DATA_DIR)

# Временное хранилище для текущих ответов пользователей
user_sessions = {}
user_states = {}


class UserResponse:
    def __init__(self, user_id):
        self.user_id = user_id
        self.username = None
        self.first_name = None
        self.capa_type = None
        self.main_color = None
        self.text_color = None
        self.text = None
        self.additional_elements = None
        self.elements_position = None
        self.age = None
        self.height = None
        self.font = None
        self.timestamp = None


def get_user_file_path(user_id):
    """Генерирует путь к файлу пользователя"""
    return os.path.join(USERS_DATA_DIR, f"user_{user_id}.json")


def save_user_responses(user_response):
    """Сохраняет ответы пользователя в его отдельный файл"""
    user_file = get_user_file_path(user_response.user_id)

    user_data = {
        'user_info': {
            'user_id': user_response.user_id,
            'username': user_response.username,
            'first_name': user_response.first_name,
            'timestamp': user_response.timestamp
        },
        'answers': {
            'capa_type': user_response.capa_type,
            'main_color': user_response.main_color,
            'text_color': user_response.text_color,
            'text': user_response.text,
            'additional_elements': user_response.additional_elements,
            'elements_position': user_response.elements_position,
            'age': user_response.age,
            'height': user_response.height,
            'font': user_response.font
        },
        'files_info': {  # Добавляем информацию о файлах
            'has_files': False,
            'files_count': 0,
            'photos_dir': f"user_{user_response.user_id}_photos"
        }
    }

    # Проверяем наличие файлов
    user_photos_dir = os.path.join(USERS_DATA_DIR, f"user_{user_response.user_id}_photos")
    if os.path.exists(user_photos_dir):
        files_count = len([f for f in os.listdir(user_photos_dir) if os.path.isfile(os.path.join(user_photos_dir, f))])
        user_data['files_info']['has_files'] = True
        user_data['files_info']['files_count'] = files_count

    with open(user_file, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)

def load_user_responses(user_id):
    """Загружает ответы пользователя из его файла"""
    user_file = get_user_file_path(user_id)

    print(f"🔄 Загружаю данные пользователя {user_id} из {user_file}")  # Отладочное сообщение

    if not os.path.exists(user_file):
        print(f"❌ Файл {user_file} не существует")  # Отладочное сообщение
        return None

    try:
        with open(user_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Данные пользователя {user_id} успешно загружены")  # Отладочное сообщение
        return data
    except Exception as e:
        print(f"❌ Ошибка загрузки файла {user_file}: {e}")  # Отладочное сообщение
        return None


# Главное меню
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    btn1 = types.KeyboardButton("Самые продаваемые дизайны стандартных кап")
    btn2 = types.KeyboardButton("Стандартная однослойная")
    btn3 = types.KeyboardButton("Стандартная двухслойная")
    btn4 = types.KeyboardButton("Индивидуальная капа по слепкам")
    btn5 = types.KeyboardButton("Оптовый заказ")
    btn6 = types.KeyboardButton("МЕРЧ")

    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)

    welcome_text = "Здравствуйте! 👋 Рады приветствовать вас в MORTAL в разделе по изготовлению стандартных и индивидуальных кап с личным дизайном!"
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


# Обработка текстовых сообщений (кроме команд)
@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def handle_text(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)

    # Проверяем, находится ли пользователь в процессе разработки дизайна
    if user_id in user_states and user_states[user_id] != 'completed':
        handle_design_states(message)
        return

    if message.text == "Самые продаваемые дизайны стандартных кап":
        send_popular_designs(chat_id)

    elif message.text == "Стандартная однослойная":
        send_single_layer(chat_id)

    elif message.text == "Стандартная двухслойная":
        send_double_layer(chat_id)

    elif message.text == "Индивидуальная капа по слепкам":
        send_custom_mouthguard(chat_id)

    elif message.text == "Оптовый заказ":
        send_wholesale(chat_id)

    elif message.text == "МЕРЧ":
        send_merch(chat_id)


# 1. Самые продаваемые дизайны
def send_popular_designs(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Заказать", url="https://t.me/mortal_shop_team")
    markup.add(btn)

    try:
        photo_one = open("1.JPG", "rb")
        bot.send_document(chat_id, photo_one,
                       caption="<b>Цена капы с готовым дизайном: 2.500руб.</b>\n\nДля заказа напишите : @mortal_shop_team",
                       parse_mode="HTML", reply_markup=markup)
    except:
        bot.send_message(chat_id,
                         "<b>Цена капы с готовым дизайном: 2.500руб.</b>\n\nДля заказа напишите : @mortal_shop_team",
                         parse_mode="HTML", reply_markup=markup)


# 2. Стандартная однослойная
def send_single_layer(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn_order = types.InlineKeyboardButton("Заказать", url="https://t.me/mortal_shop_team")
    btn_design = types.InlineKeyboardButton("Разработать дизайн", callback_data="design_single_layer")
    markup.add(btn_design, btn_order)

    text = """
<b>· Однослойная капа — 2 500 ₽</b>
<b>· Разработка макета — бесплатно!</b>

Выберите действие:
"""
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)


# 3. Стандартная двухслойная
def send_double_layer(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn_order = types.InlineKeyboardButton("Заказать", url="https://t.me/mortal_shop_team")
    btn_design = types.InlineKeyboardButton("Разработать дизайн", callback_data="design_double_layer")
    markup.add(btn_design, btn_order)

    text = """
<b>· Двухслойная капа — 3 000 ₽</b>
<b>· Разработка макета — бесплатно!</b>

Выберите действие:
"""
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)


# 4. Индивидуальная капа по слепкам
def send_custom_mouthguard(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Заказать", url="https://t.me/mortal_shop_team")
    markup.add(btn)

    text = """
<b>Цены на индивидуальные капы:</b>

1. ИНДИВИДУАЛЬНАЯ ПРОЗРАЧНАЯ КАПА - 9.000₽
2. ИНДИВИДУАЛЬНАЯ ЦВЕТНАЯ КАПА - 10.000₽
3. ИНДИВИДУАЛЬНАЯ КАПА С НАДПИСЬЮ,ЛОГО - 11.000₽
4. ИНДИВИДУАЛЬНАЯ ЦВЕТНАЯ КАПА С ЛИЧНЫМ ДИЗАЙНОМ - 12.000₽
5. ИНДИВИДУАЛЬНАЯ ХОККЕЙНАЯ КАПА - 13.000₽

При заказе вы будете перенаправлены менеджеру @mortal_shop_team
    """
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)


# 5. Оптовый заказ
def send_wholesale(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Заказать", url="https://t.me/mortal_shop_team")
    markup.add(btn)

    text = """
<b>Оптовые цены кап под ключ однослойные:</b>

10-19шт - 1000руб/шт
20-99 штук 900руб/шт  
100-499 штук 800руб/шт
500+ штук 700руб/шт 

Разработка упаковки и наклейки для футляра 3000руб. разово, если брендированная упаковка не нужна, то отправляем в базовой.

При заказе вы будете перенаправлены менеджеру @mortal_shop_team
    """
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)


# 6. МЕРЧ
def send_merch(chat_id):
    maiki_folders = "maiki"
    tshirt_folders = "tshirts"

    # Создаем медиагруппу для маек
    media = []
    photo_files = [
        os.path.join(maiki_folders, "maikaME1.JPG"),
        os.path.join(maiki_folders, "maikaME2.JPG"),
        os.path.join(maiki_folders, "maikaME3.JPG"),
        os.path.join(maiki_folders, "maikaME4.JPG"),
        os.path.join(maiki_folders, "maikaME5.JPG"),
        os.path.join(maiki_folders, "maikaME6.JPG")
    ]

    # Формируем медиагруппу
    for i, photo_file in enumerate(photo_files):
        if os.path.exists(photo_file):
            try:
                with open(photo_file, 'rb') as tshirt:
                    photo_data = tshirt.read()

                if i == 0:
                    media.append(types.InputMediaPhoto(photo_data,
                                                       caption="<b>Майки «ME vs ME»</b>\n\nСиний, красный, черный цвета - 3.000руб",
                                                       parse_mode="HTML"))
                else:
                    media.append(types.InputMediaPhoto(photo_data))

            except Exception as e:
                print(f"Ошибка чтения {photo_file}: {e}")

    # Отправляем медиагруппу
    if media:
        try:
            bot.send_media_group(chat_id, media)
            print("Медиагруппа отправлена успешно!")
        except Exception as e:
            print(f"Ошибка отправки медиагруппы: {e}")
            # Если медиагруппа не сработала, отправляем по одному
            for photo_file in photo_files:
                if os.path.exists(photo_file):
                    try:
                        with open(photo_file, 'rb') as tshirt:
                            bot.send_photo(chat_id, tshirt)
                    except Exception as e2:
                        print(f"Ошибка отправки {photo_file}: {e2}")
    else:
        bot.send_message(chat_id, "Фото мерча временно недоступны")
        print("Нет доступных фото для отправки")

    # Создаем медиагруппу для футболок
    media2 = []
    tshirt_files = [
        os.path.join(tshirt_folders, "tshirt1.JPG"),
        os.path.join(tshirt_folders, "tshirt2.JPG"),
        os.path.join(tshirt_folders, "tshirt3.JPG"),
        os.path.join(tshirt_folders, "tshirt4.JPG"),
        os.path.join(tshirt_folders, "tshirt5.JPG"),
        os.path.join(tshirt_folders, "tshirt6.JPG"),
        os.path.join(tshirt_folders, "tshirt7.JPG"),
        os.path.join(tshirt_folders, "tshirt8.JPG"),
        os.path.join(tshirt_folders, "tshirt9.JPG"),
        os.path.join(tshirt_folders, "tshirt10.JPG")
    ]

    # Формируем медиагруппу для футболок
    for i, tshirt_file in enumerate(tshirt_files):
        if os.path.exists(tshirt_file):
            try:
                with open(tshirt_file, 'rb') as tshirt:
                    tshirt_data = tshirt.read()

                if i == 0:
                    media2.append(types.InputMediaPhoto(tshirt_data,
                                                        caption="<b>Футболки MORTAL</b>\n\n«FRIENDS OR MONEY», «YOUR GRANDMOTHER» и другие - от 3.500руб",
                                                        parse_mode="HTML"))
                else:
                    media2.append(types.InputMediaPhoto(tshirt_data))

            except Exception as e:
                print(f"Ошибка чтения {tshirt_file}: {e}")

    # Отправляем медиагруппу с футболками
    if media2:
        try:
            bot.send_media_group(chat_id, media2)
            print("Медиагруппа с футболками отправлена успешно!")
        except Exception as e:
            print(f"Ошибка отправки медиагруппы с футболками: {e}")
    else:
        bot.send_message(chat_id, "Фото футболок временно недоступны")

    # Отправляем текстовое сообщение с кнопкой
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Заказать", url="https://t.me/mortal_shop_team")
    markup.add(btn)

    text = """
<b>Ассортимент МЕРЧ:</b>

<b>Майки «ME vs ME»</b>
• Синий цвет - 3.000руб
• Красный цвет - 3.000руб  
• Чёрный цвет - 3.000руб

<b>Футболки:</b>
• «FRIENDS OR MONEY» - 3.500руб
• «YOUR GRANDMOTHER» - 3.500руб
• «CHIKO» - 4.500руб
• «NO BOXING» - 4.500руб
• «BABY» - 4.500руб

При заказе вы будете перенаправлены менеджеру @mortal_shop_team
    """
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)


# Функции для разработки дизайна капы
def start_design_process(message, capa_type):
    user_id = str(message.from_user.id)

    # Создаем или обновляем сессию пользователя
    user_sessions[user_id] = UserResponse(user_id)
    user_sessions[user_id].username = message.from_user.username
    user_sessions[user_id].first_name = message.from_user.first_name
    user_sessions[user_id].capa_type = capa_type
    user_states[user_id] = 'waiting_main_color'

    bot.send_message(
        message.chat.id,
        f"Отлично! Вы выбрали {capa_type.lower()} капу. Давайте создадим макет.\n\n"
        "1. Укажите основной цвет капы или прикрепите фото/изображение для фона в хорошем качестве (не скриншот).\n\n"
        "Напишите название цвета или отправьте изображение:",
        reply_markup=types.ReplyKeyboardRemove()
    )


def handle_design_states(message):
    user_id = str(message.from_user.id)
    current_state = user_states.get(user_id)

    if current_state == 'waiting_main_color':
        user_sessions[user_id].main_color = message.text
        user_states[user_id] = 'waiting_text_color'

        bot.send_message(
            message.chat.id,
            "2. Какой цвет должен быть у надписи?\n\n"
            "Укажите цвет текста:"
        )

    elif current_state == 'waiting_text_color':
        user_sessions[user_id].text_color = message.text
        user_states[user_id] = 'waiting_text'

        bot.send_message(
            message.chat.id,
            "3. Напишите текст для нанесения.\n\n"
            "Укажите именно так, как должно быть отображено (например, \"ИВАНОВ\", \"Победитель\" или \"чемпион\"):"
        )

    elif current_state == 'waiting_text':
        user_sessions[user_id].text = message.text
        user_states[user_id] = 'waiting_additional_elements'

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_yes = types.KeyboardButton('Да')
        btn_no = types.KeyboardButton('Нет')
        markup.add(btn_yes, btn_no)

        bot.send_message(
            message.chat.id,
            "4. Планируются ли дополнительные элементы (логотип, картинка, фото)?\n\n"
            "Если да, пожалуйста, прикрепите файл в хорошем качестве (не скриншот).\n"
            "Сначала выберете <Да> либо <Нет>",
            reply_markup=markup
        )

    elif current_state == 'waiting_additional_elements':
        if message.text == 'Да':
            user_sessions[user_id].additional_elements = "Да (ожидается файл)"
            user_states[user_id] = 'waiting_additional_file'
            bot.send_message(
                message.chat.id,
                "Пожалуйста, прикрепите файл с дополнительными элементами:",
                reply_markup=types.ReplyKeyboardRemove()
            )
        else:
            user_sessions[user_id].additional_elements = "Нет"
            user_states[user_id] = 'waiting_elements_position'
            bot.send_message(
                message.chat.id,
                "5. Опишите расположение всех элементов на капе.\n\n"
                "Где и как именно должны находиться надпись, логотип и другие детали?",
                reply_markup=types.ReplyKeyboardRemove()
            )

    elif current_state == 'waiting_elements_position':
        user_sessions[user_id].elements_position = message.text
        user_states[user_id] = 'waiting_age_height'

        bot.send_message(
            message.chat.id,
            "6. Подтвердите, пожалуйста:\n"
            "• Ваш возраст\n"
            "• Ваш рост\n\n"
            "Укажите в формате: Возраст, Рост\n"
            "Например: 16, 175"
        )

    elif current_state == 'waiting_age_height':
        try:
            parts = message.text.split(',')
            if len(parts) == 2:
                age = parts[0].strip()
                height = parts[1].strip()
                user_sessions[user_id].age = age
                user_sessions[user_id].height = height
                user_states[user_id] = 'waiting_font'



                font = open("font.JPG", "rb")
                bot.send_document(
                    message.chat.id, font,caption="7. Выберите шрифт:")
            else:
                bot.send_message(
                    message.chat.id,
                    "Пожалуйста, укажите в правильном формате:\n"
                    "Возраст, Рост\n"
                    "Например: 16, 175"
                )
        except Exception as e:
            bot.send_message(
                message.chat.id,
                "Ошибка в формате. Пожалуйста, укажите:\n"
                "Возраст, Рост\n"
                "Например: 16, 175"
            )

    elif current_state == 'waiting_font':
        user_sessions[user_id].font = message.text
        user_sessions[user_id].timestamp = datetime.now().isoformat()

        # Сохраняем ответы в отдельный файл пользователя
        save_user_responses(user_sessions[user_id])

        # Очищаем состояние
        user_states[user_id] = 'completed'

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_send = types.KeyboardButton('/send_to_admin')
        btn_new = types.KeyboardButton('/start')
        markup.add(btn_send, btn_new)

        bot.send_message(
            message.chat.id,
            "✅ Все ответы сохранены в ваш персональный файл!\n\n"
            "Используйте команды:\n"
            "/send_to_admin - отправить заявку администратору\n"
            "/start - вернуться в главное меню",
            reply_markup=markup
        )


@bot.message_handler(content_types=['photo', 'document'])
def handle_files(message):
    user_id = str(message.from_user.id)

    print(f"🖼️ Обработка файла от пользователя {user_id}")  # Отладочное сообщение

    # Проверяем, находится ли пользователь в процессе разработки дизайна
    if user_id not in user_sessions or user_id not in user_states:
        print(f"❌ Пользователь {user_id} не в процессе дизайна")
        # Если пользователь не в процессе дизайна, игнорируем файл
        bot.send_message(message.chat.id, "❌ Сначала начните процесс разработки дизайна через меню")
        return

    current_state = user_states[user_id]
    print(f"📊 Текущее состояние пользователя: {current_state}")

    try:
        if current_state == 'waiting_main_color':
            # Создаем папку для фото пользователя
            user_photos_dir = os.path.join(USERS_DATA_DIR, f"user_{user_id}_photos")
            if not os.path.exists(user_photos_dir):
                os.makedirs(user_photos_dir)

            if message.content_type == 'photo':
                file_info = bot.get_file(message.photo[-1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                file_path = os.path.join(user_photos_dir, f"main_color_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            else:
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                file_ext = message.document.file_name.split('.')[-1] if message.document.file_name else 'bin'
                file_path = os.path.join(user_photos_dir,
                                         f"main_color_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}")

            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            user_sessions[user_id].main_color = f"Файл: {file_path}"
            user_states[user_id] = 'waiting_text_color'

            bot.send_message(
                message.chat.id,
                "✅ Файл основного цвета сохранен!\n\n"
                "2. Какой цвет должен быть у надписи?\n\n"
                "Укажите цвет текста:"
            )

        elif current_state == 'waiting_additional_file':
            user_photos_dir = os.path.join(USERS_DATA_DIR, f"user_{user_id}_photos")
            if not os.path.exists(user_photos_dir):
                os.makedirs(user_photos_dir)

            if message.content_type == 'photo':
                file_info = bot.get_file(message.photo[-1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                file_path = os.path.join(user_photos_dir, f"additional_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            else:
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                file_ext = message.document.file_name.split('.')[-1] if message.document.file_name else 'bin'
                file_path = os.path.join(user_photos_dir,
                                         f"additional_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}")

            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            user_sessions[user_id].additional_elements = f"Файл: {file_path}"
            user_states[user_id] = 'waiting_elements_position'

            bot.send_message(
                message.chat.id,
                "✅ Дополнительный файл сохранен!\n\n"
                "5. Опишите расположение всех элементов на капе.\n\n"
                "Где и как именно должны находиться надпись, логотип и другие детали?"
            )
        else:
            print(f"❌ Неожиданное состояние: {current_state}")
            bot.send_message(message.chat.id, "❌ Сейчас нельзя отправлять файлы. Продолжайте отвечать на вопросы.")

    except Exception as e:
        print(f"❌ Ошибка обработки файла: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка при обработке файла: {str(e)}")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id

    if call.data == "design_single_layer":
        bot.answer_callback_query(call.id, "Разработка дизайна однослойной капы")
        # Создаем фейковое сообщение для запуска процесса дизайна
        fake_message = type('obj', (object,), {
            'chat': type('obj', (object,), {'id': chat_id}),
            'from_user': type('obj', (object,), {
                'id': call.from_user.id,
                'username': call.from_user.username,
                'first_name': call.from_user.first_name
            })
        })
        start_design_process(fake_message, "Однослойная")

    elif call.data == "design_double_layer":
        bot.answer_callback_query(call.id, "Разработка дизайна двухслойной капы")
        # Создаем фейковое сообщение для запуска процесса дизайна
        fake_message = type('obj', (object,), {
            'chat': type('obj', (object,), {'id': chat_id}),
            'from_user': type('obj', (object,), {
                'id': call.from_user.id,
                'username': call.from_user.username,
                'first_name': call.from_user.first_name
            })
        })
        start_design_process(fake_message, "Двухслойная")


@bot.message_handler(commands=['send_to_admin'])
def send_to_admin(message):
    try:
        user_id = message.chat.id
        print(f"🔄 Отправка заявки от пользователя {user_id}")

        # Загружаем данные пользователя
        user_file = f"users_data/user_{user_id}.json"

        if not os.path.exists(user_file):
            bot.send_message(user_id, "❌ У вас нет сохраненной заявки. Сначала заполните анкету через /start")
            return

        with open(user_file, 'r', encoding='utf-8') as f:
            user_data = json.load(f)

        # Формируем сообщение для администратора
        admin_message = f"""
📋 НОВАЯ ЗАЯВКА НА КАПУ

👤 Пользователь: {user_data['user_info']['first_name']} 
📛 Username: @{user_data['user_info']['username']}
🆔 User ID: {user_data['user_info']['user_id']}
⏰ Время: {user_data['user_info']['timestamp'][:16]}

📝 ОТВЕТЫ:
1. Тип капы: {user_data['answers']['capa_type']}
2. Основной цвет: {user_data['answers']['main_color']}
3. Цвет надписи: {user_data['answers']['text_color']}
4. Текст: {user_data['answers']['text']}
5. Дополнительные элементы: {user_data['answers']['additional_elements']}
6. Расположение элементов: {user_data['answers']['elements_position']}
7. Возраст: {user_data['answers']['age']}
8. Рост: {user_data['answers']['height']}
9. Шрифт: {user_data['answers']['font']}
"""

        # Отправляем администратору текстовую заявку
        print("📤 Отправка текстовой заявки администратору")
        bot.send_message(ADMIN_ID, admin_message)

        # Проверяем и отправляем файлы, если они есть
        user_photos_dir = os.path.join(USERS_DATA_DIR, f"user_{user_id}_photos")

        if os.path.exists(user_photos_dir):
            print(f"📁 Найдена папка с файлами: {user_photos_dir}")

            # Получаем все файлы из папки
            all_files = []
            for root, dirs, files in os.walk(user_photos_dir):
                for file in files:
                    all_files.append(os.path.join(root, file))

            # Сортируем файлы по времени создания (новые первыми)
            all_files.sort(key=os.path.getmtime, reverse=True)

            # Отправляем файлы администратору
            files_sent = 0
            for file_path in all_files:
                try:
                    if file_path.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        # Это изображение
                        with open(file_path, 'rb') as photo_file:
                            bot.send_photo(ADMIN_ID, photo_file,
                                           caption=f"📎 Файл от пользователя: {os.path.basename(file_path)}")
                        files_sent += 1
                        print(f"🖼️ Отправлено фото: {os.path.basename(file_path)}")
                    else:
                        # Это другой файл
                        with open(file_path, 'rb') as doc_file:
                            bot.send_document(ADMIN_ID, doc_file,
                                              caption=f"📎 Файл от пользователя: {os.path.basename(file_path)}")
                        files_sent += 1
                        print(f"📄 Отправлен документ: {os.path.basename(file_path)}")

                    # Небольшая задержка между отправками, чтобы не спамить
                    import time
                    time.sleep(0.5)

                except Exception as file_error:
                    print(f"❌ Ошибка отправки файла {file_path}: {file_error}")

            if files_sent > 0:
                bot.send_message(ADMIN_ID, f"✅ Всего отправлено файлов: {files_sent}")
                print(f"✅ Отправлено файлов: {files_sent}")
            else:
                bot.send_message(ADMIN_ID, "📭 Файлы от пользователя отсутствуют")
                print("📭 Файлы отсутствуют")
        else:
            bot.send_message(ADMIN_ID, "📭 Пользователь не прикреплял файлов")
            print("📭 Папка с файлами не найдена")

        print(f"✅ Заявка полностью отправлена администратору {ADMIN_ID}")

        # Отправляем подтверждение пользователю
        bot.send_message(
            user_id,
            "✅ Ваша заявка отправлена администратору!\n\n"
            "Мы свяжемся с вами в ближайшее время."
        )

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        bot.send_message(
            message.chat.id,
            f"❌ Произошла ошибка: {str(e)}\n\n"
            "Попробуйте еще раз или свяжитесь с администратором."
        )


# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    print(f"Файлы пользователей сохраняются в папку: {USERS_DATA_DIR}")

    bot.polling(none_stop=True)
