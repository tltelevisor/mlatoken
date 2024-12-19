import asyncio, logging, sqlite3, datetime, random
from aiogram import Bot, Dispatcher, types, F
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command
from oai import check_openai_api_key, set_openai_api_key, oai_context, oai_fact, oai_give_question, oai_check_answer, oai_test_question
from config import BOT_TOKEN, BUTTONS, BTT_CNTX, DATABASE, SQL_CRT_MESS, SQL_CRT_TEST,SQL_VIEW
from graph import get_graph
logging.basicConfig(level=logging.INFO, filename='latoken.log',
                    format='%(asctime)s %(levelname)s %(message)s')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

conn = sqlite3.connect(DATABASE)
conn.cursor().execute(SQL_CRT_MESS)
conn.cursor().execute(SQL_CRT_TEST)
conn.cursor().execute(SQL_VIEW)
conn.commit()
conn.close()

def keyboard(buttons):
    if len(buttons) == 3:
        kb = [[types.KeyboardButton(text=buttons[0]),types.KeyboardButton(text=buttons[1]),],
            [types.KeyboardButton(text=buttons[2]),]]
    if len(buttons) == 4:
        kb = [[types.KeyboardButton(text=buttons[0]), types.KeyboardButton(text=buttons[1]), ],
              [types.KeyboardButton(text=buttons[2]), types.KeyboardButton(text=buttons[3]), ]]
    if len(buttons) == 2:
        kb = [[types.KeyboardButton(text=buttons[0]), types.KeyboardButton(text=buttons[1]), ]]
    if len(buttons) == 1:
        kb = [[types.KeyboardButton(text=buttons[0]), ]]
    if len(buttons) == 0:
        kb=[[]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb,resize_keyboard=True)
    return keyboard

def svmess(user, text, cntx=''):
    logging.info(f'user: {user}, text: {text}, cntx: {cntx}')

    sql = f"INSERT INTO mess (tlgid, text, cntx, date) VALUES({user}, '{text}', '{cntx}', '{datetime.datetime.now()}');"
    logging.info(f'sql: {sql}')
    conn = sqlite3.connect(DATABASE)
    conn.cursor().execute(sql)
    conn.commit()
    conn.close()
    return

def svtest(user, qwst, arght, awrng, irgh, dtnw):
    sql = (f"INSERT INTO test (tlgid, qwst, arght, awrng, irgh, iansw, dateqw) "
           f"VALUES({user}, '{qwst}', '{arght}', '{awrng}', {irgh}, 0, '{dtnw}');")
    logging.info(f'sql: {sql}')
    conn = sqlite3.connect(DATABASE)
    conn.cursor().execute(sql)
    conn.commit()
    conn.close()
    return

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    if message.from_user.id in user_set_api_key:
        del user_set_api_key[message.from_user.id]
    if message.from_user.id in user_data:
        del user_data[message.from_user.id]
    if message.from_user.id in user_context:
        del user_context[message.from_user.id]
    name = f'{message.from_user.full_name} ({message.from_user.username})'
    if check_openai_api_key():
        buttons = ['Случайный факт о LATOKEN', 'Пройти тест', 'Выбрать контекст']
        await message.answer(f'Привет, {name}!\nСпроси о LATOKEN!', reply_markup=keyboard(buttons))
    else:
        buttons = ['Ввести OpenAI API key', '/start']
        await message.answer(f'Привет, {name}!\n'
                             f'Для работы бота нужен OpenAI API key.\n'
                             f'https://platform.openai.com/settings/organization/api-keys', reply_markup=keyboard(buttons))
user_set_api_key = {}
user_api_key = {}
# Получение OpenAI API key от пользователя
@dp.message(F.text == 'Ввести OpenAI API key')
async def facts(message: types.Message):
    user_set_api_key[message.from_user.id] = True
    buttons=[]
    # await message.answer(f'Вводите OpenAI API key', reply_markup=keyboard(buttons))
    await message.answer(f'Вводите OpenAI API key', reply_markup=types.ReplyKeyboardRemove())

