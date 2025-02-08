
from flask import Flask, jsonify, request, send_from_directory, redirect, url_for, session
from flask_cors import CORS
import sqlite3
import datetime
import os
from datetime import date
import secrets

app = Flask(__name__)
CORS(app)

# Secret key for sessions
app.secret_key = secrets.token_hex(16)

DATABASE = 'data.db'
DEFAULT_APROOV = 0.6

# --- Credentials ---
LOGIN = "admin"  # Замените на желаемый логин
PASS = "qwertyuiop123A"  # Замените на желаемый пароль

# --- Database Helper Functions ---
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def close_db_connection(conn):
    if conn:
        conn.close()

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
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
                    print(f"Ladder {ladder} already exists in salary_table")
                    conn.rollback()
        conn.commit()  # Commit after creating the table
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        close_db_connection(conn)

# --- Calculation and Lookup Functions ---
def vlookup(value, table, column):
    """Имитация функции VLOOKUP."""
    keys = sorted([row['ladder'] for row in table])
    for i in range(len(keys) - 1):
        if value >= keys[i] and value < keys[i + 1]:
            return next((row[column] for row in table if row['ladder'] == keys[i]), 0)
    return next((row[column] for row in table if row['ladder'] == keys[-1]), 0)

def calculate_data(item):
    """Вычисляет значения для элемента данных."""
    try:
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

        # Новая логика расчета зарплаты
        money12 = plus12  # Исправлено
        money3 = plus3    # Исправлено

        salarySupervizer = 0 if money12 == 0 else (
            vlookup(money12 - spent12, table, 'supervisor')
            if (money12 - spent12) > 20000
            else 2100
        )

        salaryTraficman = 0 if (money12 + money3) == 0 else (
            vlookup((money12 - spent12) + (money3 - spent3), table, 'traffic_man')
            if ((money12 - spent12) + (money3 - spent3)) > 20000
            else 1400
        )

        salaryDirector = 0 if money3 == 0 else (
            vlookup(money3 - spent3 + 20000, table, 'director')
            if (money3 - spent3) > 20000
            else 3000
        )

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
    except Exception as e:
        print(f"Calculation error: {e}")
        return None

def recalculate_all_data():
    """Пересчитывает все записи данных с использованием текущей таблицы."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM data")
        rows = cursor.fetchall()
        data = [dict(row) for row in rows]  # Преобразуем в список словарей

        for i in range(len(data)):
            calculated_data = calculate_data(data[i].copy())
            if calculated_data:
                data[i] = calculated_data

        # Обновляем данные в базе данных
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
    except sqlite3.Error as e:
        print(f"Database error during recalculation: {e}")
        conn.rollback()
    finally:
        close_db_connection(conn)

def get_salary_table_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ladder, director, supervisor, traffic_man, id FROM salary_table")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"Database error while fetching salary table: {e}")
        return []
    finally:
        close_db_connection(conn)

# --- Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == LOGIN and password == PASS:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return '''
            <script>
                alert("Invalid credentials");
                window.location.href = "/login";
            </script>
            '''
    return send_from_directory('.', 'login.html')

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if not session.get('logged_in') and path not in ['login.html', 'style.css', 'script.js']:
        return redirect(url_for('login'))
    return send_from_directory('.', path)

# --- API Endpoints ---
@app.route('/api/data', methods=['GET', 'POST'])
def handle_data():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM data")
            rows = cursor.fetchall()
            data = [dict(row) for row in rows]
            return jsonify(data)
        except sqlite3.Error as e:
            print(f"Database error during data retrieval: {e}")
            return jsonify({'error': 'Failed to retrieve data'}), 500
        finally:
            close_db_connection(conn)
    elif request.method == 'POST':
        new_data_item = request.get_json()
        calculated_data = calculate_data(new_data_item)

        if calculated_data:
            try:
                cursor.execute("""
                    INSERT INTO data (date, sumHold12, sumHold3, robot, oklad, office, aproov,
                        nalog12, nalog3, salary12, salary3, spent12, spent3,
                        salaryDirector, salarySupervizer, salaryTraficman, plus12, plus3, total)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (calculated_data['date'], calculated_data['sumHold12'], calculated_data['sumHold3'],
                      calculated_data['robot'], calculated_data['oklad'], calculated_data['office'], calculated_data['aproov'],
                      calculated_data['nalog12'], calculated_data['nalog3'], calculated_data['salary12'], calculated_data['salary3'],
                      calculated_data['spent12'], calculated_data['spent3'], calculated_data['salaryDirector'],
                      calculated_data['salarySupervizer'], calculated_data['salaryTraficman'], calculated_data['plus12'],
                      calculated_data['plus3'], calculated_data['total']))
                conn.commit()
                return jsonify({'message': 'Data added'}), 201
            except sqlite3.Error as e:
                conn.rollback()
                print(f"Database error during data insertion: {e}")
                return jsonify({'error': 'Failed to add data'}), 500
            finally:
                close_db_connection(conn)
        else:
            return jsonify({'error': 'Failed to calculate data'}), 400

