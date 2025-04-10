import pandas as pd
import numpy
from datetime import datetime

gtu_path = 'Excel/2_Наработка_ГТЭС.xlsx'

# Читаем данные
gtu_data = pd.read_excel(gtu_path, sheet_name='Лист1', header=None)

last_col = gtu_data.columns[-1]
last_row = gtu_data.loc[3:,2].last_valid_index()
m_hours = gtu_data.loc[4:, last_col].to_numpy(dtype=float)
m_to_hours = numpy.where(m_hours > 1500, m_hours % 1500, m_hours)
m_kr_hours = numpy.where(m_hours > 10000, m_hours % 10000, m_hours)

m_hours = numpy.round(m_hours, 3)

print(last_row)
print(m_hours)
print(m_to_hours)
print(m_kr_hours)
print(11023.34%10000)

gtes = [i for i in range(len(m_hours))]
print(enumerate(gtes))