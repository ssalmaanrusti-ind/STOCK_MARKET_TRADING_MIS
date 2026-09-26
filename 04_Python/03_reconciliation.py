# ============================================================
# STOCK MARKET TRADING MIS & ANALYTICS
# 03 - ADVANCED TRADING ANALYSIS
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

CHARGES_FILE = DATA_DIR / "09_Brokerage_Charges.csv"

POSITION_FILE = DATA_DIR / "10_Position_Data.csv"

CLIENT_FILE = DATA_DIR / "02_Client_Master.csv"

INSTRUMENT_FILE = DATA_DIR / "01_Instrument_Master.csv"

# ============================================================
# 3. LOAD DATA
# ============================================================

print("=" * 70)
print("ADVANCED TRADING ANALYSIS")
print("=" * 70)

orders = pd.read_csv(ORDER_FILE)
trades = pd.read_csv(TRADE_FILE)
rejections = pd.read_csv(REJECTION_FILE)
charges = pd.read_csv(CHARGES_FILE)
positions = pd.read_csv(POSITION_FILE)
clients = pd.read_csv(CLIENT_FILE)
instruments = pd.read_csv(INSTRUMENT_FILE)

print("\nDATA LOADED")
print("-" * 70)

print(f"Orders loaded       : {len(orders):,}")
print(f"Trades loaded       : {len(trades):,}")
print(f"Rejections loaded   : {len(rejections):,}")
print(f"Charges loaded      : {len(charges):,}")
print(f"Positions loaded    : {len(positions):,}")


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

trades["ExecutionDate"] = pd.to_datetime(
    trades["ExecutionDate"],
    errors="coerce"
)

trades["ExecutionDateTime"] = pd.to_datetime(
    trades["ExecutionDateTime"],
    errors="coerce"
)

trades["SettlementDate"] = pd.to_datetime(
    trades["SettlementDate"],
    errors="coerce"
)

positions["PositionDate"] = pd.to_datetime(
    positions["PositionDate"],
    errors="coerce"
)


# ============================================================
# 5. REJECTION ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("1. REJECTION ANALYSIS")
print("=" * 70)


# Rejection reason summary

rejection_reason = (
    rejections
    .groupby("RejectionReason", as_index=False)
    .agg(
        RejectedOrders=("RejectionID", "nunique")
    )
    .sort_values(
        "RejectedOrders",
        ascending=False
    )
)

rejection_reason["RejectionPct"] = (
    rejection_reason["RejectedOrders"]
    / rejection_reason["RejectedOrders"].sum()
    * 100
)


# Client rejection