# Расскажи случайный факт
@dp.message(F.text == 'Расскажи случайный факт')
@dp.message(F.text == 'Случайный факт о LATOKEN')
async def facts(message: types.Message):
    if message.from_user.id in user_data:
        del user_data[message.from_user.id]
    if message.from_user.id in user_context:
        cntx = user_context[message.from_user.id]
        fact = oai_fact(message.from_user.id, cntx)
        svmess(message.from_user.id, fact, cntx=cntx['name'])
        del user_context[message.from_user.id]
    else:
        fact = oai_fact(message.from_user.id)
        svmess(message.from_user.id, fact)
    await message.answer(fact)

# Задай вопрос
user_data = {} # Здесь будет хранится заданный ботом вопрос
@dp.message(F.text == 'Задай вопрос')
async def check_q(message: types.Message):
    if message.from_user.id in user_context:
        question = oai_give_question(message.from_user.id, user_context[message.from_user.id])
        del user_context[message.from_user.id]
    else:
        question = oai_give_question(message.from_user.id)
        user_data[message.from_user.id] = question
    await message.answer(question)

# Выбрать контекст
user_context={} # Здесь будет храниться выбранное меню (контекст)
@dp.message(F.text == 'Выбрать контекст')
@dp.message(F.text == f'Контекст - {BUTTONS[0]}. Изменить?')
@dp.message(F.text == f'Контекст - {BUTTONS[1]}. Изменить?')
@dp.message(F.text == f'Контекст - {BUTTONS[2]}. Изменить?')
@dp.message(F.text == f'Контекст - {BUTTONS[3]}. Изменить?')
async def check_c(message: types.Message):
    if message.from_user.id in user_data:
        del user_data[message.from_user.id]
    await message.answer('Выберите контекст', reply_markup=keyboard(BUTTONS))

# Выбран контекст
@dp.message(F.text == BUTTONS[0])
@dp.message(F.text == BUTTONS[1])
@dp.message(F.text == BUTTONS[2])
async def check_n(message: types.Message):
    user_context[message.from_user.id] = BTT_CNTX[message.text]
    if message.from_user.id in user_data:
        del user_data[message.from_user.id]
    buttons = ['Расскажи случайный факт', 'Пройти тест', f'Контекст - {message.text}. Изменить?']
    await message.answer(f'Выбран контекст {message.text}', reply_markup=keyboard(buttons))

# Выбран контекст "Все категории"
@dp.message(F.text == f'{BUTTONS[3]}')
@dp.message(F.text == f'Вернуться к обучению')
async def cmd_start(message: types.Message):
    if message.from_user.id in test_all:
        del test_all[message.from_user.id]
    if message.from_user.id in user_data:
        del user_data[message.from_user.id]
    if message.from_user.id in user_context:
        del user_context[message.from_user.id]
    buttons = ['Расскажи случайный факт', 'Пройти тест', f'Контекст - {BUTTONS[3]}. Изменить?']
    await message.answer(f'Спроси о LATOKEN', reply_markup=keyboard(buttons))


@dp.message(F.text == 'Пройти тест')
async def test(message: types.Message):
    buttons = ['По пройденным вопросам', 'По всему материалу', 'Вернуться к обучению', 'Результаты' ]
    await message.answer(f'Выбери вид теста или вернись к обучению', reply_markup=keyboard(buttons))

@dp.message(F.text == 'Результаты')
async def test_res(message: types.Message):
    sql = (f'SELECT total, right, time FROM user_tests WHERE tlgid = {message.from_user.id};')
    conn = sqlite3.connect(DATABASE)
    total, right, time = conn.cursor().execute(sql).fetchone()
    conn.commit()
    conn.close()
    buttons = ['Вернуться к обучению', 'Пройти тест']
    name = f'{message.from_user.full_name} ({message.from_user.username})'
    file_path = get_graph(message.from_user.id, name)
    await message.answer(f'Ваши результаты:\n'
                         f'Всего вопросов: {total}\n'
                         f'Из них правильно: {right}\n'
                         f'Среднее время ответа, с: {time}', reply_markup=keyboard(buttons))
    if file_path:
        photo = FSInputFile(file_path)
        await bot.send_photo(chat_id=message.chat.id,photo=photo)

