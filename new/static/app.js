
const { createApp } = Vue;

createApp({
    data() {
        return {
            formData: {
                date: '',
                robot: 0,
                summHold: 0,
                differ: 0,
                oklad: 0,
                office: 0
            },
            defaultValues: {
                defaultSuper: 1400,
                defaultDirector: 1500,
                defaultTraffic: 1000
            },
            ladder: {
                0: {'ladderValue':0,'Директор': 3000, 'Супервайзер': 2100, 'Трафик-менеджер': 1400},
                20000: {'ladderValue':20000,'Директор': 3600, 'Супервайзер': 2600, 'Трафик-менеджер': 1700},
                40000: {'ladderValue':40000,'Директор': 4250, 'Супервайзер': 3150, 'Трафик-менеджер': 2050},
                60000: {'ladderValue':60000,'Директор': 4950, 'Супервайзер': 3750, 'Трафик-менеджер': 2450},
                80000: {'ladderValue':80000,'Директор': 5700, 'Супервайзер': 4400, 'Трафик-менеджер': 2900},
                100000: {'ladderValue':100000,'Директор': 6500, 'Супервайзер': 5100, 'Трафик-менеджер': 3400},
                120000: {'ladderValue':120000,'Директор': 7350, 'Супервайзер': 5850, 'Трафик-менеджер': 3950},
                140000: {'ladderValue':140000,'Директор': 8250, 'Супервайзер': 6650, 'Трафик-менеджер': 4550},
                160000: {'ladderValue':160000,'Директор': 9250, 'Супервайзер': 7500, 'Трафик-менеджер': 5200},
                180000: {'ladderValue':180000,'Директор': 10300, 'Супервайзер': 8400, 'Трафик-менеджер': 5900},
                200000: {'ladderValue':200000,'Директор': 11400, 'Супервайзер': 9350, 'Трафик-менеджер': 6650},
                220000: {'ladderValue':220000,'Директор': 12550, 'Супервайзер': 10350, 'Трафик-менеджер': 7450},
                240000: {'ladderValue':240000,'Директор': 13750, 'Супервайзер': 11400, 'Трафик-менеджер': 8300},
                260000: {'ladderValue':260000,'Директор': 15000, 'Супервайзер': 12500, 'Трафик-менеджер': 9200},
                280000: {'ladderValue':280000,'Директор': 16300, 'Супервайзер': 13650, 'Трафик-менеджер': 10200},
                300000: {'ladderValue':300000,'Директор': 17650, 'Супервайзер': 14850, 'Трафик-менеджер': 11250}
            },
            results: null,
            calculations: [],
            showMonthlyTable: true,
            showYearlyTable: false,
            isAdding: false,
        };
    },
    mounted() {
        this.fetchCalculations();
        this.fetchLadder();
    },
    delimiters: ['[[', ']]'], 
    computed: {
        monthlyCalculations() {
            const monthlyData = {};
            this.calculations.forEach(calc => {
                const date = new Date(calc.date);
                const month = date.toLocaleString('default', {month: 'long'});
                const year = date.getFullYear();
                const monthYear = `${month} ${year}`;
                if (!monthlyData[monthYear]) {
                    monthlyData[monthYear] = {
                        monthYear: monthYear,
                        salaryTraffic: 0,
                        salarySuper: 0,
                        salaryDirector: 0,
                        total: 0
                    };
                }
                monthlyData[monthYear].salaryTraffic += calc.salaryTraffic;
                monthlyData[monthYear].salarySuper += calc.salarySuper;
                monthlyData[monthYear].salaryDirector += calc.salaryDirector;
                monthlyData[monthYear].total += calc.total;

            });
            return Object.values(monthlyData);
        },
        yearlyCalculations() {
            const yearlyData = {};
            this.calculations.forEach(calc => {
                const year = new Date(calc.date).getFullYear();
                if (!yearlyData[year]) {
                    yearlyData[year] = {
                        year: year,
                        salaryTraffic: 0,
                        salarySuper: 0,
                        salaryDirector: 0,
                        total: 0
                    };
                }
                yearlyData[year].salaryTraffic += calc.salaryTraffic;
                yearlyData[year].salarySuper += calc.salarySuper;
                yearlyData[year].salaryDirector += calc.salaryDirector;
                yearlyData[year].total += calc.total;
            });
            return Object.values(yearlyData);
        },
        middleMounth(){

            let traficSumm = 0;
            let superSumm = 0;
            let directorSumm = 0;
            let total = 0

            for (let item in this.monthlyCalculations) {
                traficSumm += this.monthlyCalculations[item].salaryTraffic;
                superSumm += this.monthlyCalculations[item].salarySuper;
                directorSumm += this.monthlyCalculations[item].salaryDirector;
                total += this.monthlyCalculations[item].total;
            }

            traficSumm = traficSumm / this.monthlyCalculations.length
            superSumm = superSumm / this.monthlyCalculations.length
            directorSumm = directorSumm / this.monthlyCalculations.length
            total = total / this.monthlyCalculations.length

            return {
                trafic: Math.floor(traficSumm),
                super: Math.floor(superSumm),
                director: Math.floor(directorSumm),
                total: Math.floor(total)
            }
        }
    },
    methods: {
        async addRecord() {
            this.isAdding = true;
            try {
                const response = await axios.post('http://localhost:5000/calculate', {
                    ...this.formData,
                    ...this.defaultValues
                });

                this.fetchCalculations();
                this.resetForm();

            } catch (error) {
                console.error('Error submitting form:', error);
            } finally {
                setTimeout(() => {
                    this.isAdding = false;
                }, 300);
            }
        },
        async handleFileChange(event) { // handleFileChange теперь асинхронная функция
            const file = event.target.files[0];
            if (file) {
              const reader = new FileReader();
              reader.onload = async (e) => { // Сделайте функцию onload асинхронной
                try {
                  const jsonData = JSON.parse(e.target.result);
                  for (const item of jsonData) { // Используйте цикл for...of для ожидания каждого запроса
                    console.log(item);
                    const response = await axios.post('http://localhost:5000/calculate', {
                        date: item["Дата"],
                        defaultDirector: this.defaultValues['defaultDirector'],
                        defaultSuper: this.defaultValues['defaultSuper'],
                        defaultTraffic: this.defaultValues['defaultTraffic'],
                        differ: item["Сумма_HOLD_Разница"],
                        office: item["Офис"],
                        oklad: item["Окладчики"],
                        robot: item["Робот"],
                        summHold: item["Сумма_HOLD_Итого"],
                    });
                    //console.log('Response:', response.data); // Вывод ответа от сервера
                  }
                } catch (error) {
                  console.error("Ошибка при парсинге JSON или отправке запроса:", error);
                }
              };
              reader.readAsText(file);
            }
          },
      
        resetForm() {
            this.formData = {
                date: '',
                robot: 0,
                summHold: 0,
                differ: 0,
                oklad: 0,
                office: 0
            };
        },
        async updateDefaults() {
            console.log("Updating defaults:", this.defaultValues);
        },
        async saveLadder() {
            try {
                const ladderToSend = {};
                for (const key in this.ladder) {
                    ladderToSend[parseInt(key)] = this.ladder[key];
                }

                const response = await axios.post('http://localhost:5000/update_ladder', ladderToSend);
                if (response.status === 200) {
                    alert('Лестница сохранена успешно!');
                    this.fetchCalculations();
                } else {
                    alert('Не удалось сохранить лестницу.');
                }
            } catch (error) {
                console.error('Error saving ladder:', error);
                alert('Ошибка при сохранении лестницы.');
            }
        },
        async fetchCalculations() {
            try {
                const response = await axios.get('http://localhost:5000/get_calculations');
                this.calculations = response.data;
            } catch (error) {
                console.error('Error fetching calculations:', error);
            }
        },
        async fetchLadder() {
            try {
                const response = await axios.get('http://localhost:5000/get_ladder');
                this.ladder = response.data;
            } catch (error) {
                console.error('Error fetching ladder:', error);
            }
        },
        async deleteCalculation(id) {
            try {
                const response = await axios.delete(`http://localhost:5000/delete_calculation/${id}`);
                if (response.status === 200) {
                    console.log(`Calculation with id ${id} deleted successfully`);
                    // Refresh the calculations list
                    this.fetchCalculations();
                } else {
                    console.error(`Failed to delete calculation with id ${id}. Status: ${response.status}`);
                }
            } catch (error) {
                console.error('Error deleting calculation:', error);
            }
        },
        toggleMonthlyTable() {
            this.showMonthlyTable = !this.showMonthlyTable;
        },
        toggleYearlyTable() {
            this.showYearlyTable = !this.showYearlyTable;
        },
        getTotalColor(total) {
            if (total > 0) {
                return 'rgba(0, 255, 0, 0.1)'; // Green for positive total
            } else if (total < 0) {
                return 'rgba(255, 0, 0, 0.1)'; // Red for negative total
            } else {
                return 'rgba(255, 255, 0, 0.1)'; // Yellow for zero
            }
        },
    }
}).mount('#app');
