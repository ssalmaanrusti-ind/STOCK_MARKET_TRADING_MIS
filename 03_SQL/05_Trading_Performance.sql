/* =========================================================
   STOCK MARKET TRADING MIS
   05 - TRADING PERFORMANCE
   ========================================================= */

USE StockMarketTradingMIS;
GO


/* =========================================================
   1. OVERALL TRADING PERFORMANCE
   ========================================================= */

SELECT
    COUNT(*) AS TotalTrades,

    COUNT(DISTINCT OrderID) AS OrdersWithExecution,

    SUM(ExecutedQuantity) AS TotalExecutedQuantity,

    CAST(
        SUM(TradeValue)
        AS DECIMAL(18,2)
    ) AS TotalTurnover,

    CAST(
        AVG(CAST(TradeValue AS DECIMAL(18,2)))
        AS DECIMAL(18,2)
    ) AS AverageTradeValue,

    CAST(
        AVG(CAST(ExecutionTimeSeconds AS DECIMAL(18,2)))
        AS DECIMAL(18,2)
    ) AS AverageExecutionTimeSeconds,

    MIN(ExecutionTimeSeconds) AS MinimumExecutionTimeSeconds,

    MAX(ExecutionTimeSeconds) AS MaximumExecutionTimeSeconds

FROM dbo.[07_Trade_Execution_Book];
GO


/* =========================================================
   2. DAILY TRADING PERFORMANCE
   ========================================================= */

SELECT
    CAST(TradeDate AS DATE) AS TradeDate,

    COUNT(*) AS TradeCount,

    COUNT(DISTINCT OrderID) AS OrdersExecuted,

    COUNT(DISTINCT ClientID) AS ActiveClients,

    COUNT(DISTINCT Symbol) AS ActiveSymbols,

    SUM(ExecutedQuantity) AS ExecutedQuantity,

    CAST(
        SUM(TradeValue)
        AS DECIMAL(18,2)
    ) AS Turnover,

    CAST(
        AVG(CAST(ExecutionTimeSeconds AS DECIMAL(18,2)))
        AS DECIMAL(18,2)
    ) AS AverageExecutionTimeSeconds

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    CAST(TradeDate AS DATE)

ORDER BY
    TradeDate;
GO


/* =========================================================
   3. MONTHLY TRADING PERFORMANCE
   ========================================================= */

SELECT
    YEAR(TradeDate) AS TradeYear,

    MONTH(TradeDate) AS TradeMonth,

    COUNT(*) AS TradeCount,

    COUNT(DISTINCT OrderID) AS OrdersExecuted,

    COUNT(DISTINCT ClientID) AS ActiveClients,

    SUM(ExecutedQuantity) AS ExecutedQuantity,

    CAST(
        SUM(TradeValue)
        AS DECIMAL(18,2)
    ) AS Turnover

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    YEAR(TradeDate),
    MONTH(TradeDate)

ORDER BY
    TradeYear,
    TradeMonth;
GO


/* =========================================================
   4. BUY VS SELL TRADING PERFORMANCE
   ========================================================= */

SELECT
    Side,

    COUNT(*) AS TradeCount,

    COUNT(DISTINCT OrderID) AS OrdersExecuted,

    SUM(ExecutedQuantity) AS ExecutedQuantity,

    CAST(
        SUM(TradeValue)
        AS DECIMAL(18,2)
    ) AS Turnover,

    CAST(
        AVG(CAST(TradeValue AS DECIMAL(18,2)))
        AS DECIMAL(18,2)
    ) AS AverageTradeValue

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    Side

ORDER BY
    Turnover DESC;
GO


/* =========================================================
   5. MARKET VS LIMIT TRADING PERFORMANCE
   ========================================================= */

SELECT
    OrderType,

    COUNT(*) AS TradeCount,

    COUNT(DISTINCT OrderID) AS OrdersExecuted,

    SUM(ExecutedQuantity) AS ExecutedQuantity,

    CAST(
        SUM(TradeValue)
        AS DECIMAL(18,2)
    ) AS Turnover,

    CAST(
        AVG(CAST(ExecutionTimeSeconds AS DECIMAL(18,2)))
        AS DECIMAL(18,2)
    ) AS AverageExecutionTime,

    CAST(
        AVG(CAST(SlippagePct AS DECIMAL(18,6)))
        AS DECIMAL(18,6)
    ) AS AverageSlippagePct

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    OrderType

