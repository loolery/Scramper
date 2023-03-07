--
-- File generated with SQLiteStudio v3.4.3 on Di Mrz 7 17:09:45 2023
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: tbl_land
CREATE TABLE IF NOT EXISTS tbl_land (
    ID        INTEGER     PRIMARY KEY AUTOINCREMENT
                          UNIQUE
                          NOT NULL,
    Name      STRING (32) UNIQUE
                          NOT NULL,
    Name2     STRING (32) UNIQUE
                          NOT NULL,
    Einwohner DOUBLE      NOT NULL,
    Punkte    INTEGER (5) NOT NULL
);

INSERT INTO tbl_land (ID, Name, Name2, Einwohner, Punkte) VALUES (1, 'Deutschland', 'Germany', 84079811.0, 1647);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
