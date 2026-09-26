/* =========================================================
   STOCK MARKET TRADING MIS
   08 - ADVANCED MIS VIEWS
   ========================================================= */

USE StockMarketTradingMIS;
GO


/* =========================================================
   1. EXECUTIVE TRADING KPI VIEW
   ========================================================= */

CREATE OR ALTER VIEW dbo.vw_Trading_KPI
AS

SELECT
    COUNT(DISTINCT o.OrderID) AS TotalOrders,

    COUNT(DISTINCT t.OrderID) AS OrdersWithExecution,

    COUNT(DISTINCT
        CASE
            WHEN o.Status = 'EXECUTED'
                THEN o.OrderID
        END
    ) AS FullyExecutedOrders,

    COUNT(DISTINCT
        CASE
            WHEN o.Status = 'PARTIAL'
                THEN o.OrderID
        END
    ) AS PartialOrders,

    COUNT(DISTINCT
        CASE
            WHEN o.Status = 'REJECTED'
                THEN o.OrderID
        END
    ) AS RejectedOrders,

    COUNT(DISTINCT
        CASE
            WHEN o.Status = 'CANCELLED'
                THEN o.OrderID
        END
    ) AS CancelledOrders,

    COUNT(DISTINCT
        CASE
            WHEN o.Status = 'PENDING'
                THEN o.OrderID
        END
    ) AS PendingOrders,

    CAST(
        COUNT(DISTINCT t.OrderID) * 100.0 /
        NULLIF(COUNT(DISTINCT o.OrderID),0)
        AS DECIMAL(10,2)
    ) AS ExecutionCompletionRate,

    CAST(
        COUNT(DISTINCT
            CASE
                WHEN o.Status = 'EXECUTED'
                    THEN o.OrderID
            END
        ) * 100.0 /
        NULLIF(COUNT(DISTINCT o.OrderID),0)
        AS DECIMAL(10,2)
    ) AS FullyExecutedRate,

    CAST(
        COUNT(DISTINCT
            CASE
                WHEN o.Status = 'REJECTED'
                    THEN o.OrderID
            END
        ) * 100.0 /
        NULLIF(COUNT(DISTINCT o.OrderID),0)
        AS DECIMAL(10,2)
    ) AS RejectionRate,

    CAST(
        SUM(o.OrderValue)
        AS DECIMAL(18,2)
    ) AS TotalOrderValue,

    CAST(
        SUM(t.TradeValue)
        AS DECIMAL(18,2)
    ) AS TotalTurnover,

    CAST(
        AVG(
            CAST(t.ExecutionTimeSeconds AS DECIMAL(18,2))
        )
        AS DECIMAL(18,2)
    ) AS AverageExecutionTime,

    CAST(
        SUM(t.ExecutedQuantity)
        AS DECIMAL(18,2)
    ) AS TotalExecutedQuantity

FROM dbo.[06_Order_Book] o

LEFT JOIN dbo.[07_Trade_Execution_Book] t
    ON o.OrderID = t.OrderID;
GO


/* =========================================================
   2. DAILY TRADING MIS VIEW
   ========================================================= */

CREATE OR ALTER VIEW dbo.vw_Daily_Trading_MIS
AS