ORDER BY
    Turnover DESC;
GO


/* =========================================================
   6. EXCHANGE-WISE PERFORMANCE
   ========================================================= */

SELECT
    Exchange,

    COUNT(*) AS TradeCount,

    COUNT(DISTINCT OrderID) AS OrdersExecuted,

    COUNT(DISTINCT ClientID) AS ActiveClients,

    SUM(ExecutedQuantity) AS ExecutedQuantity,

    CAST(
        SUM(TradeValue)
        AS DECIMAL(18,2)
    ) AS Turnover,

    CAST(
        AVG(CAST(ExecutionTimeSeconds AS DECIMAL(18,2)))
        AS DECIMAL(18,2)
    ) AS AverageExecutionTime

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    Exchange

ORDER BY
    Turnover DESC;
GO


/* =========================================================
   7. INTRADAY PERFORMANCE
   ========================================================= */

SELECT
    o.IntradayBucket,

    COUNT(DISTINCT o.OrderID) AS TotalOrders,

    COUNT(DISTINCT t.OrderID) AS OrdersExecuted,

    COUNT(t.TradeID) AS TradeCount,

    SUM(t.ExecutedQuantity) AS ExecutedQuantity,

    CAST(
        SUM(t.TradeValue)
        AS DECIMAL(18,2)
    ) AS Turnover,

    CAST(
        AVG(
            CAST(t.ExecutionTimeSeconds AS DECIMAL(18,2))
        )
        AS DECIMAL(18,2)
    ) AS AverageExecutionTime

FROM dbo.[06_Order_Book] o

LEFT JOIN dbo.[07_Trade_Execution_Book] t
    ON o.OrderID = t.OrderID

GROUP BY
    o.IntradayBucket

ORDER BY
    o.IntradayBucket;
GO


/* =========================================================
   8. TOP 20 CLIENTS BY TURNOVER
   ========================================================= */

SELECT TOP 20

    ClientID,

    COUNT(*) AS TradeCount,

    COUNT(DISTINCT OrderID) AS OrdersExecuted,

    COUNT(DISTINCT Symbol) AS SymbolsTraded,

    SUM(ExecutedQuantity) AS ExecutedQuantity,

    CAST(
        SUM(TradeValue)
        AS DECIMAL(18,2)
    ) AS Turnover,

    CAST(
        AVG(CAST(ExecutionTimeSeconds AS DECIMAL(18,2)))
        AS DECIMAL(18,2)
    ) AS AverageExecutionTime

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    ClientID

ORDER BY
    Turnover DESC;
GO


/* =========================================================
   9. TOP 20 SYMBOLS BY TURNOVER
   ========================================================= */

SELECT TOP 20

    Symbol,

    COUNT(*) AS TradeCount,

    COUNT(DISTINCT OrderID) AS OrdersExecuted,

    COUNT(DISTINCT ClientID) AS ActiveClients,

    SUM(ExecutedQuantity) AS ExecutedQuantity,

    CAST(
        SUM(TradeValue)
        AS DECIMAL(18,2)
    ) AS Turnover,

    CAST(
        AVG(CAST(ExecutionPrice AS DECIMAL(18,4)))
        AS DECIMAL(18,4)
    ) AS AverageExecutionPrice

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    Symbol

ORDER BY
    Turnover DESC;
GO


/* =========================================================
   10. BROKERAGE & CHARGES SUMMARY
   ========================================================= */

SELECT
    COUNT(*) AS ChargeRecords,

    CAST(
        SUM(Brokerage)
        AS DECIMAL(18,2)
    ) AS TotalBrokerage,

    CAST(
        SUM(TotalCharges)
        AS DECIMAL(18,2)
    ) AS TotalTransactionCharges

FROM dbo.[09_Brokerage_Charges];
GO


/* =========================================================
   11. CLIENT-WISE BROKERAGE & CHARGES
   ========================================================= */

SELECT
    ClientID,

    COUNT(*) AS ChargeRecords,

    CAST(
        SUM(Brokerage)
        AS DECIMAL(18,2)
    ) AS Brokerage,

    CAST(
        SUM(TotalCharges)
        AS DECIMAL(18,2)
    ) AS TotalCharges

FROM dbo.[09_Brokerage_Charges]

GROUP BY
    ClientID

ORDER BY
    TotalCharges DESC;
GO


