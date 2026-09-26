# ============================================================
# STOCK MARKET MIS PROJECT
# 01_DATA_QUALITY.PY
# ============================================================
# Purpose:
#   Perform complete data-quality validation across all
#   stock-market trading MIS datasets.
#
# Input:
#   01_Raw_Data/*.csv
#
# Output:
#   02_Data_Quality/Stock_Market_Data_Quality_Report.xlsx
# ============================================================

import os
import pandas as pd
import numpy as np


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(BASE_DIR, "01_Raw_Data")
OUTPUT_DIR = os.path.join(BASE_DIR, "02_Data_Quality")

os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "Stock_Market_Data_Quality_Report.xlsx"
)


# ============================================================
# 2. FILE CONFIGURATION
# ============================================================

FILES = {
    "Instrument_Master": "01_Instrument_Master.csv",
    "Client_Master": "02_Client_Master.csv",
    "Account_Portfolio": "03_Account_Portfolio.csv",
    "Funds_Margin": "04_Funds_Margin.csv",
    "Market_Price_Data": "05_Market_Price_Data.csv",
    "Order_Book": "06_Order_Book.csv",
    "Trade_Execution_Book": "07_Trade_Execution_Book.csv",
    "Order_Rejection_Data": "08_Order_Rejection_Data.csv",
    "Brokerage_Charges": "09_Brokerage_Charges.csv",
    "Position_Data": "10_Position_Data.csv"
}


# ============================================================
# 3. LOAD DATA
# ============================================================

print("=" * 70)
print("STOCK MARKET MIS - DATA QUALITY ANALYSIS")
print("=" * 70)

data = {}

for table_name, file_name in FILES.items():

    file_path = os.path.join(RAW_DIR, file_name)

    try:
        df = pd.read_csv(file_path)

        data[table_name] = df

        print(
            f"Loaded: {file_name:<35} "
            f"{len(df):>10,} rows | {len(df.columns):>3} columns"
        )

    except Exception as e:

        print(f"ERROR loading {file_name}: {e}")


print("=" * 70)


# ============================================================
# 4. TABLE PROFILE
# ============================================================

table_profile = []

for table_name, df in data.items():

    table_profile.append({
        "Table": table_name,
        "Rows": len(df),
        "Columns": len(df.columns),
        "Memory_MB": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
        "Duplicate_Rows": int(df.duplicated().sum()),
        "Null_Cells": int(df.isna().sum().sum()),
        "Null_Percentage": round(
            df.isna().sum().sum() /
            (len(df) * len(df.columns)) * 100,
            2
        ) if len(df) > 0 else 0
    })

table_profile_df = pd.DataFrame(table_profile)


# ============================================================
# 5. COLUMN PROFILE
# ============================================================

column_profile = []

for table_name, df in data.items():

    for column in df.columns:

        column_profile.append({
            "Table": table_name,
            "Column": column,
            "DataType": str(df[column].dtype),
            "Rows": len(df),
            "NonNull": int(df[column].notna().sum()),
            "NullCount": int(df[column].isna().sum()),
            "NullPercentage": round(
                df[column].isna().mean() * 100,
                2
            ),
            "UniqueValues": int(df[column].nunique(dropna=True))
        })

column_profile_df = pd.DataFrame(column_profile)


# ============================================================
# 6. NULL ANALYSIS
# ============================================================

null_analysis = []

for table_name, df in data.items():

    for column in df.columns:

        null_count = int(df[column].isna().sum())

        if null_count > 0:

            null_analysis.append({
                "Table": table_name,
                "Column": column,
                "NullCount": null_count,
                "NullPercentage": round(
                    null_count / len(df) * 100,
                    2
                )
            })

null_analysis_df = pd.DataFrame(null_analysis)


# ============================================================
# 7. DUPLICATE ANALYSIS
# ============================================================

duplicate_analysis = []

for table_name, df in data.items():

    duplicate_count = int(df.duplicated().sum())

    duplicate_analysis.append({
        "Table": table_name,
        "TotalRows": len(df),
        "DuplicateRows": duplicate_count,
        "DuplicatePercentage": round(
            duplicate_count / len(df) * 100,
            2
        ) if len(df) else 0
    })

duplicate_analysis_df = pd.DataFrame(duplicate_analysis)


# ============================================================
# 8. PRIMARY KEY VALIDATION
# ============================================================

PRIMARY_KEYS = {
    "Instrument_Master": "InstrumentID",
    "Client_Master": "ClientID",
    "Account_Portfolio": "AccountID",
    "Market_Price_Data": "MarketPriceID",
    "Order_Book": "OrderID",
    "Trade_Execution_Book": "TradeID",
    "Order_Rejection_Data": "RejectionID",
    "Position_Data": "PositionID"
}

