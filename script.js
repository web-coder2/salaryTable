new Vue({
    el: '#app',
    data: {
        table: [],
        data: [],
        newEntry: {
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
        showTable: true  // Новая переменная для управления видимостью таблицы
    },
    computed: {},
    mounted() {
        this.fetchData();
        this.fetchTable();
    },
    methods: {
        async fetchData() {
            try {
                const response = await axios.get('/api/data');
                this.data = response.data;
            } catch (error) {
                console.error('Ошибка при загрузке данных:', error);
            }
        },
        async addData() {
            try {
                await axios.post('/api/data', this.newEntry);
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
        async deleteData(itemId, index) {
            try {
                await axios.delete(`/api/data/${itemId}`);
                this.data.splice(index, 1);
                this.fetchData();
            } catch (error) {
                console.error('Ошибка при удалении данных:', error);
            }
        },
        async fetchTable() {
            try {
                const response = await axios.get('/api/table');
                this.table = response.data;
            } catch (error) {
                console.error('Ошибка при загрузке таблицы:', error);
            }
        },
        async saveTable() {
            try {
                await axios.post('/api/table', this.table);
                alert('Таблица сохранена!');
            } catch (error) {
                console.error('Ошибка при сохранении таблицы:', error);
            }
        },
        async toggleMonthlyData() {
            if (!this.showMonthlyData) {
                try {
                    const response = await axios.get('/api/data/grouped/monthly');
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
                    const response = await axios.get('/api/data/grouped/yearly');
                    this.yearlyData = response.data;
                } catch (error) {
                    console.error('Ошибка при загрузке годовых данных:', error);
                }
            }
            this.showYearlyData = !this.showYearlyData;
        },
        toggleTable() {
            this.showTable = !this.showTable;  // Изменяем видимость таблицы
        }
    }
});