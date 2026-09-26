/* =========================================================
   STOCK MARKET TRADING MIS
   03 - ORDER EXECUTION ANALYSIS
   ========================================================= */

USE StockMarketTradingMIS;
GO


/* =========================================================
   1. CORE ORDER KPIs
   ========================================================= */

WITH OrderExecution AS
(
    SELECT
        o.OrderID,
        o.OrderQuantity,
        o.OrderValue,
        o.Status,

        COALESCE(
            SUM(t.ExecutedQuantity),
            0
        ) AS ExecutedQuantity,

        COUNT(t.TradeID) AS TradeCount,

        COALESCE(
            SUM(t.TradeValue),
            0
        ) AS ExecutedValue

    FROM dbo.[06_Order_Book] o

    LEFT JOIN dbo.[07_Trade_Execution_Book] t
        ON o.OrderID = t.OrderID

    GROUP BY
        o.OrderID,
        o.OrderQuantity,
        o.OrderValue,
        o.Status
)

SELECT
    COUNT(*) AS TotalOrders,

    SUM(
        CASE
            WHEN ExecutedQuantity > 0
            THEN 1
            ELSE 0
        END
    ) AS OrdersWithExecution,

    SUM(
        CASE
            WHEN ExecutedQuantity >= OrderQuantity
            THEN 1
            ELSE 0
        END
    ) AS FullyExecutedOrders,

    SUM(
        CASE
            WHEN ExecutedQuantity > 0
             AND ExecutedQuantity < OrderQuantity
            THEN 1
            ELSE 0
        END
    ) AS PartialExecutionOrders,

    SUM(
        CASE
            WHEN ExecutedQuantity = 0
            THEN 1
            ELSE 0
        END
    ) AS OrdersWithoutExecution,

    CAST(
        SUM(
            CASE
                WHEN ExecutedQuantity > 0
                THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*)
        AS DECIMAL(10,2)
    ) AS ExecutionCompletionRate,

    CAST(
        SUM(
            CASE
                WHEN ExecutedQuantity >= OrderQuantity
                THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*)
        AS DECIMAL(10,2)
    ) AS FullExecutionRate,

    CAST(
        SUM(
            CASE
                WHEN ExecutedQuantity > 0
                 AND ExecutedQuantity < OrderQuantity
                THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*)
        AS DECIMAL(10,2)
    ) AS PartialExecutionRate,

    CAST(
        AVG(CAST(OrderValue AS DECIMAL(18,2)))
        AS DECIMAL(18,2)
    ) AS AverageOrderValue,

    CAST(
        SUM(ExecutedValue)
        AS DECIMAL(18,2)
    ) AS TotalExecutedTurnover

FROM OrderExecution;
GO


/* =========================================================
   2. ORDER STATUS ANALYSIS
   ========================================================= */

SELECT
    Status,
    COUNT(*) AS OrderCount,

    CAST(
        COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER ()
        AS DECIMAL(10,2)
    ) AS PercentageOfOrders,

    SUM(OrderQuantity) AS TotalOrderQuantity,

    CAST(
        SUM(OrderValue)
        AS DECIMAL(18,2)
    ) AS TotalOrderValue

FROM dbo.[06_Order_Book]

GROUP BY Status

ORDER BY OrderCount DESC;
GO


/* =========================================================
   3. ORDER STATUS VS ACTUAL EXECUTION
   ========================================================= */

WITH ExecutionSummary AS
(
    SELECT
        o.OrderID,
        o.Status,
        o.OrderQuantity,

        COALESCE(
            SUM(t.ExecutedQuantity),
            0
        ) AS ExecutedQuantity

    FROM dbo.[06_Order_Book] o

    LEFT JOIN dbo.[07_Trade_Execution_Book] t
        ON o.OrderID = t.OrderID

    GROUP BY
        o.OrderID,
        o.Status,
        o.OrderQuantity
)