key_validation = []

for table_name, key_column in PRIMARY_KEYS.items():

    df = data[table_name]

    null_count = int(df[key_column].isna().sum())
    duplicate_count = int(df[key_column].duplicated().sum())

    key_validation.append({
        "Table": table_name,
        "KeyColumn": key_column,
        "Rows": len(df),
        "NullKeys": null_count,
        "DuplicateKeys": duplicate_count,
        "UniqueKeys": int(df[key_column].nunique(dropna=True)),
        "Status": (
            "PASS"
            if null_count == 0 and duplicate_count == 0
            else "CHECK"
        )
    })

key_validation_df = pd.DataFrame(key_validation)


# ============================================================
# 9. FOREIGN KEY / RELATIONSHIP VALIDATION
# ============================================================

relationship_checks = []


def check_relationship(
    child_table,
    child_column,
    parent_table,
    parent_column
):

    child_df = data[child_table]
    parent_df = data[parent_table]

    child_values = set(
        child_df[child_column]
        .dropna()
        .unique()
    )

    parent_values = set(
        parent_df[parent_column]
        .dropna()
        .unique()
    )

    unmatched = child_values - parent_values

    relationship_checks.append({
        "ChildTable": child_table,
        "ChildColumn": child_column,
        "ParentTable": parent_table,
        "ParentColumn": parent_column,
        "ChildUniqueValues": len(child_values),
        "UnmatchedValues": len(unmatched),
        "Status": "PASS" if len(unmatched) == 0 else "CHECK"
    })


# Account -> Client
check_relationship(
    "Account_Portfolio",
    "ClientID",
    "Client_Master",
    "ClientID"
)

# Funds -> Account
check_relationship(
    "Funds_Margin",
    "AccountID",
    "Account_Portfolio",
    "AccountID"
)

# Orders -> Account
check_relationship(
    "Order_Book",
    "AccountID",
    "Account_Portfolio",
    "AccountID"
)

# Orders -> Client
check_relationship(
    "Order_Book",
    "ClientID",
    "Client_Master",
    "ClientID"
)

# Orders -> Instrument
check_relationship(
    "Order_Book",
    "InstrumentID",
    "Instrument_Master",
    "InstrumentID"
)

# Trades -> Orders
check_relationship(
    "Trade_Execution_Book",
    "OrderID",
    "Order_Book",
    "OrderID"
)

# Trades -> Account
check_relationship(
    "Trade_Execution_Book",
    "AccountID",
    "Account_Portfolio",
    "AccountID"
)

# Trades -> Client
check_relationship(
    "Trade_Execution_Book",
    "ClientID",
    "Client_Master",
    "ClientID"
)

# Trades -> Instrument
check_relationship(
    "Trade_Execution_Book",
    "InstrumentID",
    "Instrument_Master",
    "InstrumentID"
)

# Rejections -> Orders
check_relationship(
    "Order_Rejection_Data",
    "OrderID",
    "Order_Book",
    "OrderID"
)

# Charges -> Trades
check_relationship(
    "Brokerage_Charges",
    "TradeID",
    "Trade_Execution_Book",
    "TradeID"
)

# Positions -> Account
check_relationship(
    "Position_Data",
    "AccountID",
    "Account_Portfolio",
    "AccountID"
)

# Positions -> Client
check_relationship(
    "Position_Data",
    "ClientID",
    "Client_Master",
    "ClientID"
)

# Positions -> Instrument
check_relationship(
    "Position_Data",
    "InstrumentID",
    "Instrument_Master",
    "InstrumentID"
)

relationship_df = pd.DataFrame(relationship_checks)


# ============================================================
# 10. BUSINESS RULE VALIDATION
# ============================================================

business_issues = []


def add_rule(
    table,
    rule,
    issue_count,
    severity="Medium",
    description=""
):

    business_issues.append({
        "Table": table,
        "Rule": rule,
        "IssueCount": int(issue_count),
        "Severity": severity,
        "Description": description,
        "Status": "PASS" if issue_count == 0 else "CHECK"
    })


# ------------------------------------------------------------
# ORDER BOOK
# ------------------------------------------------------------

orders = data["Order_Book"].copy()

# OrderQuantity > 0
if "OrderQuantity" in orders.columns:

    issue = (orders["OrderQuantity"] <= 0).sum()

    add_rule(
        "Order_Book",
        "OrderQuantity > 0",
        issue,
        "High",
        "Every order should have a positive quantity."
    )


