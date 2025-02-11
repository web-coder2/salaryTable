
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
            },
            results: null,
            calculations: [],
            showMonthlyTable: true,
            showYearlyTable: false,
            isAdding: false
        };
    },
    delimiters: ['[[', ']]'],
    mounted() {
        this.fetchCalculations();
        this.fetchLadder();
    },
    computed: {
        monthlyCalculations() {
            const monthlyData = {};
            this.calculations.forEach(calc => {
                const date = new Date(calc.date);
                const month = date.toLocaleString('default', {month: 'long'});
                if (!monthlyData[month]) {
                    monthlyData[month] = {month: month, total: 0};
                }
                monthlyData[month].total += calc.total;
            });
            return Object.values(monthlyData);
        },
        yearlyCalculations() {
            const yearlyData = {};
            this.calculations.forEach(calc => {
                const year = new Date(calc.date).getFullYear();
                if (!yearlyData[year]) {
                    yearlyData[year] = {year: year, total: 0};
                }
                yearlyData[year].total += calc.total;
            });
            return Object.values(yearlyData);
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
        async deleteCalculation(id) {
            try {
                await axios.delete(`http://localhost:5000/delete_calculation/${id}`);
                this.fetchCalculations();
            } catch (error) {
                console.error('Error deleting calculation:', error);
                alert('Ошибка при удалении записи.');
            }
        }
    }
}).mount('#app');
