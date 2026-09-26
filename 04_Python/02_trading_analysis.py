# ============================================================
# STOCK MARKET TRADING MIS
# 02_TRADING_ANALYSIS.PY
# ============================================================
# Purpose:
#   Core trading lifecycle analysis:
#
#   Orders
#   Executions
#   Rejections
#   Cancellations
#   Pending Orders
#   Turnover
#   Execution Rate
#   Average Execution Time
#   Average Order Value
#   Order Quantity vs Executed Quantity
#   Partial Executions
#   Intraday Activity
#   MARKET vs LIMIT
#   Client Activity
#   Symbol Activity
#
# Input:
#   01_Raw_Data/*.csv
#
# Output:
#   07_Output/Trading_Analysis_Report.xlsx
# ============================================================

import os
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

RAW_DIR = os.path.join(
    BASE_DIR,
    "01_Raw_Data"
)

OUTPUT_DIR = Path(r"D:\STOCK_MARKET_TRADING_MIS\07_Output")

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "Trading_Analysis_Report.xlsx"
)


# ============================================================
# 2. LOAD DATA
# ============================================================

print("=" * 70)
print("STOCK MARKET MIS - TRADING ANALYSIS")
print("=" * 70)

orders = pd.read_csv(
    os.path.join(
        RAW_DIR,
        "06_Order_Book.csv"
    )
)

trades = pd.read_csv(
    os.path.join(
        RAW_DIR,
        "07_Trade_Execution_Book.csv"
    )
)

rejections = pd.read_csv(
    os.path.join(
        RAW_DIR,
        "08_Order_Rejection_Data.csv"
    )
)

charges = pd.read_csv(
    os.path.join(
        RAW_DIR,
        "09_Brokerage_Charges.csv"
    )
)

positions = pd.read_csv(
    os.path.join(
        RAW_DIR,
        "10_Position_Data.csv"
    )
)

clients = pd.read_csv(
    os.path.join(
        RAW_DIR,
        "02_Client_Master.csv"
    )
)

instruments = pd.read_csv(
    os.path.join(
        RAW_DIR,
        "01_Instrument_Master.csv"
    )
)

print(f"Orders loaded       : {len(orders):,}")
print(f"Trades loaded       : {len(trades):,}")
print(f"Rejections loaded   : {len(rejections):,}")
print(f"Charges loaded      : {len(charges):,}")
print(f"Positions loaded    : {len(positions):,}")

print("=" * 70)


# ============================================================
# 3. STANDARDIZE DATE/TIME COLUMNS
# ============================================================

orders["OrderDateTime"] = pd.to_datetime(
    orders["OrderDateTime"],
    errors="coerce"
)

trades["ExecutionDateTime"] = pd.to_datetime(
    trades["ExecutionDateTime"],
    errors="coerce"
)

orders["OrderDate"] = pd.to_datetime(
    orders["OrderDate"],
    errors="coerce"
)

trades["TradeDate"] = pd.to_datetime(
    trades["TradeDate"],
    errors="coerce"
)


# ============================================================
# 4. BASIC ORDER STATUS COUNTS
# ============================================================

status_counts = (
    orders["Status"]
    .value_counts()
    .rename_axis("Status")
    .reset_index(name="Orders")
)

total_orders = len(orders)

executed_orders = int(
    (orders["Status"] == "EXECUTED").sum()
)

partial_orders = int(
    (orders["Status"] == "PARTIAL").sum()
)

rejected_orders = int(
    (orders["Status"] == "REJECTED").sum()
)

cancelled_orders = int(
    (orders["Status"] == "CANCELLED").sum()
)

pending_orders = int(
    (orders["Status"] == "PENDING").sum()
)


# ============================================================
# 5. EXECUTION ORDER ANALYSIS
# ============================================================

executed_order_ids = set(
    trades["OrderID"].dropna().unique()
)

orders_with_execution = int(
    orders["OrderID"].isin(
        executed_order_ids
    ).sum()
)

execution_completion_rate = (
    orders_with_execution /
    total_orders *
    100
)

fully_executed_rate = (
    executed_orders /
    total_orders *
    100
)

rejection_rate = (
    rejected_orders /
    total_orders *
    100
)

cancellation_rate = (
    cancelled_orders /
    total_orders *
    100
)


# ============================================================
# 6. ORDER VALUE ANALYSIS
# ============================================================

average_order_value = orders[
    "OrderValue"
].mean()

total_order_value = orders[
    "OrderValue"
].sum()

total_turnover = trades[
    "TradeValue"
].sum()

average_trade_value = trades[
    "TradeValue"
].mean()


# ============================================================
# 7. EXECUTION TIME
# ============================================================

average_execution_time = trades[
    "ExecutionTimeSeconds"
].mean()

median_execution_time = trades[
    "ExecutionTimeSeconds"
].median()

max_execution_time = trades[
    "ExecutionTimeSeconds"
].max()


