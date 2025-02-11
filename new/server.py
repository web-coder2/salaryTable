
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import sqlite3
import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random, secure key!
CORS(app)

DATABASE = 'data.db'

# Replace with your desired username and password
USERNAME = 'admin'
PASSWORD = 'qwertyuiop123A'


def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS salary_calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            robot INTEGER,
            summHold INTEGER,
            differ INTEGER,
            oklad INTEGER,
            office INTEGER,
            defaultSuper INTEGER,
            defaultDirector INTEGER,
            defaultTraffic INTEGER,
            nalog REAL,
            salary REAL,
            spent REAL,
            officeSalary REAL,
            salarySuper REAL,
            salaryDirector REAL,
            salaryTraffic REAL,
            total REAL
        )
    ''')
    conn.commit()
    conn.close()


create_table()

LADDER = {
    0: {'Директор': 3000, 'Супервайзер': 2100, 'Трафик-менеджер': 1400},
    20000: {'Директор': 3600, 'Супервайзер': 2600, 'Трафик-менеджер': 1700},
    40000: {'Директор': 4250, 'Супервайзер': 3150, 'Трафик-менеджер': 2050},
    60000: {'Директор': 4950, 'Супервайзер': 3750, 'Трафик-менеджер': 2450},
    80000: {'Директор': 5700, 'Супервайзер': 4400, 'Трафик-менеджер': 2900},
    100000: {'Директор': 6500, 'Супервайзер': 5100, 'Трафик-менеджер': 3400},
    120000: {'Директор': 7350, 'Супервайзер': 5850, 'Трафик-менеджер': 3950},
    140000: {'Директор': 8250, 'Супервайзер': 6650, 'Трафик-менеджер': 4550},
    160000: {'Директор': 9250, 'Супервайзер': 7500, 'Трафик-менеджер': 5200},
    180000: {'Директор': 10300, 'Супервайзер': 8400, 'Трафик-менеджер': 5900},
    200000: {'Директор': 11400, 'Супервайзер': 9350, 'Трафик-менеджер': 6650},
    220000: {'Директор': 12550, 'Супервайзер': 10350, 'Трафик-менеджер': 7450},
    240000: {'Директор': 13750, 'Супервайзер': 11400, 'Трафик-менеджер': 8300},
    260000: {'Директор': 15000, 'Супервайзер': 12500, 'Трафик-менеджер': 9200},
    280000: {'Директор': 16300, 'Супервайзер': 13650, 'Трафик-менеджер': 10200},
    300000: {'Директор': 17650, 'Супервайзер': 14850, 'Трафик-менеджер': 11250}
}


def lookup_ladder(office_salary, role):
    keys = sorted(LADDER.keys())
    for i in range(len(keys) - 1):
        if keys[i] <= office_salary < keys[i + 1]:
            return LADDER[keys[i]][role]
    if office_salary >= keys[-1]:
        return LADDER[keys[-1]][role]
    return LADDER[keys[0]][role]


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != USERNAME or request.form['password'] != PASSWORD:
            error = 'Неверный логин или пароль'
        else:
            session['logged_in'] = True
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
@login_required
def calculate():
    data = request.get_json()

    aproov = 0.6
    date = data['date']
    robot = int(data['robot'])
    summHold = int(data['summHold'])
    differ = int(data['differ'])
    oklad = int(data['oklad'])
    office = int(data['office'])
    defaultSuper = int(data['defaultSuper'])
    defaultDirector = int(data['defaultDirector'])
    defaultTraffic = int(data['defaultTraffic'])

    nalog = round((summHold + differ) * 10 * aproov * 0.07, 2)
    salary = round((0.37 * summHold) / 0.63 + summHold * aproov, 2)
    spent = round(robot + oklad + office + nalog + salary, 2)
    officeSalary = round((differ + summHold) * aproov * 10, 2)

    salarySuper = round(lookup_ladder(officeSalary, 'Супервайзер') if officeSalary > 0 else defaultSuper, 2)
    salaryDirector = round(lookup_ladder(officeSalary, 'Директор') if officeSalary > 0 else defaultDirector, 2)
    salaryTraffic = round(lookup_ladder(officeSalary, 'Трафик-менеджер') if officeSalary > 0 else defaultTraffic, 2)

    total = round(officeSalary - spent - salaryDirector - salarySuper - salaryTraffic, 2)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO salary_calculations (date, robot, summHold, differ, oklad, office, defaultSuper, defaultDirector, defaultTraffic, nalog, salary, spent, officeSalary, salarySuper, salaryDirector, salaryTraffic, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, robot, summHold, differ, oklad, office, defaultSuper, defaultDirector, defaultTraffic, nalog, salary, spent, officeSalary, salarySuper, salaryDirector, salaryTraffic, total))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Calculation added successfully'})


@app.route('/get_calculations', methods=['GET'])
@login_required
def get_calculations():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM salary_calculations")
    rows = cursor.fetchall()
    conn.close()

    calculations = []
    for row in rows:
        calculations.append({
            'id': row[0],
            'date': row[1],
            'robot': row[2],
            'summHold': row[3],
            'differ': row[4],
            'oklad': row[5],
            'office': row[6],
            'defaultSuper': row[7],
            'defaultDirector': row[8],
            'defaultTraffic': row[9],
            'nalog': row[10],
            'salary': row[11],
            'spent': row[12],
            'officeSalary': row[13],
            'salarySuper': row[14],
            'salaryDirector': row[15],
            'salaryTraffic': row[16],
            'total': row[17]
        })
    return jsonify(calculations)


@app.route('/delete_calculation/<int:id>', methods=['DELETE'])
@login_required
def delete_calculation(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM salary_calculations WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Calculation deleted successfully'})


@app.route('/update_ladder', methods=['POST'])
@login_required
def update_ladder():
    global LADDER
    ladder_data = request.get_json()

    if not isinstance(ladder_data, dict):
        return jsonify({'error': 'Invalid ladder data format'}), 400

    try:
        LADDER.clear()
        for k, v in ladder_data.items():
            LADDER[int(k)] = v

        print("Ladder updated successfully:", LADDER)
        return jsonify({'message': 'Ladder updated successfully'}), 200

    except Exception as e:
        print(f"Error updating ladder: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/get_ladder', methods=['GET'])
@login_required
def get_ladder():
    return jsonify(LADDER)


if __name__ == '__main__':
    app.run(debug=True)
