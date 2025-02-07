new Vue({
    el: '#app',
    data: {
        table: {}, // Инициализируйте table как пустой объект
        data: [],
        newEntry: {
            date: '',
            sumHold12: 0,
            sumHold3: 0,
            robot: 0,
            oklad: 0,
            office: 0
        },
        editingIndex: null,
        editedEntry: {
            date: '',
            sumHold12: 0,
            sumHold3: 0,
            robot: 0,
            oklad: 0,
            office: 0
        },
        monthlyData: {},
        yearlyData: {},
        showMonthlyData: false,
        showYearlyData: false,
        tableKeys: []
    },
    computed: {},
    mounted() {
        this.fetchData();
        this.fetchTable();
    },
    methods: {
        async fetchData() {
            try {
                const response = await axios.get('http://localhost:5000/api/data');
                this.data = response.data;
            } catch (error) {
                console.error('Ошибка при загрузке данных:', error);
            }
        },
        async addData() {
            try {
                await axios.post('http://localhost:5000/api/data', this.newEntry);
                this.newEntry = {
                    date: '',
                    sumHold12: 0,
                    sumHold3: 0,
                    robot: 0,
                    oklad: 0,
                    office: 0
                };
                await this.fetchData();
            } catch (error) {
                console.error('Ошибка при добавлении данных:', error);
            }
        },
        async deleteData(index) {
            try {
                await axios.delete(`http://localhost:5000/api/data/${index}`);
                await this.fetchData();
            } catch (error) {
                console.error('Ошибка при удалении данных:', error);
            }
        },
        async updateData() {
            try {
                await axios.put(`http://localhost:5000/api/data/${this.editingIndex}`, this.editedEntry);
                await this.fetchData(); // Обновляем таблицу
                this.editingIndex = null; // Скрываем форму
            } catch (error) {
                console.error('Ошибка при обновлении данных:', error);
            }
        },
        async fetchTable() {
            try {
                const response = await axios.get('http://localhost:5000/api/table');
                this.table = response.data;

                // Преобразуем ключи в массив объектов
                this.tableKeys = Object.keys(this.table).sort((a, b) => a - b).map(key => ({value: key}));
            } catch (error) {
                console.error('Ошибка при загрузке таблицы:', error);
                this.table = {}; // Обработка ошибки: устанавливаем table в пустой объект
                this.tableKeys = [];// Обработка ошибки: устанавливаем table в пустой массив
            }
        },
        async saveTable() {
            try {
                const newTable = {};
                this.tableKeys.forEach(item => {
                    if (this.table[item.value]) { // Добавляем проверку на существование this.table[item.value]
                        newTable[item.value] = this.table[item.value];
                    }
                });
                await axios.post('http://localhost:5000/api/table', newTable);
                alert('Таблица сохранена!');
                await this.fetchData();
            } catch (error) {
                console.error('Ошибка при сохранении таблицы:', error);
            }
        },
        async toggleMonthlyData() {
            if (!this.showMonthlyData) {
                try {
                    const response = await axios.get('http://localhost:5000/api/data/grouped/monthly');
                    this.monthlyData = response.data;
                } catch (error) {
                    console.error('Ошибка при загрузке месячных данных:', error);
                }
            }
            this.showMonthlyData = !this.showMonthlyData;
        },
        async toggleYearlyData() {
            if (!this.showYearlyData) {
                try {
                    const response = await axios.get('http://localhost:5000/api/data/grouped/yearly');
                    this.yearlyData = response.data;
                } catch (error) {
                    console.error('Ошибка при загрузке годовых данных:', error);
                }
            }
            this.showYearlyData = !this.showYearlyData;
        }
    }
})