
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================
# 1. CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="E-Commerce Dashboard",
    layout="wide"
)

# Lokasi folder data
DATA_PATH = Path(__file__).resolve().parent.parent / "data"

st.title("E-Commerce Sales Dashboard")
st.caption("Brazilian E-Commerce Public Dataset | 2016 - 2018")


# ==========================================
# 2. LOAD DATA
# ==========================================

@st.cache_data
def load_data():

    orders = pd.read_csv(DATA_PATH / "orders_dataset.csv")
    items = pd.read_csv(DATA_PATH / "order_items_dataset.csv")
    products = pd.read_csv(DATA_PATH / "products_dataset.csv")
    translation = pd.read_csv(
        DATA_PATH / "product_category_name_translation.csv"
    )
    customers = pd.read_csv(DATA_PATH / "customers_dataset.csv")

    # Menggabungkan dataset
    df = orders.merge(items, on="order_id", how="inner")

    df = df.merge(
        products[["product_id", "product_category_name"]],
        on="product_id",
        how="left"
    )

    df = df.merge(
        translation,
        on="product_category_name",
        how="left"
    )

    df = df.merge(
        customers[["customer_id", "customer_unique_id"]],
        on="customer_id",
        how="left"
    )

    # Mengisi kategori yang kosong
    df["product_category_name_english"] = (
        df["product_category_name_english"].fillna("Unknown")
    )

    # Mengubah tipe data tanggal
    date_columns = [
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


try:
    df = load_data()

except FileNotFoundError:
    st.error("File CSV tidak ditemukan. Periksa kembali folder data.")
    st.stop()


# ==========================================
# 3. FILTER
# ==========================================

st.sidebar.header("Dashboard Filter")

# Filter tanggal
min_date = df["order_purchase_timestamp"].min().date()
max_date = df["order_purchase_timestamp"].max().date()

selected_date = st.sidebar.date_input(
    "Pilih Periode",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if not isinstance(selected_date, (tuple, list)) or len(selected_date) != 2:
    st.warning("Silakan pilih tanggal awal dan akhir.")
    st.stop()

start_date, end_date = selected_date

if start_date > end_date:
    st.error("Tanggal awal tidak boleh melebihi tanggal akhir.")
    st.stop()

# Filter kategori
category_list = sorted(
    df["product_category_name_english"].dropna().unique().tolist()
)

selected_category = st.sidebar.multiselect(
    "Pilih Kategori Produk",
    options=category_list,
    default=category_list
)

if not selected_category:
    st.warning("Pilih minimal satu kategori produk.")
    st.stop()

# Filter data berdasarkan tanggal dan kategori
filtered_df = df[
    (df["order_purchase_timestamp"].dt.date >= start_date) &
    (df["order_purchase_timestamp"].dt.date <= end_date) &
    (df["product_category_name_english"].isin(selected_category))
].copy()

if filtered_df.empty:
    st.warning("Tidak ada data pada filter yang dipilih.")
    st.stop()


# ==========================================
# 4. KEY PERFORMANCE INDICATORS
# ==========================================

st.header("Business Overview")

total_revenue = filtered_df["price"].sum()

total_orders = filtered_df["order_id"].nunique()

total_customers = filtered_df["customer_unique_id"].nunique()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Revenue",
    f"R$ {total_revenue:,.2f}"
)

col2.metric(
    "Total Orders",
    f"{total_orders:,}"
)

col3.metric(
    "Total Customers",
    f"{total_customers:,}"
)


# ==========================================
# 5. SALES PERFORMANCE
# ==========================================

st.divider()
st.header("1. Sales Performance")

monthly_sales = filtered_df.groupby(
    filtered_df["order_purchase_timestamp"].dt.to_period("M")
).agg(
    total_revenue=("price", "sum"),
    total_orders=("order_id", "nunique")
).reset_index()

monthly_sales["month"] = (
    monthly_sales["order_purchase_timestamp"].astype(str)
)

fig_sales = px.line(
    monthly_sales,
    x="month",
    y="total_revenue",
    markers=True,
    title="Monthly Revenue Trend",
    labels={
        "month": "Month",
        "total_revenue": "Revenue (R$)"
    }
)

fig_sales.update_layout(
    hovermode="x unified"
)

st.plotly_chart(fig_sales, use_container_width=True)

# Grafik jumlah pesanan
fig_orders = px.bar(
    monthly_sales,
    x="month",
    y="total_orders",
    text="total_orders",
    title="Monthly Orders Trend",
    labels={
        "month": "Month",
        "total_orders": "Number of Orders"
    }
)

st.plotly_chart(fig_orders, use_container_width=True)

with st.expander("View Monthly Sales Data"):
    st.dataframe(
        monthly_sales[["month", "total_revenue", "total_orders"]],
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 6. PRODUCT CATEGORY PERFORMANCE
# ==========================================

st.divider()
st.header("2. Product Category Performance")

category_sales = filtered_df[
    filtered_df["product_category_name_english"] != "Unknown"
].groupby("product_category_name_english").agg(
    total_revenue=("price", "sum"),
    total_sales=("product_id", "count")
).reset_index()

if not category_sales.empty:

    col1, col2 = st.columns(2)

    # Top 10 berdasarkan pendapatan
    top_revenue = category_sales.nlargest(
        10, "total_revenue"
    ).sort_values("total_revenue")

    with col1:

        fig_revenue = px.bar(
            top_revenue,
            x="total_revenue",
            y="product_category_name_english",
            orientation="h",
            title="Top 10 Categories by Revenue",
            labels={
                "total_revenue": "Revenue (R$)",
                "product_category_name_english": "Category"
            }
        )

        st.plotly_chart(
            fig_revenue,
            use_container_width=True
        )

    # Top 10 berdasarkan jumlah produk terjual
    top_sales = category_sales.nlargest(
        10, "total_sales"
    ).sort_values("total_sales")

    with col2:

        fig_quantity = px.bar(
            top_sales,
            x="total_sales",
            y="product_category_name_english",
            orientation="h",
            title="Top 10 Categories by Sales Quantity",
            labels={
                "total_sales": "Number of Products Sold",
                "product_category_name_english": "Category"
            }
        )

        st.plotly_chart(
            fig_quantity,
            use_container_width=True
        )

    with st.expander("View Category Data"):
        st.dataframe(
            category_sales.sort_values(
                "total_revenue", ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )

else:
    st.info("Tidak ada data kategori yang dapat ditampilkan.")


# ==========================================
# 7. DELIVERY PERFORMANCE
# ==========================================

st.divider()
st.header("3. Delivery Performance")

# Analisis pengiriman menggunakan seluruh kategori
delivery_df = df[
    (df["order_purchase_timestamp"].dt.date >= start_date) &
    (df["order_purchase_timestamp"].dt.date <= end_date)
].drop_duplicates(subset="order_id").copy()

# Hanya pesanan yang berhasil dikirim
delivery_df = delivery_df[
    (delivery_df["order_status"] == "delivered") &
    (delivery_df["order_delivered_customer_date"].notna()) &
    (delivery_df["order_estimated_delivery_date"].notna())
].copy()

if not delivery_df.empty:

    delivery_df["delivery_status"] = (
        delivery_df["order_delivered_customer_date"]
        <= delivery_df["order_estimated_delivery_date"]
    ).map({
        True: "On Time",
        False: "Late"
    })

    delivery_summary = (
        delivery_df["delivery_status"]
        .value_counts()
        .reset_index()
    )

    delivery_summary.columns = [
        "delivery_status",
        "total_orders"
    ]

    delivery_summary["percentage"] = (
        delivery_summary["total_orders"] /
        delivery_summary["total_orders"].sum() * 100
    )

    on_time = delivery_summary.loc[
        delivery_summary["delivery_status"] == "On Time",
        "percentage"
    ].sum()

    late = delivery_summary.loc[
        delivery_summary["delivery_status"] == "Late",
        "percentage"
    ].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("On-Time Delivery", f"{on_time:.2f}%")
    col2.metric("Late Delivery", f"{late:.2f}%")
    col3.metric("Delivered Orders", f"{len(delivery_df):,}")

    fig_delivery = px.pie(
        delivery_summary,
        names="delivery_status",
        values="total_orders",
        hole=0.5,
        title="On-Time vs Late Delivery"
    )

    fig_delivery.update_traces(
        textinfo="label+percent"
    )

    st.plotly_chart(
        fig_delivery,
        use_container_width=True
    )

    with st.expander("View Delivery Data"):
        st.dataframe(
            delivery_summary,
            use_container_width=True,
            hide_index=True
        )

else:
    st.warning("Tidak ada data pengiriman pada periode ini.")


# ==========================================
# 8. RFM ANALYSIS
# ==========================================

st.divider()
st.header("4. Customer Segmentation (RFM Analysis)")

# RFM hanya menggunakan pesanan delivered
rfm_data = filtered_df[
    filtered_df["order_status"] == "delivered"
].copy()

if not rfm_data.empty:

    snapshot_date = (
        rfm_data["order_purchase_timestamp"].max()
        + pd.Timedelta(days=1)
    )

    # Menghitung Recency, Frequency, dan Monetary
    rfm = rfm_data.groupby("customer_unique_id").agg(
        Recency=(
            "order_purchase_timestamp",
            lambda x: (snapshot_date - x.max()).days
        ),
        Frequency=("order_id", "nunique"),
        Monetary=("price", "sum")
    ).reset_index()

    # Membuat skor RFM
    # Recency: semakin kecil semakin baik
    rfm["R_Score"] = (
        5 - (
            rfm["Recency"].rank(method="first", pct=True) * 4
        ).apply(lambda x: int(x) if x == int(x) else int(x) + 1)
    ).clip(1, 4).astype(int)

    # Frequency: jumlah transaksi
    rfm["F_Score"] = pd.cut(
        rfm["Frequency"],
        bins=[0, 1, 2, float("inf")],
        labels=[1, 2, 4]
    ).astype(int)

    # Monetary: semakin besar semakin baik
    rfm["M_Score"] = (
        (rfm["Monetary"].rank(method="first", pct=True) * 4)
        .apply(lambda x: int(x) if x == int(x) else int(x) + 1)
    ).clip(1, 4).astype(int)

    # Segmentasi pelanggan
    def segment_customer(row):

        r = row["R_Score"]
        f = row["F_Score"]
        m = row["M_Score"]

        if r >= 3 and f >= 3 and m >= 3:
            return "Champions"

        elif f >= 3 and m >= 3:
            return "Loyal Customers"

        elif r >= 3 and f <= 2:
            return "Potential Loyalists"

        elif r <= 2 and f >= 2:
            return "At Risk"

        else:
            return "Others"

    rfm["Customer_Segment"] = rfm.apply(
        segment_customer,
        axis=1
    )

    # Ringkasan segmentasi
    segment_summary = rfm.groupby(
        "Customer_Segment",
        observed=False
    ).agg(
        total_customers=("customer_unique_id", "count"),
        total_revenue=("Monetary", "sum")
    ).reset_index()

    segment_summary["percentage"] = (
        segment_summary["total_customers"] /
        segment_summary["total_customers"].sum() * 100
    )

    # Grafik jumlah pelanggan
    col1, col2 = st.columns(2)

    with col1:

        fig_customer = px.bar(
            segment_summary,
            x="Customer_Segment",
            y="total_customers",
            text="total_customers",
            title="Customers by Segment",
            labels={
                "Customer_Segment": "Customer Segment",
                "total_customers": "Number of Customers"
            }
        )

        st.plotly_chart(
            fig_customer,
            use_container_width=True
        )

    # Grafik pendapatan per segmen
    with col2:

        fig_rfm_revenue = px.bar(
            segment_summary,
            x="Customer_Segment",
            y="total_revenue",
            text="total_revenue",
            title="Revenue by Customer Segment",
            labels={
                "Customer_Segment": "Customer Segment",
                "total_revenue": "Revenue (R$)"
            }
        )

        st.plotly_chart(
            fig_rfm_revenue,
            use_container_width=True
        )

    with st.expander("View RFM Summary"):
        st.dataframe(
            segment_summary,
            use_container_width=True,
            hide_index=True
        )

    with st.expander("View Customer RFM Data"):
        st.dataframe(
            rfm,
            use_container_width=True,
            hide_index=True
        )

else:
    st.warning("Tidak ada data delivered untuk analisis RFM.")