# ============================================================
# 8. ORDER QUANTITY VS EXECUTED QUANTITY
# ============================================================

order_quantity = (
    orders[
        [
            "OrderID",
            "OrderQuantity"
        ]
    ]
    .groupby("OrderID")
    .first()
    .reset_index()
)

executed_quantity = (
    trades
    .groupby("OrderID")[
        "ExecutedQuantity"
    ]
    .sum()
    .reset_index()
)

quantity_analysis = order_quantity.merge(
    executed_quantity,
    on="OrderID",
    how="left"
)

quantity_analysis[
    "ExecutedQuantity"
] = quantity_analysis[
    "ExecutedQuantity"
].fillna(0)

quantity_analysis[
    "RemainingQuantity"
] = (
    quantity_analysis["OrderQuantity"]
    -
    quantity_analysis["ExecutedQuantity"]
)

quantity_analysis[
    "ExecutionPercentage"
] = np.where(
    quantity_analysis["OrderQuantity"] > 0,
    quantity_analysis["ExecutedQuantity"]
    /
    quantity_analysis["OrderQuantity"]
    * 100,
    0
)


# ============================================================
# 9. PARTIAL EXECUTION ANALYSIS
# ============================================================

partial_execution_orders = quantity_analysis[
    (
        quantity_analysis["ExecutedQuantity"] > 0
    )
    &
    (
        quantity_analysis["ExecutedQuantity"]
        <
        quantity_analysis["OrderQuantity"]
    )
]

partial_execution_count = len(
    partial_execution_orders
)


# ============================================================
# 10. OVER-EXECUTION CHECK
# ============================================================

over_executed_orders = quantity_analysis[
    quantity_analysis["ExecutedQuantity"]
    >
    quantity_analysis["OrderQuantity"]
].copy()


# ============================================================
# 11. INTRADAY TRADING ACTIVITY
# ============================================================

def classify_intraday(dt):

    if pd.isna(dt):
        return "Unknown"

    time = dt.time()

    if time >= pd.Timestamp("09:15").time() and \
       time < pd.Timestamp("10:00").time():

        return "09:15-10:00"

    elif time >= pd.Timestamp("10:00").time() and \
         time < pd.Timestamp("12:00").time():

        return "10:00-12:00"

    elif time >= pd.Timestamp("12:00").time() and \
         time < pd.Timestamp("14:00").time():

        return "12:00-14:00"

    elif time >= pd.Timestamp("14:00").time() and \
         time <= pd.Timestamp("15:30").time():

        return "14:00-15:30"

    return "Outside Trading Window"


orders["IntradayBucket"] = orders[
    "OrderDateTime"
].apply(classify_intraday)

intraday_analysis = (
    orders
    .groupby("IntradayBucket")
    .agg(
        Orders=("OrderID", "count"),
        OrderValue=("OrderValue", "sum"),
        AverageOrderValue=("OrderValue", "mean")
    )
    .reset_index()
)


# ============================================================
# 12. MARKET VS LIMIT ANALYSIS
# ============================================================

order_type_analysis = (
    orders
    .groupby("OrderType")
    .agg(
        Orders=("OrderID", "count"),
        OrderQuantity=("OrderQuantity", "sum"),
        OrderValue=("OrderValue", "sum"),
        AverageOrderValue=("OrderValue", "mean")
    )
    .reset_index()
)

order_type_analysis[
    "OrderSharePct"
] = (
    order_type_analysis["Orders"]
    /
    total_orders
    * 100
)


# ============================================================
# 13. CLIENT-WISE ACTIVITY
# ============================================================

client_activity = (
    orders
    .groupby("ClientID")
    .agg(
        Orders=("OrderID", "count"),
        OrderQuantity=("OrderQuantity", "sum"),
        OrderValue=("OrderValue", "sum")
    )
    .reset_index()
)

client_turnover = (
    trades
    .groupby("ClientID")
    .agg(
        Trades=("TradeID", "count"),
        ExecutedQuantity=(
            "ExecutedQuantity",
            "sum"
        ),
        Turnover=("TradeValue", "sum")
    )
    .reset_index()
)

client_activity = client_activity.merge(
    client_turnover,
    on="ClientID",
    how="left"
)

client_activity[
    "Turnover"
] = client_activity[
    "Turnover"
].fillna(0)


# ============================================================
# 14. SYMBOL-WISE ACTIVITY
# ============================================================

symbol_activity = (
    orders
    .groupby(
        [
            "InstrumentID",
            "Symbol"
        ]
    )
    .agg(
        Orders=("OrderID", "count"),
        OrderQuantity=("OrderQuantity", "sum"),
        OrderValue=("OrderValue", "sum")
    )
    .reset_index()
)

symbol_turnover = (
    trades
    .groupby(
        [
            "InstrumentID",
            "Symbol"
        ]
    )
    .agg(
        Trades=("TradeID", "count"),
        ExecutedQuantity=(
            "ExecutedQuantity",
            "sum"
        ),
        Turnover=("TradeValue", "sum")
    )
    .reset_index()
)

