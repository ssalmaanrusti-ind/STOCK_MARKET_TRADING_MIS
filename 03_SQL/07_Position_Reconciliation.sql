/* =========================================================
   STOCK MARKET TRADING MIS
   07 - POSITION RECONCILIATION
   ========================================================= */

USE StockMarketTradingMIS;
GO


/* =========================================================
   1. POSITION DATA OVERVIEW
   ========================================================= */

SELECT
    COUNT(*) AS TotalPositions,

    COUNT(DISTINCT ClientID) AS ClientsWithPositions,

    COUNT(DISTINCT AccountID) AS AccountsWithPositions,

    COUNT(DISTINCT InstrumentID) AS InstrumentsWithPositions,

    SUM(BuyQty) AS TotalBuyQuantity,

    SUM(SellQty) AS TotalSellQuantity,

    SUM(NetQuantity) AS TotalNetQuantity

FROM dbo.[10_Position_Data];
GO


/* =========================================================
   2. INTERNAL POSITION RECONCILIATION
      Expected NetQuantity = BuyQty - SellQty
   ========================================================= */

SELECT
    PositionID,
    AccountID,
    ClientID,
    InstrumentID,
    Symbol,
    BuyQty,
    SellQty,
    NetQuantity,

    BuyQty - SellQty AS CalculatedNetQuantity,

    NetQuantity -
    (BuyQty - SellQty) AS Difference,

    CASE
        WHEN NetQuantity = BuyQty - SellQty
            THEN 'RECONCILED'
        ELSE 'EXCEPTION'
    END AS ReconciliationStatus

FROM dbo.[10_Position_Data]

ORDER BY
    CASE
        WHEN NetQuantity <> BuyQty - SellQty
            THEN 1
        ELSE 2
    END,
    ABS(NetQuantity - (BuyQty - SellQty)) DESC;
GO


/* =========================================================
   3. POSITION RECONCILIATION SUMMARY
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
    ) AS ExceptionPositions,

    CAST(
        SUM(
            CASE
                WHEN NetQuantity = BuyQty - SellQty
                    THEN 1
                ELSE 0
            END
        ) * 100.0 / NULLIF(COUNT(*),0)
        AS DECIMAL(10,2)
    ) AS ReconciliationRate,

    CAST(
        SUM(
            CASE
                WHEN NetQuantity <> BuyQty - SellQty
                    THEN 1
                ELSE 0
            END
        ) * 100.0 / NULLIF(COUNT(*),0)
        AS DECIMAL(10,2)
    ) AS ExceptionRate

FROM dbo.[10_Position_Data];
GO


/* =========================================================
   4. POSITION EXCEPTIONS ONLY
   ========================================================= */

SELECT
    PositionID,
    AccountID,
    ClientID,
    InstrumentID,
    Symbol,
    BuyQty,
    SellQty,
    NetQuantity,

    BuyQty - SellQty AS CalculatedNetQuantity,

    NetQuantity -
    (BuyQty - SellQty) AS Difference

FROM dbo.[10_Position_Data]

WHERE
    NetQuantity <> BuyQty - SellQty

ORDER BY
    ABS(NetQuantity - (BuyQty - SellQty)) DESC;
GO


/* =========================================================
   5. POSITION EXCEPTIONS BY CLIENT
   ========================================================= */

SELECT
    ClientID,

    COUNT(*) AS ExceptionCount,

    SUM(
        NetQuantity - (BuyQty - SellQty)
    ) AS TotalDifference,

    SUM(BuyQty) AS BuyQuantity,

    SUM(SellQty) AS SellQuantity,

    SUM(NetQuantity) AS ReportedNetQuantity

FROM dbo.[10_Position_Data]

WHERE
    NetQuantity <> BuyQty - SellQty

GROUP BY
    ClientID

ORDER BY
    ExceptionCount DESC;
GO


/* =========================================================
   6. POSITION EXCEPTIONS BY SYMBOL
   ========================================================= */

SELECT
    Symbol,

    COUNT(*) AS ExceptionCount,

    SUM(
        NetQuantity - (BuyQty - SellQty)
    ) AS TotalDifference,

    SUM(BuyQty) AS BuyQuantity,

    SUM(SellQty) AS SellQuantity,

    SUM(NetQuantity) AS ReportedNetQuantity

FROM dbo.[10_Position_Data]

WHERE
    NetQuantity <> BuyQty - SellQty

GROUP BY
    Symbol

ORDER BY
    ExceptionCount DESC;
