import streamlit as st
import pandas as pd
from datetime import date
import os

FILE = "orders.xlsx"

# Price list
PRICES = {
    "Biriyani": 120,
    "Chilli Biriyani": 140,
    "MT": 90,
    "Chilli": 100,
    "Gilma": 150,
    "Gravy": 100
}

ITEMS = list(PRICES.keys())
MODES = ["Parcel", "Line", "Swiggy"]

# Load existing data
if os.path.exists(FILE):
    df = pd.read_excel(FILE)
else:
    df = pd.DataFrame(columns=["Date", "Item", "Mode", "Qty", "Price"])

st.set_page_config(page_title="Achis Chicken Biriyani", layout="wide")
st.title("🍗 Achis Chicken Biriyani - Bodipalayam, Coimbatore")

tab1, tab2, tab3 = st.tabs(["Add/Update Order", "Daily Report", "All Data"])

with tab1:
    st.subheader("Add or Update Order")

    col1, col2, col3 = st.columns(3)
    with col1:
        sel_date = st.date_input("Date", value=date.today())
    with col2:
        item = st.selectbox("Item Name", ITEMS)
    with col3:
        mode = st.selectbox("Mode", MODES)

    # Show price automatically
    price = PRICES[item]
    st.info(f"**Price**: ₹{price} per {item}")

    qty = st.number_input("Qty", min_value=0, step=1)

    col6, col7 = st.columns(2)
    with col6:
        if st.button("➕ Add Order", use_container_width=True):
            new_row = pd.DataFrame([{
                "Date": str(sel_date), "Item": item, "Mode": mode,
                "Qty": qty, "Price": price
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(FILE, index=False)
            st.success("Order added successfully!")
            st.rerun()

    with col7:
        if st.button("✏️ Update Order", use_container_width=True):
            mask = (df["Date"] == str(sel_date)) & (df["Item"] == item) & (df["Mode"] == mode)
            if mask.any():
                df.loc[mask, ["Qty", "Price"]] = [qty, price]
                df.to_excel(FILE, index=False)
                st.success("Order updated successfully!")
                st.rerun()
            else:
                st.error("No matching order found to update!")

with tab2:
    st.subheader("Daily Report / Receipt")
    report_date = st.date_input("Select Date for Report", value=date.today(), key="report")

    day_df = df[df["Date"] == str(report_date)]

    if not day_df.empty:
        pivot = day_df.pivot_table(
            index="Item",
            columns="Mode",
            values="Qty",
            aggfunc="sum",
            fill_value=0
        )

        pivot["Total Qty"] = pivot.sum(axis=1)

        income_df = day_df.groupby("Item").apply(
            lambda x: (x["Qty"] * x["Price"]).sum()
        ).reset_index(name="Income")

        final_df = pivot.reset_index().merge(income_df, on="Item", how="left")

        st.dataframe(final_df, use_container_width=True)

        total_income = day_df["Qty"].mul(day_df["Price"]).sum()
        total_qty = day_df["Qty"].sum()

        st.markdown("---")
        st.subheader("🧾 Receipt Summary")
        st.write(f"**Hotel**: Achis Chicken Biriyani, Bodipalayam, Coimbatore")
        st.write(f"**Date**: {report_date}")
        st.write(f"**Total Items Sold**: {int(total_qty)}")
        st.write(f"**Total Income**: ₹{total_income:.2f}")

        csv = final_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Report as CSV", csv,
                          file_name=f"report_{report_date}.csv", mime="text/csv")
    else:
        st.info("No orders found for this date")

with tab3:
    st.subheader("All Orders Data")
    st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True)

    if st.button("🗑️ Clear All Data"):
        df = pd.DataFrame(columns=["Date", "Item", "Mode", "Qty", "Price"])
        df.to_excel(FILE, index=False)
        st.warning("All data cleared!")
        st.rerun()