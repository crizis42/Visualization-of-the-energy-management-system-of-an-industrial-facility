import pandas as pd
import numpy as np
from datetime import datetime

gas_path = 'Excel/3_Стоимость_СОГ.xlsx'

# Читаем данные
df = pd.read_excel(gas_path, sheet_name='Лист1', header=None)

# Определяем количество столбцов с данными (строка 2 начиная с колонки 1)
last_col = df.loc[2, 1:].last_valid_index()  # Последняя не пустая колонка

# Получаем месяцы и цены
months = df.loc[0, 1:last_col].to_numpy()
gas_prices = df.loc[2, 1:last_col].to_numpy()

# Текущая дата
now = datetime.now()
current_month = now.month
current_year = 2024

# Получение цены
price = None
def price_calc(current_year, current_month, months, gas_prices, price):
  if current_year == 2024:
      if current_month <= len(gas_prices):
          price = gas_prices[current_month - 1]
          print(f'Стоимость газа за {current_month}.{current_year} = {price/1000} руб/тыс.м3')
      else:
          print('Нет данных на этот месяц')
  elif current_year == 2025:
      price = gas_prices[15]
      print(f'Стоимость газа за {current_month}.{current_year} = {price/1000} руб/тыс.м3')
  elif current_year == 2026:
      price = gas_prices[16]
      print(f'Стоимость газа за {current_month}.{current_year} = {price/1000} руб/тыс.м3')
  else:
      print('Нет данных на этот год')

price_calc(current_year, current_month, months, gas_prices, price)