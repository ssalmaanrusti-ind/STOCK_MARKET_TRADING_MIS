# ============================================================
# STOCK MARKET TRADING MIS & ANALYTICS
# 04 - ANOMALY DETECTION
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# 1. PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(r"D:\STOCK_MARKET_TRADING_MIS")

DATA_DIR = BASE_DIR / "01_Raw_Data"
OUTPUT_DIR = BASE_DIR / "07_Output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. FILE PATHS
# ============================================================

ORDER_FILE = DATA_DIR / "06_Order_Book.csv"

TRADE_FILE = DATA_DIR / "07_Trade_Execution_Book.csv"

REJECTION_FILE = DATA_DIR / "08_Order_Rejection_Data.csv"


# ============================================================
# 3. LOAD DATA
# ============================================================

print("=" * 70)
print("STOCK MARKET ANOMALY DETECTION")
print("=" * 70)

orders = pd.read_csv(ORDER_FILE)

trades = pd.read_csv(TRADE_FILE)

rejections = pd.read_csv(REJECTION_FILE)


print("\nDATA LOADED")
print("-" * 70)

print(f"Orders loaded       : {len(orders):,}")
print(f"Trades loaded       : {len(trades):,}")
print(f"Rejections loaded   : {len(rejections):,}")


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


# ============================================================
# 5. ANOMALY 1 - HIGH VOLUME CLIENTS
# ============================================================

print("\n" + "=" * 70)
print("1. HIGH VOLUME CLIENTS")
print("=" * 70)


client_activity = (
    trades
    .groupby("ClientID", as_index=False)
    .agg(
        TradeCount=("TradeID", "nunique"),
        TotalTurnover=("TradeValue", "sum"),
        ExecutedQuantity=("ExecutedQuantity", "sum")
    )
)


client_mean = client_activity["TradeCount"].mean()

client_std = client_activity["TradeCount"].std()

client_threshold = client_mean + (2 * client_std)


high_volume_clients = client_activity[
    client_activity["TradeCount"] > client_threshold
].copy()


high_volume_clients["AnomalyType"] = (
    "Unusually High Client Trade Volume"
)

high_volume_clients["Threshold"] = client_threshold

high_volume_clients = high_volume_clients.sort_values(
    "TradeCount",
    ascending=False
)


print(f"Mean trades/client      : {client_mean:,.2f}")

print(f"Anomaly threshold       : {client_threshold:,.2f}")

print(
    f"High-volume clients     : "
    f"{len(high_volume_clients):,}"
)


# ============================================================
# 6. ANOMALY 2 - HIGH VOLUME SYMBOLS
# ============================================================

print("\n" + "=" * 70)
print("2. HIGH VOLUME SYMBOLS")
print("=" * 70)


symbol_activity = (
    trades
    .groupby(
        ["InstrumentID", "Symbol"],
        as_index=False
    )
    .agg(
        TradeCount=("TradeID", "nunique"),
        TotalTurnover=("TradeValue", "sum"),
        ExecutedQuantity=("ExecutedQuantity", "sum")
    )
)


symbol_mean = symbol_activity["TradeCount"].mean()

symbol_std = symbol_activity["TradeCount"].std()

symbol_threshold = symbol_mean + (2 * symbol_std)


high_volume_symbols = symbol_activity[
    symbol_activity["TradeCount"] > symbol_threshold
].copy()


high_volume_symbols["AnomalyType"] = (
    "Unusually High Symbol Trade Volume"
)

high_volume_symbols["Threshold"] = symbol_threshold

high_volume_symbols = high_volume_symbols.sort_values(
    "TradeCount",
    ascending=False
)


print(f"Mean trades/symbol      : {symbol_mean:,.2f}")

print(f"Anomaly threshold       : {symbol_threshold:,.2f}")

print(
    f"High-volume symbols     : "
    f"{len(high_volume_symbols):,}"
)


# ============================================================
# 7. ANOMALY 3 - HIGH REJECTION CLIENTS
# ============================================================

print("\n" + "=" * 70)
print("3. HIGH REJECTION-RATE CLIENTS")
print("=" * 70)


client_orders = (
    orders
    .groupby("ClientID", as_index=False)
    .agg(
        TotalOrders=("OrderID", "nunique"),
        RejectedOrders=(
            "Status",
            lambda x: (x == "REJECTED").sum()
        )
    )
)


client_orders["RejectionRatePct"] = np.where(
    client_orders["TotalOrders"] > 0,
    client_orders["RejectedOrders"]
    / client_orders["TotalOrders"]
    * 100,
    0
)


# Minimum 20 orders avoids flagging very small samples

