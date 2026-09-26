# ============================================================
# STOCK MARKET TRADING MIS & ANALYTICS
# 05 - VISUALIZATION
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# 1. PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(r"D:\STOCK_MARKET_TRADING_MIS")

DATA_DIR = BASE_DIR / "01_Raw_Data"

OUTPUT_DIR = BASE_DIR / "07_Output"

VISUAL_DIR = OUTPUT_DIR / "Visualizations"

VISUAL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. FILE PATHS
# ============================================================

ORDER_FILE = DATA_DIR / "06_Order_Book.csv"

TRADE_FILE = DATA_DIR / "07_Trade_Execution_Book.csv"

REJECTION_FILE = DATA_DIR / "08_Order_Rejection_Data.csv"

POSITION_FILE = DATA_DIR / "10_Position_Data.csv"


# ============================================================
# 3. LOAD DATA
# ============================================================

print("=" * 70)
print("STOCK MARKET TRADING VISUALIZATION")
print("=" * 70)

orders = pd.read_csv(ORDER_FILE)

trades = pd.read_csv(TRADE_FILE)

rejections = pd.read_csv(REJECTION_FILE)

positions = pd.read_csv(POSITION_FILE)


print("\nDATA LOADED")
print("-" * 70)

print(f"Orders       : {len(orders):,}")
print(f"Trades       : {len(trades):,}")
print(f"Rejections   : {len(rejections):,}")
print(f"Positions    : {len(positions):,}")


# ============================================================
# 4. DATE CONVERSION
# ============================================================

orders["OrderDate"] = pd.to_datetime(
    orders["OrderDate"],
    errors="coerce"
)

orders["OrderDateTime"] = pd.to_datetime(
    orders["OrderDateTime"],
    errors="coerce"
)

trades["TradeDate"] = pd.to_datetime(
    trades["TradeDate"],
    errors="coerce"
)

trades["ExecutionDateTime"] = pd.to_datetime(
    trades["ExecutionDateTime"],
    errors="coerce"
)

positions["PositionDate"] = pd.to_datetime(
    positions["PositionDate"],
    errors="coerce"
)


# ============================================================
# 5. HELPER FUNCTION
# ============================================================

def save_chart(filename):
    """
    Save chart as high-resolution PNG.
    """
    
    filepath = VISUAL_DIR / filename
    
    plt.tight_layout()
    
    plt.savefig(
        filepath,
        dpi=150,
        bbox_inches="tight"
    )
    
    plt.close()
    
    print(f"Created: {filename}")


# ============================================================
# 6. ORDER STATUS DISTRIBUTION
# ============================================================

print("\n1. ORDER STATUS")

order_status = (
    orders["Status"]
    .value_counts()
    .sort_values(ascending=False)
)


plt.figure(figsize=(10, 6))

order_status.plot(
    kind="bar"
)

plt.title(
    "Order Status Distribution"
)

plt.xlabel(
    "Order Status"
)

plt.ylabel(
    "Number of Orders"
)

plt.xticks(
    rotation=45,
    ha="right"
)

save_chart(
    "01_order_status_distribution.png"
)


# ============================================================
# 7. DAILY ORDER VOLUME
# ============================================================

print("\n2. DAILY ORDER VOLUME")

daily_orders = (
    orders
    .groupby(
        orders["OrderDate"].dt.date
    )
    .agg(
        Orders=("OrderID", "nunique")
    )
    .reset_index()
)


daily_orders.columns = [
    "Date",
    "Orders"
]


plt.figure(figsize=(12, 6))

plt.plot(
    daily_orders["Date"],
    daily_orders["Orders"]
)

plt.title(
    "Daily Order Volume"
)

plt.xlabel(
    "Date"
)

plt.ylabel(
    "Number of Orders"
)

plt.xticks(
    rotation=45
)

save_chart(
    "02_daily_order_volume.png"
)


# ============================================================
# 8. DAILY TURNOVER
# ============================================================

print("\n3. DAILY TURNOVER")

daily_turnover = (
    trades
    .groupby(
        trades["TradeDate"].dt.date
    )
    .agg(
        Turnover=("TradeValue", "sum")
    )
    .reset_index()
)


daily_turnover.columns = [
    "Date",
    "Turnover"
]


plt.figure(figsize=(12, 6))

plt.plot(
    daily_turnover["Date"],
    daily_turnover["Turnover"]
)

plt.title(
    "Daily Trading Turnover"
)

plt.xlabel(
    "Date"
)

plt.ylabel(
    "Turnover"
)

plt.xticks(
    rotation=45
)

save_chart(
    "03_daily_turnover.png"
)


# ============================================================
# 9. INTRADAY TRADING ACTIVITY
# ============================================================

print("\n4. INTRADAY ACTIVITY")

intraday = (
    orders
    .groupby("IntradayBucket")
    .agg(
        Orders=("OrderID", "nunique")
    )
    .reset_index()
)


# Preserve logical market sequence

bucket_order = [
    "09:15-10:00",
    "10:00-12:00",
    "12:00-14:00",
    "14:00-15:30"
]