symbol_activity = symbol_activity.merge(
    symbol_turnover,
    on=[
        "InstrumentID",
        "Symbol"
    ],
    how="left"
)

symbol_activity[
    "Turnover"
] = symbol_activity[
    "Turnover"
].fillna(0)


# ============================================================
# 15. DAILY TURNOVER TREND
# ============================================================

daily_turnover = (
    trades
    .groupby("TradeDate")
    .agg(
        Trades=("TradeID", "count"),
        ExecutedQuantity=(
            "ExecutedQuantity",
            "sum"
        ),
        Turnover=("TradeValue", "sum")
    )
    .reset_index()
    .sort_values("TradeDate")
)


# ============================================================
# 16. DAILY ORDER TREND
# ============================================================

daily_orders = (
    orders
    .groupby("OrderDate")
    .agg(
        Orders=("OrderID", "count"),
        OrderValue=("OrderValue", "sum")
    )
    .reset_index()
    .sort_values("OrderDate")
)


# ============================================================
# 17. KPI SUMMARY
# ============================================================

kpi_summary = pd.DataFrame([
    {
        "KPI": "Total Orders",
        "Value": total_orders
    },
    {
        "KPI": "Executed Orders",
        "Value": executed_orders
    },
    {
        "KPI": "Partial Orders",
        "Value": partial_orders
    },
    {
        "KPI": "Rejected Orders",
        "Value": rejected_orders
    },
    {
        "KPI": "Cancelled Orders",
        "Value": cancelled_orders
    },
    {
        "KPI": "Pending Orders",
        "Value": pending_orders
    },
    {
        "KPI": "Orders With Execution",
        "Value": orders_with_execution
    },
    {
        "KPI": "Execution Completion Rate %",
        "Value": round(
            execution_completion_rate,
            2
        )
    },
    {
        "KPI": "Fully Executed Order Rate %",
        "Value": round(
            fully_executed_rate,
            2
        )
    },
    {
        "KPI": "Rejection Rate %",
        "Value": round(
            rejection_rate,
            2
        )
    },
    {
        "KPI": "Cancellation Rate %",
        "Value": round(
            cancellation_rate,
            2
        )
    },
    {
        "KPI": "Average Order Value",
        "Value": round(
            average_order_value,
            2
        )
    },
    {
        "KPI": "Total Order Value",
        "Value": round(
            total_order_value,
            2
        )
    },
    {
        "KPI": "Total Turnover",
        "Value": round(
            total_turnover,
            2
        )
    },
    {
        "KPI": "Average Trade Value",
        "Value": round(
            average_trade_value,
            2
        )
    },
    {
        "KPI": "Average Execution Time Seconds",
        "Value": round(
            average_execution_time,
            2
        )
    },
    {
        "KPI": "Median Execution Time Seconds",
        "Value": round(
            median_execution_time,
            2
        )
    },
    {
        "KPI": "Maximum Execution Time Seconds",
        "Value": round(
            max_execution_time,
            2
        )
    },
    {
        "KPI": "Partial Execution Orders",
        "Value": partial_execution_count
    },
    {
        "KPI": "Over-Executed Orders",
        "Value": len(
            over_executed_orders
        )
    }
])


# ============================================================
# 18. CLIENT TURNOVER RANKING
# ============================================================

client_activity = client_activity.sort_values(
    "Turnover",
    ascending=False
)

client_activity[
    "TurnoverSharePct"
] = (
    client_activity["Turnover"]
    /
    total_turnover
    * 100
)


# ============================================================
# 19. SYMBOL TURNOVER RANKING
# ============================================================

symbol_activity = symbol_activity.sort_values(
    "Turnover",
    ascending=False
)

symbol_activity[
    "TurnoverSharePct"
] = (
    symbol_activity["Turnover"]
    /
    total_turnover
    * 100
)


# ============================================================
# 20. CONSOLE SUMMARY
# ============================================================

print()
print("CORE TRADING KPIs")
print("-" * 70)

print(
    f"Total Orders              : {total_orders:,}"
)

print(
    f"Executed Orders           : {executed_orders:,}"
)

print(
    f"Partial Orders            : {partial_orders:,}"
)

print(
    f"Rejected Orders           : {rejected_orders:,}"
)

print(
    f"Cancelled Orders          : {cancelled_orders:,}"
)

print(
    f"Pending Orders            : {pending_orders:,}"
)

print(
    f"Orders With Execution     : {orders_with_execution:,}"
)

print(
    f"Execution Completion Rate : "
    f"{execution_completion_rate:.2f}%"
)

print(
    f"Fully Executed Rate       : "
    f"{fully_executed_rate:.2f}%"
)

print(
    f"Rejection Rate            : "
    f"{rejection_rate:.2f}%"
)

print(
    f"Average Order Value       : "
    f"₹{average_order_value:,.2f}"
)

