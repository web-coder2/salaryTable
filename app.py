
from flask import Flask, jsonify, request
import datetime
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DATABASE = 'data.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            sumHold12 INTEGER NOT NULL,
            sumHold3 INTEGER NOT NULL,
            robot INTEGER NOT NULL,
            oklad INTEGER NOT NULL,
            office INTEGER NOT NULL,
            aproov REAL NOT NULL,
            nalog12 INTEGER,
            nalog3 INTEGER,
            salary12 INTEGER,
            salary3 INTEGER,
            spent12 INTEGER,
            spent3 INTEGER,
            salaryDirector INTEGER,
            salarySupervizer INTEGER,
            salaryTraficman INTEGER,
            plus12 INTEGER,
            plus3 INTEGER,
            total INTEGER
        )
    """)
    conn.commit()
    conn.close()

# Создаем таблицу table, если она не существует
def init_table_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salary_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ladder INTEGER NOT NULL UNIQUE,
            director INTEGER NOT NULL,
            supervisor INTEGER NOT NULL,
            traffic_man INTEGER NOT NULL
        )
    """)

    # Заполняем таблицу значениями по умолчанию, если она пуста
    cursor.execute("SELECT COUNT(*) FROM salary_table")
    count = cursor.fetchone()[0]
    if count == 0:
        default_table = {
            0: {"director": 3000, "supervisor": 2100, "traffic_man": 1400},
            20000: {"director": 3600, "supervisor": 2600, "traffic_man": 1700},
            40000: {"director": 4250, "supervisor": 3150, "traffic_man": 2050},
            60000: {"director": 4950, "supervisor": 3750, "traffic_man": 2450},
            80000: {"director": 5700, "supervisor": 4400, "traffic_man": 2900},
            100000: {"director": 6500, "supervisor": 5100, "traffic_man": 3400},
            120000: {"director": 7350, "supervisor": 5850, "traffic_man": 3950},
            140000: {"director": 8250, "supervisor": 6650, "traffic_man": 4550},
            160000: {"director": 9250, "supervisor": 7500, "traffic_man": 5200},
            180000: {"director": 10300, "supervisor": 8400, "traffic_man": 5900},
            200000: {"director": 11400, "supervisor": 9350, "traffic_man": 6650},
            220000: {"director": 12550, "supervisor": 10350, "traffic_man": 7450},
            240000: {"director": 13750, "supervisor": 11400, "traffic_man": 8300},
            260000: {"director": 15000, "supervisor": 12500, "traffic_man": 9200},
            280000: {"director": 16300, "supervisor": 13650, "traffic_man": 10200},
            300000: {"director": 17650, "supervisor": 14850, "traffic_man": 11250}
        }
        for ladder, values in default_table.items():
            try:
                cursor.execute("""
                    INSERT INTO salary_table (ladder, director, supervisor, traffic_man)
                    VALUES (?, ?, ?, ?)
                """, (ladder, values["director"], values["supervisor"], values["traffic_man"]))
                conn.commit()
            except sqlite3.IntegrityError:
                # Обработка ошибки, если ladder уже существует
                print(f"Ladder {ladder} already exists in salary_table")
                conn.rollback()
    conn.close()

# Default aproov value
DEFAULT_APROOV = 0.6

def vlookup(value, table, column):
    """Имитация функции VLOOKUP."""
    keys = sorted(table.keys())
    for i in range(len(keys) - 1):
        if value >= keys[i] and value < keys[i + 1]:
            return table[keys[i]][column]
    return table[keys[-1]][column]

def calculate_data(item):
    """Вычисляет значения для элемента данных."""
    aproov = float(item.get('aproov', DEFAULT_APROOV))
    sumHold12 = int(item['sumHold12'])
    sumHold3 = int(item['sumHold3'])
    robot = int(item['robot'])
    oklad = int(item['oklad'])
    office = int(item['office'])

    nalog12 = int(sumHold12 * 10 * aproov * 0.07)
    nalog3 = int(sumHold3 * 10 * aproov * 0.07)

    salary12 = int(0.37 * (sumHold12 * aproov) / 0.63 + sumHold12 * aproov)
    salary3 = int(0.37 * (sumHold3 * aproov) / 0.63 + sumHold3 * aproov)

    spent12 = int((robot / 2) + oklad + nalog12 + salary12)
    spent3 = int((robot / 2) + office + nalog3 + salary3)

    plus12 = int(sumHold12 * aproov * 10)
    plus3 = int(sumHold3 * aproov * 10)

    # Получаем таблицу из базы данных
    table = get_salary_table_from_db()

    salaryDirector = int(vlookup(plus3 + plus12 - spent12 - spent3, table, 'director'))
    salarySupervizer = int(vlookup(plus3 - spent3, table, 'supervisor'))
    salaryTraficman = int(vlookup(plus12 - spent12, table, 'traffic_man'))

    total = int(plus12 + plus3 - salaryDirector - salarySupervizer - salaryTraficman - spent12 - spent3)

    item['aproov'] = aproov
    item['sumHold12'] = sumHold12
    item['sumHold3'] = sumHold3
    item['robot'] = robot
    item['oklad'] = oklad
    item['office'] = office
    item['nalog12'] = nalog12
    item['nalog3'] = nalog3
    item['salary12'] = salary12
    item['salary3'] = salary3
    item['spent12'] = spent12
    item['spent3'] = spent3
    item['salaryDirector'] = salaryDirector
    item['salarySupervizer'] = salarySupervizer
    item['salaryTraficman'] = salaryTraficman
    item['plus12'] = plus12
    item['plus3'] = plus3
    item['total'] = total

    return item