SELECT
    Status,

    COUNT(*) AS Orders,

    SUM(
        CASE
            WHEN ExecutedQuantity > 0
            THEN 1
            ELSE 0
        END
    ) AS OrdersWithExecution,

    SUM(
        CASE
            WHEN ExecutedQuantity >= OrderQuantity
            THEN 1
            ELSE 0
        END
    ) AS FullyExecuted,

    SUM(
        CASE
            WHEN ExecutedQuantity > 0
             AND ExecutedQuantity < OrderQuantity
            THEN 1
            ELSE 0
        END
    ) AS PartiallyExecuted,

    SUM(
        CASE
            WHEN ExecutedQuantity = 0
            THEN 1
            ELSE 0
        END
    ) AS NotExecuted

FROM ExecutionSummary

GROUP BY Status

ORDER BY Orders DESC;
GO


/* =========================================================
   4. PARTIAL EXECUTION ANALYSIS
   ========================================================= */

WITH ExecutionSummary AS
(
    SELECT
        o.OrderID,
        o.ClientID,
        o.AccountID,
        o.Symbol,
        o.Side,
        o.OrderQuantity,
        o.OrderPrice,

        COALESCE(
            SUM(t.ExecutedQuantity),
            0
        ) AS ExecutedQuantity

    FROM dbo.[06_Order_Book] o

    LEFT JOIN dbo.[07_Trade_Execution_Book] t
        ON o.OrderID = t.OrderID

    GROUP BY
        o.OrderID,
        o.ClientID,
        o.AccountID,
        o.Symbol,
        o.Side,
        o.OrderQuantity,
        o.OrderPrice
)

SELECT
    OrderID,
    ClientID,
    AccountID,
    Symbol,
    Side,
    OrderQuantity,
    ExecutedQuantity,

    OrderQuantity - ExecutedQuantity
        AS RemainingQuantity,

    CAST(
        ExecutedQuantity * 100.0 /
        NULLIF(OrderQuantity,0)
        AS DECIMAL(10,2)
    ) AS ExecutionPercentage

FROM ExecutionSummary

WHERE
    ExecutedQuantity > 0
    AND ExecutedQuantity < OrderQuantity

ORDER BY
    ExecutionPercentage ASC;
GO


/* =========================================================
   5. ORDER QUANTITY VS EXECUTED QUANTITY
   ========================================================= */

WITH ExecutionSummary AS
(
    SELECT
        o.OrderID,
        o.OrderQuantity,

        COALESCE(
            SUM(t.ExecutedQuantity),
            0
        ) AS ExecutedQuantity

    FROM dbo.[06_Order_Book] o

    LEFT JOIN dbo.[07_Trade_Execution_Book] t
        ON o.OrderID = t.OrderID

    GROUP BY
        o.OrderID,
        o.OrderQuantity
)

SELECT
    COUNT(*) AS TotalOrders,

    SUM(OrderQuantity) AS TotalOrderedQuantity,

    SUM(ExecutedQuantity) AS TotalExecutedQuantity,

    SUM(
        OrderQuantity - ExecutedQuantity
    ) AS TotalUnexecutedQuantity,

    CAST(
        SUM(ExecutedQuantity) * 100.0 /
        NULLIF(SUM(OrderQuantity),0)
        AS DECIMAL(10,2)
    ) AS QuantityExecutionRate

FROM ExecutionSummary;
GO


/* =========================================================
   6. DAILY ORDER ACTIVITY
   ========================================================= */

SELECT
    CAST(OrderDate AS DATE) AS OrderDate,

    COUNT(*) AS TotalOrders,

    SUM(OrderQuantity) AS OrderQuantity,

    CAST(
        SUM(OrderValue)
        AS DECIMAL(18,2)
    ) AS OrderValue,

    COUNT(
        CASE
            WHEN Status = 'EXECUTED'
            THEN 1
        END
    ) AS ExecutedOrders,

    COUNT(
        CASE
            WHEN Status = 'PARTIAL'
            THEN 1
        END
    ) AS PartialOrders,

    COUNT(
        CASE
            WHEN Status = 'REJECTED'
            THEN 1
        END
    ) AS RejectedOrders,

    COUNT(
        CASE
            WHEN Status = 'CANCELLED'
            THEN 1
        END
    ) AS CancelledOrders,

    COUNT(
        CASE
            WHEN Status = 'PENDING'
            THEN 1
        END
    ) AS PendingOrders