high_rejection_clients = client_orders[
    (
        client_orders["TotalOrders"] >= 20
    )
    &
    (
        client_orders["RejectionRatePct"] >= 20
    )
].copy()


high_rejection_clients["AnomalyType"] = (
    "High Client Rejection Rate"
)

high_rejection_clients = high_rejection_clients.sort_values(
    "RejectionRatePct",
    ascending=False
)


print(
    f"High rejection clients : "
    f"{len(high_rejection_clients):,}"
)


# ============================================================
# 8. ANOMALY 4 - HIGH REJECTION SYMBOLS
# ============================================================

print("\n" + "=" * 70)
print("4. HIGH REJECTION-RATE SYMBOLS")
print("=" * 70)


symbol_orders = (
    orders
    .groupby(
        ["InstrumentID", "Symbol"],
        as_index=False
    )
    .agg(
        TotalOrders=("OrderID", "nunique"),
        RejectedOrders=(
            "Status",
            lambda x: (x == "REJECTED").sum()
        )
    )
)


symbol_orders["RejectionRatePct"] = np.where(
    symbol_orders["TotalOrders"] > 0,
    symbol_orders["RejectedOrders"]
    / symbol_orders["TotalOrders"]
    * 100,
    0
)


high_rejection_symbols = symbol_orders[
    (
        symbol_orders["TotalOrders"] >= 20
    )
    &
    (
        symbol_orders["RejectionRatePct"] >= 20
    )
].copy()


high_rejection_symbols["AnomalyType"] = (
    "High Symbol Rejection Rate"
)

high_rejection_symbols = high_rejection_symbols.sort_values(
    "RejectionRatePct",
    ascending=False
)


print(
    f"High rejection symbols : "
    f"{len(high_rejection_symbols):,}"
)


# ============================================================
# 9. ANOMALY 5 - HIGH SLIPPAGE
# ============================================================

print("\n" + "=" * 70)
print("5. HIGH SLIPPAGE")
print("=" * 70)


trade_slippage = trades.merge(
    orders[
        [
            "OrderID",
            "OrderPrice",
            "OrderType"
        ]
    ],
    on="OrderID",
    how="left"
)


# MARKET orders may have blank OrderPrice.
# Slippage against order price is calculated only
# where OrderPrice exists.

slippage_data = trade_slippage[
    trade_slippage["OrderPrice"].notna()
].copy()


# Direction-aware adverse slippage

slippage_data["AdverseSlippage"] = np.where(
    slippage_data["Side"] == "BUY",

    slippage_data["ExecutionPrice"]
    - slippage_data["OrderPrice"],

    slippage_data["OrderPrice"]
    - slippage_data["ExecutionPrice"]
)


slippage_data["AdverseSlippagePct"] = np.where(
    slippage_data["OrderPrice"] != 0,

    slippage_data["AdverseSlippage"]
    / slippage_data["OrderPrice"]
    * 100,

    np.nan
)


# Analytical threshold: absolute adverse slippage > 1%

high_slippage = slippage_data[
    slippage_data["AdverseSlippagePct"].abs() > 1
].copy()


high_slippage["AnomalyType"] = (
    "High Execution Slippage"
)


high_slippage = high_slippage.sort_values(
    "AdverseSlippagePct",
    ascending=False
)


print(
    f"Trades with order price : "
    f"{len(slippage_data):,}"
)

print(
    f"High-slippage trades    : "
    f"{len(high_slippage):,}"
)


# ============================================================
# 10. ANOMALY 6 - DAILY ACTIVITY SPIKES
# ============================================================

print("\n" + "=" * 70)
print("6. DAILY ACTIVITY SPIKES")
print("=" * 70)


daily_activity = (
    trades
    .groupby(
        trades["TradeDate"].dt.date,
        as_index=False
    )
    .agg(
        Trades=("TradeID", "nunique"),
        Turnover=("TradeValue", "sum"),
        ExecutedQuantity=("ExecutedQuantity", "sum")
    )
)


daily_activity = daily_activity.rename(
    columns={
        "TradeDate": "TradeDay"
    }
)


daily_activity["Rolling7DayAvgTrades"] = (
    daily_activity["Trades"]
    .rolling(
        window=7,
        min_periods=3
    )
    .mean()
)


daily_activity["ActivityChangePct"] = np.where(
    daily_activity["Rolling7DayAvgTrades"] > 0,

    (
        (
            daily_activity["Trades"]
            - daily_activity["Rolling7DayAvgTrades"]
        )
        / daily_activity["Rolling7DayAvgTrades"]
    )
    * 100,

    np.nan
)


# Activity spike threshold = 50% above rolling average

activity_spikes = daily_activity[
    daily_activity["ActivityChangePct"] >= 50
].copy()