SELECT
    CAST(o.OrderDate AS DATE) AS TradingDate,

    COUNT(DISTINCT o.OrderID) AS TotalOrders,

    COUNT(DISTINCT t.OrderID) AS OrdersWithExecution,

    COUNT(DISTINCT t.TradeID) AS TradeCount,

    COUNT(DISTINCT o.ClientID) AS ActiveClients,

    COUNT(DISTINCT o.Symbol) AS ActiveSymbols,

    SUM(o.OrderQuantity) AS OrderedQuantity,

    ISNULL(SUM(t.ExecutedQuantity),0)
        AS ExecutedQuantity,

    CAST(
        SUM(o.OrderValue)
        AS DECIMAL(18,2)
    ) AS OrderValue,

    CAST(
        ISNULL(SUM(t.TradeValue),0)
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
    CAST(o.OrderDate AS DATE);
GO


/* =========================================================
   3. CLIENT PERFORMANCE VIEW
   ========================================================= */

CREATE OR ALTER VIEW dbo.vw_Client_Performance
AS

SELECT
    o.ClientID,

    COUNT(DISTINCT o.OrderID) AS TotalOrders,

    COUNT(DISTINCT t.OrderID) AS OrdersWithExecution,

    COUNT(DISTINCT t.TradeID) AS TradeCount,

    COUNT(DISTINCT o.Symbol) AS SymbolsTraded,

    SUM(o.OrderQuantity) AS OrderedQuantity,

    ISNULL(SUM(t.ExecutedQuantity),0)
        AS ExecutedQuantity,

    CAST(
        ISNULL(SUM(t.TradeValue),0)
        AS DECIMAL(18,2)
    ) AS Turnover,

    CAST(
        COUNT(DISTINCT t.OrderID) * 100.0 /
        NULLIF(COUNT(DISTINCT o.OrderID),0)
        AS DECIMAL(10,2)
    ) AS ExecutionRate,

    CAST(
        AVG(
            CAST(t.ExecutionTimeSeconds AS DECIMAL(18,2))
        )
        AS DECIMAL(18,2)
    ) AS AverageExecutionTime,

    CAST(
        AVG(
            CAST(t.SlippagePct AS DECIMAL(18,6))
        )
        AS DECIMAL(18,6)
    ) AS AverageSlippagePct

FROM dbo.[06_Order_Book] o

LEFT JOIN dbo.[07_Trade_Execution_Book] t
    ON o.OrderID = t.OrderID

GROUP BY
    o.ClientID;
GO


/* =========================================================
   4. SYMBOL PERFORMANCE VIEW
   ========================================================= */

CREATE OR ALTER VIEW dbo.vw_Symbol_Performance
AS

SELECT
    o.Symbol,

    COUNT(DISTINCT o.OrderID) AS TotalOrders,

    COUNT(DISTINCT t.OrderID) AS OrdersWithExecution,

    COUNT(DISTINCT t.TradeID) AS TradeCount,

    COUNT(DISTINCT o.ClientID) AS ActiveClients,

    SUM(o.OrderQuantity) AS OrderedQuantity,

    ISNULL(SUM(t.ExecutedQuantity),0)
        AS ExecutedQuantity,

    CAST(
        ISNULL(SUM(t.TradeValue),0)
        AS DECIMAL(18,2)
    ) AS Turnover,

    CAST(
        ISNULL(SUM(t.ExecutedQuantity),0) * 100.0 /
        NULLIF(SUM(o.OrderQuantity),0)
        AS DECIMAL(10,2)
    ) AS QuantityExecutionRate,

    CAST(
        AVG(
            CAST(t.SlippagePct AS DECIMAL(18,6))
        )
        AS DECIMAL(18,6)
    ) AS AverageSlippagePct,

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
    o.Symbol;
GO


/* =========================================================
   5. REJECTION MIS VIEW
   ========================================================= */

CREATE OR ALTER VIEW dbo.vw_Rejection_MIS
AS

SELECT
    r.ClientID,

    r.Symbol,

    r.RejectionReason,

    COUNT(*) AS RejectionCount

FROM dbo.[08_Order_Rejection_Data] r

GROUP BY
    r.ClientID,
    r.Symbol,
    r.RejectionReason;
GO


/* =========================================================
   6. INTRADAY TRADING VIEW
   ========================================================= */

CREATE OR ALTER VIEW dbo.vw_Intraday_Trading
AS

SELECT
    o.IntradayBucket,

    COUNT(DISTINCT o.OrderID) AS TotalOrders,

    COUNT(DISTINCT t.OrderID) AS OrdersExecuted,

    COUNT(DISTINCT t.TradeID) AS TradeCount,

    SUM(o.OrderQuantity) AS OrderedQuantity,

    ISNULL(SUM(t.ExecutedQuantity),0)
        AS ExecutedQuantity,

    CAST(
        ISNULL(SUM(t.TradeValue),0)
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
    o.IntradayBucket;
GO


/* =========================================================
   7. MARKET VS LIMIT VIEW
   ========================================================= */

CREATE OR ALTER VIEW dbo.vw_OrderType_Performance
AS

SELECT
    o.OrderType,

    COUNT(DISTINCT o.OrderID) AS TotalOrders,

    COUNT(DISTINCT t.OrderID) AS OrdersExecuted,

    COUNT(DISTINCT t.TradeID) AS TradeCount,

    SUM(o.OrderQuantity) AS OrderedQuantity,

    ISNULL(SUM(t.ExecutedQuantity),0)
        AS ExecutedQuantity,

    CAST(
        ISNULL(SUM(t.TradeValue),0)
        AS DECIMAL(18,2)
    ) AS Turnover,

    CAST(
        COUNT(DISTINCT t.OrderID) * 100.0 /
        NULLIF(COUNT(DISTINCT o.OrderID),0)
        AS DECIMAL(10,2)
    ) AS ExecutionRate,

    CAST(
        AVG(
            CAST(t.SlippagePct AS DECIMAL(18,6))
        )
        AS DECIMAL(18,6)
    ) AS AverageSlippagePct

FROM dbo.[06_Order_Book] o

LEFT JOIN dbo.[07_Trade_Execution_Book] t
    ON o.OrderID = t.OrderID

GROUP BY
    o.OrderType;
GO


/* =========================================================
   8. CLIENT TURNOVER RANKING VIEW
   ========================================================= */

CREATE OR ALTER VIEW dbo.vw_Client_Turnover_Ranking
AS

WITH ClientTurnover AS
(
    SELECT
        ClientID,
        SUM(TradeValue) AS Turnover
    FROM dbo.[07_Trade_Execution_Book]
    GROUP BY ClientID
)

SELECT
    ClientID,

    CAST(
        Turnover
        AS DECIMAL(18,2)
    ) AS Turnover,

    RANK() OVER (
        ORDER BY Turnover DESC
    ) AS TurnoverRank

FROM ClientTurnover;
GO


/* =========================================================
   9. SYMBOL TURNOVER RANKING VIEW
   ========================================================= */

CREATE OR ALTER VIEW dbo.vw_Symbol_Turnover_Ranking
AS

WITH SymbolTurnover AS
(
    SELECT
        Symbol,
        SUM(TradeValue) AS Turnover
    FROM dbo.[07_Trade_Execution_Book]
    GROUP BY Symbol
)

SELECT
    Symbol,

    CAST(
        Turnover
        AS DECIMAL(18,2)
    ) AS Turnover,

    RANK() OVER (
        ORDER BY Turnover DESC
    ) AS TurnoverRank

FROM SymbolTurnover;
GO


/* =========================================================
   10. POSITION RECONCILIATION VIEW
   ========================================================= */

CREATE OR ALTER VIEW dbo.vw_Position_Reconciliation
AS

SELECT
    PositionID,

    AccountID,

    ClientID,

    InstrumentID,

    Symbol,

    BuyQty,

    SellQty,

    NetQuantity,

    BuyQty - SellQty
        AS CalculatedNetQuantity,

    NetQuantity -
        (BuyQty - SellQty)
        AS Difference,

    CASE
        WHEN NetQuantity = BuyQty - SellQty
            THEN 'RECONCILED'
        ELSE 'EXCEPTION'
    END AS ReconciliationStatus

FROM dbo.[10_Position_Data];
GO


/* =========================================================
   11. TRADE POSITION RECONCILIATION VIEW
   ========================================================= */

CREATE OR ALTER VIEW dbo.vw_Trade_Position_Reconciliation
AS

WITH TradeSummary AS
(
    SELECT
        ClientID,
        AccountID,
        InstrumentID,
        Symbol,

        SUM(
            CASE
                WHEN Side = 'BUY'
                    THEN ExecutedQuantity

                WHEN Side = 'SELL'
                    THEN -ExecutedQuantity

                ELSE 0
            END
        ) AS TradeNetQuantity,

        SUM(
            CASE
                WHEN Side = 'BUY'
                    THEN ExecutedQuantity
                ELSE 0
            END
        ) AS TradeBuyQuantity,

        SUM(
            CASE
                WHEN Side = 'SELL'
                    THEN ExecutedQuantity
                ELSE 0
            END
        ) AS TradeSellQuantity

    FROM dbo.[07_Trade_Execution_Book]

    GROUP BY
        ClientID,
        AccountID,
        InstrumentID,
        Symbol
),

PositionSummary AS
(
    SELECT
        ClientID,
        AccountID,
        InstrumentID,
        Symbol,

        SUM(BuyQty) AS PositionBuyQuantity,

        SUM(SellQty) AS PositionSellQuantity,

        SUM(NetQuantity) AS PositionNetQuantity

    FROM dbo.[10_Position_Data]

    GROUP BY
        ClientID,
        AccountID,
        InstrumentID,
        Symbol
)

SELECT
    COALESCE(t.ClientID,p.ClientID)
        AS ClientID,

    COALESCE(t.AccountID,p.AccountID)
        AS AccountID,

    COALESCE(t.InstrumentID,p.InstrumentID)
        AS InstrumentID,

    COALESCE(t.Symbol,p.Symbol)
        AS Symbol,

    ISNULL(t.TradeBuyQuantity,0)
        AS TradeBuyQuantity,

    ISNULL(p.PositionBuyQuantity,0)
        AS PositionBuyQuantity,

    ISNULL(t.TradeSellQuantity,0)
        AS TradeSellQuantity,

    ISNULL(p.PositionSellQuantity,0)
        AS PositionSellQuantity,

    ISNULL(t.TradeNetQuantity,0)
        AS TradeNetQuantity,

    ISNULL(p.PositionNetQuantity,0)
        AS PositionNetQuantity,

    ISNULL(p.PositionNetQuantity,0)
        -
        ISNULL(t.TradeNetQuantity,0)
        AS Difference,

    CASE
        WHEN t.ClientID IS NULL
            THEN 'POSITION_WITHOUT_TRADE'

        WHEN p.ClientID IS NULL
            THEN 'TRADE_WITHOUT_POSITION'

        WHEN t.TradeNetQuantity
             =
             p.PositionNetQuantity
            THEN 'RECONCILED'

        ELSE 'QUANTITY_MISMATCH'
    END AS ReconciliationStatus

FROM TradeSummary t

FULL OUTER JOIN PositionSummary p

    ON t.ClientID = p.ClientID

    AND t.AccountID = p.AccountID

    AND t.InstrumentID = p.InstrumentID

    AND t.Symbol = p.Symbol;
GO


/* =========================================================
   12. DAILY REJECTION VIEW
   ========================================================= */

CREATE OR ALTER VIEW dbo.vw_Daily_Rejection
AS

SELECT
    CAST(o.OrderDate AS DATE) AS TradingDate,

    COUNT(DISTINCT o.OrderID) AS TotalOrders,

    COUNT(DISTINCT r.RejectionID) AS RejectedOrders,

    CAST(
        COUNT(DISTINCT r.RejectionID) * 100.0 /
        NULLIF(COUNT(DISTINCT o.OrderID),0)
        AS DECIMAL(10,2)
    ) AS RejectionRate

FROM dbo.[06_Order_Book] o

LEFT JOIN dbo.[08_Order_Rejection_Data] r
    ON o.OrderID = r.OrderID

GROUP BY
    CAST(o.OrderDate AS DATE);
GO


/* =========================================================
   13. DAILY TURNOVER & EXECUTION VIEW
   ========================================================= */

CREATE OR ALTER VIEW dbo.vw_Daily_Turnover
AS

SELECT
    CAST(TradeDate AS DATE) AS TradingDate,

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
        AVG(
            CAST(ExecutionTimeSeconds AS DECIMAL(18,2))
        )
        AS DECIMAL(18,2)
    ) AS AverageExecutionTime,

    CAST(
        AVG(
            CAST(SlippagePct AS DECIMAL(18,6))
        )
        AS DECIMAL(18,6)
    ) AS AverageSlippagePct

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    CAST(TradeDate AS DATE);
GO

/* ============================================================
   09_Order_Status.sql
   Purpose: Order Funnel / Order Status Analysis for Power BI
   ============================================================ */

CREATE OR ALTER VIEW dbo.vw_Order_Status
AS

SELECT
    Status AS OrderStatus,
    COUNT(*) AS OrderCount
FROM dbo.[06_Order_Book]
GROUP BY
    Status;

GO

CREATE OR ALTER VIEW dbo.vw_Order_Execution_Detail
AS
SELECT
    o.OrderID,
    o.OrderDate,
    o.OrderDateTime,
    o.AccountID,
    o.ClientID,
    o.InstrumentID,
    o.Symbol,
    o.Exchange,
    o.Side,
    o.OrderType,
    o.OrderQuantity,
    o.OrderPrice,
    o.OrderValue,
    o.Status,
    o.Channel,
    o.IntradayBucket,

    -- Execution information
    ISNULL(t.ExecutedQuantity, 0) AS ExecutedQuantity,

    ISNULL(t.ExecutionCount, 0) AS ExecutionCount,

    t.AverageExecutionPrice,

    ISNULL(t.ExecutedTradeValue, 0) AS ExecutedTradeValue,

    t.ExecutionTimeSeconds,

    t.TotalSlippageValue,

    t.AverageSlippagePct

FROM dbo.[06_Order_Book] o

LEFT JOIN
(
    SELECT
        OrderID,

        SUM(ExecutedQuantity) AS ExecutedQuantity,

        COUNT(*) AS ExecutionCount,

        CASE
            WHEN SUM(ExecutedQuantity) > 0
            THEN
                SUM(ExecutedQuantity * ExecutionPrice)
                / SUM(ExecutedQuantity)
            ELSE NULL
        END AS AverageExecutionPrice,

        SUM(TradeValue) AS ExecutedTradeValue,

        MAX(ExecutionTimeSeconds) AS ExecutionTimeSeconds,

        SUM(ISNULL(SlippageValue, 0)) AS TotalSlippageValue,

        CASE
            WHEN SUM(ExecutedQuantity) > 0
            THEN
                SUM(
                    ISNULL(SlippagePct, 0) * ExecutedQuantity
                ) / SUM(ExecutedQuantity)
            ELSE NULL
        END AS AverageSlippagePct

    FROM dbo.[07_Trade_Execution_Book]

    GROUP BY OrderID
) t
    ON o.OrderID = t.OrderID;
GO
/*----------------------------------------------------------
      brokerage view
-----------------------------------------------------------*/
CREATE OR ALTER VIEW dbo.vw_Brokerage_Charges_MIS
AS
SELECT
    TradeID,
    OrderID,
    TradeDate,
    SettlementDate,
    AccountID,
    ClientID,
    InstrumentID,
    Symbol,
    Side,

    ExecutedQuantity,
    ExecutionPrice,
    TradeValue,

    -- Individual Charges
    Brokerage,
    STT,
    ExchangeCharges,
    GST,
    SEBICharges,
    StampDuty,

    -- Total Transaction Charges
    TotalCharges,

    -- Charge as % of Trade Value
    CASE
        WHEN TradeValue <> 0
        THEN (TotalCharges / TradeValue) * 100
        ELSE 0
    END AS ChargePct,

    ChargeDateTime

FROM dbo.[09_Brokerage_Charges];
GO
/*----------------------------------
   p&l view
   --------------------------------*/

CREATE OR ALTER VIEW dbo.PnL_MIS
AS
SELECT
    PositionID,
    PositionDate,
    AccountID,
    ClientID,
    InstrumentID,
    Symbol,

    BuyQty,
    SellQty,
    NetQuantity,

    AvgBuyPrice,
    AvgSellPrice,
    MarketPrice,

    RealizedPnL,
    UnrealizedPnL,
    GrossPnL

FROM dbo.[10_Position_Data];
GO

------------------------------------------

CREATE OR ALTER VIEW dbo.Settlement_MIS
AS
SELECT
    TradeID,
    OrderID,
    TradeDate,
    ExecutionDate,
    SettlementDate,
    AccountID,
    ClientID,
    InstrumentID,
    Symbol,
    Exchange,
    ExecutedQuantity,
    ExecutionPrice,
    TradeValue,

    DATEDIFF(
        DAY,
        CAST(ExecutionDate AS DATE),
        CAST(SettlementDate AS DATE)
    ) AS SettlementDays,

    CASE
        WHEN SettlementDate IS NULL
            THEN 'Missing Settlement Date'

        WHEN CAST(SettlementDate AS DATE)
             < CAST(ExecutionDate AS DATE)
            THEN 'Invalid Settlement Date'

        WHEN CAST(SettlementDate AS DATE)
             = CAST(ExecutionDate AS DATE)
            THEN 'Same Day Settlement'

        ELSE 'Future Settlement'
    END AS SettlementStatus

FROM dbo.[07_Trade_Execution_Book];
GO
----------------------------------------------------


CREATE OR ALTER VIEW dbo.High_Volume_Anomalies
AS

WITH ClientStats AS
(
    SELECT
        ClientID,
        COUNT(*) AS TradeCount
    FROM dbo.[07_Trade_Execution_Book]
    GROUP BY ClientID
),
ClientThreshold AS
(
    SELECT
        AVG(CAST(TradeCount AS FLOAT)) AS MeanTrades,
        STDEV(CAST(TradeCount AS FLOAT)) AS StdTrades
    FROM ClientStats
),

SymbolStats AS
(
    SELECT
        Symbol,
        COUNT(*) AS TradeCount
    FROM dbo.[07_Trade_Execution_Book]
    GROUP BY Symbol
),
SymbolThreshold AS
(
    SELECT
        AVG(CAST(TradeCount AS FLOAT)) AS MeanTrades,
        STDEV(CAST(TradeCount AS FLOAT)) AS StdTrades
    FROM SymbolStats
)

SELECT
    'CLIENT' AS EntityType,
    CAST(C.ClientID AS VARCHAR(100)) AS Entity,
    C.TradeCount,
    T.MeanTrades,
    T.StdTrades,
    T.MeanTrades + (2 * T.StdTrades) AS AnomalyThreshold,
    'High Volume' AS AnomalyType
FROM ClientStats C
CROSS JOIN ClientThreshold T
WHERE C.TradeCount > T.MeanTrades + (2 * T.StdTrades)

UNION ALL

SELECT
    'SYMBOL' AS EntityType,
    CAST(S.Symbol AS VARCHAR(100)) AS Entity,
    S.TradeCount,
    T.MeanTrades,
    T.StdTrades,
    T.MeanTrades + (2 * T.StdTrades) AS AnomalyThreshold,
    'High Volume' AS AnomalyType
FROM SymbolStats S
CROSS JOIN SymbolThreshold T
WHERE S.TradeCount > T.MeanTrades + (2 * T.StdTrades);
GO

---------------------------------------------------------------

CREATE OR ALTER VIEW dbo.High_Rejection_Anomalies
AS

WITH ClientRejection AS
(
    SELECT
        O.ClientID,
        COUNT(*) AS TotalOrders,
        SUM(
            CASE
                WHEN O.Status = 'REJECTED' THEN 1
                ELSE 0
            END
        ) AS RejectedOrders
    FROM dbo.[06_Order_Book] O
    GROUP BY O.ClientID
),
SymbolRejection AS
(
    SELECT
        O.Symbol,
        COUNT(*) AS TotalOrders,
        SUM(
            CASE
                WHEN O.Status = 'REJECTED' THEN 1
                ELSE 0
            END
        ) AS RejectedOrders
    FROM dbo.[06_Order_Book] O
    GROUP BY O.Symbol
)

SELECT
    'CLIENT' AS EntityType,
    CAST(ClientID AS VARCHAR(100)) AS Entity,
    TotalOrders,
    RejectedOrders,
    CAST(
        RejectedOrders * 100.0 / NULLIF(TotalOrders,0)
        AS DECIMAL(10,2)
    ) AS RejectionRate,
    'High Rejection Rate' AS AnomalyType
FROM ClientRejection
WHERE TotalOrders >= 20
  AND RejectedOrders * 100.0 / NULLIF(TotalOrders,0) >= 20

UNION ALL

SELECT
    'SYMBOL' AS EntityType,
    CAST(Symbol AS VARCHAR(100)) AS Entity,
    TotalOrders,
    RejectedOrders,
    CAST(
        RejectedOrders * 100.0 / NULLIF(TotalOrders,0)
        AS DECIMAL(10,2)
    ) AS RejectionRate,
    'High Rejection Rate' AS AnomalyType
FROM SymbolRejection
WHERE TotalOrders >= 20
  AND RejectedOrders * 100.0 / NULLIF(TotalOrders,0) >= 20;
GO

-------------------------------------------------------------


CREATE OR ALTER VIEW dbo.High_Slippage_Anomalies
AS
SELECT
    T.TradeID,
    T.OrderID,
    T.ClientID,
    T.Symbol,
    T.Side,
    T.OrderType,
    O.OrderPrice,
    T.ExecutionPrice,
    T.ExecutedQuantity,
    T.TradeValue,
    T.SlippageValue,
    T.SlippagePct,

    CASE
        WHEN ABS(T.SlippagePct) > 1
            THEN 'High Slippage'
        ELSE 'Normal'
    END AS SlippageStatus

FROM dbo.[07_Trade_Execution_Book] T
INNER JOIN dbo.[06_Order_Book] O
    ON T.OrderID = O.OrderID

WHERE O.OrderPrice IS NOT NULL
  AND ABS(T.SlippagePct) > 1;
GO

----------------------------------------------------------

CREATE OR ALTER VIEW dbo.Activity_Spikes
AS

WITH DailyActivity AS
(
    SELECT
        CAST(TradeDate AS DATE) AS TradingDate,
        COUNT(*) AS TradeCount,
        SUM(TradeValue) AS Turnover
    FROM dbo.[07_Trade_Execution_Book]
    GROUP BY CAST(TradeDate AS DATE)
),

RollingActivity AS
(
    SELECT
        TradingDate,
        TradeCount,
        Turnover,

        AVG(CAST(TradeCount AS FLOAT))
        OVER (
            ORDER BY TradingDate
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) AS Previous7DayAvgTrades,

        AVG(CAST(Turnover AS FLOAT))
        OVER (
            ORDER BY TradingDate
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) AS Previous7DayAvgTurnover

    FROM DailyActivity
)

SELECT
    TradingDate,
    TradeCount,
    Turnover,
    Previous7DayAvgTrades,
    Previous7DayAvgTurnover,

    CAST(
        TradeCount * 100.0 /
        NULLIF(Previous7DayAvgTrades,0)
        AS DECIMAL(10,2)
    ) AS ActivityVs7DayAvgPct,

    CAST(
        Turnover * 100.0 /
        NULLIF(Previous7DayAvgTurnover,0)
        AS DECIMAL(10,2)
    ) AS TurnoverVs7DayAvgPct,

    CASE
        WHEN Previous7DayAvgTrades IS NOT NULL
         AND TradeCount >= Previous7DayAvgTrades * 1.50
            THEN 'Activity Spike'

        WHEN Previous7DayAvgTurnover IS NOT NULL
         AND Turnover >= Previous7DayAvgTurnover * 1.50
            THEN 'Turnover Spike'

        ELSE 'Normal'
    END AS ActivityStatus

FROM RollingActivity;
GO
/* =========================================================
   14. POWER BI VIEW INVENTORY
   ========================================================= */

SELECT
    TABLE_SCHEMA,
    TABLE_NAME

FROM INFORMATION_SCHEMA.VIEWS

WHERE
    TABLE_SCHEMA = 'dbo'

ORDER BY
    TABLE_NAME;
GO

