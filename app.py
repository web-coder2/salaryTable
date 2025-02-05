
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Разрешаем запросы с Vue.js

# Инициализация базы данных (SQLite)
DATABASE = 'salary_data.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Возвращает результаты в виде словарей
    return conn

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salary_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            summHold12 INTEGER NOT NULL,
            summHold3 INTEGER NOT NULL,
            isWorkDay INTEGER NOT NULL,  -- 1 для True, 0 для False
            office INTEGER NOT NULL,
            oklad INTEGER NOT NULL,
            robot INTEGER NOT NULL,
            aproov REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

create_table()

# --- API Endpoints ---

# Получение всех данных
@app.route('/api/data', methods=['GET'])
def get_all_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM salary_data")
    data = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in data])  # Преобразуем в список словарей

# Добавление новых данных
@app.route('/api/data', methods=['POST'])
def add_data():
    data = request.get_json()
    date = data['date']
    summHold12 = data['summHold12']
    summHold3 = data['summHold3']
    isWorkDay = int(data['isWorkDay'])  # Преобразуем в int (1 или 0)
    office = data['office']
    oklad = data['oklad']
    robot = data['robot']
    aproov = data['aproov']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO salary_data (date, summHold12, summHold3, isWorkDay, office, oklad, robot, aproov)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, summHold12, summHold3, isWorkDay, office, oklad, robot, aproov))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Data added successfully!'}), 201  # 201 Created

# Обновление данных (по ID)
@app.route('/api/data/<int:id>', methods=['PUT'])
def update_data(id):
    data = request.get_json()
    date = data['date']
    summHold12 = data['summHold12']
    summHold3 = data['summHold3']
    isWorkDay = int(data['isWorkDay'])  # Преобразуем в int (1 или 0)
    office = data['office']
    oklad = data['oklad']
    robot = data['robot']
    aproov = data['aproov']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE salary_data
        SET date = ?, summHold12 = ?, summHold3 = ?, isWorkDay = ?, office = ?, oklad = ?, robot = ?, aproov = ?
        WHERE id = ?
    """, (date, summHold12, summHold3, isWorkDay, office, oklad, robot, aproov, id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Data updated successfully!'})

# Удаление данных (по ID)
@app.route('/api/data/<int:id>', methods=['DELETE'])
def delete_data(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM salary_data WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Data deleted successfully!'})

#Функция расчета зарплаты (пример)
@app.route('/api/calculate/<int:id>', methods=['GET'])
def calculate_salary(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM salary_data WHERE id = ?", (id,))
    data = cursor.fetchone()
    conn.close()

    if not data:
        return jsonify({'error': 'Data not found'}), 404

    data = dict(data) # конвертируем Row object в dict

    table = {
        0: [3000, 2100, 1400],
        20000: [3600, 2600, 1700],
        40000: [4250, 3150, 2050],
        60000: [4950, 3750, 2450],
        80000: [5700, 4400, 2900],
        100000: [6500, 5100, 3400],
        120000: [7350, 5850, 3950],
        140000: [8250, 6650, 4550],
        160000: [9250, 7500, 5200],
        180000: [10300, 8400, 5900],
        200000: [11400, 9350, 6650],
        220000: [12550, 10350, 7450],
        240000: [13750, 11400, 8300],
        260000: [15000, 12500, 9200],
        280000: [16300, 13650, 10200],
        300000: [17650, 14850, 11250]
    }

    def vlookup(value, table, column_index):
        """Эмуляция VLOOKUP."""
        keys = sorted(table.keys())
        for i in range(len(keys) - 1):
            if value >= keys[i] and value < keys[i + 1]:
                return table[keys[i]][column_index]
        return table[keys[-1]][column_index]  # Для значений больше последнего ключа

    summHold12 = data['summHold12']
    summHold3 = data['summHold3']
    office = data['office']
    oklad = data['oklad']
    robot = data['robot']
    aproov = data['aproov']

    salary12 = (0.37 * (summHold12 + summHold3) * aproov) / 0.63 + summHold12 * aproov
    salary3 = (0.37 * (summHold12 + summHold3) * aproov) / 0.63 + summHold3 * aproov
    nalog12 = salary12 * aproov * 0.07
    nalog3 = salary3 * aproov * 0.07
    spent12 = (robot / 2) + office + nalog12 + salary12
    spent3 = (robot / 2) + oklad + nalog3 + salary3
    money12 = summHold12 * 10 * aproov
    money3 = summHold3 * 10 * aproov

    salaryDirector = vlookup(money3 + money12 - spent12 - spent3, table, 0)
    salarySupervizer = vlookup(money3 - spent3, table, 1)
    salaryTraficman = vlookup(money12 - spent12, table, 2)

    result = {
        'salary12': salary12,
        'salary3': salary3,
        'nalog12': nalog12,
        'nalog3': nalog3,
        'spent12': spent12,
        'spent3': spent3,
        'money12': money12,
        'money3': money3,
        'salaryDirector': salaryDirector,
        'salarySupervizer': salarySupervizer,
        'salaryTraficman': salaryTraficman
    }

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