activity_spikes["AnomalyType"] = (
    "Sudden Trading Activity Increase"
)


activity_spikes = activity_spikes.sort_values(
    "ActivityChangePct",
    ascending=False
)


print(
    f"Activity spike days : "
    f"{len(activity_spikes):,}"
)


# ============================================================
# 11. ANOMALY 7 - DAILY TURNOVER SPIKES
# ============================================================

print("\n" + "=" * 70)
print("7. DAILY TURNOVER SPIKES")
print("=" * 70)


daily_activity["Rolling7DayAvgTurnover"] = (
    daily_activity["Turnover"]
    .rolling(
        window=7,
        min_periods=3
    )
    .mean()
)


daily_activity["TurnoverChangePct"] = np.where(
    daily_activity["Rolling7DayAvgTurnover"] > 0,

    (
        (
            daily_activity["Turnover"]
            - daily_activity["Rolling7DayAvgTurnover"]
        )
        / daily_activity["Rolling7DayAvgTurnover"]
    )
    * 100,

    np.nan
)


turnover_spikes = daily_activity[
    daily_activity["TurnoverChangePct"] >= 50
].copy()


turnover_spikes["AnomalyType"] = (
    "Sudden Turnover Increase"
)


turnover_spikes = turnover_spikes.sort_values(
    "TurnoverChangePct",
    ascending=False
)


print(
    f"Turnover spike days : "
    f"{len(turnover_spikes):,}"
)


# ============================================================
# 12. ANOMALY 8 - CLIENT TURNOVER CONCENTRATION
# ============================================================

print("\n" + "=" * 70)
print("8. CLIENT TURNOVER CONCENTRATION")
print("=" * 70)


client_turnover = (
    trades
    .groupby(
        "ClientID",
        as_index=False
    )
    .agg(
        Turnover=("TradeValue", "sum"),
        TradeCount=("TradeID", "nunique")
    )
)


total_turnover = client_turnover["Turnover"].sum()


client_turnover["TurnoverSharePct"] = np.where(
    total_turnover > 0,

    client_turnover["Turnover"]
    / total_turnover
    * 100,

    0
)


# Flag clients contributing >= 2% of total turnover

high_turnover_concentration = client_turnover[
    client_turnover["TurnoverSharePct"] >= 2
].copy()


high_turnover_concentration["AnomalyType"] = (
    "High Client Turnover Concentration"
)


high_turnover_concentration = (
    high_turnover_concentration
    .sort_values(
        "TurnoverSharePct",
        ascending=False
    )
)


print(
    f"High turnover-concentration clients : "
    f"{len(high_turnover_concentration):,}"
)


# ============================================================
# 13. ANOMALY 9 - P&L VS TURNOVER
# ============================================================

print("\n" + "=" * 70)
print("9. P&L VS TURNOVER ANOMALIES")
print("=" * 70)


# P&L is available in Position Data,
# while turnover comes from executed trades.

POSITION_FILE = DATA_DIR / "10_Position_Data.csv"

positions = pd.read_csv(POSITION_FILE)


positions["PositionDate"] = pd.to_datetime(
    positions["PositionDate"],
    errors="coerce"
)


daily_pnl = (
    positions
    .groupby(
        positions["PositionDate"].dt.date,
        as_index=False
    )
    .agg(
        GrossPnL=("GrossPnL", "sum"),
        RealizedPnL=("RealizedPnL", "sum"),
        UnrealizedPnL=("UnrealizedPnL", "sum")
    )
)


daily_pnl = daily_pnl.rename(
    columns={
        "PositionDate": "TradeDay"
    }
)


daily_pnl = daily_pnl.merge(
    daily_activity[
        [
            "TradeDay",
            "Trades",
            "Turnover"
        ]
    ],
    on="TradeDay",
    how="left"
)


daily_pnl["PnLToTurnoverPct"] = np.where(
    daily_pnl["Turnover"] != 0,

    daily_pnl["GrossPnL"]
    / daily_pnl["Turnover"]
    * 100,

    np.nan
)


# Rolling statistics

daily_pnl["RollingPnLMean"] = (
    daily_pnl["GrossPnL"]
    .rolling(
        window=7,
        min_periods=3
    )
    .mean()
)


daily_pnl["RollingPnLStd"] = (
    daily_pnl["GrossPnL"]
    .rolling(
        window=7,
        min_periods=3
    )
    .std()
)


daily_pnl["PnLDeviation"] = np.where(
    daily_pnl["RollingPnLStd"] > 0,

    (
        daily_pnl["GrossPnL"]
        - daily_pnl["RollingPnLMean"]
    )
    / daily_pnl["RollingPnLStd"],

    0
)


