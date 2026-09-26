/* =========================================================
   STOCK MARKET TRADING MIS
   06 - CLIENT & SYMBOL ANALYSIS
   ========================================================= */

USE StockMarketTradingMIS;
GO


/* =========================================================
   1. CLIENT-WISE ORDER & EXECUTION SUMMARY
   ========================================================= */

SELECT
    o.ClientID,

    COUNT(DISTINCT o.OrderID) AS TotalOrders,

    COUNT(DISTINCT t.OrderID) AS OrdersWithExecution,

    COUNT(DISTINCT t.TradeID) AS TradeCount,

    SUM(o.OrderQuantity) AS OrderedQuantity,

    ISNULL(SUM(t.ExecutedQuantity), 0) AS ExecutedQuantity,

    CAST(
        ISNULL(SUM(t.TradeValue), 0)
        AS DECIMAL(18,2)
    ) AS Turnover,

    CAST(
        COUNT(DISTINCT t.OrderID) * 100.0 /
        NULLIF(COUNT(DISTINCT o.OrderID), 0)
        AS DECIMAL(10,2)
    ) AS ExecutionRate,

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
    o.ClientID

ORDER BY
    Turnover DESC;
GO


/* =========================================================
   2. TOP 20 CLIENTS BY ORDER VOLUME
   ========================================================= */

SELECT TOP 20
    ClientID,

    COUNT(*) AS TotalOrders,

    SUM(OrderQuantity) AS TotalOrderQuantity,

    CAST(
        SUM(OrderValue)
        AS DECIMAL(18,2)
    ) AS TotalOrderValue

FROM dbo.[06_Order_Book]

GROUP BY
    ClientID

ORDER BY
    TotalOrders DESC;
GO


/* =========================================================
   3. TOP 20 CLIENTS BY TURNOVER
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
    ) AS Turnover

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    ClientID

ORDER BY
    Turnover DESC;
GO


/* =========================================================
   4. CLIENT BUY VS SELL ACTIVITY
   ========================================================= */

SELECT
    ClientID,

    SUM(
        CASE
            WHEN Side = 'BUY'
            THEN ExecutedQuantity
            ELSE 0
        END
    ) AS BuyQuantity,

    SUM(
        CASE
            WHEN Side = 'SELL'
            THEN ExecutedQuantity
            ELSE 0
        END
    ) AS SellQuantity,

    CAST(
        SUM(
            CASE
                WHEN Side = 'BUY'
                THEN TradeValue
                ELSE 0
            END
        )
        AS DECIMAL(18,2)
    ) AS BuyTurnover,

    CAST(
        SUM(
            CASE
                WHEN Side = 'SELL'
                THEN TradeValue
                ELSE 0
            END
        )
        AS DECIMAL(18,2)
    ) AS SellTurnover

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    ClientID

ORDER BY
    ClientID;
GO


/* =========================================================
   5. CLIENT ORDER TYPE BEHAVIOR
   ========================================================= */

SELECT
    ClientID,

    SUM(
        CASE
            WHEN OrderType = 'MARKET'
            THEN 1
            ELSE 0
        END
    ) AS MarketOrders,

    SUM(
        CASE
            WHEN OrderType = 'LIMIT'
            THEN 1
            ELSE 0
        END
    ) AS LimitOrders,

    COUNT(*) AS TotalTrades,

    CAST(
        SUM(
            CASE
                WHEN OrderType = 'MARKET'
                THEN 1
                ELSE 0
            END
        ) * 100.0 / NULLIF(COUNT(*),0)
        AS DECIMAL(10,2)
    ) AS MarketOrderPercentage

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    ClientID

ORDER BY
    TotalTrades DESC;
GO


/* =========================================================
   6. CLIENT SLIPPAGE ANALYSIS
   ========================================================= */

SELECT
    ClientID,

    COUNT(*) AS Trades,

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

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    ClientID

ORDER BY
    AverageSlippagePct DESC;
GO


/* =========================================================
   7. CLIENT EXECUTION SPEED
   ========================================================= */

SELECT
    ClientID,

    COUNT(*) AS TradeCount,

    CAST(
        AVG(CAST(ExecutionTimeSeconds AS DECIMAL(18,2)))
        AS DECIMAL(18,2)
    ) AS AverageExecutionTime,

    MIN(ExecutionTimeSeconds) AS MinimumExecutionTime,

    MAX(ExecutionTimeSeconds) AS MaximumExecutionTime

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    ClientID

ORDER BY
    AverageExecutionTime DESC;
GO


/* =========================================================
   8. CLIENT TURNOVER CONCENTRATION
   ========================================================= */

WITH ClientTurnover AS
(
    SELECT
        ClientID,
        SUM(TradeValue) AS Turnover
    FROM dbo.[07_Trade_Execution_Book]
    GROUP BY ClientID
),

