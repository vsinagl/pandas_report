import streamlit as st
import seaborn as see
from matplotlib import pyplot as plt
import pandas as pd

from data_prepartion import df_ciselniky, df_kusovnik, df_vyroba, df_dodavky, df_tovarny

predstaveni = """
Firma XY v oblasti automotive nás požádala o analýzu její činnosti.
Firma má k dispozici 3 výrobní závody rozmístěné po ČR: - závod v Přerově, - závod v Plzni, - závod v Ostravě. V každém závodě se vyrábí a každý závod má svůj vlastní sklad, příp. více skladů.
Firma se zabývá výrobou náhradních dílů pro automobily. Jednotlivé náhradní díly se vyrábí z více komponent.
Firma odebírá jednotlivé komponenty od 4 různých dodavatelů. Každý dodavatel garantuje dodací lhůtu 7 dnů.
"""
md_naklady_na_dil = """
1) příprava dat pro analýzu nákladů na výrobu jednotlivých náhradních dílů:
```python
#creating df_ciselnky and df_kusovnik dataframe
df_ciselniky = pd.read_excel(excel_file, sheet_name='ciselniky',usecols='G:H', skiprows=1)
df_kusovnik = pd.read_excel(excel_file, sheet_name='matice_vyroby')
```
2) spojení tabulek ciselniky a matice výroby + přídání částečného součtu nákladů komponent:
```python
df_naklady = pd.merge(df_kusovnik, df_ciselniky, how="left", on = "ID_komponenty")
df_naklady['Celkova_cena_komponenty'] = df_naklady['Mnozstvi'] * df_naklady['Porizovaci_cena']
```
"""
md_naklady_na_dil2 = """
3) groupby funkce a agregace pro celkovou cenu komponenty:
```python
df_naklady.groupby('ID_produktu')[['Mnozstvi', 'Celkova_cena_komponenty']].sum().reset_index()
```

"""

last_task = """
4) Statisticky zpracovat transporty od dodavatelů:
- počet dodávek od každého dodavatele,
- jaké množství firma odebírá od jakého dodavatele, 
- průměrnou délku zpožděných objednávek na celku
- směrodatná odchylka délky zpožděných objednávek na celku
- průměrná délka zpoždění u zpožděných objednávek
- směrodatná odchylka zpoždění u zpožděných objednávek
"""

st.title("Příklad výrobní firmy, zpracování a analýza dat, test Logio s.r.o." )
st.write(" K testu lze přistupovat různě. Není nezbytně nutné dosáhnout u jednotlivých úkolů kompletního řešení, ale lze prezentovat myšlenku postupu k dosažení řešení.")
st.title("Zadání")
with st.popover("Zobrazit zadání"):
	st.write(predstaveni)
	st.title("Cíl analýzy")
	st.write("1) Stanovit náklady na výrobu jednotlivých náhradních dílů. ")
	st.write("2) Zobrazit vývoj výroby za poslední rok po měsících v jednotlivých závodech.")
	st.write("3) Označit, jaké dodávky od dodavatele dorazily se zpožděním.")
	st.write(last_task)

st.title("Řešení 🔍")


#Náklady na výrobu jednotlivých náhradních dílů
st.subheader("Náklady na výrobu jednotlivých náhradních dílů", divider="gray")
df_naklady = pd.merge(df_kusovnik, df_ciselniky, how="left", on = "ID_komponenty")
st.subheader("Předpříprava dat")
st.markdown(md_naklady_na_dil)
df_naklady['Celkova_cena_komponenty'] = df_naklady['Mnozstvi'] * df_naklady['Porizovaci_cena']
st.dataframe(df_naklady)
st.markdown(md_naklady_na_dil2)
st.dataframe(df_naklady.groupby('ID_produktu')[['Mnozstvi', 'Celkova_cena_komponenty']].sum().reset_index())


#Vývoj výroby za poslední rok po měsících v jednotlivých závodech
st.subheader("Vývoj výroby za poslední rok po měsících v jednotlivých závodech", divider="gray")
st.markdown("""
	1. příprava dat - tabulka výroba:
```python



# extracting manufacturing data from csv_excel file
wb = op.load_workbook(excel_file)
sheet = wb['vyroba_text']

#creating data frame vyroba
csv_data = get_csv_data(sheet)
df_vyroba = pd.DataFrame(csv_data[1:], columns=csv_data[0])
```
jelikož data byla ve formátu csv, bylo nutné je přeformátovat do tabulky. K tomu jsem použil custom funkce která vytvořila list listů, kde každý list obsahoval jeden řádek z csv souboru.

```python
def get_csv_data(sheet):
	csv_data = []
	for row in sheet.iter_rows(values_only=True):
		row_list = []
		for element in row[0].split(';'):
			row_list.append(element)
		csv_data.append(row_list)
	return csv_data
```
2. přidání sloupce 'Rok-Mesic' a převedení dat do formátu datetime

```python
# Converting datatypes (default is object)
df_vyroba['Datum'] = df_vyroba['Datum'].apply(date_parser)
df_vyroba['Mnozstvi'] = pd.to_numeric(df_vyroba['Mnozstvi'],).astype('Int64')
# Adding colum 'mesic;
df_vyroba['Mesic'] = df_vyroba['Datum'].dt.month
df_vyroba['Rok'] = df_vyroba['Datum'].dt.year
df_vyroba['Rok-Mesic'] = df_vyroba['Datum'].dt.strftime('%Y-%m')
```

3. grouby (ID_zavodu, Rok-mesic) --> unikátní záznamy pro měsíc a danou továrnum aggregace množství vyrobených dílů pro danouu továrnu
```python
df_vyroba_mesice = df_vyroba.groupby(['ID_zavodu', 'Rok', 'Rok-Mesic'])['Mnozstvi'].sum().reset_index()
df_vyroba_mesice_tovarny = pd.merge(df_vyroba_mesice, df_tovarny, on="ID_zavodu", how="left")
```
4. join s číselníky --> pro název továrny dle lokality
"""
)