# Flag P&L observations more than 2 standard deviations
# away from recent rolling average.

pnl_anomalies = daily_pnl[
    daily_pnl["PnLDeviation"].abs() >= 2
].copy()


pnl_anomalies["AnomalyType"] = (
    "Unusual Daily P&L Movement"
)


pnl_anomalies = pnl_anomalies.sort_values(
    "PnLDeviation",
    key=lambda x: x.abs(),
    ascending=False
)


print(
    f"P&L anomaly days : "
    f"{len(pnl_anomalies):,}"
)


# ============================================================
# 14. ANOMALY 10 - LARGE P&L CHANGE
# ============================================================

daily_pnl = daily_pnl.sort_values(
    "TradeDay"
)


daily_pnl["PreviousDayPnL"] = (
    daily_pnl["GrossPnL"]
    .shift(1)
)


daily_pnl["PnLChangePct"] = np.where(
    daily_pnl["PreviousDayPnL"].abs() > 0,

    (
        (
            daily_pnl["GrossPnL"]
            - daily_pnl["PreviousDayPnL"]
        )
        / daily_pnl["PreviousDayPnL"].abs()
    )
    * 100,

    np.nan
)


large_pnl_changes = daily_pnl[
    daily_pnl["PnLChangePct"].abs() >= 50
].copy()


large_pnl_changes["AnomalyType"] = (
    "Large Day-over-Day P&L Change"
)


large_pnl_changes = large_pnl_changes.sort_values(
    "PnLChangePct",
    key=lambda x: x.abs(),
    ascending=False
)


print(
    f"Large P&L change days : "
    f"{len(large_pnl_changes):,}"
)


# ============================================================
# 15. MASTER ANOMALY SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("MASTER ANOMALY SUMMARY")
print("=" * 70)


anomaly_summary = pd.DataFrame({
    "AnomalyCategory": [
        "High Volume Clients",
        "High Volume Symbols",
        "High Rejection Clients",
        "High Rejection Symbols",
        "High Slippage Trades",
        "Activity Spike Days",
        "Turnover Spike Days",
        "High Turnover Concentration Clients",
        "P&L Anomaly Days",
        "Large P&L Change Days"
    ],

    "AnomalyCount": [
        len(high_volume_clients),
        len(high_volume_symbols),
        len(high_rejection_clients),
        len(high_rejection_symbols),
        len(high_slippage),
        len(activity_spikes),
        len(turnover_spikes),
        len(high_turnover_concentration),
        len(pnl_anomalies),
        len(large_pnl_changes)
    ]
})


anomaly_summary = anomaly_summary.sort_values(
    "AnomalyCount",
    ascending=False
)


# ============================================================
# 16. EXPORT REPORT
# ============================================================

output_file = (
    OUTPUT_DIR
    / "Anomaly_Detection_Report.xlsx"
)


with pd.ExcelWriter(
    output_file,
    engine="openpyxl"
) as writer:

    anomaly_summary.to_excel(
        writer,
        sheet_name="Anomaly_Summary",
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

    high_slippage.to_excel(
        writer,
        sheet_name="High_Slippage",
        index=False
    )

    activity_spikes.to_excel(
        writer,
        sheet_name="Activity_Spikes",
        index=False
    )

    turnover_spikes.to_excel(
        writer,
        sheet_name="Turnover_Spikes",
        index=False
    )

    high_turnover_concentration.to_excel(
        writer,
        sheet_name="Turnover_Concentration",
        index=False
    )

    pnl_anomalies.to_excel(
        writer,
        sheet_name="PnL_Anomalies",
        index=False
    )

    large_pnl_changes.to_excel(
        writer,
        sheet_name="Large_PnL_Changes",
        index=False
    )

    daily_pnl.to_excel(
        writer,
        sheet_name="Daily_PnL_Analysis",
        index=False
    )

    daily_activity.to_excel(
        writer,
        sheet_name="Daily_Activity",
        index=False
    )


# ============================================================
# 17. FINAL OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("ANOMALY DETECTION COMPLETED")
print("=" * 70)

print(f"\nOutput file:")
print(output_file)

print("\nSheets created:")
print("1.  Anomaly_Summary")
print("2.  High_Volume_Clients")
print("3.  High_Volume_Symbols")
print("4.  High_Rejection_Clients")
print("5.  High_Rejection_Symbols")
print("6.  High_Slippage")
print("7.  Activity_Spikes")
print("8.  Turnover_Spikes")
print("9.  Turnover_Concentration")
print("10. PnL_Anomalies")
print("11. Large_PnL_Changes")
print("12. Daily_PnL_Analysis")
print("13. Daily_Activity")

print("\nDone.")