# OrderValue >= 0
if "OrderValue" in orders.columns:

    issue = (orders["OrderValue"] < 0).sum()

    add_rule(
        "Order_Book",
        "OrderValue >= 0",
        issue,
        "High",
        "Order value cannot be negative."
    )


# OrderType
if "OrderType" in orders.columns:

    valid_types = {"MARKET", "LIMIT"}

    issue = (
        ~orders["OrderType"]
        .astype(str)
        .str.upper()
        .isin(valid_types)
    ).sum()

    add_rule(
        "Order_Book",
        "Valid OrderType",
        issue,
        "High",
        "Expected MARKET or LIMIT."
    )


# Status
if "Status" in orders.columns:

    valid_status = {
        "EXECUTED",
        "PARTIAL",
        "REJECTED",
        "CANCELLED",
        "PENDING"
    }

    issue = (
        ~orders["Status"]
        .astype(str)
        .str.upper()
        .isin(valid_status)
    ).sum()

    add_rule(
        "Order_Book",
        "Valid Order Status",
        issue,
        "High",
        "Expected EXECUTED, PARTIAL, REJECTED, CANCELLED or PENDING."
    )


# LIMIT order must normally have OrderPrice
limit_orders = orders[
    orders["OrderType"].astype(str).str.upper() == "LIMIT"
]

limit_missing_price = limit_orders["OrderPrice"].isna().sum()

add_rule(
    "Order_Book",
    "LIMIT orders should have OrderPrice",
    limit_missing_price,
    "High",
    "MARKET orders may legitimately have blank OrderPrice."
)


# MARKET orders with price are not automatically errors
# because some systems may record reference prices.
# Therefore we only report them as information.

market_orders = orders[
    orders["OrderType"].astype(str).str.upper() == "MARKET"
]

market_with_price = market_orders["OrderPrice"].notna().sum()

add_rule(
    "Order_Book",
    "MARKET orders with OrderPrice",
    market_with_price,
    "Info",
    "Reported for information only; not treated as a data-quality error."
)


# ------------------------------------------------------------
# TRADE EXECUTION BOOK
# ------------------------------------------------------------

trades = data["Trade_Execution_Book"].copy()


# ExecutedQuantity > 0
issue = (trades["ExecutedQuantity"] <= 0).sum()

add_rule(
    "Trade_Execution_Book",
    "ExecutedQuantity > 0",
    issue,
    "High",
    "Execution quantity must be positive."
)


# ExecutionPrice > 0
issue = (trades["ExecutionPrice"] <= 0).sum()

add_rule(
    "Trade_Execution_Book",
    "ExecutionPrice > 0",
    issue,
    "High",
    "Execution price must be positive."
)


# TradeValue >= 0
issue = (trades["TradeValue"] < 0).sum()

add_rule(
    "Trade_Execution_Book",
    "TradeValue >= 0",
    issue,
    "High",
    "Trade value cannot be negative."
)


# Execution time >= 0
issue = (trades["ExecutionTimeSeconds"] < 0).sum()

add_rule(
    "Trade_Execution_Book",
    "ExecutionTimeSeconds >= 0",
    issue,
    "Medium",
    "Execution time cannot be negative."
)


# Slippage percentage should be finite
issue = (
    trades["SlippagePct"]
    .replace([np.inf, -np.inf], np.nan)
    .isna()
    .sum()
)

# This is informational because missing/undefined slippage can occur.
add_rule(
    "Trade_Execution_Book",
    "Valid SlippagePct",
    issue,
    "Info",
    "Reported for review; undefined slippage may be legitimate."
)


# ------------------------------------------------------------
# EXECUTION VS ORDER QUANTITY
# ------------------------------------------------------------

order_qty = orders[
    ["OrderID", "OrderQuantity"]
].copy()

execution_qty = (
    trades
    .groupby("OrderID", as_index=False)["ExecutedQuantity"]
    .sum()
)

execution_comparison = order_qty.merge(
    execution_qty,
    on="OrderID",
    how="left"
)

execution_comparison["ExecutedQuantity"] = (
    execution_comparison["ExecutedQuantity"]
    .fillna(0)
)

issue = (
    execution_comparison["ExecutedQuantity"]
    >
    execution_comparison["OrderQuantity"]
).sum()

add_rule(
    "Order_Book / Trade_Execution_Book",
    "Total ExecutedQuantity <= OrderQuantity",
    issue,
    "Critical",
    "Total executions for an order should not exceed its ordered quantity."
)


# ------------------------------------------------------------
# EXECUTION TIME CONSISTENCY
# ------------------------------------------------------------

orders_time = orders[
    ["OrderID", "OrderDateTime"]
].copy()