print(
    f"Total Turnover            : "
    f"₹{total_turnover:,.2f}"
)

print(
    f"Average Execution Time    : "
    f"{average_execution_time:.2f} seconds"
)

print(
    f"Partial Execution Orders  : "
    f"{partial_execution_count:,}"
)

print(
    f"Over-Executed Orders      : "
    f"{len(over_executed_orders):,}"
)


# ============================================================
# 21. EXPORT EXCEL REPORT
# ============================================================

print()
print("Creating Trading Analysis Excel report...")

with pd.ExcelWriter(
    OUTPUT_FILE,
    engine="openpyxl"
) as writer:

    kpi_summary.to_excel(
        writer,
        sheet_name="Trading_KPIs",
        index=False
    )

    status_counts.to_excel(
        writer,
        sheet_name="Order_Status",
        index=False
    )

    quantity_analysis.to_excel(
        writer,
        sheet_name="Order_Execution",
        index=False
    )

    partial_execution_orders.to_excel(
        writer,
        sheet_name="Partial_Executions",
        index=False
    )

    over_executed_orders.to_excel(
        writer,
        sheet_name="Over_Execution",
        index=False
    )

    intraday_analysis.to_excel(
        writer,
        sheet_name="Intraday_Activity",
        index=False
    )

    order_type_analysis.to_excel(
        writer,
        sheet_name="Market_vs_Limit",
        index=False
    )

    daily_orders.to_excel(
        writer,
        sheet_name="Daily_Orders",
        index=False
    )

    daily_turnover.to_excel(
        writer,
        sheet_name="Daily_Turnover",
        index=False
    )

    client_activity.to_excel(
        writer,
        sheet_name="Client_Activity",
        index=False
    )

    symbol_activity.to_excel(
        writer,
        sheet_name="Symbol_Activity",
        index=False
    )


# ============================================================
# 22. FINAL MESSAGE
# ============================================================

print()
print("=" * 70)
print("TRADING ANALYSIS COMPLETED")
print("=" * 70)

print()
print("Output:")
print(OUTPUT_FILE)

print()
print("Excel sheets created:")
print("  1. Trading_KPIs")
print("  2. Order_Status")
print("  3. Order_Execution")
print("  4. Partial_Executions")
print("  5. Over_Execution")
print("  6. Intraday_Activity")
print("  7. Market_vs_Limit")
print("  8. Daily_Orders")
print("  9. Daily_Turnover")
print(" 10. Client_Activity")
print(" 11. Symbol_Activity")

print("=" * 70)

# ============================================================
# ADVANCED TRADING ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("ADVANCED TRADING ANALYSIS")
print("=" * 70)


# ------------------------------------------------------------
# 1. REJECTION ANALYSIS
# ------------------------------------------------------------

rejection_reason = (
    rejections
    .groupby("RejectionReason")
    .agg(
        RejectedOrders=("OrderID", "nunique"),
        AvgRejectionTimeSeconds=("RejectionTimeSeconds", "mean")
    )
    .reset_index()
)

rejection_reason["RejectionRatePct"] = (
    rejection_reason["RejectedOrders"]
    / len(orders)
    * 100
)

rejection_reason = rejection_reason.sort_values(
    "RejectedOrders",
    ascending=False
)


# Client-wise rejection analysis
client_rejection = (
    rejections
    .groupby(["ClientID"])
    .agg(
        RejectedOrders=("OrderID", "nunique")
    )
    .reset_index()
)

client_orders = (
    orders
    .groupby("ClientID")
    .agg(
        TotalOrders=("OrderID", "nunique")
    )
    .reset_index()
)

client_rejection = client_rejection.merge(
    client_orders,
    on="ClientID",
    how="left"
)

client_rejection["RejectionRatePct"] = (
    client_rejection["RejectedOrders"]
    / client_rejection["TotalOrders"]
    * 100
)

client_rejection = client_rejection.sort_values(
    "RejectionRatePct",
    ascending=False
)


# Symbol-wise rejection analysis
symbol_rejection = (
    rejections
    .groupby("Symbol")
    .agg(
        RejectedOrders=("OrderID", "nunique")
    )
    .reset_index()
)

symbol_orders = (
    orders
    .groupby("Symbol")
    .agg(
        TotalOrders=("OrderID", "nunique")
    )
    .reset_index()
)

symbol_rejection = symbol_rejection.merge(
    symbol_orders,
    on="Symbol",
    how="left"
)

symbol_rejection["RejectionRatePct"] = (
    symbol_rejection["RejectedOrders"]
    / symbol_rejection["TotalOrders"]
    * 100
)

symbol_rejection = symbol_rejection.sort_values(
    "RejectionRatePct",
    ascending=False
)


# ------------------------------------------------------------
# 2. SLIPPAGE ANALYSIS
# ------------------------------------------------------------

