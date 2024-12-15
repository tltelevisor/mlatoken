import sqlite3, logging
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from config import DATABASE, BASE_DIR
from os.path import join
from time import sleep
logging.basicConfig(level=logging.INFO, filename='latoken.log',
                    format='%(asctime)s %(levelname)s %(message)s')

def calculate_cumulative_avg(db_path, tlgid_value):

    # Подключаемся к базе данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL-запрос для выбора данных
    #ROUND(AVG((JULIANDAY(datean) - JULIANDAY(dateqw)) * 86400), 2)
    query = """
    SELECT id, irgh, iansw 
    FROM test
    WHERE tlgid = ? 
    ORDER BY id ASC
    """
    cursor.execute(query, (tlgid_value,))
    rows = cursor.fetchall()

    # Закрываем соединение с базой данных
    conn.close()

    # Если данных нет, возвращаем пустой результат
    if not rows:
        return [], []

    # Извлекаем ID и вычисляем нарастающее среднее
    ids = []
    cumulative_avg = []
    cumulative_sum = 0

    for i, (row_id, irgh, iansw) in enumerate(rows, start=1):
        #print(i, row_id, irgh, iansw)
        ids.append(i)
        if irgh == iansw:
            cumulative_sum += 1  # Учитываем строку, где irgh == iansw
        cumulative_avg.append(100*cumulative_sum / i)  # Нарастающее среднее

    return ids, cumulative_avg

def plot_cumulative_avg(ids, cumulative_avg, file_path, name):
    plt.ion()
    plt.figure(figsize=(10, 6))
    plt.plot(ids, cumulative_avg, marker='o', label=f'{name}')
    plt.xlim(1, max(ids))
    plt.ylim(0, 100)
    plt.xlabel('Порядковый номер вопроса')
    # plt.ylabel('')
    plt.title('Доля правильных ответов, %')
    plt.legend()
    plt.grid()
    # plt.show()
    plt.savefig(file_path)  # Сохраняем график в файл
    # plt.pause(1)
    sleep(1)
    plt.close()
# Путь к базе данных
DATABASE_PATH = DATABASE

# Значение tlgid для анализа
def get_graph(userid, name):

    # Получаем данные для построения графика
    ids, cumulative_avg = calculate_cumulative_avg(DATABASE_PATH, userid)

    # Проверяем, есть ли данные для построения графика
    if ids and cumulative_avg:
        file_path = join(BASE_DIR, f'{userid}.png')
        plot_cumulative_avg(ids, cumulative_avg, file_path, name)
        return(file_path)
    else:
        logging.error(f'Нет данных для графика: {userid}')
        return None
if __name__ == '__main__':
    # вместо 1 вставить Телеграм id 
    get_graph(1)