import pandas as pd
import os
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

def clean_html_tags(df): # додаткове завдання
    for column in df.columns:
        df[column] = df[column].astype(str).str.replace(r'<.*?>', '', regex=True)
    return df

def download_vhi_data(SAVE_DIR):
    columns = ["Year", "Week", "SMN", "SMT", "VCI", "TCI", "VHI", "empty"]
    all_data = []
    
    csv_files = filter(lambda x: x.endswith('.csv'), os.listdir(SAVE_DIR))
    
    for file_name in csv_files:
        file_path = os.path.join(SAVE_DIR, file_name)
        print(file_path)
        
        df = pd.read_csv(file_path, header=1, names=columns, index_col=False)
        df = clean_html_tags(df)
        df = df.drop(df.loc[df['VHI'] == -1].index)
        df = df.drop("empty", axis=1)
        df = df.drop(df.index[-1])
        
        try:
            province_id = int(file_name.split('_')[2])
        except (IndexError, ValueError):
            print(f"Невірний формат імені файлу: {file_name}. Пропускаємо файл.")
            continue
        
        df['province_id'] = province_id
        
        all_data.append(df)
    
    df_res = pd.concat(all_data, ignore_index=True)
    df_res['Week'] = pd.to_numeric(df_res['Week'], errors='coerce').fillna(0).astype(int)
    df_res['province_id'] = df_res['province_id'].astype(int)
    df_res['Year'] = df_res['Year'].astype(int)
    df_res["VCI"] = pd.to_numeric(df_res["VCI"], errors='coerce')
    df_res["TCI"] = pd.to_numeric(df_res["TCI"], errors='coerce')
    df_res["VHI"] = pd.to_numeric(df_res["VHI"], errors='coerce')
    df_res = df_res.sort_values(by=['province_id', 'Year', 'Week']).reset_index(drop=True)
    return df_res

SAVE_DIR = "/home/iulia/lab2"  
df = download_vhi_data(SAVE_DIR)

def reset_filters():
    st.session_state.clear()
    st.session_state['indicator'] = 'VCI'
    st.session_state['selected_province'] = df['province_id'].unique()[0]
    st.session_state['week_range'] = (1, 52)
    st.session_state['year_range'] = (1997, 2025)
    st.session_state['sort_option'] = "Без сортування"
    st.rerun()

if 'indicator' not in st.session_state:
    st.session_state['indicator'] = 'VCI'
    st.session_state['selected_province'] = df['province_id'].unique()[0]
    st.session_state['week_range'] = (1, 52)
    st.session_state['year_range'] =  (1997, 2025)
    st.session_state['sort_option'] = "Без сортування"

st.sidebar.header("Фільтри")
indicator = st.sidebar.selectbox("Оберіть показник", ["VCI", "TCI", "VHI"], key='indicator')
selected_province = st.sidebar.selectbox("Оберіть область", df['province_id'].unique(), key='selected_province')
week_range = st.sidebar.slider("Виберіть інтервал тижнів", 1, 52, st.session_state['week_range'], key='week_range')
year_range = st.sidebar.slider("Виберіть інтервал років", 1997, 2025, st.session_state['year_range'], key='year_range')

if st.sidebar.button("Скинути фільтри"):
    reset_filters()

filtered_data = df[(df['Year'].between(*year_range)) & 
                   (df['Week'].between(*week_range)) & 
                   (df['province_id'] == selected_province)]

grown = st.checkbox("Сортувати за зростанням")
decline = st.checkbox("Сортувати за спаданням")

if grown and decline:
    st.error("Ви можете обрати тільки один варіант сортування.")
elif grown:
    sorted_data = filtered_data.sort_values(by=indicator, ascending=True)
    st.write("Дані відсортовані за зростанням:")
    st.write(sorted_data)
elif decline:
    sorted_data = filtered_data.sort_values(by=indicator, ascending=False)
    st.write("Дані відсортовані за спаданням:")
    st.write(sorted_data)
else:
    st.write("Дані без сортування:")
    

tab1, tab2, tab3 = st.tabs(["Таблиця", "Графік", "Теплова карта"])

with tab1:
    st.write("Таблиця з відфільтрованими даними")
    st.dataframe(filtered_data)

with tab2:
    st.write(f"Графік {indicator} для області {selected_province}")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(x='Week', y=indicator, data=filtered_data, hue='Year', ax=ax)
    ax.set_xlabel("Тиждень")
    ax.set_ylabel(indicator)
    st.pyplot(fig)

with tab3:
    st.write(f"Теплова карта {indicator}")
    pivot_table = filtered_data.pivot(index="Year", columns="Week", values=indicator, annot = True)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot_table, cmap="YlGnBu", linewidths=0.5, ax=ax)
    st.pyplot(fig)

    st.write(f"Порівняння {indicator} для {selected_province}")
    comparison = df.groupby('province_id')[indicator].mean().sort_values()
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    comparison.plot(kind='bar', ax=ax2)
    ax2.set_title(f'Порівняння середніх значень {indicator} по областях')
    ax2.set_xlabel('Код області')
    ax2.set_ylabel(f'Середнє значення {indicator}')
    st.pyplot(fig2)