/* =========================================================
   12. SYMBOL-WISE BROKERAGE & CHARGES
   ========================================================= */

SELECT
    Symbol,

    COUNT(*) AS ChargeRecords,

    CAST(
        SUM(Brokerage)
        AS DECIMAL(18,2)
    ) AS Brokerage,

    CAST(
        SUM(TotalCharges)
        AS DECIMAL(18,2)
    ) AS TotalCharges

FROM dbo.[09_Brokerage_Charges]

GROUP BY
    Symbol

ORDER BY
    TotalCharges DESC;
GO


/* =========================================================
   13. CHARGES AS % OF TURNOVER
   ========================================================= */

WITH Trading AS
(
    SELECT
        SUM(TradeValue) AS Turnover
    FROM dbo.[07_Trade_Execution_Book]
),

Charges AS
(
    SELECT
        SUM(TotalCharges) AS TotalCharges
    FROM dbo.[09_Brokerage_Charges]
)

SELECT
    CAST(
        Trading.Turnover
        AS DECIMAL(18,2)
    ) AS TotalTurnover,

    CAST(
        Charges.TotalCharges
        AS DECIMAL(18,2)
    ) AS TotalCharges,

    CAST(
        Charges.TotalCharges * 100.0 /
        NULLIF(Trading.Turnover,0)
        AS DECIMAL(10,4)
    ) AS ChargesPercentageOfTurnover

FROM Trading
CROSS JOIN Charges;
GO


/* =========================================================
   14. SLIPPAGE SUMMARY
   ========================================================= */

SELECT
    COUNT(*) AS TotalTrades,

    COUNT(
        CASE
            WHEN SlippageValue > 0
            THEN 1
        END
    ) AS PositiveSlippageTrades,

    COUNT(
        CASE
            WHEN SlippageValue < 0
            THEN 1
        END
    ) AS NegativeSlippageTrades,

    CAST(
        AVG(CAST(SlippageValue AS DECIMAL(18,6)))
        AS DECIMAL(18,6)
    ) AS AverageSlippageValue,

    CAST(
        AVG(CAST(SlippagePct AS DECIMAL(18,6)))
        AS DECIMAL(18,6)
    ) AS AverageSlippagePct,

    CAST(
        SUM(SlippageValue)
        AS DECIMAL(18,2)
    ) AS TotalSlippageValue

FROM dbo.[07_Trade_Execution_Book];
GO


/* =========================================================
   15. EXECUTION TIME BUCKETS
   ========================================================= */

SELECT
    CASE
        WHEN ExecutionTimeSeconds <= 30
            THEN '0-30 Seconds'

        WHEN ExecutionTimeSeconds <= 60
            THEN '31-60 Seconds'

        WHEN ExecutionTimeSeconds <= 120
            THEN '61-120 Seconds'

        WHEN ExecutionTimeSeconds <= 300
            THEN '121-300 Seconds'

        ELSE 'Above 300 Seconds'
    END AS ExecutionTimeBucket,

    COUNT(*) AS TradeCount,

    CAST(
        COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER ()
        AS DECIMAL(10,2)
    ) AS PercentageOfTrades,

    CAST(
        SUM(TradeValue)
        AS DECIMAL(18,2)
    ) AS Turnover

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    CASE
        WHEN ExecutionTimeSeconds <= 30
            THEN '0-30 Seconds'

        WHEN ExecutionTimeSeconds <= 60
            THEN '31-60 Seconds'

        WHEN ExecutionTimeSeconds <= 120
            THEN '61-120 Seconds'

        WHEN ExecutionTimeSeconds <= 300
            THEN '121-300 Seconds'

        ELSE 'Above 300 Seconds'
    END

ORDER BY
    MIN(ExecutionTimeSeconds);
GO


/* =========================================================
   16. DAILY TURNOVER RANKING
   ========================================================= */

WITH DailyTrading AS
(
    SELECT
        CAST(TradeDate AS DATE) AS TradeDate,

        SUM(TradeValue) AS Turnover

    FROM dbo.[07_Trade_Execution_Book]

    GROUP BY
        CAST(TradeDate AS DATE)
)

SELECT
    TradeDate,

    CAST(
        Turnover
        AS DECIMAL(18,2)
    ) AS Turnover,

    RANK() OVER (
        ORDER BY Turnover DESC
    ) AS TurnoverRank

FROM DailyTrading

ORDER BY
    TurnoverRank;
GO