GO


/* =========================================================
   7. EXECUTED TRADES BY CLIENT / SYMBOL
      Used as the trading-side reconciliation base
   ========================================================= */

SELECT
    ClientID,
    AccountID,
    InstrumentID,
    Symbol,

    SUM(
        CASE
            WHEN Side = 'BUY'
                THEN ExecutedQuantity
            ELSE 0
        END
    ) AS ExecutedBuyQuantity,

    SUM(
        CASE
            WHEN Side = 'SELL'
                THEN ExecutedQuantity
            ELSE 0
        END
    ) AS ExecutedSellQuantity,

    SUM(
        CASE
            WHEN Side = 'BUY'
                THEN ExecutedQuantity
            WHEN Side = 'SELL'
                THEN -ExecutedQuantity
            ELSE 0
        END
    ) AS CalculatedNetQuantity,

    COUNT(*) AS TradeCount,

    CAST(
        SUM(TradeValue)
        AS DECIMAL(18,2)
    ) AS Turnover

FROM dbo.[07_Trade_Execution_Book]

GROUP BY
    ClientID,
    AccountID,
    InstrumentID,
    Symbol

ORDER BY
    ClientID,
    Symbol;
GO


/* =========================================================
   8. TRADE VS POSITION RECONCILIATION
   ========================================================= */

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
                ELSE 0
            END
        ) AS ExecutedBuyQuantity,

        SUM(
            CASE
                WHEN Side = 'SELL'
                    THEN ExecutedQuantity
                ELSE 0
            END
        ) AS ExecutedSellQuantity,

        SUM(
            CASE
                WHEN Side = 'BUY'
                    THEN ExecutedQuantity
                WHEN Side = 'SELL'
                    THEN -ExecutedQuantity
                ELSE 0
            END
        ) AS TradeNetQuantity

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
    COALESCE(t.ClientID, p.ClientID) AS ClientID,

    COALESCE(t.AccountID, p.AccountID) AS AccountID,

    COALESCE(t.InstrumentID, p.InstrumentID) AS InstrumentID,

    COALESCE(t.Symbol, p.Symbol) AS Symbol,

    ISNULL(t.ExecutedBuyQuantity,0)
        AS ExecutedBuyQuantity,

    ISNULL(p.PositionBuyQuantity,0)
        AS PositionBuyQuantity,

    ISNULL(t.ExecutedSellQuantity,0)
        AS ExecutedSellQuantity,

    ISNULL(p.PositionSellQuantity,0)
        AS PositionSellQuantity,

    ISNULL(t.TradeNetQuantity,0)
        AS TradeNetQuantity,

    ISNULL(p.PositionNetQuantity,0)
        AS PositionNetQuantity,

    ISNULL(p.PositionNetQuantity,0)
        - ISNULL(t.TradeNetQuantity,0)
        AS NetQuantityDifference,

    CASE
        WHEN ISNULL(p.PositionNetQuantity,0)
             =
             ISNULL(t.TradeNetQuantity,0)
            THEN 'RECONCILED'

        WHEN t.ClientID IS NULL
            THEN 'POSITION_WITHOUT_TRADE'

        WHEN p.ClientID IS NULL
            THEN 'TRADE_WITHOUT_POSITION'

        ELSE 'QUANTITY_MISMATCH'
    END AS ReconciliationStatus

FROM TradeSummary t

FULL OUTER JOIN PositionSummary p

    ON t.ClientID = p.ClientID

    AND t.AccountID = p.AccountID

    AND t.InstrumentID = p.InstrumentID

    AND t.Symbol = p.Symbol

ORDER BY
    CASE
        WHEN ISNULL(p.PositionNetQuantity,0)
             =
             ISNULL(t.TradeNetQuantity,0)
            THEN 2
        ELSE 1
    END,

    ABS(
        ISNULL(p.PositionNetQuantity,0)
        -
        ISNULL(t.TradeNetQuantity,0)
    ) DESC;
GO


/* =========================================================
   9. TRADE VS POSITION EXCEPTIONS ONLY
   ========================================================= */

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
        ) AS TradeNetQuantity

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

        SUM(NetQuantity) AS PositionNetQuantity

    FROM dbo.[10_Position_Data]

    GROUP BY
        ClientID,
        AccountID,
        InstrumentID,
        Symbol
)