orders_time["OrderDateTime"] = pd.to_datetime(
    orders_time["OrderDateTime"],
    errors="coerce"
)

trades_time = trades[
    ["TradeID", "OrderID", "ExecutionDateTime"]
].copy()

trades_time["ExecutionDateTime"] = pd.to_datetime(
    trades_time["ExecutionDateTime"],
    errors="coerce"
)

time_check = trades_time.merge(
    orders_time,
    on="OrderID",
    how="left"
)

time_issue = (
    time_check["ExecutionDateTime"]
    <
    time_check["OrderDateTime"]
).sum()

add_rule(
    "Trade_Execution_Book",
    "ExecutionDateTime >= OrderDateTime",
    time_issue,
    "Critical",
    "Execution cannot occur before the corresponding order."
)


# ============================================================
# 11. REJECTION DATA VALIDATION
# ============================================================

rejections = data["Order_Rejection_Data"].copy()

issue = (rejections["RejectionTimeSeconds"] < 0).sum()

add_rule(
    "Order_Rejection_Data",
    "RejectionTimeSeconds >= 0",
    issue,
    "Medium",
    "Rejection time cannot be negative."
)


# ============================================================
# 12. BROKERAGE & CHARGES VALIDATION
# ============================================================

charges = data["Brokerage_Charges"].copy()

charge_columns = [
    "Brokerage",
    "STT",
    "ExchangeCharges",
    "GST",
    "SEBICharges",
    "StampDuty",
    "TotalCharges"
]

for column in charge_columns:

    issue = (charges[column] < 0).sum()

    add_rule(
        "Brokerage_Charges",
        f"{column} >= 0",
        issue,
        "High",
        f"{column} should not be negative."
    )


# Validate charge calculation
calculated_charges = (
    charges["Brokerage"]
    + charges["STT"]
    + charges["ExchangeCharges"]
    + charges["GST"]
    + charges["SEBICharges"]
    + charges["StampDuty"]
)

charge_difference = (
    calculated_charges.round(2)
    !=
    charges["TotalCharges"].round(2)
)

add_rule(
    "Brokerage_Charges",
    "TotalCharges = Sum of individual charges",
    charge_difference.sum(),
    "High",
    "TotalCharges should reconcile with component charges."
)


# ============================================================
# 13. POSITION DATA VALIDATION
# ============================================================

positions = data["Position_Data"].copy()

# Quantities should not be negative
for column in ["BuyQty", "SellQty"]:

    issue = (positions[column] < 0).sum()

    add_rule(
        "Position_Data",
        f"{column} >= 0",
        issue,
        "High",
        f"{column} should not be negative."
    )


# NetQuantity reconciliation
calculated_net = (
    positions["BuyQty"]
    - positions["SellQty"]
)

net_issue = (
    calculated_net.round(6)
    !=
    positions["NetQuantity"].round(6)
).sum()

add_rule(
    "Position_Data",
    "NetQuantity = BuyQty - SellQty",
    net_issue,
    "High",
    "Net position should reconcile with buy and sell quantities."
)
# ============================================================
# POSITION RECONCILIATION DETAILS
# ============================================================

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

position_reconciliation = position_reconciliation[
    position_reconciliation["Difference"] != 0
].copy()

position_reconciliation = position_reconciliation.sort_values(
    by="Difference",
    key=lambda x: x.abs(),
    ascending=False
)

# ============================================================
# 14. DATE RANGE ANALYSIS
# ============================================================

date_range = []

for table_name, df in data.items():

    for column in df.columns:

        if (
            "date" in column.lower()
            or "datetime" in column.lower()
            or "timestamp" in column.lower()
        ):

            converted = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            valid_dates = converted.dropna()

            if len(valid_dates) > 0:

                date_range.append({
                    "Table": table_name,
                    "Column": column,
                    "MinDate": valid_dates.min(),
                    "MaxDate": valid_dates.max(),
                    "InvalidDateValues": int(
                        converted.isna().sum()
                    )
                })

date_range_df = pd.DataFrame(date_range)


# ============================================================
# 15. DATA QUALITY ISSUE SUMMARY
# ============================================================

issues = []

# Table duplicates
for _, row in duplicate_analysis_df.iterrows():

    if row["DuplicateRows"] > 0:

        issues.append({
            "Category": "Duplicate",
            "Table": row["Table"],
            "Column": "",
            "Issue": "Duplicate rows detected",
            "Count": row["DuplicateRows"],
            "Severity": "Medium"
        })


# Nulls
for _, row in null_analysis_df.iterrows():

    issues.append({
        "Category": "Null",
        "Table": row["Table"],
        "Column": row["Column"],
        "Issue": "Null values detected",
        "Count": row["NullCount"],
        "Severity": "Review"
    })


