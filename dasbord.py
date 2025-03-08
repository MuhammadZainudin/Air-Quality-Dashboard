import streamlit as st
import pandas as pd
import numpy as np
import requests
import zipfile
import io
import os
import matplotlib.pyplot as plt
import seaborn as sns


# --- Fungsi untuk Mengunduh dan Membaca Dataset ---
@st.cache_data
def load_data():
    url = "https://github.com/MuhammadZainudin/Air-Quality-Dataset/archive/refs/heads/main.zip"
    response = requests.get(url)

    # Ekstrak ZIP ke dalam memori
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    zip_file.extractall("air_quality_dataset")

    # Pastikan foldernya sesuai
    folder_path = "air_quality_dataset/Air-Quality-Dataset-main"
    all_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    df_list = []
    for file in all_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        df['station'] = file.replace('.csv', '')  # Tambahkan kolom nama stasiun
        df_list.append(df)

    # Gabungkan semua data menjadi satu dataframe
    df = pd.concat(df_list, ignore_index=True)

    # Buat kolom datetime
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    df['month_year'] = df['datetime'].dt.to_period('M')  # Format Tahun-Bulan

    return df


# --- Load Data ---
st.title("📊 Dashboard Analisis Polusi Udara")
st.sidebar.header("⚙️ Pengaturan")
df = load_data()

# --- Pilihan Stasiun ---
stations = df['station'].unique()
selected_station = st.sidebar.selectbox("Pilih Stasiun", stations)

# --- Visualisasi Tren PM2.5 dengan Bar Chart ---
st.subheader("📊 Tren Bulanan PM2.5 di Berbagai Lokasi (Bar Chart)")

# Daftar warna yang akan digunakan
colors = ["#E6194B", "#3CB44B", "#0082C8", "#FFE119", "#911EB4", "#F58231",
          "#46F0F0", "#F032E6", "#BFEF45", "#800000", "#A9A9A9", "#000000"]

# Buat daftar bulan-tahun unik sebagai label sumbu X
month_labels = df['month_year'].astype(str).unique()
x_pos = np.arange(len(month_labels))  # Posisi X untuk bar

plt.figure(figsize=(14, 7))
bar_width = 0.1  # Lebar setiap batang
num_locations = len(stations)  # Jumlah lokasi unik

# Loop setiap lokasi dengan warna unik
for idx, location in enumerate(stations):
    subset = df[df['station'] == location]

    # Ambil hanya bagian ketiga dari nama lokasi (jika ada)
    location_parts = location.split('_')
    location_name = location_parts[2] if len(location_parts) >= 3 else location

    # Hitung rata-rata PM2.5 per bulan
    monthly_avg = subset.resample('M', on='datetime')['PM2.5'].mean().fillna(0)

    # Pastikan warna tidak melebihi daftar
    color = colors[idx % len(colors)]

    # Buat bar chart
    plt.bar(x_pos + (idx * bar_width), monthly_avg.values, bar_width, label=location_name, color=color, alpha=0.8)

# Pengaturan visualisasi
plt.xticks(x_pos + (num_locations * bar_width) / 2, month_labels, rotation=45)  # Label sumbu X
plt.xlabel('Bulan-Tahun', fontsize=12)
plt.ylabel('Konsentrasi PM2.5', fontsize=12)
plt.title('Tren Bulanan PM2.5 di Berbagai Lokasi (Bar Chart)', fontsize=14, fontweight='bold')
plt.legend(title="Lokasi", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(axis='y', linestyle='--', alpha=0.5)  # Tambahkan garis bantu

plt.tight_layout()  # Rapikan tata letak
st.pyplot(plt)

# --- Heatmap Periode Risiko Tinggi ---
st.subheader("🔥 Heatmap Polusi Udara Berdasarkan Jam dan Hari")
df['dayofweek'] = df['datetime'].dt.day_name()
pivot_table = df.pivot_table(values='PM2.5', index='hour', columns='dayofweek', aggfunc='mean')

plt.figure(figsize=(12, 6))
sns.heatmap(pivot_table, cmap='YlOrRd', annot=False)
plt.title('Polusi PM2.5 Berdasarkan Jam dan Hari dalam Seminggu')
st.pyplot(plt)

# --- Scatter Plot Hubungan Polusi & Cuaca ---
st.subheader("🌦️ Hubungan PM2.5 dengan Suhu")
plt.figure(figsize=(10, 5))
sns.scatterplot(data=df, x='TEMP', y='PM2.5', alpha=0.5)
plt.title('Hubungan Suhu dan PM2.5')
plt.xlabel('Suhu (°C)')
plt.ylabel('PM2.5')
st.pyplot(plt)

# --- Menampilkan Dataframe ---
st.subheader("🗂️ Data Polusi Udara")
st.write(df.head())