FROM dbo.[06_Order_Book]

GROUP BY
    CAST(OrderDate AS DATE)

ORDER BY
    OrderDate;
GO


/* =========================================================
   7. DAILY EXECUTION / TURNOVER
   ========================================================= */

SELECT
    CAST(TradeDate AS DATE) AS TradeDate,

    COUNT(*) AS TradeCount,

    COUNT(DISTINCT OrderID) AS OrdersExecuted,

    SUM(ExecutedQuantity) AS ExecutedQuantity,

    CAST(
        SUM(TradeValue)
        AS DECIMAL(18,2)
    ) AS Turnover,

    CAST(
        AVG(
            CAST(ExecutionTimeSeconds AS DECIMAL(18,2))
        )
        AS DECIMAL(18,2)
    ) AS AverageExecutionTimeSeconds

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    CAST(TradeDate AS DATE)

ORDER BY
    TradeDate;
GO


/* =========================================================
   8. INTRADAY TRADING ACTIVITY
   ========================================================= */

SELECT
    IntradayBucket,

    COUNT(*) AS OrderCount,

    SUM(OrderQuantity) AS OrderQuantity,

    CAST(
        SUM(OrderValue)
        AS DECIMAL(18,2)
    ) AS OrderValue,

    COUNT(
        CASE
            WHEN Status = 'EXECUTED'
            THEN 1
        END
    ) AS ExecutedOrders,

    COUNT(
        CASE
            WHEN Status = 'REJECTED'
            THEN 1
        END
    ) AS RejectedOrders

FROM dbo.[06_Order_Book]

GROUP BY
    IntradayBucket

ORDER BY
    IntradayBucket;
GO


/* =========================================================
   9. MARKET VS LIMIT ORDER BEHAVIOR
   ========================================================= */

SELECT
    OrderType,

    COUNT(*) AS TotalOrders,

    SUM(OrderQuantity) AS TotalOrderQuantity,

    CAST(
        SUM(OrderValue)
        AS DECIMAL(18,2)
    ) AS TotalOrderValue,

    COUNT(
        CASE
            WHEN Status = 'EXECUTED'
            THEN 1
        END
    ) AS ExecutedOrders,

    COUNT(
        CASE
            WHEN Status = 'REJECTED'
            THEN 1
        END
    ) AS RejectedOrders,

    CAST(
        COUNT(
            CASE
                WHEN Status = 'EXECUTED'
                THEN 1
            END
        ) * 100.0 / COUNT(*)
        AS DECIMAL(10,2)
    ) AS ExecutionRate

FROM dbo.[06_Order_Book]

GROUP BY
    OrderType

ORDER BY
    TotalOrders DESC;
GO


/* =========================================================
   10. CLIENT ORDER EXECUTION PERFORMANCE
   ========================================================= */

WITH ClientExecution AS
(
    SELECT
        o.ClientID,

        COUNT(DISTINCT o.OrderID) AS TotalOrders,

        COUNT(
            DISTINCT
            CASE
                WHEN t.OrderID IS NOT NULL
                THEN o.OrderID
            END
        ) AS OrdersWithExecution,

        SUM(o.OrderQuantity) AS OrderedQuantity,

        COALESCE(
            SUM(t.ExecutedQuantity),
            0
        ) AS ExecutedQuantity,

        COALESCE(
            SUM(t.TradeValue),
            0
        ) AS Turnover

    FROM dbo.[06_Order_Book] o

    LEFT JOIN dbo.[07_Trade_Execution_Book] t
        ON o.OrderID = t.OrderID

    GROUP BY
        o.ClientID
)

