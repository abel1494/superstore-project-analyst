import streamlit as st
import pandas as pd
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard Penjualan Superstore",
    page_icon="📈",
    layout="wide"
)

# --- FUNGSI UNTUK MEMUAT DATA (DENGAN CACHING) ---
@st.cache_data
def load_data(file_path):
    """
    Fungsi untuk memuat data dari file CSV dan memastikan kolom tanggal
    dikonversi ke tipe datetime.
    """
    df = pd.read_csv(file_path)
    # Konversi kolom tanggal ke datetime, abaikan error jika format tidak cocok
    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    return df

# Muat data dari file CSV yang sudah final
# Pastikan nama file ini sama dengan yang kamu unduh dari Colab
df = load_data('superstore_cleaned.csv')

# --- JUDUL DASHBOARD ---
st.title("📈 Dashboard Analisis Penjualan Superstore")
st.markdown("---")

# --- SIDEBAR UNTUK FILTER ---
st.sidebar.header("Filter Data:")

# Filter Wilayah (Region)
region = st.sidebar.multiselect(
    "Pilih Wilayah:",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

# Filter Tanggal (Date Range)
min_date = df['Order Date'].min()
max_date = df['Order Date'].max()
start_date, end_date = st.sidebar.date_input(
    "Pilih Rentang Tanggal:",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# --- TERAPKAN FILTER KE DATAFRAME ---
# Filter berdasarkan tanggal DAN wilayah
df_selection = df[
    (df['Order Date'] >= pd.to_datetime(start_date)) &
    (df['Order Date'] <= pd.to_datetime(end_date)) &
    (df['Region'].isin(region))
]

# Cek jika dataframe kosong setelah filter untuk menghindari error
if df_selection.empty:
    st.warning("Tidak ada data yang tersedia untuk filter yang dipilih.")
    st.stop() # Hentikan eksekusi jika tidak ada data

# --- HALAMAN UTAMA ---

# 1. METRIK UTAMA (KPIs)
st.header("Metrik Utama")
total_sales = int(df_selection['Sales'].sum())
total_profit = int(df_selection['Profit'].sum())
total_orders = df_selection['Order ID'].nunique()
average_profit_margin = df_selection['Profit Margin'].mean()

# Tampilkan dalam 4 kolom
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Penjualan", f"${total_sales:,}")
col2.metric("Total Profit", f"${total_profit:,}")
col3.metric("Total Pesanan", f"{total_orders:,}")
col4.metric("Rata-rata Profit Margin", f"{average_profit_margin:.2f}%")

st.markdown("---")

# 2. GRAFIK-GRAFIK UTAMA
col1, col2 = st.columns(2)

with col1:
    st.subheader("Penjualan per Kategori")
    sales_by_category = df_selection.groupby('Category', as_index=False)['Sales'].sum().sort_values(by='Sales', ascending=False)
    fig_cat = px.bar(
        sales_by_category,
        x='Category',
        y='Sales',
        title="<b>Penjualan berdasarkan Kategori Produk</b>",
        color_discrete_sequence=["#0083B8"] * len(sales_by_category),
        template="plotly_white",
        labels={'Sales': 'Total Penjualan', 'Category': 'Kategori'}
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    st.subheader("Distribusi Profit per Kategori")
    profit_by_category = df_selection.groupby('Category')['Profit'].sum()
    fig_profit_cat = px.pie(
        profit_by_category,
        names=profit_by_category.index,
        values=profit_by_category.values,
        title="<b>Distribusi Profit per Kategori</b>",
        hole=.3
    )
    st.plotly_chart(fig_profit_cat, use_container_width=True)

st.markdown("---")

# 3. GRAFIK TREN DAN ANALISIS PROFIT MARGIN
st.subheader("Analisis Tren dan Profitabilitas")
# Grafik Tren Penjualan Time Series
sales_over_time = df_selection.set_index('Order Date').resample('M')['Sales'].sum()
fig_time = px.line(
    sales_over_time,
    x=sales_over_time.index,
    y=sales_over_time.values,
    title="<b>Tren Total Penjualan per Bulan</b>",
    template="plotly_white",
    labels={'y': 'Total Penjualan', 'x': 'Bulan'}
)
st.plotly_chart(fig_time, use_container_width=True)

# Grafik Profit Margin per Kategori
margin_by_category = df_selection.groupby('Category', as_index=False)['Profit Margin'].mean().sort_values(by='Profit Margin')
fig_margin = px.bar(
    margin_by_category,
    x='Profit Margin',
    y='Category',
    orientation='h',
    title="<b>Rata-rata Profit Margin berdasarkan Kategori Produk</b>",
    template="plotly_white",
    labels={'Profit Margin': 'Rata-rata Profit Margin (%)', 'Category': 'Kategori'}
)
st.plotly_chart(fig_margin, use_container_width=True)

# Menampilkan data mentah (opsional)
if st.checkbox("Tampilkan Data Mentah"):
    st.subheader("Data Mentah yang Difilter")
    st.write(df_selection)