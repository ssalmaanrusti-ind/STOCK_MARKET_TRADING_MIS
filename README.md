# Stock Market Trading MIS & Analytics

## Overview
End-to-end trading MIS covering **Order Placement → Execution → Settlement → Position → P&L**, built with Python, SQL Server and Power BI.

## Dataset
Trading period: **03-Aug-2026 to 11-Sep-2026**

| Source | Rows | Columns |
|---|---:|---:|
| Instrument Master | 120 | 9 |
| Client Master | 500 | 6 |
| Account Portfolio | 650 | 4 |
| Funds & Margin | 650 | 6 |
| Market Price Data | 3,600 | 9 |
| Order Book | 100,000 | 16 |
| Trade Execution Book | 94,969 | 20 |
| Order Rejection Data | 10,261 | 11 |
| Brokerage & Charges | 94,969 | 20 |
| Position Data | 47,334 | 15 |
| **Total** | **353,053** | **116** |

## Technology
- Python / Pandas — data quality, analytics, anomaly detection and visualizations
- SQL Server — database, validation, reconciliation and analytical views
- Power BI / DAX — interactive MIS dashboards
- Excel — analytical and data-quality reports

## Core KPIs
- Total Orders: **100,000**
- Fully Executed Orders: **60,007**
- Partial Orders: **12,741**
- Rejected Orders: **10,261**
- Cancelled Orders: **10,054**
- Pending Orders: **6,937**
- Orders With Execution: **72,748**
- Execution Completion Rate: **72.75%**
- Fully Executed Rate: **60.01%**
- Rejection Rate: **10.26%**
- Average Order Value: **₹86,280.64**
- Total Turnover: **₹5.764B**
- Average Execution Time: **90.05 sec**
- Partial Execution Orders: **12,502**
- Over-Executed Orders: **0**

## Advanced Findings
- High-volume clients: **25**
- High-volume symbols: **4**
- High-rejection anomalies: **0**
- High-slippage anomalies: **0**
- Activity-spike days: **0**
- Turnover-spike days: **0**
- Position quantity exceptions: **47**

## Power BI Pages
1. Executive Trading Overview
2. Order & Execution Analysis
3. Rejection Analysis
4. Client & Symbol Intelligence
5. Slippage & Transaction Charges
6. P&L & Position Control

## Data Quality
- Rows analyzed: **353,053**
- Columns analyzed: **116**
- Null cells: **58,102**
- Duplicate rows: **0**
- Relationship failures: **0**
- Business-rule issues: **1**

The business-rule issue is in Position Data: **47 records have NetQuantity different from BuyQty - SellQty**. These are retained as reconciliation exceptions.

## P&L Limitation
Position Data contains only **one PositionDate**. Therefore historical P&L trends and the requirement to compare P&L changes against similar turnover cannot be demonstrated reliably. No synthetic dates or fabricated P&L history are used.

## Main Project Structure
```text
STOCK_MARKET_TRADING_MIS/
├── 02_Data_Quality/
├── 03_SQL/
├── 04_Python/
├── 07_Output/
└── Trading_MIS.pbix
```

## SQL Layer
01_Database_Setup.sql  
02_Data_Validation.sql  
03_Order_Execution_Analysis.sql  
04_Rejection_Analysis.sql  
05_Trading_Performance.sql  
06_Client_Symbol_Analysis.sql  
07_Position_Reconciliation.sql  
08_Advanced_MIS_Views.sql  

Additional Power BI views cover settlement, high-volume anomalies, high-rejection anomalies, high-slippage anomalies and activity spikes.

## Python Layer
01_data_quality.py  
02_trading_analysis.py  
03_reconciliation.py  
04_anomaly_detection.py  
05_visualization.py  

## TL Requirement Coverage
Covered: order KPIs, execution, rejection, cancellation, pending orders, turnover, partial executions, rejection reasons, client/symbol turnover, intraday activity, MARKET vs LIMIT, slippage, charges, P&L snapshot, trade-position reconciliation, exceptions, high-volume anomalies, high-rejection anomalies, high-slippage anomalies, sudden activity increases and settlement.

Not demonstrable from supplied data: historical **P&L changes vs similar turnover**, because Position Data has only one PositionDate.