intraday["SortOrder"] = (
    intraday["IntradayBucket"]
    .apply(
        lambda x:
        bucket_order.index(x)
        if x in bucket_order
        else 999
    )
)


intraday = (
    intraday
    .sort_values("SortOrder")
)


plt.figure(figsize=(10, 6))

plt.bar(
    intraday["IntradayBucket"],
    intraday["Orders"]
)

plt.title(
    "Intraday Trading Activity"
)

plt.xlabel(
    "Trading Time Window"
)

plt.ylabel(
    "Number of Orders"
)

plt.xticks(
    rotation=30
)

save_chart(
    "04_intraday_trading_activity.png"
)


# ============================================================
# 10. MARKET VS LIMIT ORDERS
# ============================================================

print("\n5. MARKET VS LIMIT")

market_limit = (
    orders["OrderType"]
    .value_counts()
)


plt.figure(figsize=(8, 6))

market_limit.plot(
    kind="bar"
)

plt.title(
    "MARKET vs LIMIT Orders"
)

plt.xlabel(
    "Order Type"
)

plt.ylabel(
    "Number of Orders"
)

plt.xticks(
    rotation=0
)

save_chart(
    "05_market_vs_limit_orders.png"
)


# ============================================================
# 11. REJECTION REASONS
# ============================================================

print("\n6. REJECTION REASONS")

rejection_reason = (
    rejections["RejectionReason"]
    .value_counts()
    .head(10)
    .sort_values()
)


plt.figure(figsize=(10, 6))

rejection_reason.plot(
    kind="barh"
)

plt.title(
    "Top Order Rejection Reasons"
)

plt.xlabel(
    "Number of Rejected Orders"
)

plt.ylabel(
    "Rejection Reason"
)

save_chart(
    "06_rejection_reasons.png"
)


# ============================================================
# 12. TOP CLIENTS BY TURNOVER
# ============================================================

print("\n7. TOP CLIENTS BY TURNOVER")

top_clients = (
    trades
    .groupby("ClientID")
    .agg(
        Turnover=("TradeValue", "sum")
    )
    .sort_values(
        "Turnover",
        ascending=False
    )
    .head(10)
    .sort_values(
        "Turnover"
    )
)


plt.figure(figsize=(10, 6))

plt.barh(
    top_clients.index.astype(str),
    top_clients["Turnover"]
)

plt.title(
    "Top 10 Clients by Trading Turnover"
)

plt.xlabel(
    "Turnover"
)

plt.ylabel(
    "Client ID"
)

save_chart(
    "07_top_clients_by_turnover.png"
)


# ============================================================
# 13. TOP SYMBOLS BY TURNOVER
# ============================================================

print("\n8. TOP SYMBOLS BY TURNOVER")

top_symbols = (
    trades
    .groupby("Symbol")
    .agg(
        Turnover=("TradeValue", "sum")
    )
    .sort_values(
        "Turnover",
        ascending=False
    )
    .head(10)
    .sort_values(
        "Turnover"
    )
)


plt.figure(figsize=(10, 6))

plt.barh(
    top_symbols.index.astype(str),
    top_symbols["Turnover"]
)

plt.title(
    "Top 10 Symbols by Trading Turnover"
)

plt.xlabel(
    "Turnover"
)

plt.ylabel(
    "Symbol"
)

save_chart(
    "08_top_symbols_by_turnover.png"
)


# ============================================================
# 14. EXECUTION TIME DISTRIBUTION
# ============================================================

print("\n9. EXECUTION TIME")

execution_time = (
    trades["ExecutionTimeSeconds"]
    .dropna()
)


plt.figure(figsize=(10, 6))

plt.hist(
    execution_time,
    bins=30
)

plt.title(
    "Execution Time Distribution"
)

plt.xlabel(
    "Execution Time (Seconds)"
)

plt.ylabel(
    "Number of Trades"
)

save_chart(
    "09_execution_time_distribution.png"
)


# ============================================================
# 15. SLIPPAGE DISTRIBUTION
# ============================================================

print("\n10. SLIPPAGE")

slippage = (
    trades["SlippagePct"]
    .dropna()
)


plt.figure(figsize=(10, 6))

plt.hist(
    slippage,
    bins=30
)

plt.title(
    "Execution Slippage Distribution"
)

plt.xlabel(
    "Slippage (%)"
)

plt.ylabel(
    "Number of Trades"
)

save_chart(
    "10_slippage_distribution.png"
)


# ============================================================
# 16. DAILY EXECUTED TRADE COUNT
# ============================================================

print("\n11. DAILY EXECUTED TRADES")

daily_trades = (
    trades
    .groupby(
        trades["TradeDate"].dt.date
    )
    .agg(
        Trades=("TradeID", "nunique")
    )
    .reset_index()
)


daily_trades.columns = [
    "Date",
    "Trades"
]


plt.figure(figsize=(12, 6))

plt.plot(
    daily_trades["Date"],
    daily_trades["Trades"]
)

plt.title(
    "Daily Executed Trade Volume"
)

plt.xlabel(
    "Date"
)

plt.ylabel(
    "Number of Trades"
)

plt.xticks(
    rotation=45
)