client_rejection = (
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

client_rejection["RejectionRatePct"] = (
    client_rejection["RejectedOrders"]
    / client_rejection["TotalOrders"]
    * 100
)

client_rejection = client_rejection.merge(
    clients,
    on="ClientID",
    how="left"
)

client_rejection = client_rejection.sort_values(
    "RejectionRatePct",
    ascending=False
)


# Symbol rejection

symbol_rejection = (
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

symbol_rejection["RejectionRatePct"] = (
    symbol_rejection["RejectedOrders"]
    / symbol_rejection["TotalOrders"]
    * 100
)

symbol_rejection = symbol_rejection.sort_values(
    "RejectionRatePct",
    ascending=False
)


# High rejection clients
# Rule: minimum 20 orders and rejection rate >= 20%

high_rejection_clients = client_rejection[
    (
        client_rejection["TotalOrders"] >= 20
    )
    &
    (
        client_rejection["RejectionRatePct"] >= 20
    )
].copy()


# High rejection symbols

high_rejection_symbols = symbol_rejection[
    (
        symbol_rejection["TotalOrders"] >= 20
    )
    &
    (
        symbol_rejection["RejectionRatePct"] >= 20
    )
].copy()


print(
    f"High rejection clients  : "
    f"{len(high_rejection_clients):,}"
)

print(
    f"High rejection symbols  : "
    f"{len(high_rejection_symbols):,}"
)


# ============================================================
# 6. SLIPPAGE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("2. SLIPPAGE ANALYSIS")
print("=" * 70)


# Merge order price into trades

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


# Only orders where OrderPrice exists
# MARKET orders may legitimately have blank OrderPrice.

limit_slippage = trade_slippage[
    trade_slippage["OrderPrice"].notna()
].copy()


# Direction-aware adverse slippage

limit_slippage["AdverseSlippage"] = np.where(
    limit_slippage["Side"] == "BUY",
    limit_slippage["ExecutionPrice"]
    - limit_slippage["OrderPrice"],
    limit_slippage["OrderPrice"]
    - limit_slippage["ExecutionPrice"]
)


limit_slippage["AdverseSlippagePct"] = np.where(
    limit_slippage["OrderPrice"] != 0,
    limit_slippage["AdverseSlippage"]
    / limit_slippage["OrderPrice"]
    * 100,
    np.nan
)


# Overall slippage summary

slippage_summary = pd.DataFrame({
    "Metric": [
        "Trades with Order Price",
        "Average Slippage",
        "Average Slippage %",
        "Maximum Adverse Slippage %",
        "Positive Adverse Slippage Trades"
    ],
    "Value": [
        len(limit_slippage),
        limit_slippage["AdverseSlippage"].mean(),
        limit_slippage["AdverseSlippagePct"].mean(),
        limit_slippage["AdverseSlippagePct"].max(),
        (
            limit_slippage["AdverseSlippage"] > 0
        ).sum()
    ]
})


# High slippage
# Analytical threshold: > 1%

high_slippage = limit_slippage[
    limit_slippage["AdverseSlippagePct"].abs() > 1
].copy()

high_slippage = high_slippage.sort_values(
    "AdverseSlippagePct",
    ascending=False
)


print(
    f"Trades with order price : "
    f"{len(limit_slippage):,}"
)

print(
    f"High slippage trades    : "
    f"{len(high_slippage):,}"
)


# ============================================================
# 7. BROKERAGE & TRANSACTION CHARGES
# ============================================================

print("\n" + "=" * 70)
print("3. BROKERAGE & TRANSACTION CHARGES")
print("=" * 70)


charge_columns = [
    "Brokerage",
    "STT",
    "ExchangeCharges",
    "GST",
    "SEBICharges",
    "StampDuty",
    "TotalCharges"
]

available_charge_columns = [
    col
    for col in charge_columns
    if col in charges.columns
]


charge_summary = pd.DataFrame({
    "ChargeType": available_charge_columns,
    "TotalAmount": [
        charges[col].sum()
        for col in available_charge_columns
    ]
})


if "TotalCharges" in charges.columns:

    charge_summary["PercentageOfTotalCharges"] = (
        charge_summary["TotalAmount"]
        / charges["TotalCharges"].sum()
        * 100
    )


print(
    f"Total Transaction Charges : "
    f"₹{charges['TotalCharges'].sum():,.2f}"
)


# Client charges

client_charges = (
    charges
    .groupby("ClientID", as_index=False)
    .agg(
        TotalCharges=("TotalCharges", "sum")
    )
    .sort_values(
        "TotalCharges",
        ascending=False
    )
)


# ============================================================
# 8. P&L ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("4. P&L ANALYSIS")
print("=" * 70)


pnl_columns = [
    "GrossPnL",
    "RealizedPnL",
    "UnrealizedPnL"
]

available_pnl_columns = [
    col
    for col in pnl_columns
    if col in positions.columns
]


pnl_summary = pd.DataFrame({
    "Metric": available_pnl_columns,
    "Total": [
        positions[col].sum()
        for col in available_pnl_columns
    ]
})


# Client P&L

client_pnl = (
    positions
    .groupby("ClientID", as_index=False)
    .agg(
        GrossPnL=("GrossPnL", "sum"),
        RealizedPnL=("RealizedPnL", "sum"),
        UnrealizedPnL=("UnrealizedPnL", "sum")
    )
    .sort_values(
        "GrossPnL",
        ascending=False
    )
)


print(
    f"Gross P&L total : "
    f"₹{positions['GrossPnL'].sum():,.2f}"
)


# ============================================================
# 9. POSITION INTERNAL RECONCILIATION
# ============================================================

print("\n" + "=" * 70)
print("5. POSITION RECONCILIATION")
print("=" * 70)


position_reconciliation = positions[
    [
        "PositionID",
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


position_exceptions = position_reconciliation[
    position_reconciliation["Difference"] != 0
].copy()


position_exceptions = position_exceptions.sort_values(
    by="Difference",
    key=lambda x: x.abs(),
    ascending=False
)


print(
    f"Position records checked : "
    f"{len(position_reconciliation):,}"
)

print(
    f"Position exceptions      : "
    f"{len(position_exceptions):,}"
)


# ============================================================
# 10. TRADE VS POSITION RECONCILIATION
# ============================================================

print("\n" + "=" * 70)
print("6. TRADE VS POSITION RECONCILIATION")
print("=" * 70)


# Separate BUY and SELL trades

buy_trades = trades[
    trades["Side"] == "BUY"
].copy()

sell_trades = trades[
    trades["Side"] == "SELL"
].copy()


# Aggregate executed trades

trade_buy = (
    buy_trades
    .groupby(
        [
            "AccountID",
            "ClientID",
            "InstrumentID",
            "Symbol"
        ],
        as_index=False
    )
    .agg(
        TradeBuyQty=("ExecutedQuantity", "sum")
    )
)


trade_sell = (
    sell_trades
    .groupby(
        [
            "AccountID",
            "ClientID",
            "InstrumentID",
            "Symbol"
        ],
        as_index=False
    )
    .agg(
        TradeSellQty=("ExecutedQuantity", "sum")
    )
)


# Combine BUY and SELL

trade_position_check = trade_buy.merge(
    trade_sell,
    on=[
        "AccountID",
        "ClientID",
        "InstrumentID",
        "Symbol"
    ],
    how="outer"
)


trade_position_check["TradeBuyQty"] = (
    trade_position_check["TradeBuyQty"]
    .fillna(0)
)

trade_position_check["TradeSellQty"] = (
    trade_position_check["TradeSellQty"]
    .fillna(0)
)


trade_position_check["TradeNetQty"] = (
    trade_position_check["TradeBuyQty"]
    - trade_position_check["TradeSellQty"]
)


# Aggregate positions

position_summary = (
    positions
    .groupby(
        [
            "AccountID",
            "ClientID",
            "InstrumentID",
            "Symbol"
        ],
        as_index=False
    )
    .agg(
        PositionBuyQty=("BuyQty", "sum"),
        PositionSellQty=("SellQty", "sum"),
        PositionNetQty=("NetQuantity", "sum")
    )
)


# Merge

trade_position_check = trade_position_check.merge(
    position_summary,
    on=[
        "AccountID",
        "ClientID",
        "InstrumentID",
        "Symbol"
    ],
    how="outer"
)


# Fill missing quantities

quantity_columns = [
    "TradeBuyQty",
    "TradeSellQty",
    "TradeNetQty",
    "PositionBuyQty",
    "PositionSellQty",
    "PositionNetQty"
]


for col in quantity_columns:

    trade_position_check[col] = (
        trade_position_check[col]
        .fillna(0)
    )


# Differences

trade_position_check["BuyQtyDifference"] = (
    trade_position_check["TradeBuyQty"]
    - trade_position_check["PositionBuyQty"]
)


trade_position_check["SellQtyDifference"] = (
    trade_position_check["TradeSellQty"]
    - trade_position_check["PositionSellQty"]
)


trade_position_check["NetQtyDifference"] = (
    trade_position_check["TradeNetQty"]
    - trade_position_check["PositionNetQty"]
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


trade_position_exceptions = trade_position_check[
    trade_position_check["ReconciliationStatus"] == "MISMATCH"
].copy()


print(
    f"Trade-position records : "
    f"{len(trade_position_check):,}"
)

print(
    f"Matching records       : "
    f"{(
        trade_position_check['ReconciliationStatus'] == 'MATCH'
    ).sum():,}"
)

print(
    f"Mismatched records     : "
    f"{len(trade_position_exceptions):,}"
)


# ============================================================
# 11. CLIENT TRADE ACTIVITY
# ============================================================

print("\n" + "=" * 70)
print("7. CLIENT ACTIVITY")
print("=" * 70)


client_trade_activity = (
    trades
    .groupby("ClientID", as_index=False)
    .agg(
        TradeCount=("TradeID", "nunique"),
        TotalTurnover=("TradeValue", "sum"),
        TotalExecutedQty=("ExecutedQuantity", "sum"),
        AvgExecutionTime=("ExecutionTimeSeconds", "mean")
    )
    .sort_values(
        "TotalTurnover",
        ascending=False
    )
)


# High volume clients
# Analytical rule: mean + 2 standard deviations

client_volume_mean = client_trade_activity[
    "TradeCount"
].mean()

client_volume_std = client_trade_activity[
    "TradeCount"
].std()

client_volume_threshold = (
    client_volume_mean
    + 2 * client_volume_std
)


high_volume_clients = client_trade_activity[
    client_trade_activity["TradeCount"]
    > client_volume_threshold
].copy()


print(
    f"High-volume clients : "
    f"{len(high_volume_clients):,}"
)


# ============================================================
# 12. SYMBOL ACTIVITY
# ============================================================

symbol_trade_activity = (
    trades
    .groupby(
        ["InstrumentID", "Symbol"],
        as_index=False
    )
    .agg(
        TradeCount=("TradeID", "nunique"),
        TotalTurnover=("TradeValue", "sum"),
        TotalExecutedQty=("ExecutedQuantity", "sum")
    )
    .sort_values(
        "TotalTurnover",
        ascending=False
    )
)


symbol_volume_mean = symbol_trade_activity[
    "TradeCount"
].mean()

symbol_volume_std = symbol_trade_activity[
    "TradeCount"
].std()

symbol_volume_threshold = (
    symbol_volume_mean
    + 2 * symbol_volume_std
)


high_volume_symbols = symbol_trade_activity[
    symbol_trade_activity["TradeCount"]
    > symbol_volume_threshold
].copy()


print(
    f"High-volume symbols : "
    f"{len(high_volume_symbols):,}"
)


# ============================================================
# 13. DAILY ACTIVITY SPIKES
# ============================================================

daily_activity = (
    trades
    .groupby(
        "TradeDate",
        as_index=False
    )
    .agg(
        Trades=("TradeID", "nunique"),
        Turnover=("TradeValue", "sum")
    )
    .sort_values("TradeDate")
)


daily_activity["Rolling7DayAvgTrades"] = (
    daily_activity["Trades"]
    .rolling(7)
    .mean()
)


daily_activity["ActivityChangePct"] = (
    (
        daily_activity["Trades"]
        - daily_activity["Rolling7DayAvgTrades"]
    )
    / daily_activity["Rolling7DayAvgTrades"]
    * 100
)


# Analytical rule: activity >= 50% above rolling average

activity_spikes = daily_activity[
    daily_activity["ActivityChangePct"] >= 50
].copy()


print(
    f"Activity spike days : "
    f"{len(activity_spikes):,}"
)


# ============================================================
# 14. P&L VS TURNOVER
# ============================================================

position_daily_pnl = (
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

position_daily_pnl = position_daily_pnl.rename(
    columns={
        "PositionDate": "AnalysisDate"
    }
)


trade_daily_turnover = (
    trades
    .groupby(
        trades["TradeDate"].dt.date,
        as_index=False
    )
    .agg(
        Turnover=("TradeValue", "sum"),
        Trades=("TradeID", "nunique")
    )
)

trade_daily_turnover = trade_daily_turnover.rename(
    columns={
        "TradeDate": "AnalysisDate"
    }
)


daily_pnl_turnover = position_daily_pnl.merge(
    trade_daily_turnover,
    on="AnalysisDate",
    how="left"
)


daily_pnl_turnover["PnLToTurnoverPct"] = np.where(
    daily_pnl_turnover["Turnover"] != 0,
    daily_pnl_turnover["GrossPnL"]
    / daily_pnl_turnover["Turnover"]
    * 100,
    np.nan
)


# ============================================================
# 15. EXECUTIVE SUMMARY
# ============================================================

executive_summary = pd.DataFrame({
    "Metric": [
        "Total Orders",
        "Total Trades",
        "Total Rejections",
        "Total Turnover",
        "Total Transaction Charges",
        "Gross P&L",
        "Position Exceptions",
        "Trade-Position Mismatches",
        "High Slippage Trades",
        "High Rejection Clients",
        "High Rejection Symbols",
        "High Volume Clients",
        "High Volume Symbols",
        "Activity Spike Days"
    ],
    "Value": [
        len(orders),
        len(trades),
        len(rejections),
        trades["TradeValue"].sum(),
        charges["TotalCharges"].sum(),
        positions["GrossPnL"].sum(),
        len(position_exceptions),
        len(trade_position_exceptions),
        len(high_slippage),
        len(high_rejection_clients),
        len(high_rejection_symbols),
        len(high_volume_clients),
        len(high_volume_symbols),
        len(activity_spikes)
    ]
})


# ============================================================
# 16. EXPORT ADVANCED REPORT
# ============================================================

advanced_output = (
    OUTPUT_DIR
    / "Advanced_Trading_Analysis.xlsx"
)


with pd.ExcelWriter(
    advanced_output,
    engine="openpyxl"
) as writer:

    executive_summary.to_excel(
        writer,
        sheet_name="Executive_Summary",
        index=False
    )

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


# ============================================================
# 17. FINAL MESSAGE
# ============================================================

print("\n" + "=" * 70)
print("ADVANCED ANALYSIS COMPLETED")
print("=" * 70)

print(
    f"\nOutput file:\n{advanced_output}"
)

print("\nSheets created:")
print("1.  Executive_Summary")
print("2.  Rejection_Reason")
print("3.  Client_Rejection")
print("4.  Symbol_Rejection")
print("5.  High_Rejection_Clients")
print("6.  High_Rejection_Symbols")
print("7.  Slippage_Summary")
print("8.  High_Slippage")
print("9.  Charge_Summary")
print("10. Client_Charges")
print("11. PnL_Summary")
print("12. Client_PnL")
print("13. Position_Reconciliation")
print("14. Position_Exceptions")
print("15. Trade_Position_Reconciliation")
print("16. Trade_Position_Exceptions")
print("17. Client_Activity")
print("18. Symbol_Activity")
print("19. High_Volume_Clients")
print("20. High_Volume_Symbols")
print("21. Activity_Spikes")
print("22. PnL_vs_Turnover")

print("\nDone.")