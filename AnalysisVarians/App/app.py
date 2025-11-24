import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Aplikasi Akuntansi Sederhana",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Aplikasi Akuntansi Sederhana")
st.write("Aplikasi untuk mengelola keuangan pribadi atau bisnis kecil")

# Session state untuk menyimpan data
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

if 'categories' not in st.session_state:
    st.session_state.categories = ["Makanan", "Transportasi", "Belanja", "Hiburan", "Gaji", "Lainnya"]

# ===== SIDEBAR =====
with st.sidebar:
    st.header("➕ Tambah Transaksi Baru")
    
    date = st.date_input("Tanggal")
    type_transaction = st.radio("Jenis Transaksi", ["Pemasukan", "Pengeluaran"])
    category = st.selectbox("Kategori", st.session_state.categories)
    amount = st.number_input("Jumlah (Rp)", min_value=0, step=1000)
    description = st.text_input("Keterangan")
    
    if st.button("Simpan Transaksi"):
        if amount > 0:
            new_transaction = {
                'Tanggal': date,
                'Jenis': type_transaction,
                'Kategori': category,
                'Jumlah': amount,
                'Keterangan': description
            }
            st.session_state.transactions.append(new_transaction)
            st.success("Transaksi berhasil disimpan!")
        else:
            st.error("Jumlah harus lebih dari 0")

# ===== MAIN CONTENT =====

# Hitung summary
if st.session_state.transactions:
    df = pd.DataFrame(st.session_state.transactions)
    
    # Summary cards
    total_income = df[df['Jenis'] == 'Pemasukan']['Jumlah'].sum()
    total_expense = df[df['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
    balance = total_income - total_expense
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Pemasukan", f"Rp {total_income:,}")
    
    with col2:
        st.metric("Total Pengeluaran", f"Rp {total_expense:,}")
    
    with col3:
        st.metric("Saldo", f"Rp {balance:,}", delta=f"Rp {balance:,}")

    # Tampilkan data transaksi
    st.subheader("📋 Daftar Transaksi")
    st.dataframe(df, use_container_width=True)
    
    # Download data
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Data CSV",
        data=csv,
        file_name="laporan_keuangan.csv",
        mime="text/csv"
    )

    # Visualisasi sederhana
    st.subheader("📊 Grafik Keuangan")
    
    # Grafik pemasukan vs pengeluaran
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Pemasukan per Kategori**")
        income_by_category = df[df['Jenis'] == 'Pemasukan'].groupby('Kategori')['Jumlah'].sum()
        if not income_by_category.empty:
            st.bar_chart(income_by_category)
        else:
            st.info("Belum ada data pemasukan")
    
    with col2:
        st.write("**Pengeluaran per Kategori**")
        expense_by_category = df[df['Jenis'] == 'Pengeluaran'].groupby('Kategori')['Jumlah'].sum()
        if not expense_by_category.empty:
            st.bar_chart(expense_by_category)
        else:
            st.info("Belum ada data pengeluaran")
    
    # Grafik trend bulanan
    st.write("**Trend Bulanan**")
    df['Bulan'] = pd.to_datetime(df['Tanggal']).dt.to_period('M')
    monthly_data = df.groupby(['Bulan', 'Jenis'])['Jumlah'].sum().unstack(fill_value=0)
    if not monthly_data.empty:
        st.line_chart(monthly_data)
    
    # Analisis sederhana
    st.subheader("📈 Analisis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Top 5 Pengeluaran Tertinggi**")
        top_expenses = df[df['Jenis'] == 'Pengeluaran'].nlargest(5, 'Jumlah')[['Kategori', 'Jumlah', 'Keterangan']]
        st.dataframe(top_expenses)
    
    with col2:
        st.write("**Kategori Pengeluaran Terbesar**")
        category_expenses = df[df['Jenis'] == 'Pengeluaran'].groupby('Kategori')['Jumlah'].sum().nlargest(5)
        st.dataframe(category_expenses)

else:
    st.info("💡 Belum ada transaksi. Silakan tambah transaksi di sidebar!")

# ===== FITUR TAMBAHAN =====
with st.expander("⚙️ Pengaturan"):
    st.subheader("Kelola Kategori")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_category = st.text_input("Tambah Kategori Baru")
        if st.button("Tambah Kategori") and new_category:
            if new_category not in st.session_state.categories:
                st.session_state.categories.append(new_category)
                st.success(f"Kategori '{new_category}' berhasil ditambah!")
            else:
                st.error("Kategori sudah ada")
    
    with col2:
        category_to_delete = st.selectbox("Hapus Kategori", st.session_state.categories)
        if st.button("Hapus Kategori"):
            st.session_state.categories.remove(category_to_delete)
            st.success(f"Kategori '{category_to_delete}' berhasil dihapus!")
    
    st.subheader("Reset Data")
    if st.button("🗑️ Hapus Semua Data"):
        st.session_state.transactions = []
        st.success("Semua data berhasil dihapus!")
        st.rerun()

# ===== INSTRUKSI =====
with st.expander("❓ Cara Menggunakan"):
    st.markdown("""
    **Panduan Penggunaan:**
    
    1. **Tambah Transaksi**: Gunakan sidebar untuk menambah transaksi baru
    2. **Pilih Jenis**: Pemasukan atau Pengeluaran
    3. **Pilih Kategori**: Sesuaikan dengan jenis transaksi
    4. **Lihat Laporan**: Data akan otomatis terupdate di main content
    5. **Download Data**: Simpan data sebagai CSV untuk backup
    
    **Fitur:**
    - 📊 Grafik otomatis
    - 📈 Analisis pengeluaran
    - 📥 Export data
    - ⚙️ Kelola kategori
    """)