test_all={} # Здесь будет храниться вид теста
user_test={} # Здесь будет храниться date вопроса
@dp.message(F.text == 'По всему материалу')
@dp.message(F.text == 'По пройденным вопросам')
@dp.message(F.text == 'Следующий вопрос')
async def test_qw(message: types.Message):
    if message.text == 'По всему материалу':
        test_all[message.from_user.id] = True
    elif message.text == 'По пройденным вопросам':
        test_all[message.from_user.id] = False
    qwst, arght, awrng = oai_test_question(message.from_user.id, test_all[message.from_user.id])
    irgh = random.randint(1, 2)
    if irgh == 1:
        mess = f'{qwst}\n\nВариант 1: {arght}\n\nВариант 2: {awrng}'
    else:
        mess = f'{qwst}\n\nВариант 1: {awrng}\n\nВариант 2: {arght}'
    dateqw = datetime.datetime.now()
    user_test[message.from_user.id] = dateqw
    svtest(message.from_user.id, qwst, arght, awrng, irgh, dateqw)
    buttons = ['Вариант 1', 'Вариант 2', 'Вернуться к обучению', 'Результаты' ]

    await message.answer(mess, reply_markup=keyboard(buttons))

@dp.message(F.text == 'Вариант 1')
@dp.message(F.text == 'Вариант 2')
async def test_a(message: types.Message):
    dateqw = user_test[message.from_user.id]
    if message.text == 'Вариант 1':
        iansw = 1
    elif message.text == 'Вариант 2':
        iansw = 2
    sql = f'UPDATE test SET iansw={iansw}, datean="{datetime.datetime.now()}" WHERE dateqw="{dateqw}";'
    logging.info(f'sql: {sql}')
    conn = sqlite3.connect(DATABASE)
    conn.cursor().execute(sql)
    conn.commit()
    conn.close()
    del user_test[message.from_user.id]
    sql = f'SELECT irgh FROM test WHERE dateqw="{dateqw}";'
    conn = sqlite3.connect(DATABASE)
    irgh, *rest = conn.cursor().execute(sql).fetchone()
    conn.commit()
    conn.close()
    if irgh == iansw:
        mess = f'Правильный ответ!'
    else:
        mess = f'Неправильный ответ!'
    buttons = ['Следующий вопрос', 'Вернуться к обучению', 'Результаты' ]
    await message.answer(mess, reply_markup=keyboard(buttons))

# Ответ на вопрос
@dp.message()
async def oai_answer(message: types.Message):
    # Если пользователь в режием ввода api_key
    if message.from_user.id in user_set_api_key:
        user_api_key[message.from_user.id] = message.text
        set_openai_api_key(message.from_user.id, message.text)
        if check_openai_api_key():
            mess = 'Ключ успешно установлен. Продолжим'
            buttons = ['Случайный факт о LATOKEN', 'Пройти тест', 'Выбрать контекст']
            await message.answer(mess, reply_markup=keyboard(buttons))
        else:
            mess = 'Сервер не принял ключ'
            buttons = ['Ввести OpenAI API key', '/start']
            await message.answer(mess, reply_markup=keyboard(buttons))
            del user_api_key[message.from_user.id]
        del user_set_api_key[message.from_user.id]
    # Если пользователь в режиме теста
    elif check_openai_api_key():
        if message.from_user.id in user_test:
            await message.answer(f'Не подглядывай!')
        else:
            # Если пользователю не был задан вопрос
            if message.from_user.id not in user_data:
                # Если пользователь не выбрал контекст
                if message.from_user.id not in user_context:
                    oai_answer = oai_context(message.from_user.id, message.text)
                    svmess(message.from_user.id, oai_answer)
                # Если пользователь выбрал контекст
                else:
                    cntx = user_context[message.from_user.id]
                    oai_answer = oai_context(message.from_user.id, message.text, cntx)
                    svmess(message.from_user.id, oai_answer, cntx=cntx['name'])
            # Если пользователю был задан вопрос
            else:
                oai_answer = oai_check_answer(message.from_user.id, user_data[message.from_user.id], message.text)
                del user_data[message.from_user.id]
            await message.answer(f'{oai_answer}')
    else:
        buttons = ['Ввести OpenAI API key', '/start']
        await message.answer(f'Для работы бота нужен OpenAI API key.\n'
                             f'https://platform.openai.com/settings/organization/api-keys', reply_markup=keyboard(buttons))

async def main():
    print("Start bot")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())