SELECT
    ClientID,
    TotalOrders,
    OrdersWithExecution,
    OrderedQuantity,
    ExecutedQuantity,

    CAST(
        OrdersWithExecution * 100.0 /
        NULLIF(TotalOrders,0)
        AS DECIMAL(10,2)
    ) AS ExecutionRate,

    CAST(
        Turnover
        AS DECIMAL(18,2)
    ) AS Turnover

FROM ClientExecution

ORDER BY
    Turnover DESC;
GO


/* =========================================================
   11. SYMBOL ORDER EXECUTION PERFORMANCE
   ========================================================= */

WITH SymbolExecution AS
(
    SELECT
        o.Symbol,

        COUNT(DISTINCT o.OrderID) AS TotalOrders,

        COUNT(
            DISTINCT
            CASE
                WHEN t.OrderID IS NOT NULL
                THEN o.OrderID
            END
        ) AS OrdersWithExecution,

        SUM(o.OrderQuantity) AS OrderedQuantity,

        COALESCE(
            SUM(t.ExecutedQuantity),
            0
        ) AS ExecutedQuantity,

        COALESCE(
            SUM(t.TradeValue),
            0
        ) AS Turnover

    FROM dbo.[06_Order_Book] o

    LEFT JOIN dbo.[07_Trade_Execution_Book] t
        ON o.OrderID = t.OrderID

    GROUP BY
        o.Symbol
)

SELECT
    Symbol,
    TotalOrders,
    OrdersWithExecution,
    OrderedQuantity,
    ExecutedQuantity,

    CAST(
        OrdersWithExecution * 100.0 /
        NULLIF(TotalOrders,0)
        AS DECIMAL(10,2)
    ) AS ExecutionRate,

    CAST(
        Turnover
        AS DECIMAL(18,2)
    ) AS Turnover

FROM SymbolExecution

ORDER BY
    Turnover DESC;
GO


/* =========================================================
   12. EXECUTION TIME ANALYSIS
   ========================================================= */

SELECT
    COUNT(*) AS TotalTrades,

    CAST(
        AVG(
            CAST(ExecutionTimeSeconds AS DECIMAL(18,2))
        )
        AS DECIMAL(18,2)
    ) AS AverageExecutionTime,

    MIN(ExecutionTimeSeconds) AS MinimumExecutionTime,

    MAX(ExecutionTimeSeconds) AS MaximumExecutionTime,

    CAST(
        SUM(
            CASE
                WHEN ExecutionTimeSeconds <= 30
                THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*)
        AS DECIMAL(10,2)
    ) AS ExecutedWithin30Seconds,

    CAST(
        SUM(
            CASE
                WHEN ExecutionTimeSeconds > 300
                THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*)
        AS DECIMAL(10,2)
    ) AS ExecutionsAbove5Minutes

FROM dbo.[07_Trade_Execution_Book];
GO


/* =========================================================
   13. ORDER-LEVEL EXECUTION SUMMARY
   ========================================================= */

WITH ExecutionSummary AS
(
    SELECT
        o.OrderID,
        o.OrderDate,
        o.ClientID,
        o.AccountID,
        o.Symbol,
        o.Exchange,
        o.Side,
        o.OrderType,
        o.OrderQuantity,
        o.OrderPrice,
        o.Status,

        COALESCE(
            SUM(t.ExecutedQuantity),
            0
        ) AS ExecutedQuantity,

        COALESCE(
            SUM(t.TradeValue),
            0
        ) AS ExecutedValue,

        COUNT(t.TradeID) AS TradeCount,

        COALESCE(
            AVG(t.ExecutionTimeSeconds),
            0
        ) AS AverageExecutionTime

    FROM dbo.[06_Order_Book] o

    LEFT JOIN dbo.[07_Trade_Execution_Book] t
        ON o.OrderID = t.OrderID

    GROUP BY
        o.OrderID,
        o.OrderDate,
        o.ClientID,
        o.AccountID,
        o.Symbol,
        o.Exchange,
        o.Side,
        o.OrderType,
        o.OrderQuantity,
        o.OrderPrice,
        o.Status
)