SELECT
    COALESCE(t.ClientID,p.ClientID) AS ClientID,

    COALESCE(t.AccountID,p.AccountID) AS AccountID,

    COALESCE(t.InstrumentID,p.InstrumentID) AS InstrumentID,

    COALESCE(t.Symbol,p.Symbol) AS Symbol,

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

        ELSE 'QUANTITY_MISMATCH'
    END AS ExceptionType

FROM TradeSummary t

FULL OUTER JOIN PositionSummary p

    ON t.ClientID = p.ClientID

    AND t.AccountID = p.AccountID

    AND t.InstrumentID = p.InstrumentID

    AND t.Symbol = p.Symbol

WHERE
    ISNULL(t.TradeNetQuantity,0)
    <>
    ISNULL(p.PositionNetQuantity,0)

ORDER BY
    ABS(
        ISNULL(p.PositionNetQuantity,0)
        -
        ISNULL(t.TradeNetQuantity,0)
    ) DESC;
GO


/* =========================================================
   10. RECONCILIATION SUMMARY BY STATUS
   ========================================================= */

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
        ) AS TradeNetQuantity

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

        SUM(NetQuantity) AS PositionNetQuantity

    FROM dbo.[10_Position_Data]

    GROUP BY
        ClientID,
        AccountID,
        InstrumentID,
        Symbol
),

Reconciliation AS
(
    SELECT
        COALESCE(t.ClientID,p.ClientID) AS ClientID,

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

        AND t.Symbol = p.Symbol
)

SELECT
    ReconciliationStatus,

    COUNT(*) AS RecordCount,

    CAST(
        COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER ()
        AS DECIMAL(10,2)
    ) AS PercentageOfRecords

FROM Reconciliation

GROUP BY
    ReconciliationStatus

ORDER BY
    RecordCount DESC;
GO


/* =========================================================
   11. CLIENT-LEVEL RECONCILIATION EXCEPTIONS
   ========================================================= */

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
        ) AS TradeNetQuantity

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

        SUM(NetQuantity) AS PositionNetQuantity

    FROM dbo.[10_Position_Data]

    GROUP BY
        ClientID,
        AccountID,
        InstrumentID,
        Symbol
)

SELECT
    COALESCE(t.ClientID,p.ClientID) AS ClientID,

    COUNT(*) AS ExceptionCount,

    SUM(
        ISNULL(p.PositionNetQuantity,0)
        -
        ISNULL(t.TradeNetQuantity,0)
    ) AS TotalDifference,

    SUM(
        ABS(
            ISNULL(p.PositionNetQuantity,0)
            -
            ISNULL(t.TradeNetQuantity,0)
        )
    ) AS AbsoluteDifference

FROM TradeSummary t

FULL OUTER JOIN PositionSummary p

    ON t.ClientID = p.ClientID

    AND t.AccountID = p.AccountID

    AND t.InstrumentID = p.InstrumentID

    AND t.Symbol = p.Symbol

WHERE
    ISNULL(t.TradeNetQuantity,0)
    <>
    ISNULL(p.PositionNetQuantity,0)

GROUP BY
    COALESCE(t.ClientID,p.ClientID)

ORDER BY
    AbsoluteDifference DESC;
GO


/* =========================================================
   12. SYMBOL-LEVEL RECONCILIATION EXCEPTIONS
   ========================================================= */

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
        ) AS TradeNetQuantity

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

        SUM(NetQuantity) AS PositionNetQuantity

    FROM dbo.[10_Position_Data]

    GROUP BY
        ClientID,
        AccountID,
        InstrumentID,
        Symbol
)

SELECT
    COALESCE(t.Symbol,p.Symbol) AS Symbol,

    COUNT(*) AS ExceptionCount,

    SUM(
        ISNULL(p.PositionNetQuantity,0)
        -
        ISNULL(t.TradeNetQuantity,0)
    ) AS TotalDifference,

    SUM(
        ABS(
            ISNULL(p.PositionNetQuantity,0)
            -
            ISNULL(t.TradeNetQuantity,0)
        )
    ) AS AbsoluteDifference

FROM TradeSummary t

FULL OUTER JOIN PositionSummary p

    ON t.ClientID = p.ClientID

    AND t.AccountID = p.AccountID

    AND t.InstrumentID = p.InstrumentID

    AND t.Symbol = p.Symbol

WHERE
    ISNULL(t.TradeNetQuantity,0)
    <>
    ISNULL(p.PositionNetQuantity,0)

GROUP BY
    COALESCE(t.Symbol,p.Symbol)

ORDER BY
    AbsoluteDifference DESC;
GO