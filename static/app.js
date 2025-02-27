
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
            showMonthlyTable: false,
            showYearlyTable: false,
            isAdding: false,
            api_route: "http://localhost:5000/",  // перед продом поменять на http://31.130.151.240:80/
            //api_route: "http://31.130.151.240:80/",
            monthNames: [
                "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
            ],
            sortMode: true,
        };
    },
    async mounted() {
        await this.fetchCalculations();
        await this.fetchDefault()
        await this.fetchLadder();

        console.log(this.monthlyCalculations)

        this.calculations.sort((a, b) => {
            return new Date(b.date) - new Date(a.date)
        })
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
    delimiters: ['[[', ']]'],
    computed: {
        monthlyCalculations() {
            const yearlyData = {};

            this.calculations.forEach(calc => {
                const date = new Date(calc.date);
                const year = date.getFullYear();
                const month = date.getMonth();
                const monthName = this.monthNames[month];

                if (!yearlyData[year]) {
                    yearlyData[year] = {
                        year: year,
                        months: Array(12).fill(null).map((_, i) => ({
                            month: this.monthNames[i],
                            monthNumber: i,
                            salaryTraffic: 0,
                            salarySuper: 0,
                            salaryDirector: 0,
                            total: 0,
                            count: 0,
                            robot: 0,
                            summHold: 0,
                            differ: 0,
                            oklad: 0,
                            office: 0,
                            salaryTraffic2: 0,
                            salaryDirector2: 0,
                            salarySuper2: 0,
                            total2: 0
                        })),
                        totalSalaryTraffic: 0,
                        totalSalarySuper: 0,
                        totalSalaryDirector: 0,
                        totalTotal: 0,
                        totalMonthsWithData: 0,
                        totalRobot: 0,
                        totalSummHold: 0,
                        totalDiffer: 0,
                        totalOklad: 0,
                        totalOffice: 0,
                        totalSalarySuper2: 0,
                        totalSalaryDirector2: 0,
                        totalSalaryTraffic2: 0,
                        totalTotal2: 0
                    };
                }

                yearlyData[year].months[month].salaryTraffic += calc.salaryTraffic;
                yearlyData[year].months[month].salarySuper += calc.salarySuper;
                yearlyData[year].months[month].salaryDirector += calc.salaryDirector;
                yearlyData[year].months[month].salarySuper2 += calc.salarySuper2
                yearlyData[year].months[month].salaryTraffic2 += calc.salaryTraffic2
                yearlyData[year].months[month].salaryDirector2 += calc.salaryDirector2
                yearlyData[year].months[month].total2 += calc.total2
                yearlyData[year].months[month].total += calc.total;
                yearlyData[year].months[month].robot += calc.robot;
                yearlyData[year].months[month].summHold += calc.summHold;
                yearlyData[year].months[month].differ += calc.differ;
                yearlyData[year].months[month].oklad += calc.oklad;
                yearlyData[year].months[month].office += calc.office;
                yearlyData[year].months[month].count++;
                yearlyData[year].totalSalaryTraffic2 += calc.salaryTraffic2
                yearlyData[year].totalSalaryDirector2 += calc.salaryDirector2
                yearlyData[year].totalSalarySuper2 += calc.salarySuper2
                yearlyData[year].totalTotal2 += calc.total2                   
                yearlyData[year].totalSalaryTraffic += calc.salaryTraffic;
                yearlyData[year].totalSalarySuper += calc.salarySuper;
                yearlyData[year].totalSalaryDirector += calc.salaryDirector;
                yearlyData[year].totalTotal += calc.total;
                yearlyData[year].totalRobot += calc.robot;
                yearlyData[year].totalSummHold += calc.summHold;
                yearlyData[year].totalDiffer += calc.differ;
                yearlyData[year].totalOklad += calc.oklad;
                yearlyData[year].totalOffice += calc.office;

            });

            const result = Object.values(yearlyData).map(yearData => {

                let monthsWithData = 0;
                yearData.months.forEach(month => {
                    if (month.count > 0) {
                        monthsWithData++;
                    }
                });

                const averageSalaryTraffic = monthsWithData > 0 ? yearData.totalSalaryTraffic / monthsWithData : 0;
                const averageSalarySuper = monthsWithData > 0 ? yearData.totalSalarySuper / monthsWithData : 0;
                const averageSalaryDirector = monthsWithData > 0 ? yearData.totalSalaryDirector / monthsWithData : 0;
                const averageTotal = monthsWithData > 0 ? yearData.totalTotal / monthsWithData : 0;
                const averageRobot = monthsWithData > 0 ? yearData.totalRobot / monthsWithData : 0;
                const averageSummHold = monthsWithData > 0 ? yearData.totalSummHold / monthsWithData : 0;
                const averageDiffer = monthsWithData > 0 ? yearData.totalDiffer / monthsWithData : 0;
                const averageOklad = monthsWithData > 0 ? yearData.totalOklad / monthsWithData : 0;
                const averageOffice = monthsWithData > 0 ? yearData.totalOffice / monthsWithData : 0;
                const averageTotal2 = monthsWithData > 0 ? yearData.totalTotal2 / monthsWithData : 0;
                const averageSalaryTraffic2 = monthsWithData > 0 ? yearData.totalSalaryTraffic2 / monthsWithData : 0;
                const averageSalarySuper2 = monthsWithData > 0 ? yearData.totalSalarySuper2 / monthsWithData : 0;
                const averageSalaryDirector2 = monthsWithData > 0 ? yearData.totalSalaryDirector2 / monthsWithData : 0;

                return {
                    year: yearData.year,
                    months: yearData.months,
                    
                    averageSalaryTraffic: averageSalaryTraffic,
                    averageSalarySuper: averageSalarySuper,
                    averageSalaryDirector: averageSalaryDirector,
                    averageTotal: averageTotal,
                    averageRobot: averageRobot,
                    averageSummHold: averageSummHold,
                    averageDiffer: averageDiffer,
                    averageOklad: averageOklad,
                    averageOffice: averageOffice,
                    averageTotal2: averageTotal2,
                    averageSalarySuper2: averageSalarySuper2,
                    averageSalaryDirector2: averageSalaryDirector2,
                    averageSalaryTraffic2: averageSalaryTraffic2,

                    totalSalaryTraffic: yearData.totalSalaryTraffic,
                    totalSalarySuper: yearData.totalSalarySuper,
                    totalSalaryDirector:  yearData.totalSalaryDirector,
                    totalTotal: yearData.totalTotal,
                    totalSalaryTraffic2: yearData.totalSalaryTraffic2,
                    totalSalarySuper2: yearData.totalSalarySuper2,
                    totalSalaryDirector2:  yearData.totalSalaryDirector2,
                    totalTotal2: yearData.totalTotal2,
                    totalRobot: yearData.totalRobot,
                    totalSummHold: yearData.totalSummHold,
                    totalDiffer: yearData.totalDiffer,
                    totalOklad: yearData.totalOklad,
                    totalOffice: yearData.totalOffice,
                };
            });

            // Sort years in descending order (newest first)
            result.sort((a, b) => b.year - a.year);

            return result;
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

            let monthCount = 0;

            this.monthlyCalculations.forEach(yearData => {
                yearData.months.forEach(monthData => {
                    traficSumm += monthData.salaryTraffic;
                    superSumm += monthData.salarySuper;
                    directorSumm += monthData.salaryDirector;
                    total += monthData.total;
                    monthCount++;
                });
            });


            traficSumm = monthCount > 0 ? traficSumm / monthCount : 0;
            superSumm = monthCount > 0 ? superSumm / monthCount : 0;
            directorSumm = monthCount > 0 ? directorSumm / monthCount : 0;
            total = monthCount > 0 ? total / monthCount : 0;

            return {
                trafic: Math.floor(traficSumm),
                super: Math.floor(superSumm),
                director: Math.floor(directorSumm),
                total: Math.floor(total)
            }
        },
        middleYear(){
            let traficSumm = 0;
            let superSumm = 0;
            let directorSumm = 0;
            let total = 0

            for (let item in this.yearlyCalculations) {
                traficSumm += this.yearlyCalculations[item].salaryTraffic;
                superSumm += this.yearlyCalculations[item].salarySuper;
                directorSumm += this.yearlyCalculations[item].salaryDirector;
                total += this.yearlyCalculations[item].total;
            }

            traficSumm = traficSumm / this.yearlyCalculations.length
            superSumm = superSumm / this.yearlyCalculations.length
            directorSumm = directorSumm / this.yearlyCalculations.length
            total = total / this.yearlyCalculations.length

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
        parseDate(dateString) {
            if (typeof dateString !== 'string') {
                console.warn('Invalid dateString format:', dateString);
                return null;
            }

            const date = dayjs(dateString, 'MM.DD.YY', true); // true включает строгий режим парсинга

            if (!date.isValid()) {
                console.warn('Invalid date:', dateString);
                return null;
            }

            return date;
        },
        formatDate(dateString) {
            const date = this.parseDate(dateString);

            if (!date) {
                return '';
            }

            return `${date.format('DD')} ${this.monthNames[date.month()]} ${date.format('YYYY')}`;
        },
        sorterByDate(mode) {
            this.calculations.sort((a, b) => {
                const dateA = this.parseDate(a.date);
                const dateB = this.parseDate(b.date);

                if (!dateA && !dateB) return 0; // Обе даты невалидны - порядок не важен
                if (!dateA) return mode ? 1 : -1; // dateA невалидна - отправляем ее в конец (или начало)
                if (!dateB) return mode ? -1 : 1; // dateB невалидна - отправляем ее в конец (или начало)

                return mode ? dateA.valueOf() - dateB.valueOf() : dateB.valueOf() - dateA.valueOf();
            });
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
        async fetchCalculations() {
            try {
                const response = await axios.get(this.api_route + 'get_calculations');
                this.calculations = response.data;
            } catch (error) {
                console.error('Error fetching calculations:', error);
            }
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
                this.defaultValues["defaultDirector"] = response.data["director-default"]
                this.defaultValues["defaultTraffic"] = response.data["traffic-default"]
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
        getTotalColor(total, idx) {
            if (total > 0 && idx % 2 == 0) {
                return 'rgba(42, 96, 42, 0.5)'; // Green for positive total
            } if (total < 0 && idx % 2 == 0) {
                return 'rgba(240, 63, 63, 0.5)'; // Red for negative total
            } if (total == 0 && idx % 2 == 0) {
                return 'rgba(250, 250, 11, 0.5)'; // Yellow for zero
            } if (total > 0 && idx % 2 != 0) {
                return 'rgba(70, 96, 45, 0.7)';
            } if (total < 0 && idx % 2 != 0) {
                return 'rgba(213, 60, 60, 0.7)';
            } else {
                return 'rgba(186, 254, 11, 0.7)';
            }
        },
    }
}).mount('#app');