def recalculate_all_data():
    """Пересчитывает все записи данных с использованием текущей таблицы."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data")
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]  # Преобразуем в список словарей
    conn.close()

    for i in range(len(data)):
        data[i] = calculate_data(data[i].copy())

    # Обновляем данные в базе данных
    conn = get_db_connection()
    cursor = conn.cursor()
    for item in data:
        cursor.execute("""
            UPDATE data SET 
                date=?, sumHold12=?, sumHold3=?, robot=?, oklad=?, office=?, aproov=?,
                nalog12=?, nalog3=?, salary12=?, salary3=?, spent12=?, spent3=?,
                salaryDirector=?, salarySupervizer=?, salaryTraficman=?, plus12=?, plus3=?, total=?
            WHERE id=?
        """, (item['date'], item['sumHold12'], item['sumHold3'], item['robot'], item['oklad'], item['office'], item['aproov'],
              item['nalog12'], item['nalog3'], item['salary12'], item['salary3'], item['spent12'], item['spent3'],
              item['salaryDirector'], item['salarySupervizer'], item['salaryTraficman'], item['plus12'], item['plus3'], item['total'],
              item['id']))
    conn.commit()
    conn.close()

# Helper function to get the salary table from the database
def get_salary_table_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ladder, director, supervisor, traffic_man FROM salary_table")
    rows = cursor.fetchall()
    conn.close()

    # Преобразуем данные в словарь, как требуется для vlookup
    table = {}
    for row in rows:
        table[row['ladder']] = {
            'director': row['director'],
            'supervisor': row['supervisor'],
            'traffic_man': row['traffic_man']
        }
    return table

# API endpoints
@app.route('/api/table', methods=['GET', 'POST'])
def handle_table():
    if request.method == 'GET':
        table = get_salary_table_from_db()
        return jsonify(table)
    elif request.method == 'POST':
        table_data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Удаляем старые значения из базы данных
        cursor.execute("DELETE FROM salary_table")

        # Записываем новые значения
        for ladder, values in table_data.items():
            cursor.execute("""
                INSERT INTO salary_table (ladder, director, supervisor, traffic_man)
                VALUES (?, ?, ?, ?)
            """, (int(ladder), values["director"], values["supervisor"], values["traffic_man"]))

        conn.commit()
        conn.close()

        recalculate_all_data()
        return jsonify({'message': 'Table updated'}), 200

@app.route('/api/data', methods=['GET', 'POST'])
def handle_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT * FROM data")
        rows = cursor.fetchall()
        data = [dict(row) for row in rows]
        conn.close()
        return jsonify(data)
    elif request.method == 'POST':
        new_data_item = request.get_json()
        new_data_item = calculate_data(new_data_item)

        cursor.execute("""
            INSERT INTO data (date, sumHold12, sumHold3, robot, oklad, office, aproov,
                nalog12, nalog3, salary12, salary3, spent12, spent3,
                salaryDirector, salarySupervizer, salaryTraficman, plus12, plus3, total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_data_item['date'], new_data_item['sumHold12'], new_data_item['sumHold3'],
              new_data_item['robot'], new_data_item['oklad'], new_data_item['office'], new_data_item['aproov'],
              new_data_item['nalog12'], new_data_item['nalog3'], new_data_item['salary12'], new_data_item['salary3'],
              new_data_item['spent12'], new_data_item['spent3'], new_data_item['salaryDirector'],
              new_data_item['salarySupervizer'], new_data_item['salaryTraficman'], new_data_item['plus12'],
              new_data_item['plus3'], new_data_item['total']))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Data added'}), 201


@app.route('/api/data/<int:data_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_data_item(data_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM data WHERE id=?", (data_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Invalid data ID'}), 400
    data_item = dict(row)

    if request.method == 'GET':
        conn.close()
        return jsonify(data_item)
    elif request.method == 'PUT':
        updated_item = request.get_json()
        updated_item = calculate_data(updated_item)

        cursor.execute("""
            UPDATE data SET
                date=?, sumHold12=?, sumHold3=?, robot=?, oklad=?, office=?, aproov=?,
                nalog12=?, nalog3=?, salary12=?, salary3=?, spent12=?, spent3=?,
                salaryDirector=?, salarySupervizer=?, salaryTraficman=?, plus12=?, plus3=?, total=?
            WHERE id=?
        """, (updated_item['date'], updated_item['sumHold12'], updated_item['sumHold3'],
              updated_item['robot'], updated_item['oklad'], updated_item['office'], updated_item['aproov'],
              updated_item['nalog12'], updated_item['nalog3'], updated_item['salary12'], updated_item['salary3'],
              updated_item['spent12'], updated_item['spent3'], updated_item['salaryDirector'],
              updated_item['salarySupervizer'], updated_item['salaryTraficman'], updated_item['plus12'],
              updated_item['plus3'], updated_item['total'], data_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Data updated'}), 200
    elif request.method == 'DELETE':
        cursor.execute("DELETE FROM data WHERE id=?", (data_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Data deleted'}), 200

@app.route('/api/data/grouped/monthly', methods=['GET'])
def get_monthly_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%Y-%m', date) as month, SUM(total) as total 
        FROM data 
        GROUP BY month
    """)
    rows = cursor.fetchall()
    conn.close()
    monthly_data = {row['month']: {'total': row['total']} for row in rows}
    return jsonify(monthly_data)

@app.route('/api/data/grouped/yearly', methods=['GET'])
def get_yearly_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%Y', date) as year, SUM(total) as total 
        FROM data 
        GROUP BY year
    """)
    rows = cursor.fetchall()
    conn.close()
    yearly_data = {row['year']: {'total': row['total']} for row in rows}
    return jsonify(yearly_data)

if __name__ == '__main__':
    init_db()
    init_table_db()
    app.run(debug=True)