# Relationship failures
for _, row in relationship_df.iterrows():

    if row["UnmatchedValues"] > 0:

        issues.append({
            "Category": "Relationship",
            "Table": row["ChildTable"],
            "Column": row["ChildColumn"],
            "Issue": (
                f"Unmatched values against "
                f"{row['ParentTable']}.{row['ParentColumn']}"
            ),
            "Count": row["UnmatchedValues"],
            "Severity": "High"
        })


# Business rules
for _, row in pd.DataFrame(business_issues).iterrows():

    if row["IssueCount"] > 0 and row["Severity"] != "Info":

        issues.append({
            "Category": "Business Rule",
            "Table": row["Table"],
            "Column": "",
            "Issue": row["Rule"],
            "Count": row["IssueCount"],
            "Severity": row["Severity"]
        })


issues_df = pd.DataFrame(issues)


# ============================================================
# 16. EXECUTIVE SUMMARY
# ============================================================

summary = []

total_tables = len(data)
total_rows = sum(len(df) for df in data.values())
total_columns = sum(len(df.columns) for df in data.values())
total_nulls = sum(
    int(df.isna().sum().sum())
    for df in data.values()
)
total_duplicates = sum(
    int(df.duplicated().sum())
    for df in data.values()
)

relationship_failures = (
    relationship_df["UnmatchedValues"] > 0
).sum()

business_rule_failures = (
    pd.DataFrame(business_issues)["IssueCount"] > 0
).sum()


summary.append({
    "Metric": "Total Tables",
    "Value": total_tables
})

summary.append({
    "Metric": "Total Rows",
    "Value": total_rows
})

summary.append({
    "Metric": "Total Columns",
    "Value": total_columns
})

summary.append({
    "Metric": "Total Null Cells",
    "Value": total_nulls
})

summary.append({
    "Metric": "Total Duplicate Rows",
    "Value": total_duplicates
})

summary.append({
    "Metric": "Relationship Checks Failed",
    "Value": relationship_failures
})

summary.append({
    "Metric": "Business Rule Checks With Issues",
    "Value": business_rule_failures
})

summary.append({
    "Metric": "Overall Data Quality Status",
    "Value": (
        "REVIEW REQUIRED"
        if (
            total_nulls > 0
            or total_duplicates > 0
            or relationship_failures > 0
            or business_rule_failures > 0
        )
        else "PASS"
    )
})

summary_df = pd.DataFrame(summary)


# ============================================================
# 17. EXPORT TO EXCEL
# ============================================================

print()
print("Creating Excel data-quality report...")

with pd.ExcelWriter(
    OUTPUT_FILE,
    engine="openpyxl"
) as writer:

    summary_df.to_excel(
        writer,
        sheet_name="Executive_Summary",
        index=False
    )

    table_profile_df.to_excel(
        writer,
        sheet_name="Table_Profile",
        index=False
    )

    column_profile_df.to_excel(
        writer,
        sheet_name="Column_Profile",
        index=False
    )

    null_analysis_df.to_excel(
        writer,
        sheet_name="Null_Analysis",
        index=False
    )

    duplicate_analysis_df.to_excel(
        writer,
        sheet_name="Duplicate_Analysis",
        index=False
    )

    key_validation_df.to_excel(
        writer,
        sheet_name="Key_Validation",
        index=False
    )

    relationship_df.to_excel(
        writer,
        sheet_name="Relationship_Check",
        index=False
    )

    pd.DataFrame(business_issues).to_excel(
        writer,
        sheet_name="Business_Rule_Check",
        index=False
    )

    date_range_df.to_excel(
        writer,
        sheet_name="Date_Range",
        index=False
    )
    position_reconciliation.to_excel(
    writer,
    sheet_name="Position_Reconciliation",
    index=False
    )

    issues_df.to_excel(
        writer,
        sheet_name="Data_Quality_Issues",
        index=False
    )


# ============================================================
# 18. FINAL CONSOLE OUTPUT
# ============================================================

print()
print("=" * 70)
print("DATA QUALITY ANALYSIS COMPLETED")
print("=" * 70)

print(f"Tables analyzed       : {total_tables}")
print(f"Total rows            : {total_rows:,}")
print(f"Total columns         : {total_columns:,}")
print(f"Null cells            : {total_nulls:,}")
print(f"Duplicate rows        : {total_duplicates:,}")
print(f"Relationship failures : {relationship_failures}")
print(f"Business rule issues  : {business_rule_failures}")

print()
print("Output file:")
print(OUTPUT_FILE)

print("=" * 70)