# Join order price with execution data
slippage_df = trades[
    [
        "TradeID",
        "OrderID",
        "ClientID",
        "AccountID",
        "InstrumentID",
        "Symbol",
        "Side",
        "OrderType",
        "ExecutedQuantity",
        "ExecutionPrice",
        "TradeValue",
        "SlippageValue",
        "SlippagePct"
    ]
].copy()

slippage_df = slippage_df.merge(
    orders[
        [
            "OrderID",
            "OrderPrice"
        ]
    ],
    on="OrderID",
    how="left"
)

# Calculate price difference where order price exists
slippage_df["PriceDifference"] = (
    slippage_df["ExecutionPrice"]
    - slippage_df["OrderPrice"]
)

# Direction-aware adverse slippage
slippage_df["AdverseSlippage"] = 0.0

buy_mask = (
    (slippage_df["Side"] == "BUY") &
    slippage_df["OrderPrice"].notna()
)

sell_mask = (
    (slippage_df["Side"] == "SELL") &
    slippage_df["OrderPrice"].notna()
)

slippage_df.loc[buy_mask, "AdverseSlippage"] = (
    slippage_df.loc[buy_mask, "PriceDifference"]
)

slippage_df.loc[sell_mask, "AdverseSlippage"] = (
    -slippage_df.loc[sell_mask, "PriceDifference"]
)

slippage_df["AdverseSlippageValue"] = (
    slippage_df["AdverseSlippage"]
    * slippage_df["ExecutedQuantity"]
)

# Only orders with an actual reference order price
limit_slippage = slippage_df[
    slippage_df["OrderPrice"].notna()
].copy()

slippage_summary = pd.DataFrame({
    "Metric": [
        "Trades with Order Price",
        "Average Price Difference",
        "Average Stored Slippage %",
        "Average Adverse Slippage",
        "Total Adverse Slippage Value",
        "High Slippage Trades"
    ],
    "Value": [
        len(limit_slippage),
        limit_slippage["PriceDifference"].mean(),
        limit_slippage["SlippagePct"].mean(),
        limit_slippage["AdverseSlippage"].mean(),
        limit_slippage["AdverseSlippageValue"].sum(),
        (
            limit_slippage["SlippagePct"].abs() > 1
        ).sum()
    ]
})

# High slippage trades
high_slippage = limit_slippage[
    limit_slippage["SlippagePct"].abs() > 1
].copy()

high_slippage = high_slippage.sort_values(
    "SlippagePct",
    key=lambda x: x.abs(),
    ascending=False
)


# ------------------------------------------------------------
# 3. BROKERAGE & TRANSACTION CHARGES
# ------------------------------------------------------------

charge_summary = pd.DataFrame({
    "Metric": [
        "Brokerage",
        "STT",
        "Exchange Charges",
        "GST",
        "SEBI Charges",
        "Stamp Duty",
        "Total Transaction Charges"
    ],
    "Amount": [
        charges["Brokerage"].sum(),
        charges["STT"].sum(),
        charges["ExchangeCharges"].sum(),
        charges["GST"].sum(),
        charges["SEBICharges"].sum(),
        charges["StampDuty"].sum(),
        charges["TotalCharges"].sum()
    ]
})

charge_summary["Amount"] = charge_summary["Amount"].round(2)


# Client-wise charges
client_charges = (
    charges
    .groupby("ClientID")
    .agg(
        TradeValue=("TradeValue", "sum"),
        Brokerage=("Brokerage", "sum"),
        STT=("STT", "sum"),
        ExchangeCharges=("ExchangeCharges", "sum"),
        GST=("GST", "sum"),
        SEBICharges=("SEBICharges", "sum"),
        StampDuty=("StampDuty", "sum"),
        TotalCharges=("TotalCharges", "sum")
    )
    .reset_index()
)

client_charges["ChargeRatePct"] = (
    client_charges["TotalCharges"]
    / client_charges["TradeValue"]
    * 100
)


# ------------------------------------------------------------
# 4. GROSS & NET P&L
# ------------------------------------------------------------

pnl_summary = pd.DataFrame({
    "Metric": [
        "Gross P&L",
        "Total Transaction Charges",
        "Net P&L"
    ],
    "Amount": [
        positions["GrossPnL"].sum(),
        charges["TotalCharges"].sum(),
        positions["GrossPnL"].sum()
        - charges["TotalCharges"].sum()
    ]
})

pnl_summary["Amount"] = pnl_summary["Amount"].round(2)


# P&L by client
client_pnl = (
    positions
    .groupby("ClientID")
    .agg(
        GrossPnL=("GrossPnL", "sum"),
        RealizedPnL=("RealizedPnL", "sum"),
        UnrealizedPnL=("UnrealizedPnL", "sum")
    )
    .reset_index()
)

client_charge_pnl = (
    charges
    .groupby("ClientID")
    .agg(
        TransactionCharges=("TotalCharges", "sum")
    )
    .reset_index()
)

client_pnl = client_pnl.merge(
    client_charge_pnl,
    on="ClientID",
    how="left"
)

