/* =========================================================
   STOCK MARKET TRADING MIS
   02 - DATA VALIDATION
   ========================================================= */

USE StockMarketTradingMIS;
GO


/* =========================================================
   1. TABLE ROW COUNTS
   ========================================================= */

SELECT
    '01_Instrument_Master' AS TableName,
    COUNT(*) AS [RowCount]
FROM dbo.[01_Instrument_Master]

UNION ALL

SELECT
    '02_Client_Master',
    COUNT(*)
FROM dbo.[02_Client_Master]

UNION ALL

SELECT
    '03_Account_Portfolio',
    COUNT(*)
FROM dbo.[03_Account_Portfolio]

UNION ALL

SELECT
    '04_Funds_Margin',
    COUNT(*)
FROM dbo.[04_Funds_Margin]

UNION ALL

SELECT
    '05_Market_Price_Data',
    COUNT(*)
FROM dbo.[05_Market_Price_Data]

UNION ALL

SELECT
    '06_Order_Book',
    COUNT(*)
FROM dbo.[06_Order_Book]

UNION ALL

SELECT
    '07_Trade_Execution_Book',
    COUNT(*)
FROM dbo.[07_Trade_Execution_Book]

UNION ALL

SELECT
    '08_Order_Rejection_Data',
    COUNT(*)
FROM dbo.[08_Order_Rejection_Data]

UNION ALL

SELECT
    '09_Brokerage_Charges',
    COUNT(*)
FROM dbo.[09_Brokerage_Charges]

UNION ALL

SELECT
    '10_Position_Data',
    COUNT(*)
FROM dbo.[10_Position_Data]

ORDER BY TableName;
GO


/* =========================================================
   2. ORDER DATE RANGE
   ========================================================= */

SELECT
    MIN(OrderDate) AS FirstOrderDate,
    MAX(OrderDate) AS LastOrderDate,
    COUNT(*) AS TotalOrders
FROM dbo.[06_Order_Book];
GO


/* =========================================================
   3. TRADE DATE RANGE
   ========================================================= */

SELECT
    MIN(TradeDate) AS FirstTradeDate,
    MAX(TradeDate) AS LastTradeDate,
    COUNT(*) AS TotalTrades
FROM dbo.[07_Trade_Execution_Book];
GO


/* =========================================================
   4. ORDER STATUS VALIDATION
   ========================================================= */

SELECT
    Status,
    COUNT(*) AS OrderCount,
    CAST(
        COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER ()
        AS DECIMAL(10,2)
    ) AS PercentageOfOrders
FROM dbo.[06_Order_Book]
GROUP BY Status
ORDER BY OrderCount DESC;
GO


/* =========================================================
   5. ORDER TYPE VALIDATION
   ========================================================= */

SELECT
    OrderType,
    COUNT(*) AS OrderCount,
    SUM(OrderQuantity) AS TotalOrderQuantity
FROM dbo.[06_Order_Book]
GROUP BY OrderType
ORDER BY OrderCount DESC;
GO


/* =========================================================
   6. BUY VS SELL VALIDATION
   ========================================================= */

SELECT
    Side,
    COUNT(*) AS OrderCount,
    SUM(OrderQuantity) AS TotalQuantity,
    SUM(OrderValue) AS TotalOrderValue
FROM dbo.[06_Order_Book]
GROUP BY Side
ORDER BY Side;
GO


/* =========================================================
   7. TRADE EXECUTION VALIDATION
   ========================================================= */

SELECT
    COUNT(*) AS TotalTrades,
    SUM(ExecutedQuantity) AS TotalExecutedQuantity,
    SUM(TradeValue) AS TotalTurnover,
    CAST(
        AVG(CAST(ExecutionTimeSeconds AS DECIMAL(18,2)))
        AS DECIMAL(18,2)
    ) AS AverageExecutionTimeSeconds
FROM dbo.[07_Trade_Execution_Book];
GO


/* =========================================================
   8. REJECTION VALIDATION
   ========================================================= */

SELECT
    COUNT(*) AS TotalRejectedOrders
FROM dbo.[08_Order_Rejection_Data];
GO


/* =========================================================
   9. POSITION RECONCILIATION
   ========================================================= */

SELECT
    COUNT(*) AS TotalPositions,

    SUM(
        CASE
            WHEN NetQuantity = BuyQty - SellQty
            THEN 1
            ELSE 0
        END
    ) AS ReconciledPositions,

    SUM(
        CASE
            WHEN NetQuantity <> BuyQty - SellQty
            THEN 1
            ELSE 0
        END
    ) AS ExceptionPositions

FROM dbo.[10_Position_Data];
GO


/* =========================================================
   10. DUPLICATE ORDER IDs
   ========================================================= */

SELECT
    OrderID,
    COUNT(*) AS Occurrences
FROM dbo.[06_Order_Book]
GROUP BY OrderID
HAVING COUNT(*) > 1
ORDER BY Occurrences DESC;
GO


/* =========================================================
   11. DUPLICATE TRADE IDs
   ========================================================= */

SELECT
    TradeID,
    COUNT(*) AS Occurrences
FROM dbo.[07_Trade_Execution_Book]
GROUP BY TradeID
HAVING COUNT(*) > 1
ORDER BY Occurrences DESC;
GO