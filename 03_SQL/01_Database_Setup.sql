/* =========================================================
   STOCK MARKET TRADING MIS
   01 - DATABASE SETUP
   ========================================================= */


/* =========================================================
   1. CREATE DATABASE IF NOT EXISTS
   ========================================================= */

USE master;
GO

IF DB_ID('StockMarketTradingMIS') IS NULL
BEGIN
    CREATE DATABASE StockMarketTradingMIS;
END;
GO


/* =========================================================
   2. SWITCH TO DATABASE
   ========================================================= */

USE StockMarketTradingMIS;
GO


/* =========================================================
   3. VERIFY CURRENT DATABASE
   ========================================================= */

SELECT
    DB_NAME() AS CurrentDatabase,
    GETDATE() AS SetupDate;
GO


/* =========================================================
   4. LIST IMPORTED TABLES
   ========================================================= */

SELECT
    TABLE_SCHEMA,
    TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY
    TABLE_SCHEMA,
    TABLE_NAME;
GO


/* =========================================================
   5. VERIFY ROW COUNTS
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