client_pnl["TransactionCharges"] = (
    client_pnl["TransactionCharges"]
    .fillna(0)
)

client_pnl["NetPnL"] = (
    client_pnl["GrossPnL"]
    - client_pnl["TransactionCharges"]
)


# ------------------------------------------------------------
# 5. POSITION RECONCILIATION
# ------------------------------------------------------------

position_reconciliation = positions[
    [
        "PositionID",
        "PositionDate",
        "AccountID",
        "ClientID",
        "InstrumentID",
        "Symbol",
        "BuyQty",
        "SellQty",
        "NetQuantity"
    ]
].copy()

position_reconciliation["CalculatedNetQuantity"] = (
    position_reconciliation["BuyQty"]
    - position_reconciliation["SellQty"]
)

position_reconciliation["Difference"] = (
    position_reconciliation["NetQuantity"]
    - position_reconciliation["CalculatedNetQuantity"]
)

position_reconciliation["ReconciliationStatus"] = np.where(
    position_reconciliation["Difference"] == 0,
    "MATCH",
    "MISMATCH"
)

position_exceptions = position_reconciliation[
    position_reconciliation["Difference"] != 0
].copy()

position_exceptions = position_exceptions.sort_values(
    "Difference",
    key=lambda x: x.abs(),
    ascending=False
)


# ------------------------------------------------------------
# 6. TRADE ACTIVITY BY CLIENT
# ------------------------------------------------------------

client_trade_activity = (
    trades
    .groupby("ClientID")
    .agg(
        Trades=("TradeID", "nunique"),
        ExecutedQuantity=("ExecutedQuantity", "sum"),
        Turnover=("TradeValue", "sum"),
        AvgExecutionTime=("ExecutionTimeSeconds", "mean"),
        AvgSlippagePct=("SlippagePct", "mean")
    )
    .reset_index()
)

client_trade_activity["TurnoverSharePct"] = (
    client_trade_activity["Turnover"]
    / client_trade_activity["Turnover"].sum()
    * 100
)

client_trade_activity = client_trade_activity.sort_values(
    "Turnover",
    ascending=False
)


# ------------------------------------------------------------
# 7. SYMBOL ACTIVITY
# ------------------------------------------------------------

symbol_trade_activity = (
    trades
    .groupby("Symbol")
    .agg(
        Trades=("TradeID", "nunique"),
        ExecutedQuantity=("ExecutedQuantity", "sum"),
        Turnover=("TradeValue", "sum"),
        AvgExecutionTime=("ExecutionTimeSeconds", "mean"),
        AvgSlippagePct=("SlippagePct", "mean")
    )
    .reset_index()
)

symbol_trade_activity["TurnoverSharePct"] = (
    symbol_trade_activity["Turnover"]
    / symbol_trade_activity["Turnover"].sum()
    * 100
)

symbol_trade_activity = symbol_trade_activity.sort_values(
    "Turnover",
    ascending=False
)


# ------------------------------------------------------------
# 8. UNUSUALLY HIGH ORDER VOLUME
# ------------------------------------------------------------

client_volume_threshold = (
    client_trade_activity["Trades"].mean()
    + 2 * client_trade_activity["Trades"].std()
)

high_volume_clients = client_trade_activity[
    client_trade_activity["Trades"] > client_volume_threshold
].copy()

symbol_volume_threshold = (
    symbol_trade_activity["Trades"].mean()
    + 2 * symbol_trade_activity["Trades"].std()
)

high_volume_symbols = symbol_trade_activity[
    symbol_trade_activity["Trades"] > symbol_volume_threshold
].copy()


# ------------------------------------------------------------
# 9. HIGH REJECTION RATE
# ------------------------------------------------------------

# Require at least 20 orders so tiny samples don't dominate
high_rejection_clients = client_rejection[
    (client_rejection["TotalOrders"] >= 20) &
    (client_rejection["RejectionRatePct"] >= 20)
].copy()

high_rejection_symbols = symbol_rejection[
    (symbol_rejection["TotalOrders"] >= 20) &
    (symbol_rejection["RejectionRatePct"] >= 20)
].copy()


# ------------------------------------------------------------
# 10. ACTIVITY SPIKE ANALYSIS
# ------------------------------------------------------------

daily_activity = (
    orders
    .groupby("OrderDate")
    .agg(
        Orders=("OrderID", "nunique"),
        OrderValue=("OrderValue", "sum")
    )
    .reset_index()
)

daily_activity["Rolling7DayAvgOrders"] = (
    daily_activity["Orders"]
    .rolling(7, min_periods=3)
    .mean()
)

daily_activity["ActivitySpikePct"] = (
    (
        daily_activity["Orders"]
        - daily_activity["Rolling7DayAvgOrders"]
    )
    / daily_activity["Rolling7DayAvgOrders"]
    * 100
)

activity_spikes = daily_activity[
    daily_activity["ActivitySpikePct"] >= 50
].copy()

