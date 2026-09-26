/* =========================================================
   STOCK MARKET TRADING MIS
   04 - REJECTION ANALYSIS
   ========================================================= */

USE StockMarketTradingMIS;
GO


/* =========================================================
   1. TOTAL REJECTION KPIs
   ========================================================= */

SELECT
    COUNT(*) AS TotalRejectedOrders,

    COUNT(DISTINCT OrderID) AS UniqueRejectedOrders,

    COUNT(DISTINCT ClientID) AS AffectedClients,

    COUNT(DISTINCT Symbol) AS AffectedSymbols

FROM dbo.[08_Order_Rejection_Data];
GO


/* =========================================================
   2. REJECTION REASON ANALYSIS
   ========================================================= */

SELECT
    RejectionReason,

    COUNT(*) AS RejectionCount,

    CAST(
        COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER ()
        AS DECIMAL(10,2)
    ) AS RejectionPercentage

FROM dbo.[08_Order_Rejection_Data]

GROUP BY
    RejectionReason

ORDER BY
    RejectionCount DESC;
GO


/* =========================================================
   3. REJECTION BY CLIENT
   ========================================================= */

SELECT
    r.ClientID,

    COUNT(*) AS RejectedOrders,

    COUNT(DISTINCT r.OrderID) AS UniqueRejectedOrders,

    COUNT(DISTINCT r.Symbol) AS SymbolsAffected

FROM dbo.[08_Order_Rejection_Data] r

GROUP BY
    r.ClientID

ORDER BY
    RejectedOrders DESC;
GO


/* =========================================================
   4. CLIENT REJECTION RATE
   ========================================================= */

WITH ClientOrders AS
(
    SELECT
        ClientID,
        COUNT(DISTINCT OrderID) AS TotalOrders
    FROM dbo.[06_Order_Book]
    GROUP BY ClientID
),

ClientRejections AS
(
    SELECT
        ClientID,
        COUNT(DISTINCT OrderID) AS RejectedOrders
    FROM dbo.[08_Order_Rejection_Data]
    GROUP BY ClientID
)

SELECT
    o.ClientID,

    o.TotalOrders,

    COALESCE(r.RejectedOrders, 0) AS RejectedOrders,

    CAST(
        COALESCE(r.RejectedOrders, 0) * 100.0 /
        NULLIF(o.TotalOrders, 0)
        AS DECIMAL(10,2)
    ) AS RejectionRate

FROM ClientOrders o

LEFT JOIN ClientRejections r
    ON o.ClientID = r.ClientID

ORDER BY
    RejectionRate DESC;
GO


/* =========================================================
   5. HIGH REJECTION CLIENTS
   Minimum 20 orders
   Rejection rate >= 20%
   ========================================================= */

WITH ClientOrders AS
(
    SELECT
        ClientID,
        COUNT(DISTINCT OrderID) AS TotalOrders
    FROM dbo.[06_Order_Book]
    GROUP BY ClientID
),

ClientRejections AS
(
    SELECT
        ClientID,
        COUNT(DISTINCT OrderID) AS RejectedOrders
    FROM dbo.[08_Order_Rejection_Data]
    GROUP BY ClientID
)

SELECT
    o.ClientID,

    o.TotalOrders,

    COALESCE(r.RejectedOrders, 0) AS RejectedOrders,

    CAST(
        COALESCE(r.RejectedOrders, 0) * 100.0 /
        NULLIF(o.TotalOrders, 0)
        AS DECIMAL(10,2)
    ) AS RejectionRate

FROM ClientOrders o

LEFT JOIN ClientRejections r
    ON o.ClientID = r.ClientID

WHERE
    o.TotalOrders >= 20

    AND
    COALESCE(r.RejectedOrders, 0) * 100.0 /
    NULLIF(o.TotalOrders, 0) >= 20

ORDER BY
    RejectionRate DESC,
    RejectedOrders DESC;
GO


/* =========================================================
   6. REJECTION BY SYMBOL
   ========================================================= */

SELECT
    Symbol,

    COUNT(*) AS RejectedOrders,

    COUNT(DISTINCT ClientID) AS AffectedClients

FROM dbo.[08_Order_Rejection_Data]

GROUP BY
    Symbol

ORDER BY
    RejectedOrders DESC;
GO


/* =========================================================
   7. SYMBOL REJECTION RATE
   ========================================================= */

WITH SymbolOrders AS
(
    SELECT
        Symbol,
        COUNT(DISTINCT OrderID) AS TotalOrders
    FROM dbo.[06_Order_Book]
    GROUP BY Symbol
),

SymbolRejections AS
(
    SELECT
        Symbol,
        COUNT(DISTINCT OrderID) AS RejectedOrders
    FROM dbo.[08_Order_Rejection_Data]
    GROUP BY Symbol
)

SELECT
    o.Symbol,

    o.TotalOrders,

    COALESCE(r.RejectedOrders, 0) AS RejectedOrders,

    CAST(
        COALESCE(r.RejectedOrders, 0) * 100.0 /
        NULLIF(o.TotalOrders, 0)
        AS DECIMAL(10,2)
    ) AS RejectionRate

FROM SymbolOrders o

LEFT JOIN SymbolRejections r
    ON o.Symbol = r.Symbol

ORDER BY
    RejectionRate DESC;
GO


/* =========================================================
   8. HIGH REJECTION SYMBOLS
   Minimum 20 orders
   Rejection rate >= 20%
   ========================================================= */

WITH SymbolOrders AS
(
    SELECT
        Symbol,
        COUNT(DISTINCT OrderID) AS TotalOrders
    FROM dbo.[06_Order_Book]
    GROUP BY Symbol
),