@app.route('/api/data/<int:data_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_data_item(data_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM data WHERE id=?", (data_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'Invalid data ID'}), 404
        data_item = dict(row)

        if request.method == 'GET':
            return jsonify(data_item)
        elif request.method == 'PUT':
            updated_item = request.get_json()
            calculated_data = calculate_data(updated_item)

            if calculated_data:
                cursor.execute("""
                    UPDATE data SET
                        date=?, sumHold12=?, sumHold3=?, robot=?, oklad=?, office=?, aproov=?,
                        nalog12=?, nalog3=?, salary12=?, salary3=?, spent12=?, spent3=?,
                        salaryDirector=?, salarySupervizer=?, salaryTraficman=?, plus12=?, plus3=?, total=?
                    WHERE id=?
                """, (calculated_data['date'], calculated_data['sumHold12'], calculated_data['sumHold3'],
                      calculated_data['robot'], calculated_data['oklad'], calculated_data['office'], calculated_data['aproov'],
                      calculated_data['nalog12'], calculated_data['nalog3'], calculated_data['salary12'], calculated_data['salary3'],
                      calculated_data['spent12'], calculated_data['spent3'], calculated_data['salaryDirector'],
                      calculated_data['salarySupervizer'], calculated_data['salaryTraficman'], calculated_data['plus12'],
                      calculated_data['plus3'], calculated_data['total'], data_id))
                conn.commit()
                return jsonify({'message': 'Data updated'}), 200
            else:
                return jsonify({'error': 'Failed to calculate data'}), 400
        elif request.method == 'DELETE':
            cursor.execute("DELETE FROM data WHERE id=?", (data_id,))
            conn.commit()
            return jsonify({'message': 'Data deleted'}), 200
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error during data operation: {e}")
        return jsonify({'error': 'Failed to perform data operation'}), 500
    finally:
        close_db_connection(conn)

@app.route('/api/data/grouped/monthly', methods=['GET'])
def get_monthly_data():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT strftime('%Y-%m', date) as month, SUM(total) as total 
            FROM data 
            GROUP BY month
        """)
        rows = cursor.fetchall()
        monthly_data = {row['month']: {'total': row['total']} for row in rows}
        return jsonify(monthly_data)
    except sqlite3.Error as e:
        print(f"Database error while fetching monthly data: {e}")
        return jsonify({'error': 'Failed to retrieve monthly data'}), 500
    finally:
        close_db_connection(conn)

@app.route('/api/data/grouped/yearly', methods=['GET'])
def get_yearly_data():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT strftime('%Y', date) as year, SUM(total) as total 
            FROM data 
            GROUP BY year
        """)
        rows = cursor.fetchall()
        yearly_data = {row['year']: {'total': row['total']} for row in rows}
        return jsonify(yearly_data)
    except sqlite3.Error as e:
        print(f"Database error while fetching yearly data: {e}")
        return jsonify({'error': 'Failed to retrieve yearly data'}), 500
    finally:
        close_db_connection(conn)

@app.route('/api/table', methods=['GET', 'POST'])
def handle_table():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        try:
            cursor.execute("SELECT ladder, director, supervisor, traffic_man, id FROM salary_table")
            rows = cursor.fetchall()
            # Преобразуем данные в список объектов
            table = [dict(row) for row in rows]
            return jsonify(table)
        except sqlite3.Error as e:
            print(f"Database error during salary_table retrieval: {e}")
            return jsonify({'error': 'Failed to retrieve salary table'}), 500
        finally:
            close_db_connection(conn)

    elif request.method == 'POST':
        table_data = request.get_json()

        try:
            # Удаляем старые значения из базы данных
            cursor.execute("DELETE FROM salary_table")

            # Записываем новые значения
            for item in table_data:
                cursor.execute("""
                    INSERT INTO salary_table (ladder, director, supervisor, traffic_man)
                    VALUES (?, ?, ?, ?)
                """, (item['ladder'], item['director'], item['supervisor'], item['traffic_man']))

            conn.commit()
            recalculate_all_data()
            return jsonify({'message': 'Table updated'}), 200
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error during table update: {e}")
            return jsonify({'error': 'Failed to update table'}), 500
        finally:
            close_db_connection(conn)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
