class UtilizationBoiler:
    """Котел утилизатор КВ-ГМ-3,15-95.

    
    Внутренние атрибуты:
    num_boiler - номер утилизатора 
    pwr - номинальная мощность, Гкал
    kpd - КПД
    load - уровень загрузки, %
    status - True/False (вкл/выкл)
    """
    
    def __init__(self, num_boiler):
        self.num = num_boiler
        self.pwr = 2.7
        self.kpd = 0.935
        self.load = 0
        self.status = False

    def start(self):
        """Запуск котла"""
        if not self.status:
            self.status = True
            return f'Котел-утилизатор {self.num} запущен.'
        return f'Котел-утилизатор {self.num} уже запущен.'

    def stop(self):
        """Останов котла"""
        if self.status:
            self.status = False
            return f'Котел-утилизатор {self.num} остановлен.'
            
        return f'Котел-утилизатор {self.num} уже остановлен.'

    def load_b(self, load_boil):
        """Изменение загрузки котла"""
        self.load = load_boil
        
        return f'Уровень загрузки котла {self.num}: {self.load} %'

    
    def heat_otpt(self):
        """генерируемая тепловая мощность от процента загрузки котла, Гкал

        load - загрузка котла, % """

        if self.load > 100:
            self.load = 100
        elif self.load < 0:
            self.load = 0
            
        heat = 0
        if self.status:
            heat = float(format(
                                (self.pwr * self.load/100), '.3f'
                                )
                        )
        return heat
        
    def gas_cons(self):
        """Потребление газа котлом, м3/ч"""
        cons = 0
        gas_cal_val = 0.01075 # теплотворная способность газа, Гкал/м3
        
        if self.status:
            cons = float(format(
                                ((self.heat_otpt()/gas_cal_val)/self.kpd), '.3f'
                                )
                        )
        return cons

    def __str__(self):
        return f'''Номер котла: {self.num}
        Номинальная мощность: {self.pwr}
        Уровень загрузки: {self.load} % / {self.heat_otpt()} Гкал
        Состояние вкл/выкл: {self.status}
        '''
    

def heat_from_temp(temp):
    """ Функция потребности тепла в зависимости от отрицательной температуры воздуха 
    temp - температура воздуха"""

    """Функция должна срабатывать, когда среднесуточная температура 
    на улице держится ниже +8 °C в течение 5 дней подряд"""
    heat_need = 0
    
    if temp < 8:
        # кубическая регрессия от x: 0 -10 -24 -38 -48; y: 1.126 2.345 5.63 8.914 11.26;
        heat_need = float(format(
                                (0.00006180 * temp ** 3 + 0.00559107 * temp ** 2 - 0.08512969 * temp + 1.09309420), '.3f'
                                )
                         )
    
    return heat_need

def heat_load_distribution(ht_fr_dist):
    """Функция распределяет выработку тепла между работающими котлами.
    
    quant_boiler - количество работающих котлов
    ht_fr_dist - тепло, подлежащее распределению (из выхода ф-ии heat_from_temp)"""

    quant_boiler = 6
    load = float(format(
                        (((ht_fr_dist / quant_boiler) / 2.7) * 100), '.3f'
                        )
                )

    if load < 45.0: 
        while load < 45.0:
            quant_boiler = quant_boiler - 1
            
            if quant_boiler != 1:
                load = float(format(
                                    (((ht_fr_dist / quant_boiler) / 2.7) * 100), '.3f'
                                    )
                            )
            else:
                break

    if ht_fr_dist == 0:
        load = 0
        quant_boiler = 0
        
    return load, quant_boiler

def heat_cost(boilers):
    """Функция стоимости газа, руб/ч"""

    """boilers - массив работающих котлов
    
    gas_cons - значения метода gas_cons от каждого котла)"""
    gas_cons = []
    for boiler in boilers:
        gas_cons.append( boiler.gas_cons() )
    
    price = 43 # руб/м3
    cost = sum(gas_cons) * price
    return cost

# Инициализация котлов
boilers = [UtilizationBoiler(i) for i in range(6)]
for boiler in boilers:
    print(boiler)

"""Входные данные"""
temp = [-28.1 -27.3 -21.6 -14.9 -5.4 6.1 13.7 10.8 3.9 -8.3 -20.5 -24.7] # Температура окружающей среды

heat_need = heat_from_temp(temp) # Потребность в тепле
print(f'Потребность в тепле: {heat_need} Гкал/ч')

load_val = heat_load_distribution( heat_need )[0]
print(f'Загрузка одного котла: {load_val} %')

num_boilers_must_on = heat_load_distribution( heat_need )[1] # Число котлов, которые должны быть запущены
print(f'Должно быть запущено котлов: {num_boilers_must_on}')

# Вкл нужного количества котлов
n_boil_on = 6 - num_boilers_must_on

for boiler in boilers:
    if boiler.num > n_boil_on - 1:
        print(boiler.start())
    if boiler.num < n_boil_on - 1:
        if not boiler.status:
            print(boiler.stop())

# Передача нужного значения загрузки котлу
for boiler in boilers:
    if boiler.status:
        load = boiler.load_b(load_val)
        print(load)

print(f'Стоимость газа: {heat_cost(boilers)} руб/ч')

# Вывод информации о каждом котле после расчета
for boiler in boilers:
    print(boiler)