df_vyroba_mesice = df_vyroba.groupby(['ID_zavodu', 'Rok', 'Rok-Mesic'])['Mnozstvi'].sum().reset_index()
df_vyroba_mesice_tovarny = pd.merge(df_vyroba_mesice, df_tovarny, on="ID_zavodu", how="left")
st.dataframe(df_vyroba_mesice_tovarny[['ID_zavodu', 'Místo', 'Rok-Mesic', 'Mnozstvi']])

st.subheader("Celková výroba po měsících ve všech závodech")
st.line_chart(data = df_vyroba.groupby('Rok-Mesic')['Mnozstvi'].sum().reset_index(),
					 x='Rok-Mesic', y = 'Mnozstvi')
st.subheader("Celková výroba po měsících v jednotlivých závodech")
# creating seaborn plot

#roky = st.slider("Select a range of values", 2015, 2020, (2017, 2018))
#fig1 = see.lineplot(data=df_vyroba_mesice_tovarny.query("(Rok >= @roky[0]) & (Rok <= @roky[1])"), x='Rok-Mesic', y = 'Mnozstvi', hue = "ID_zavodu")
fig1, ax = plt.subplots(figsize=(10, 5))
fig1s = see.lineplot(data=df_vyroba_mesice_tovarny, x='Rok-Mesic', y = 'Mnozstvi', hue = "ID_zavodu", ax=ax)
#fig1.set_xticklabels(rotation=45, ha='right')
ax.set_title('Výroba po měsících - závody')
ax.set_ylabel('Počet vyrobených dílů')
ax.set_xlabel('Datum [rok-měsíc]')
ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels
st.pyplot(fig1)

#Zpožděné dodávky

st.subheader("Dodávky se zpožděním")
st.markdown("""
			1. Načtení dat z excelu do pandas dataframe
			2. Přidání sloupce 'Zpozdeno', 'Deadline' a 'Dodaci_doba'
```python
df_dodavky['Zpozdeno'] = (df_dodavky['Datum_dodani'] - df_dodavky['Datum_objednani']).dt.days.apply(lambda x: x > 7)
df_dodavky['Deadline'] = (df_dodavky['Datum_objednani'] + pd.Timedelta(days=7))
df_dodavky['Dodaci_doba'] = df_dodavky['Datum_dodani'] - df_dodavky['Datum_objednani']
df_dodavky_zpozdene = df_dodavky.query('Zpozdeno == True')
```
""")
df_dodavky['Dodaci_doba'] =  df_dodavky['Datum_dodani'] - df_dodavky['Datum_objednani']
df_dodavky_zpozdene = df_dodavky.query('Zpozdeno == True')

with st.container(border=True):
	st.write(f"Časové období: {df_dodavky['Datum_objednani'].min()} {df_dodavky['Datum_objednani'].max()}")
	st.write("Celkový počet dodávek v datasetu: ", len(df_dodavky))
	st.write("Celkový počet zpožděných dodávek v datasetu: ", len(df_dodavky_zpozdene))
	st.write("% Zpožděných dodávek: ", f"{(1 - (len(df_dodavky) - len(df_dodavky_zpozdene)) / len(df_dodavky)) * 100:.2f}")

st.dataframe(df_dodavky_zpozdene)


st.subheader('Počet dodávek od dodavetele a počet zpožděných dodávek')
st.markdown("""
```python
df_dodavky.groupby('ID_dodavatele')['ID_komponenty'].count().reset_index(name='Pocet objednavek')
df_dodavky_zpozdene.groupby('ID_dodavatele').size().reset_index(name= 'Pocet_zpozdenych_objednavek')
```
			 """)
st.dataframe(df_dodavky.groupby('ID_dodavatele')['ID_komponenty'].count().reset_index(name='Pocet objednavek'))
st.dataframe(df_dodavky_zpozdene.groupby('ID_dodavatele').size().reset_index(name= 'Pocet_zpozdenych_objednavek'))

st.subheader('Počet náhradních dílů od každého dodavatele')
st.markdown("""
```python
df_dodavky.groupby('ID_dodavatele')['Mnozstvi'].sum().reset_index(name='Celkove_mnozstvi')
```
""")
st.dataframe(df_dodavky.groupby('ID_dodavatele')['Mnozstvi'].sum().reset_index(name='Celkove_mnozstvi'))

st.subheader('Statistický popis zpoždění')
st.markdown("""
```python
st.dataframe(df_dodavky_zpozdene['Dodaci_doba'].describe())
```
""")
st.dataframe(df_dodavky_zpozdene['Dodaci_doba'].describe())