activity_spikes = activity_spikes.sort_values(
    "ActivitySpikePct",
    ascending=False
)


# ------------------------------------------------------------
# 11. DAILY P&L VS TURNOVER
# ------------------------------------------------------------

# Make sure both date columns use the same datetime type
positions["PositionDate"] = pd.to_datetime(
    positions["PositionDate"],
    errors="coerce"
)

trades["TradeDate"] = pd.to_datetime(
    trades["TradeDate"],
    errors="coerce"
)

# Convert to date only for daily analysis
positions["PositionDate"] = positions["PositionDate"].dt.date
trades["TradeDate"] = trades["TradeDate"].dt.date


position_daily_pnl = (
    positions
    .groupby("PositionDate")
    .agg(
        GrossPnL=("GrossPnL", "sum"),
        RealizedPnL=("RealizedPnL", "sum"),
        UnrealizedPnL=("UnrealizedPnL", "sum")
    )
    .reset_index()
)

trade_daily_turnover = (
    trades
    .groupby("TradeDate")
    .agg(
        Turnover=("TradeValue", "sum"),
        Trades=("TradeID", "nunique")
    )
    .reset_index()
)

daily_pnl_turnover = position_daily_pnl.merge(
    trade_daily_turnover,
    left_on="PositionDate",
    right_on="TradeDate",
    how="left"
)

daily_pnl_turnover["PnLToTurnoverPct"] = (
    daily_pnl_turnover["GrossPnL"]
    / daily_pnl_turnover["Turnover"]
    * 100
)

daily_pnl_turnover = daily_pnl_turnover.drop(
    columns=["TradeDate"],
    errors="ignore"
)
# ------------------------------------------------------------
# ADVANCED CONSOLE SUMMARY
# ------------------------------------------------------------

print("\nREJECTION ANALYSIS")
print("-" * 50)
print("Total rejected orders       :", len(rejections))
print("Top rejection reason       :",
      rejection_reason.iloc[0]["RejectionReason"])
print("Top rejection count        :",
      int(rejection_reason.iloc[0]["RejectedOrders"]))

print("\nSLIPPAGE ANALYSIS")
print("-" * 50)
print("Trades with order price    :", len(limit_slippage))
print("High slippage trades       :", len(high_slippage))

print("\nCHARGES")
print("-" * 50)
print("Total Brokerage             : ₹{:,.2f}".format(
    charges["Brokerage"].sum()
))
print("Total Transaction Charges   : ₹{:,.2f}".format(
    charges["TotalCharges"].sum()
))

print("\nP&L")
print("-" * 50)
print("Gross P&L                   : ₹{:,.2f}".format(
    positions["GrossPnL"].sum()
))
print("Net P&L                     : ₹{:,.2f}".format(
    positions["GrossPnL"].sum()
    - charges["TotalCharges"].sum()
))

print("\nPOSITION RECONCILIATION")
print("-" * 50)
print("Position records            :", len(positions))
print("Position mismatches         :", len(position_exceptions))

print("\nANOMALIES")
print("-" * 50)
print("High-volume clients        :", len(high_volume_clients))
print("High-volume symbols        :", len(high_volume_symbols))
print("High-rejection clients     :", len(high_rejection_clients))
print("High-rejection symbols     :", len(high_rejection_symbols))
print("Activity spike days        :", len(activity_spikes))

# ------------------------------------------------------------
# 12. TRADE VS POSITION RECONCILIATION
# ------------------------------------------------------------

print("\nTRADE VS POSITION RECONCILIATION")

# Aggregate executed trades by Account + Instrument
trade_position_check = (
    trades
    .groupby(
        ["AccountID", "ClientID", "InstrumentID", "Symbol"],
        as_index=False
    )
    .agg(
        TradeBuyQty=(
            "ExecutedQuantity",
            lambda x: x[trades.loc[x.index, "Side"].eq("BUY")].sum()
        ),
        TradeSellQty=(
            "ExecutedQuantity",
            lambda x: x[trades.loc[x.index, "Side"].eq("SELL")].sum()
        ),
        TradeCount=("TradeID", "nunique"),
        TradeTurnover=("TradeValue", "sum")
    )
)

# Calculate net quantity from executed trades
trade_position_check["CalculatedTradeNetQty"] = (
    trade_position_check["TradeBuyQty"]
    - trade_position_check["TradeSellQty"]
)

# Aggregate position data
position_summary = (
    positions
    .groupby(
        ["AccountID", "ClientID", "InstrumentID", "Symbol"],
        as_index=False
    )
    .agg(
        PositionBuyQty=("BuyQty", "sum"),
        PositionSellQty=("SellQty", "sum"),
        ReportedNetQty=("NetQuantity", "sum")
    )
)

# Merge trades with positions
trade_position_check = trade_position_check.merge(
    position_summary,
    on=["AccountID", "ClientID", "InstrumentID", "Symbol"],
    how="outer"
)

