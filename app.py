
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import datetime
import json  # Для работы с JSON

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Только для разработки!

DATABASE = 'salary_data.db'
GRID_FILE = 'grid_data.json' # Файл для хранения сетки

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS salary_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                summHold12 INTEGER NOT NULL,
                summHold3 INTEGER NOT NULL,
                isWorkDay INTEGER NOT NULL,
                office INTEGER NOT NULL,
                oklad INTEGER NOT NULL,
                robot INTEGER NOT NULL,
                aproov REAL NOT NULL,
                salary12 REAL,
                salary3 REAL,
                nalog12 REAL,
                nalog3 REAL,
                spent12 REAL,
                spent3 REAL,
                money12 REAL,
                money3 REAL,
                salaryDirector REAL,
                salarySupervizer REAL,
                salaryTraficman REAL,
                totalOfDay REAL
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        conn.close()

create_table()

# --- API для сетки ---
def load_grid():
    """Загрузка сетки из файла."""
    try:
        with open(GRID_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return { # Значение по умолчанию, если файл не найден
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
    except json.JSONDecodeError:
        print("Error decoding grid data from JSON.  Using default grid.")
        return { # Значение по умолчанию, если JSON поврежден
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

def save_grid(grid_data):
    """Сохранение сетки в файл."""
    try:
        with open(GRID_FILE, 'w') as f:
            json.dump(grid_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving grid: {e}")
        return False

@app.route('/api/grid', methods=['GET'])
def get_grid():
    """Получение текущей сетки."""
    grid = load_grid()
    return jsonify(grid)

@app.route('/api/grid', methods=['POST'])
def update_grid():
    """Обновление сетки."""
    grid_data = request.get_json()
    if save_grid(grid_data):
        # Пересчитать все данные в базе данных после изменения сетки!
        recalculate_all_data()
        return jsonify({'message': 'Grid updated successfully!'})
    else:
        return jsonify({'message': 'Error updating grid'}), 500

def calculate_data(data, grid):  # Передаем сетку как аргумент
    """Вычисление зарплаты и связанных данных."""
    def vlookup(value, table, column_index):
        """Эмуляция VLOOKUP."""
        keys = sorted(table.keys())
        for i in range(len(keys) - 1):
            if value >= keys[i] and value < keys[i + 1]:
                return table[keys[i]][column_index]
        return table[keys[-1]][column_index]

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

    salaryDirector = vlookup(money3 + money12 - spent12 - spent3, grid, 0)
    salarySupervizer = vlookup(money3 - spent3, grid, 1)
    salaryTraficman = vlookup(money12 - spent12, grid, 2)
    totalOfDay = money12 + money3 - spent12 - spent3 - salaryDirector - salarySupervizer - salaryTraficman

    return {
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
        'salaryTraficman': salaryTraficman,
        'totalOfDay': totalOfDay
    }

def recalculate_data(data, grid):  # Pass data and grid
    """Recalculates salary data based on the grid."""
    try:
        calculated_data = calculate_data(data, grid) # Pass grid
        data.update(calculated_data)
        return data
    except Exception as e:
        print(f"Error recalculating data: {e}")
        return None

def recalculate_all_data():
    """Пересчитывает все данные в базе данных."""
    grid = load_grid() # Load the grid

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM salary_data")
        all_data = cursor.fetchall()

        for row in all_data:
            data = dict(row)  # Convert to dictionary
            recalculated_data = recalculate_data(data, grid) # Pass grid

            if recalculated_data:
                cursor.execute("""
                    UPDATE salary_data
                    SET salary12 = ?, salary3 = ?, nalog12 = ?, nalog3 = ?, spent12 = ?, spent3 = ?,
                        money12 = ?, money3 = ?, salaryDirector = ?, salarySupervizer = ?, salaryTraficman = ?,
                        totalOfDay = ?
                    WHERE id = ?
                """, (recalculated_data['salary12'], recalculated_data['salary3'], recalculated_data['nalog12'],
                      recalculated_data['nalog3'], recalculated_data['spent12'], recalculated_data['spent3'],
                      recalculated_data['money12'], recalculated_data['money3'], recalculated_data['salaryDirector'],
                      recalculated_data['salarySupervizer'], recalculated_data['salaryTraficman'],
                      recalculated_data['totalOfDay'], data['id']))

        conn.commit()
        print("All data recalculated successfully!")

    except Exception as e:
        print(f"Error recalculating all data: {e}")
    finally:
        conn.close()

@app.route('/api/data', methods=['POST'])
def add_data():
    data = request.get_json()
    try:
        date_str = data['date']
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        day_of_week = date_obj.weekday()

        if day_of_week in [5, 6]:
            isWorkDay = 0
        else:
            isWorkDay = int(data['isWorkDay'])

        office = data['office'] if isWorkDay else 0
        oklad = data['oklad'] if isWorkDay else 0

        data['isWorkDay'] = isWorkDay
        data['office'] = office
        data['oklad'] = oklad

        grid = load_grid() # Load the grid
        calculated_data = calculate_data(data, grid) # Pass the grid
        data.update(calculated_data)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO salary_data (date, summHold12, summHold3, isWorkDay, office, oklad, robot, aproov,
                salary12, salary3, nalog12, nalog3, spent12, spent3, money12, money3,
                salaryDirector, salarySupervizer, salaryTraficman, totalOfDay)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (data['date'], data['summHold12'], data['summHold3'], data['isWorkDay'], data['office'],
              data['oklad'], data['robot'], data['aproov'], data['salary12'], data['salary3'],
              data['nalog12'], data['nalog3'], data['spent12'], data['spent3'], data['money12'],
              data['money3'], data['salaryDirector'], data['salarySupervizer'], data['salaryTraficman'],
              data['totalOfDay']))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Data added successfully!'}), 201

    except Exception as e:
        print(f"Error adding data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/<int:id>', methods=['PUT'])
def update_data(id):
    data = request.get_json()
    try:
        date_str = data['date']
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        day_of_week = date_obj.weekday()

        if day_of_week in [5, 6]:
            isWorkDay = 0
        else:
            isWorkDay = int(data['isWorkDay'])

        office = data['office'] if isWorkDay else 0
        oklad = data['oklad'] if isWorkDay else 0

        data['isWorkDay'] = isWorkDay
        data['office'] = office
        data['oklad'] = oklad

        grid = load_grid() # Load the grid
        calculated_data = calculate_data(data, grid)  # Pass the grid
        data.update(calculated_data)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE salary_data
            SET date = ?, summHold12 = ?, summHold3 = ?, isWorkDay = ?, office = ?, oklad = ?, robot = ?, aproov = ?,
                salary12 = ?, salary3 = ?, nalog12 = ?, nalog3 = ?, spent12 = ?, spent3 = ?, money12 = ?, money3 = ?,
                salaryDirector = ?, salarySupervizer = ?, salaryTraficman = ?, totalOfDay = ?
            WHERE id = ?
        """, (data['date'], data['summHold12'], data['summHold3'], data['isWorkDay'], data['office'],
              data['oklad'], data['robot'], data['aproov'], data['salary12'], data['salary3'],
              data['nalog12'], data['nalog3'], data['spent12'], data['spent3'], data['money12'],
              data['money3'], data['salaryDirector'], data['salarySupervizer'], data['salaryTraficman'],
              data['totalOfDay'], id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Data updated successfully!'})

    except Exception as e:
        print(f"Error updating data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data', methods=['GET'])
def get_all_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM salary_data")
        data = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in data])
    except Exception as e:
        print(f"Error getting all data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/<int:id>', methods=['GET'])
def get_data(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM salary_data WHERE id = ?", (id,))
        data = cursor.fetchone()
        conn.close()

        if data:
            return jsonify(dict(data))
        return jsonify({'message': 'Data not found'}), 404
    except Exception as e:
        print(f"Error getting data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/<int:id>', methods=['DELETE'])
def delete_data(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM salary_data WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Data deleted successfully!'})
    except Exception as e:
        print(f"Error deleting data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/summary/month', methods=['GET'])
def get_monthly_summary():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT strftime('%Y-%m', date) AS month, SUM(totalOfDay) AS totalOfDay
            FROM salary_data
            GROUP BY strftime('%Y-%m', date)
        """)
        data = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in data])
    except Exception as e:
        print(f"Error fetching monthly summary: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/summary/year', methods=['GET'])
def get_yearly_summary():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT strftime('%Y', date) AS year, SUM(totalOfDay) AS totalOfDay
            FROM salary_data
            GROUP BY strftime('%Y', date)
        """)
        data = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in data])
    except Exception as e:
        print(f"Error fetching yearly summary: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