TotalMarket AS
(
    SELECT
        SUM(TradeValue) AS TotalTurnover
    FROM dbo.[07_Trade_Execution_Book]
)

SELECT
    c.ClientID,

    CAST(
        c.Turnover
        AS DECIMAL(18,2)
    ) AS Turnover,

    CAST(
        c.Turnover * 100.0 /
        NULLIF(t.TotalTurnover,0)
        AS DECIMAL(10,4)
    ) AS MarketTurnoverPercentage,

    RANK() OVER (
        ORDER BY c.Turnover DESC
    ) AS TurnoverRank

FROM ClientTurnover c

CROSS JOIN TotalMarket t

ORDER BY
    Turnover DESC;
GO


/* =========================================================
   9. TOP 20 SYMBOLS BY ORDER VOLUME
   ========================================================= */

SELECT TOP 20
    Symbol,

    COUNT(*) AS TotalOrders,

    COUNT(DISTINCT ClientID) AS ActiveClients,

    SUM(OrderQuantity) AS OrderedQuantity,

    CAST(
        SUM(OrderValue)
        AS DECIMAL(18,2)
    ) AS OrderValue

FROM dbo.[06_Order_Book]

GROUP BY
    Symbol

ORDER BY
    TotalOrders DESC;
GO


/* =========================================================
   10. TOP 20 SYMBOLS BY TURNOVER
   ========================================================= */

SELECT TOP 20
    Symbol,

    COUNT(*) AS TradeCount,

    COUNT(DISTINCT ClientID) AS ActiveClients,

    COUNT(DISTINCT OrderID) AS OrdersExecuted,

    SUM(ExecutedQuantity) AS ExecutedQuantity,

    CAST(
        SUM(TradeValue)
        AS DECIMAL(18,2)
    ) AS Turnover

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    Symbol

ORDER BY
    Turnover DESC;
GO


/* =========================================================
   11. SYMBOL BUY VS SELL ACTIVITY
   ========================================================= */

SELECT
    Symbol,

    SUM(
        CASE
            WHEN Side = 'BUY'
            THEN ExecutedQuantity
            ELSE 0
        END
    ) AS BuyQuantity,

    SUM(
        CASE
            WHEN Side = 'SELL'
            THEN ExecutedQuantity
            ELSE 0
        END
    ) AS SellQuantity,

    CAST(
        SUM(
            CASE
                WHEN Side = 'BUY'
                THEN TradeValue
                ELSE 0
            END
        )
        AS DECIMAL(18,2)
    ) AS BuyTurnover,

    CAST(
        SUM(
            CASE
                WHEN Side = 'SELL'
                THEN TradeValue
                ELSE 0
            END
        )
        AS DECIMAL(18,2)
    ) AS SellTurnover

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    Symbol

ORDER BY
    Turnover DESC;
GO


/* =========================================================
   12. SYMBOL EXECUTION PERFORMANCE
   ========================================================= */

SELECT
    Symbol,

    COUNT(DISTINCT o.OrderID) AS TotalOrders,

    COUNT(DISTINCT t.OrderID) AS OrdersExecuted,

    SUM(o.OrderQuantity) AS OrderedQuantity,

    ISNULL(SUM(t.ExecutedQuantity),0) AS ExecutedQuantity,

    CAST(
        ISNULL(SUM(t.ExecutedQuantity),0) * 100.0 /
        NULLIF(SUM(o.OrderQuantity),0)
        AS DECIMAL(10,2)
    ) AS QuantityExecutionRate,

    CAST(
        ISNULL(SUM(t.TradeValue),0)
        AS DECIMAL(18,2)
    ) AS Turnover

FROM dbo.[06_Order_Book] o

LEFT JOIN dbo.[07_Trade_Execution_Book] t
    ON o.OrderID = t.OrderID

GROUP BY
    o.Symbol

ORDER BY
    Turnover DESC;
GO


/* =========================================================
   13. SYMBOL SLIPPAGE ANALYSIS
   ========================================================= */

SELECT
    Symbol,

    COUNT(*) AS TradeCount,

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

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    Symbol

ORDER BY
    AverageSlippagePct DESC;
GO


/* =========================================================
   14. SYMBOL EXECUTION TIME
   ========================================================= */

SELECT
    Symbol,

    COUNT(*) AS TradeCount,

    CAST(
        AVG(
            CAST(ExecutionTimeSeconds AS DECIMAL(18,2))
        )
        AS DECIMAL(18,2)
    ) AS AverageExecutionTime,

    MIN(ExecutionTimeSeconds) AS MinimumExecutionTime,

    MAX(ExecutionTimeSeconds) AS MaximumExecutionTime

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    Symbol

ORDER BY
    AverageExecutionTime DESC;
GO


/* =========================================================
   15. CLIENT-SYMBOL TRADING MATRIX
   ========================================================= */

