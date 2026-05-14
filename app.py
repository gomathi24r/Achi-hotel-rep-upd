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

    # Vertical layout - no columns
    sel_date = st.date_input("Date", value=date.today())
    item = st.selectbox("Item Name", ITEMS)

    # Show price automatically
    price = PRICES[item]
    st.info(f"**Price**: ₹{price} per {item}")

    mode = st.selectbox("Mode", MODES)
    qty = st.number_input("Qty", min_value=0, step=1)

    # Calculate total live
    total_amt = qty * price
    st.success(f"**Total Amount**: ₹{total_amt}")

    if st.button("➕ Add Order", use_container_width=True):
        new_row = pd.DataFrame([{
            "Date": str(sel_date), "Item": item, "Mode": mode,
            "Qty": qty, "Price": price
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(FILE, index=False)
        st.success("✅ Order Added Successfully!")
        st.rerun()

    if st.button("✏️ Update Order", use_container_width=True):
        mask = (df["Date"] == str(sel_date)) & (df["Item"] == item) & (df["Mode"] == mode)
        if mask.any():
            df.loc[mask, ["Qty", "Price"]] = [qty, price]
            df.to_excel(FILE, index=False)
            st.success("✅ Order Updated Successfully!")
            st.rerun()
        else:
            st.error("No matching order found to update!")

with tab2:
    st.subheader("Daily Report / Receipt")
    report_date = st.date_input("Select Date for Report", value=date.today(), key="report")

    day_df = df[df["Date"] == str(report_date)].copy()

    if not day_df.empty:
        # Pivot table for item-wise mode breakdown
        pivot = day_df.pivot_table(
            index="Item",
            columns="Mode",
            values="Qty",
            aggfunc="sum",
            fill_value=0
        ).reset_index()

        # Add total qty and amount
        pivot["Total Qty"] = pivot.iloc[:, 1:].sum(axis=1)
        pivot["Total Amount"] = pivot["Total Qty"] * pivot["Item"].map(PRICES)

        # Add S.No
        pivot.insert(0, "S.No", range(1, len(pivot) + 1))

        st.dataframe(pivot, use_container_width=True)

        # Final total at bottom
        final_qty = pivot["Total Qty"].sum()
        final_amt = pivot["Total Amount"].sum()

        st.markdown("---")
        st.subheader("🧾 Receipt Summary")
        st.write(f"**Hotel**: Achis Chicken Biriyani, Bodipalayam, Coimbatore")
        st.write(f"**Date**: {report_date}")
        st.write(f"**Total Items Sold**: {int(final_qty)}")
        st.write(f"**Total Income**: ₹{final_amt:.2f}")

        csv = pivot.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Report as CSV", csv,
                          file_name=f"report_{report_date}.csv", mime="text/csv")
    else:
        st.info("No orders found for this date")

with tab3:
    st.subheader("All Orders Data")

    if not df.empty:
        # Remove Date column for display
        df_display = df.drop(columns=["Date"], errors="ignore").copy()

        # Add S.No
        df_display.insert(0, "S.No", range(1, len(df_display) + 1))

        # Show date range on top
        min_date = df["Date"].min()
        max_date = df["Date"].max()

        if min_date == max_date:
            st.subheader(f"All Orders on {min_date}")
        else:
            st.subheader(f"All Orders from {min_date} to {max_date}")

        st.dataframe(df_display.sort_values("S.No", ascending=False), use_container_width=True)
    else:
        st.info("No data available")

    if st.button("🗑️ Clear All Data"):
        df = pd.DataFrame(columns=["Date", "Item", "Mode", "Qty", "Price"])
        df.to_excel(FILE, index=False)
        st.warning("All data cleared!")
        st.rerun()
