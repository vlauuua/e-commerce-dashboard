# E-Commerce Public Dataset Analysis

## Deskripsi Proyek

Proyek ini merupakan analisis data terhadap Brazilian E-Commerce Public Dataset (Olist) untuk memahami performa penjualan, kategori produk, kinerja pengiriman, serta karakteristik pelanggan.

Analisis dilakukan menggunakan Python dengan tahapan data gathering, assessing, cleaning, exploratory data analysis (EDA), dan visualisasi data. Hasil analisis kemudian disajikan melalui dashboard interaktif menggunakan Streamlit.

## Business Questions

Analisis ini berfokus pada beberapa pertanyaan bisnis berikut:

1. Bagaimana tren total pendapatan penjualan dan jumlah pesanan setiap bulan selama periode September 2016 hingga September 2018?
2. Kategori produk apa yang menghasilkan total pendapatan dan jumlah penjualan tertinggi selama periode tersebut?
3. Berapa jumlah dan persentase pesanan yang berhasil dikirim tepat waktu selama periode tersebut?

Selain itu, dilakukan **Customer Segmentation Using RFM Analysis** untuk mengidentifikasi karakteristik pelanggan berdasarkan Recency, Frequency, dan Monetary.

## Dataset

Dataset yang digunakan adalah Brazilian E-Commerce Public Dataset dari Olist.

Dataset yang digunakan meliputi:

- `orders_dataset.csv`
- `order_items_dataset.csv`
- `products_dataset.csv`
- `product_category_name_translation.csv`
- `customers_dataset.csv`

Periode data transaksi yang dianalisis: **4 September 2016 – 3 September 2018**.

## Tools & Technologies

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Plotly
- Streamlit
- Jupyter Notebook

## How to Run the Dashboard

### 1. Clone Repository

```bash
git clone <repository-url>
```

### 2. Masuk ke Folder Proyek

```bash
cd AnalisisData_Vlaura
```

### 3. Install Dependencies

```bash
python -m pip install -r requirement.txt
```

### 4. Run Streamlit Dashboard

```bash
python -m streamlit run dashboard/dashboard.py
```

## Author

**Vlaura**

Data Analysis Project – Dicoding x Asah
