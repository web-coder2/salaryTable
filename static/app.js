
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
                defaultTraffic: 1000
            },
            ladder: {
                0: {'ladderValue':0, 'Супервайзер': 2100, 'Трафик-менеджер': 1400},
                20000: {'ladderValue':20000, 'Супервайзер': 2600, 'Трафик-менеджер': 1700},
                40000: {'ladderValue':40000, 'Супервайзер': 3150, 'Трафик-менеджер': 2050},
                60000: {'ladderValue':60000, 'Супервайзер': 3750, 'Трафик-менеджер': 2450},
                80000: {'ladderValue':80000, 'Супервайзер': 4400, 'Трафик-менеджер': 2900},
                100000: {'ladderValue':100000, 'Супервайзер': 5100, 'Трафик-менеджер': 3400},
                120000: {'ladderValue':120000, 'Супервайзер': 5850, 'Трафик-менеджер': 3950},
                140000: {'ladderValue':140000, 'Супервайзер': 6650, 'Трафик-менеджер': 4550},
                160000: {'ladderValue':160000, 'Супервайзер': 7500, 'Трафик-менеджер': 5200},
                180000: {'ladderValue':180000, 'Супервайзер': 8400, 'Трафик-менеджер': 5900},
                200000: {'ladderValue':200000, 'Супервайзер': 9350, 'Трафик-менеджер': 6650},
                220000: {'ladderValue':220000, 'Супервайзер': 10350, 'Трафик-менеджер': 7450},
                240000: {'ladderValue':240000, 'Супервайзер': 11400, 'Трафик-менеджер': 8300},
                260000: {'ladderValue':260000, 'Супервайзер': 12500, 'Трафик-менеджер': 9200},
                280000: {'ladderValue':280000, 'Супервайзер': 13650, 'Трафик-менеджер': 10200},
                300000: {'ladderValue':300000, 'Супервайзер': 14850, 'Трафик-менеджер': 11250}
            },
            results: null,
            calculations: [],
            showMonthlyTable: false,
            showYearlyTable: false,
            isAdding: false,
            api_route: "http://localhost:5000/",  // перед продом поменять на http://31.130.151.240:5000/
            // api_route: "http://31.130.151.240:5000/"
            monthNames: [
                "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
            ],
            sortMode: true, 
        };
    },
    mounted() {
        this.fetchCalculations();
        this.fetchDefault()
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
                        date: date,
                        monthYear: monthYear,
                        salaryTraffic: 0,
                        salarySuper: 0,
                        total: 0
                    };
                }
                monthlyData[monthYear].salaryTraffic += calc.salaryTraffic;
                monthlyData[monthYear].salarySuper += calc.salarySuper;
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
                        total: 0
                    };
                }
                yearlyData[year].salaryTraffic += calc.salaryTraffic;
                yearlyData[year].salarySuper += calc.salarySuper;
                yearlyData[year].total += calc.total;
            });
            return Object.values(yearlyData);
        },
        middleMounth(){

            let traficSumm = 0;
            let superSumm = 0;
            let total = 0

            for (let item in this.monthlyCalculations) {
                traficSumm += this.monthlyCalculations[item].salaryTraffic;
                superSumm += this.monthlyCalculations[item].salarySuper;
                total += this.monthlyCalculations[item].total;
            }

            traficSumm = traficSumm / this.monthlyCalculations.length
            superSumm = superSumm / this.monthlyCalculations.length
            total = total / this.monthlyCalculations.length

            return {
                trafic: Math.floor(traficSumm),
                super: Math.floor(superSumm),
                total: Math.floor(total)
            }
        },
        middleYear(){
            let traficSumm = 0;
            let superSumm = 0;
            let total = 0

            for (let item in this.yearlyCalculations) {
                traficSumm += this.yearlyCalculations[item].salaryTraffic;
                superSumm += this.yearlyCalculations[item].salarySuper;
                total += this.yearlyCalculations[item].total;
            }

            traficSumm = traficSumm / this.yearlyCalculations.length
            superSumm = superSumm / this.yearlyCalculations.length
            total = total / this.yearlyCalculations.length

            return {
                trafic: Math.floor(traficSumm),
                super: Math.floor(superSumm),
                total: Math.floor(total)
            }
        }
    },
    watch: {
        sortMode() {
            this.calculations.sort((a, b) => {
                if (this.sortMode) {
                    return new Date(b.date) - new Date(a.date);
                } else {
                    return new Date(a.date) - new Date(b.date);
                }
            });
        }
    },
    methods: {
        async addRecord() {
            this.isAdding = true;
            try {
                // для разработки будем использовать localhost:5000
                // а для продакшена 31.130.151.240:5000
                const response = await axios.post(this.api_route + 'calculate', {
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
                    const response = await axios.post(this.api_route + 'calculate', {
                        date: item["Дата"],
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
            try {
                const response = await axios.post(this.api_route + 'update_defaults', this.defaultValues);
                if (response.status === 200) {
                    alert('Значения по умолчанию сохранены успешно!');
                    this.fetchCalculations();
                } else {
                    alert('Не удалось сохранить значения по умолчанию.');
                }
            } catch {
                console.log('Error updating defaults:');
                alert('Ошибка при сохранении значений по умолчанию.');
            }
        },
        async saveLadder() {
            try {
                const ladderToSend = {};
                for (const key in this.ladder) {
                    ladderToSend[parseInt(key)] = this.ladder[key];
                }

                const response = await axios.post(this.api_route + 'update_ladder', ladderToSend);
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
        parseDate(dateString) {
            const [month, day, year] = dateString.split('.'); // Extract components
            if (year.length == 2) {
                return new Date(`20${year}`, month - 1, day);
            } if (year.length == 4) {
                return new Date(year, month -1, day)
            }
        },
        formatDate(dateString) {
            const date = this.parseDate(dateString);
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0'); // +1 because months are 0-indexed
            const year = date.getFullYear();
            const monthName = this.monthNames[date.getMonth()];
            //return `${day}-${month}-${year} ${monthName}`;
            return `${day} ${monthName} ${year}`;
        },
        sorterByDate(mode) {
            if (mode == true) {
                this.calculations.sort((a,b) => {
                    const dateA = this.parseDate(a.date);
                    const dateB = this.parseDate(b.date);
                    return dateA.getTime() - dateB.getTime();
                })
            } else {
                this.calculations.sort((a,b) => {
                    const dateA = this.parseDate(a.date);
                    const dateB = this.parseDate(b.date);
                    return dateB.getTime() - dateA.getTime();
                })
            }
        },
        async fetchCalculations() {
            try {
                const response = await axios.get(this.api_route + 'get_calculations');
                this.calculations = response.data;
            } catch (error) {
                console.error('Error fetching calculations:', error);
            }
            this.calculations.sort((a,b) => {
                const dateA = this.parseDate(a.date);
                const dateB = this.parseDate(b.date);
                return dateB.getTime() - dateA.getTime(); // Для сортировки по убыванию
            })
        },
        async fetchLadder() {
            try {
                const response = await axios.get(this.api_route + 'get_ladder');
                this.ladder = response.data;
            } catch (error) {
                console.error('Error fetching ladder:', error);
            }
        },
        async fetchDefault() {
            try {
                const response = await axios.get(this.api_route + 'get_defaults')
                this.defaultValues["defaultSuper"] = response.data["super-default"]
                this.defaultValues["defaultTraffic"] = response.data["traffic-default"]
                console.log(response)
            } catch (error) {
                console.log("hui tam a ne defaults >>> ", error)
            }
        },
        async deleteCalculation(id) {
            try {
                const response = await axios.delete(this.api_route + `delete_calculation/${id}`);
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
                return 'rgba(42, 96, 42, 0.5)'; // Green for positive total
            } else if (total < 0) {
                return 'rgba(240, 63, 63, 0.5)'; // Red for negative total
            } else {
                return 'rgba(250, 250, 11, 0.5)'; // Yellow for zero
            }
        },
    }
}).mount('#app');