SELECT TOP 100

    ClientID,

    Symbol,

    COUNT(*) AS TradeCount,

    SUM(ExecutedQuantity) AS ExecutedQuantity,

    CAST(
        SUM(TradeValue)
        AS DECIMAL(18,2)
    ) AS Turnover

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    ClientID,
    Symbol

ORDER BY
    Turnover DESC;
GO


/* =========================================================
   16. HIGH-ACTIVITY CLIENTS
   ========================================================= */

WITH ClientActivity AS
(
    SELECT
        ClientID,
        COUNT(*) AS TradeCount
    FROM dbo.[07_Trade_Execution_Book]
    GROUP BY ClientID
),

ActivityStats AS
(
    SELECT
        AVG(CAST(TradeCount AS DECIMAL(18,2))) AS AvgTrades,
        STDEV(CAST(TradeCount AS DECIMAL(18,2))) AS StdTrades
    FROM ClientActivity
)

SELECT
    c.ClientID,

    c.TradeCount,

    CAST(
        s.AvgTrades
        AS DECIMAL(18,2)
    ) AS AverageClientTrades,

    CAST(
        s.AvgTrades + (2 * s.StdTrades)
        AS DECIMAL(18,2)
    ) AS AnomalyThreshold

FROM ClientActivity c

CROSS JOIN ActivityStats s

WHERE
    c.TradeCount >
    s.AvgTrades + (2 * s.StdTrades)

ORDER BY
    c.TradeCount DESC;
GO


/* =========================================================
   17. HIGH-ACTIVITY SYMBOLS
   ========================================================= */

WITH SymbolActivity AS
(
    SELECT
        Symbol,
        COUNT(*) AS TradeCount
    FROM dbo.[07_Trade_Execution_Book]
    GROUP BY Symbol
),

ActivityStats AS
(
    SELECT
        AVG(CAST(TradeCount AS DECIMAL(18,2))) AS AvgTrades,
        STDEV(CAST(TradeCount AS DECIMAL(18,2))) AS StdTrades
    FROM SymbolActivity
)

SELECT
    s.Symbol,

    s.TradeCount,

    CAST(
        a.AvgTrades
        AS DECIMAL(18,2)
    ) AS AverageSymbolTrades,

    CAST(
        a.AvgTrades + (2 * a.StdTrades)
        AS DECIMAL(18,2)
    ) AS AnomalyThreshold

FROM SymbolActivity s

CROSS JOIN ActivityStats a

WHERE
    s.TradeCount >
    a.AvgTrades + (2 * a.StdTrades)

ORDER BY
    s.TradeCount DESC;
GO


/* =========================================================
   18. CLIENT DIVERSIFICATION
   ========================================================= */

SELECT
    ClientID,

    COUNT(DISTINCT Symbol) AS SymbolsTraded,

    COUNT(DISTINCT InstrumentID) AS InstrumentsTraded,

    COUNT(DISTINCT Exchange) AS ExchangesUsed,

    COUNT(*) AS TradeCount,

    CAST(
        SUM(TradeValue)
        AS DECIMAL(18,2)
    ) AS Turnover

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    ClientID

ORDER BY
    SymbolsTraded DESC;
GO


/* =========================================================
   19. SYMBOL CLIENT PARTICIPATION
   ========================================================= */

SELECT
    Symbol,

    COUNT(DISTINCT ClientID) AS ActiveClients,

    COUNT(DISTINCT AccountID) AS ActiveAccounts,

    COUNT(*) AS TradeCount,

    CAST(
        SUM(TradeValue)
        AS DECIMAL(18,2)
    ) AS Turnover

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    Symbol

ORDER BY
    ActiveClients DESC;
GO


/* =========================================================
   20. CLIENT TURNOVER SHARE - TOP 10
   ========================================================= */

WITH ClientTurnover AS
(
    SELECT
        ClientID,
        SUM(TradeValue) AS Turnover
    FROM dbo.[07_Trade_Execution_Book]
    GROUP BY ClientID
),

RankedClients AS
(
    SELECT
        ClientID,
        Turnover,

        ROW_NUMBER() OVER (
            ORDER BY Turnover DESC
        ) AS ClientRank

    FROM ClientTurnover
),

TotalMarket AS
(
    SELECT
        SUM(TradeValue) AS TotalTurnover
    FROM dbo.[07_Trade_Execution_Book]
)

SELECT
    r.ClientRank,

    r.ClientID,

    CAST(
        r.Turnover
        AS DECIMAL(18,2)
    ) AS Turnover,

    CAST(
        r.Turnover * 100.0 /
        NULLIF(t.TotalTurnover,0)
        AS DECIMAL(10,4)
    ) AS TurnoverSharePercentage

FROM RankedClients r

CROSS JOIN TotalMarket t

WHERE
    r.ClientRank <= 10

ORDER BY
    r.ClientRank;
GO