SymbolRejections AS
(
    SELECT
        Symbol,
        COUNT(DISTINCT OrderID) AS RejectedOrders
    FROM dbo.[08_Order_Rejection_Data]
    GROUP BY Symbol
)

SELECT
    o.Symbol,

    o.TotalOrders,

    COALESCE(r.RejectedOrders, 0) AS RejectedOrders,

    CAST(
        COALESCE(r.RejectedOrders, 0) * 100.0 /
        NULLIF(o.TotalOrders, 0)
        AS DECIMAL(10,2)
    ) AS RejectionRate

FROM SymbolOrders o

LEFT JOIN SymbolRejections r
    ON o.Symbol = r.Symbol

WHERE
    o.TotalOrders >= 20

    AND
    COALESCE(r.RejectedOrders, 0) * 100.0 /
    NULLIF(o.TotalOrders, 0) >= 20

ORDER BY
    RejectionRate DESC,
    RejectedOrders DESC;
GO


/* =========================================================
   9. DAILY REJECTION TREND
   ========================================================= */

SELECT
    CAST(OrderDate AS DATE) AS RejectionDate,

    COUNT(*) AS RejectedOrders,

    COUNT(DISTINCT ClientID) AS AffectedClients,

    COUNT(DISTINCT Symbol) AS AffectedSymbols

FROM dbo.[08_Order_Rejection_Data]

GROUP BY
    CAST(OrderDate AS DATE)

ORDER BY
    RejectionDate;
GO


/* =========================================================
   10. DAILY REJECTION RATE
   ========================================================= */

WITH DailyOrders AS
(
    SELECT
        CAST(OrderDate AS DATE) AS TradeDate,
        COUNT(DISTINCT OrderID) AS TotalOrders
    FROM dbo.[06_Order_Book]
    GROUP BY
        CAST(OrderDate AS DATE)
),

DailyRejections AS
(
    SELECT
        CAST(OrderDate AS DATE) AS TradeDate,
        COUNT(DISTINCT OrderID) AS RejectedOrders
    FROM dbo.[08_Order_Rejection_Data]
    GROUP BY
        CAST(OrderDate AS DATE)
)

SELECT
    o.TradeDate,

    o.TotalOrders,

    COALESCE(r.RejectedOrders, 0) AS RejectedOrders,

    CAST(
        COALESCE(r.RejectedOrders, 0) * 100.0 /
        NULLIF(o.TotalOrders, 0)
        AS DECIMAL(10,2)
    ) AS RejectionRate

FROM DailyOrders o

LEFT JOIN DailyRejections r
    ON o.TradeDate = r.TradeDate

ORDER BY
    o.TradeDate;
GO


/* =========================================================
   11. REJECTION BY ORDER TYPE
   ========================================================= */

SELECT
    o.OrderType,

    COUNT(DISTINCT o.OrderID) AS TotalOrders,

    COUNT(DISTINCT r.OrderID) AS RejectedOrders,

    CAST(
        COUNT(DISTINCT r.OrderID) * 100.0 /
        NULLIF(COUNT(DISTINCT o.OrderID), 0)
        AS DECIMAL(10,2)
    ) AS RejectionRate

FROM dbo.[06_Order_Book] o

LEFT JOIN dbo.[08_Order_Rejection_Data] r
    ON o.OrderID = r.OrderID

GROUP BY
    o.OrderType

ORDER BY
    RejectionRate DESC;
GO


/* =========================================================
   12. REJECTION BY SIDE
   ========================================================= */

SELECT
    o.Side,

    COUNT(DISTINCT o.OrderID) AS TotalOrders,

    COUNT(DISTINCT r.OrderID) AS RejectedOrders,

    CAST(
        COUNT(DISTINCT r.OrderID) * 100.0 /
        NULLIF(COUNT(DISTINCT o.OrderID), 0)
        AS DECIMAL(10,2)
    ) AS RejectionRate

FROM dbo.[06_Order_Book] o

LEFT JOIN dbo.[08_Order_Rejection_Data] r
    ON o.OrderID = r.OrderID

GROUP BY
    o.Side

ORDER BY
    RejectionRate DESC;
GO


/* =========================================================
   13. REJECTION REASON BY ORDER TYPE
   ========================================================= */

SELECT
    o.OrderType,

    r.RejectionReason,

    COUNT(*) AS RejectionCount

FROM dbo.[08_Order_Rejection_Data] r

INNER JOIN dbo.[06_Order_Book] o
    ON r.OrderID = o.OrderID

GROUP BY
    o.OrderType,
    r.RejectionReason

ORDER BY
    o.OrderType,
    RejectionCount DESC;
GO


/* =========================================================
   14. REJECTION REASON BY SYMBOL
   ========================================================= */

SELECT
    r.Symbol,

    r.RejectionReason,

    COUNT(*) AS RejectionCount

FROM dbo.[08_Order_Rejection_Data] r

GROUP BY
    r.Symbol,
    r.RejectionReason

ORDER BY
    r.Symbol,
    RejectionCount DESC;
GO


/* =========================================================
   15. TOP CLIENTS BY REJECTION COUNT
   ========================================================= */

SELECT TOP 20

    ClientID,

    COUNT(*) AS RejectedOrders,

    COUNT(DISTINCT Symbol) AS SymbolsAffected

FROM dbo.[08_Order_Rejection_Data]

GROUP BY
    ClientID

ORDER BY
    RejectedOrders DESC;
GO


/* =========================================================
   16. TOP SYMBOLS BY REJECTION COUNT
   ========================================================= */

SELECT TOP 20

    Symbol,

    COUNT(*) AS RejectedOrders,

    COUNT(DISTINCT ClientID) AS AffectedClients

FROM dbo.[08_Order_Rejection_Data]

GROUP BY
    Symbol

ORDER BY
    RejectedOrders DESC;
GO