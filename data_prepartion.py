import pandas as pd
import seaborn as see
from matplotlib import pyplot as plt
import sys
from dateutil import parser
import openpyxl as op

# dataframes that i used in analysis
"""
df_ciselniky ... tabulka ID_komponenty a jeji porizovaci ceny
df_kusovnik ... kusovnik ID_vyrobku a ID_komponenty ze kterych se sklada --> mapovaci tabulka
df_vyroba ... informace kdy byl vyroben jaky artikl (sortimentu)
df_dodavky ... list dodavek od dodavatelu
"""

def get_csv_data(sheet):
	csv_data = []
	for row in sheet.iter_rows(values_only=True):
		row_list = []
		for element in row[0].split(';'):
			row_list.append(element)
		csv_data.append(row_list)
	return csv_data

def date_parser(date_string):
    try:
        return parser.parse(date_string, dayfirst=True)
    except ValueError:
        raise Exception("We still have a problem")

#reading excel file
excel_file = 'logio.xlsx'

#creating df_ciselnky and df_kusovnik dataframe
df_ciselniky = pd.read_excel(excel_file, sheet_name='ciselniky',usecols='G:H', skiprows=1)
df_kusovnik = pd.read_excel(excel_file, sheet_name='matice_vyroby')

# extracting manufacturing data from csv_excel file
wb = op.load_workbook(excel_file)
sheet = wb['vyroba_text']

#creating data frame vyroba
csv_data = get_csv_data(sheet)
df_vyroba = pd.DataFrame(csv_data[1:], columns=csv_data[0])
# Converting datatypes (daful is object)
df_vyroba['Datum'] = df_vyroba['Datum'].apply(date_parser)
df_vyroba['Mnozstvi'] = pd.to_numeric(df_vyroba['Mnozstvi'],).astype('Int64')
# Adding colum 'mesic;
df_vyroba['Mesic'] = df_vyroba['Datum'].dt.month
df_vyroba['Rok'] = df_vyroba['Datum'].dt.year
df_vyroba['Rok-Mesic'] = df_vyroba['Datum'].dt.strftime('%Y-%m')


# zpozdene dodavky
df_dodavky = pd.read_excel(excel_file, sheet_name='dodavky')
df_dodavky['Zpozdeno'] = (df_dodavky['Datum_dodani'] - df_dodavky['Datum_objednani']).dt.days.apply(lambda x: x > 7)
df_dodavky['Deadline'] = (df_dodavky['Datum_objednani'] + pd.Timedelta(days=7))
df_dodavky.shape
df_dodavky.sample(10)

# tovarny -- kod tovarny a jeji lokalite
df_tovarny = pd.read_excel(excel_file, sheet_name='ciselniky', usecols='A:B', skiprows=1, nrows=3)