SELECT
    OrderID,
    OrderDate,
    ClientID,
    AccountID,
    Symbol,
    Exchange,
    Side,
    OrderType,
    OrderQuantity,
    ExecutedQuantity,

    OrderQuantity - ExecutedQuantity
        AS RemainingQuantity,

    CAST(
        ExecutedQuantity * 100.0 /
        NULLIF(OrderQuantity,0)
        AS DECIMAL(10,2)
    ) AS ExecutionPercentage,

    OrderPrice,

    CAST(
        ExecutedValue
        AS DECIMAL(18,2)
    ) AS ExecutedValue,

    TradeCount,

    CAST(
        AverageExecutionTime
        AS DECIMAL(18,2)
    ) AS AverageExecutionTime,

    Status

FROM ExecutionSummary

ORDER BY
    OrderDate,
    OrderID;
GO


/* =========================================================
   14. ORDER-LEVEL SLIPPAGE ANALYSIS
   MARKET ORDERS WITH NULL ORDER PRICE ARE EXCLUDED
   ========================================================= */

WITH OrderExecution AS
(
    SELECT
        o.OrderID,
        o.Symbol,
        o.Side,
        o.OrderType,
        o.OrderPrice,
        SUM(t.ExecutedQuantity) AS ExecutedQuantity,

        SUM(
            t.ExecutedQuantity * t.ExecutionPrice
        ) AS ExecutionValue,

        SUM(
            t.ExecutedQuantity
        ) * o.OrderPrice AS ExpectedValue

    FROM dbo.[06_Order_Book] o

    INNER JOIN dbo.[07_Trade_Execution_Book] t
        ON o.OrderID = t.OrderID

    WHERE
        o.OrderPrice IS NOT NULL
        AND o.OrderPrice <> 0

    GROUP BY
        o.OrderID,
        o.Symbol,
        o.Side,
        o.OrderType,
        o.OrderPrice
)

SELECT
    OrderID,
    Symbol,
    Side,
    OrderType,
    OrderPrice,
    ExecutedQuantity,

    CAST(
        ExecutionValue / NULLIF(ExecutedQuantity,0)
        AS DECIMAL(18,4)
    ) AS AverageExecutionPrice,

    CAST(
        (
            ExecutionValue - ExpectedValue
        )
        AS DECIMAL(18,2)
    ) AS RawSlippageValue,

    CAST(
        CASE
            WHEN Side = 'BUY'
            THEN
                (
                    ExecutionValue - ExpectedValue
                )

            WHEN Side = 'SELL'
            THEN
                (
                    ExpectedValue - ExecutionValue
                )

            ELSE 0
        END
        AS DECIMAL(18,2)
    ) AS AdverseSlippageValue,

    CAST(
        CASE
            WHEN Side = 'BUY'
            THEN
                (
                    ExecutionValue - ExpectedValue
                ) * 100.0 /
                NULLIF(ExpectedValue,0)

            WHEN Side = 'SELL'
            THEN
                (
                    ExpectedValue - ExecutionValue
                ) * 100.0 /
                NULLIF(ExpectedValue,0)

            ELSE 0
        END
        AS DECIMAL(10,4)
    ) AS AdverseSlippagePct

FROM OrderExecution

ORDER BY
    ABS(
        CASE
            WHEN Side = 'BUY'
            THEN
                (
                    ExecutionValue - ExpectedValue
                ) * 100.0 /
                NULLIF(ExpectedValue,0)

            WHEN Side = 'SELL'
            THEN
                (
                    ExpectedValue - ExecutionValue
                ) * 100.0 /
                NULLIF(ExpectedValue,0)

            ELSE 0
        END
    ) DESC;
GO