save_chart(
    "11_daily_executed_trades.png"
)


# ============================================================
# 17. DAILY GROSS P&L
# ============================================================

print("\n12. DAILY GROSS P&L")

daily_pnl = (
    positions
    .groupby(
        positions["PositionDate"].dt.date
    )
    .agg(
        GrossPnL=("GrossPnL", "sum")
    )
    .reset_index()
)


daily_pnl.columns = [
    "Date",
    "GrossPnL"
]


plt.figure(figsize=(12, 6))

plt.plot(
    daily_pnl["Date"],
    daily_pnl["GrossPnL"]
)

plt.title(
    "Daily Gross P&L"
)

plt.xlabel(
    "Date"
)

plt.ylabel(
    "Gross P&L"
)

plt.xticks(
    rotation=45
)

save_chart(
    "12_daily_gross_pnl.png"
)


# ============================================================
# 18. DAILY REALIZED VS UNREALIZED P&L
# ============================================================

print("\n13. REALIZED VS UNREALIZED P&L")

daily_pnl_components = (
    positions
    .groupby(
        positions["PositionDate"].dt.date
    )
    .agg(
        RealizedPnL=("RealizedPnL", "sum"),
        UnrealizedPnL=("UnrealizedPnL", "sum")
    )
    .reset_index()
)


daily_pnl_components.columns = [
    "Date",
    "RealizedPnL",
    "UnrealizedPnL"
]


plt.figure(figsize=(12, 6))

plt.plot(
    daily_pnl_components["Date"],
    daily_pnl_components["RealizedPnL"],
    label="Realized P&L"
)

plt.plot(
    daily_pnl_components["Date"],
    daily_pnl_components["UnrealizedPnL"],
    label="Unrealized P&L"
)

plt.title(
    "Daily Realized vs Unrealized P&L"
)

plt.xlabel(
    "Date"
)

plt.ylabel(
    "P&L"
)

plt.legend()

plt.xticks(
    rotation=45
)

save_chart(
    "13_realized_vs_unrealized_pnl.png"
)


# ============================================================
# 19. TURNOVER VS GROSS P&L
# ============================================================

print("\n14. TURNOVER VS GROSS P&L")

turnover_pnl = daily_turnover.merge(
    daily_pnl,
    on="Date",
    how="inner"
)


plt.figure(figsize=(10, 6))

plt.scatter(
    turnover_pnl["Turnover"],
    turnover_pnl["GrossPnL"]
)

plt.title(
    "Trading Turnover vs Gross P&L"
)

plt.xlabel(
    "Turnover"
)

plt.ylabel(
    "Gross P&L"
)

save_chart(
    "14_turnover_vs_gross_pnl.png"
)


# ============================================================
# 20. EXECUTED QUANTITY BY SIDE
# ============================================================

print("\n15. BUY VS SELL EXECUTED QUANTITY")

side_quantity = (
    trades
    .groupby("Side")
    .agg(
        ExecutedQuantity=("ExecutedQuantity", "sum")
    )
)


plt.figure(figsize=(8, 6))

side_quantity["ExecutedQuantity"].plot(
    kind="bar"
)

plt.title(
    "Executed Quantity by Trade Side"
)

plt.xlabel(
    "Trade Side"
)

plt.ylabel(
    "Executed Quantity"
)

plt.xticks(
    rotation=0
)

save_chart(
    "15_buy_vs_sell_quantity.png"
)


# ============================================================
# 21. TOP 10 SYMBOLS BY TRADE COUNT
# ============================================================

print("\n16. TOP SYMBOLS BY TRADE COUNT")

top_symbol_trade_count = (
    trades
    .groupby("Symbol")
    .agg(
        Trades=("TradeID", "nunique")
    )
    .sort_values(
        "Trades",
        ascending=False
    )
    .head(10)
    .sort_values(
        "Trades"
    )
)


plt.figure(figsize=(10, 6))

plt.barh(
    top_symbol_trade_count.index.astype(str),
    top_symbol_trade_count["Trades"]
)

plt.title(
    "Top 10 Symbols by Trade Count"
)

plt.xlabel(
    "Number of Trades"
)

plt.ylabel(
    "Symbol"
)

save_chart(
    "16_top_symbols_by_trade_count.png"
)


# ============================================================
# 22. POSITION BUY VS SELL QUANTITY
# ============================================================

print("\n17. POSITION BUY VS SELL")

position_quantity = pd.Series({
    "Buy Quantity": positions["BuyQty"].sum(),
    "Sell Quantity": positions["SellQty"].sum()
})


plt.figure(figsize=(8, 6))

position_quantity.plot(
    kind="bar"
)

plt.title(
    "Position Buy vs Sell Quantity"
)

plt.xlabel(
    "Position Type"
)

plt.ylabel(
    "Quantity"
)

plt.xticks(
    rotation=0
)

save_chart(
    "17_position_buy_vs_sell.png"
)


# ============================================================
# 23. SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("VISUALIZATION COMPLETED")
print("=" * 70)

print(f"\nVisualization folder:")
print(VISUAL_DIR)

print("\nTotal charts created: 17")

print("\nDone.")