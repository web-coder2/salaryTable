
import json

data = {
    "Ноябрь 2024": {
        "Неделя 1 (02.11.2024 - 03.11.2024)": {
            "Суббота (02.11.2024)": {
                "Дата": "02.11.2024",
                "Робот": 33000,
                "Офис": 0,
                "Окладчики": 0
            },
            "Воскресенье (03.11.2024)": {
                "Дата": "03.11.2024",
                "Робот": 0,
                "Офис": 0,
                "Окладчики": 0
            }
        },
        "Неделя 2 (04.11.2024 - 10.11.2024)": {
            "Понедельник (04.11.2024)": {
                "Дата": "04.11.2024",
                "Робот": 0,
                "Офис": 0,
                "Окладчики": 0
            },
            "Вторник (05.11.2024)": {
                "Дата": "05.11.2024",
                "Робот": 59000,
                "Офис": 37000,
                "Окладчики": 40000
            },
            "Среда (06.11.2024)": {
                "Дата": "06.11.2024",
                "Робот": 73000,
                "Офис": 23000,
                "Окладчики": 35000
            },
            "Четверг (07.11.2024)": {
                "Дата": "07.11.2024",
                "Робот": 57000,
                "Офис": 45000,
                "Окладчики": 35000
            },
            "Пятница (08.11.2024)": {
                "Дата": "08.11.2024",
                "Робот": 46000,
                "Офис": 30000,
                "Окладчики": 35000
            },
            "Суббота (09.11.2024)": {
                "Дата": "09.11.2024",
                "Робот": 15000,
                "Офис": 0,
                "Окладчики": 0
            },
            "Воскресенье (10.11.2024)": {
                "Дата": "10.11.2024",
                "Робот": 0,
                "Офис": 0,
                "Окладчики": 0
            }
        },
        "Неделя 3 (11.11.2024 - 17.11.2024)": {
            "Понедельник (11.11.2024)": {
                "Дата": "11.11.2024",
                "Робот": 82000,
                "Офис": 35000,
                "Окладчики": 35000
            },
            "Вторник (12.11.2024)": {
                "Дата": "12.11.2024",
                "Робот": 117000,
                "Офис": 35000,
                "Окладчики": 35000
            },
            "Среда (13.11.2024)": {
                "Дата": "13.11.2024",
                "Робот": 81000,
                "Офис": 35000,
                "Окладчики": 35000
            },
            "Четверг (14.11.2024)": {
                "Дата": "14.11.2024",
                "Робот": 81000,
                "Офис": 35000,
                "Окладчики": 35000
            },
            "Пятница (15.11.2024)": {
                "Дата": "15.11.2024",
                "Робот": 74000,
                "Офис": 35000,
                "Окладчики": 35000
            },
            "Суббота (16.11.2024)": {
                "Дата": "16.11.2024",
                "Робот": 2000,
                "Офис": 0,
                "Окладчики": 0
            },
            "Воскресенье (17.11.2024)": {
                "Дата": "17.11.2024",
                "Робот": 0,
                "Офис": 0,
                "Окладчики": 0
            }
        },
        "Неделя 4 (18.11.2024 - 24.11.2024)": {
            "Понедельник (18.11.2024)": {
                "Дата": "18.11.2024",
                "Робот": 85000,
                "Офис": 45000,
                "Окладчики": 35000
            },
            "Вторник (19.11.2024)": {
                "Дата": "19.11.2024",
                "Робот": 92000,
                "Офис": 35000,
                "Окладчики": 35000
            },
            "Среда (20.11.2024)": {
                "Дата": "20.11.2024",
                "Робот": 88000,
                "Офис": 25000,
                "Окладчики": 35000
            },
            "Четверг (21.11.2024)": {
                "Дата": "21.11.2024",
                "Робот": 88000,
                "Офис": 35000,
                "Окладчики": 35000
            },
            "Пятница (22.11.2024)": {
                "Дата": "22.11.2024",
                "Робот": 80000,
                "Офис": 35000,
                "Окладчики": 35000
            },
            "Суббота (23.11.2024)": {
                "Дата": "23.11.2024",
                "Робот": 11000,
                "Офис": 0,
                "Окладчики": 0
            },
            "Воскресенье (24.11.2024)": {
                "Дата": "24.11.2024",
                "Робот": 0,
                "Офис": 0,
                "Окладчики": 0
            }
        },
        "Неделя 5 (25.11.2024 - 30.11.2024)": {
            "Понедельник (25.11.2024)": {
                "Дата": "25.11.2024",
                "Робот": 38000,
                "Офис": 35000,
                "Окладчики": 35000
            },
            "Вторник (26.11.2024)": {
                "Дата": "26.11.2024",
                "Робот": 48000,
                "Офис": 35000,
                "Окладчики": 35000
            },
            "Среда (27.11.2024)": {
                "Дата": "27.11.2024",
                "Робот": 63000,
                "Офис": 35000,
                "Окладчики": 35000
            },
            "Четверг (28.11.2024)": {
                "Дата": "28.11.2024",
                "Робот": 57000,
                "Офис": 35000,
                "Окладчики": 35000
            },
            "Пятница (29.11.2024)": {
                "Дата": "29.11.2024",
                "Робот": 40000,
                "Офис": 35000,
                "Окладчики": 35000
            },
            "Суббота (30.11.2024)": {
                "Дата": "30.11.2024",
                "Робот": 10000,
                "Офис": 0,
                "Окладчики": 0
            }
        }
    }
}

with open("data_november.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("JSON файл 'dataNov.json' успешно создан.")