# Fill missing values
quantity_columns = [
    "TradeBuyQty",
    "TradeSellQty",
    "TradeCount",
    "TradeTurnover",
    "CalculatedTradeNetQty",
    "PositionBuyQty",
    "PositionSellQty",
    "ReportedNetQty"
]

for col in quantity_columns:
    if col in trade_position_check.columns:
        trade_position_check[col] = (
            trade_position_check[col]
            .fillna(0)
        )

# Compare trade-derived quantities with position quantities
trade_position_check["BuyQtyDifference"] = (
    trade_position_check["TradeBuyQty"]
    - trade_position_check["PositionBuyQty"]
)

trade_position_check["SellQtyDifference"] = (
    trade_position_check["TradeSellQty"]
    - trade_position_check["PositionSellQty"]
)

trade_position_check["NetQtyDifference"] = (
    trade_position_check["CalculatedTradeNetQty"]
    - trade_position_check["ReportedNetQty"]
)

# Reconciliation status
trade_position_check["ReconciliationStatus"] = "MATCH"

trade_position_check.loc[
    (
        trade_position_check["BuyQtyDifference"].abs() > 0
    )
    |
    (
        trade_position_check["SellQtyDifference"].abs() > 0
    )
    |
    (
        trade_position_check["NetQtyDifference"].abs() > 0
    ),
    "ReconciliationStatus"
] = "MISMATCH"

# Sort mismatches first
trade_position_check["MismatchMagnitude"] = (
    trade_position_check["BuyQtyDifference"].abs()
    + trade_position_check["SellQtyDifference"].abs()
    + trade_position_check["NetQtyDifference"].abs()
)

trade_position_check = trade_position_check.sort_values(
    by="MismatchMagnitude",
    ascending=False
)

trade_position_exceptions = trade_position_check[
    trade_position_check["ReconciliationStatus"] == "MISMATCH"
].copy()

print(
    f"Trade-Position records checked : "
    f"{len(trade_position_check):,}"
)

print(
    f"Matching records               : "
    f"{(trade_position_check['ReconciliationStatus'] == 'MATCH').sum():,}"
)

print(
    f"Mismatched records             : "
    f"{len(trade_position_exceptions):,}"
)

# ============================================================
# ADVANCED EXCEL OUTPUT
# ============================================================

advanced_output = OUTPUT_DIR / "Advanced_Trading_Analysis.xlsx"

with pd.ExcelWriter(advanced_output, engine="openpyxl") as writer:

    rejection_reason.to_excel(
        writer,
        sheet_name="Rejection_Reason",
        index=False
    )

    client_rejection.to_excel(
        writer,
        sheet_name="Client_Rejection",
        index=False
    )

    symbol_rejection.to_excel(
        writer,
        sheet_name="Symbol_Rejection",
        index=False
    )

    slippage_summary.to_excel(
        writer,
        sheet_name="Slippage_Summary",
        index=False
    )

    high_slippage.to_excel(
        writer,
        sheet_name="High_Slippage",
        index=False
    )

    charge_summary.to_excel(
        writer,
        sheet_name="Charge_Summary",
        index=False
    )

    client_charges.to_excel(
        writer,
        sheet_name="Client_Charges",
        index=False
    )

    pnl_summary.to_excel(
        writer,
        sheet_name="PnL_Summary",
        index=False
    )

    client_pnl.to_excel(
        writer,
        sheet_name="Client_PnL",
        index=False
    )

    position_reconciliation.to_excel(
        writer,
        sheet_name="Position_Reconciliation",
        index=False
    )

    position_exceptions.to_excel(
        writer,
        sheet_name="Position_Exceptions",
        index=False
    )

    client_trade_activity.to_excel(
        writer,
        sheet_name="Client_Activity",
        index=False
    )

    symbol_trade_activity.to_excel(
        writer,
        sheet_name="Symbol_Activity",
        index=False
    )

    high_volume_clients.to_excel(
        writer,
        sheet_name="High_Volume_Clients",
        index=False
    )

    high_volume_symbols.to_excel(
        writer,
        sheet_name="High_Volume_Symbols",
        index=False
    )

    high_rejection_clients.to_excel(
        writer,
        sheet_name="High_Rejection_Clients",
        index=False
    )

    high_rejection_symbols.to_excel(
        writer,
        sheet_name="High_Rejection_Symbols",
        index=False
    )

    activity_spikes.to_excel(
        writer,
        sheet_name="Activity_Spikes",
        index=False
    )

    daily_pnl_turnover.to_excel(
        writer,
        sheet_name="PnL_vs_Turnover",
        index=False
    )
    trade_position_check.to_excel(
    writer,
    sheet_name="Trade_Position_Reconciliation",
    index=False
    )

    trade_position_exceptions.to_excel(
    writer,
    sheet_name="Trade_Position_Exceptions",
    index=False
    )

print("\nAdvanced analysis saved to:")
print(advanced_output)

