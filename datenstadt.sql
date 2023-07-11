
CREATE TABLE IF NOT EXISTS tbl_stadt (
    ID          INTEGER     UNIQUE
                            PRIMARY KEY AUTOINCREMENT,
    Land_ID     INTEGER     REFERENCES tbl_land (ID)
                            NOT NULL,
    Bundesland  STRING (32) NOT NULL,
    Name        STRING (32) UNIQUE
                            NOT NULL,
    Einwohner   DOUBLE      NOT NULL
);

INSERT INTO tbl_stadt (
                          ID,
                          Land_ID,
                          Name,
                          Einwohner
                      )
                      VALUES (
                          1,
                          1,
                          'Berlin',
                          3677472.0
                      );

                          Einwohner
                      )
                      VALUES (
                          9,
                          1,
                          'Dortmund',
                          586852.0
                      );

INSERT INTO tbl_stadt (
                          ID,
                          Land_ID,
                          Name,
                          Einwohner
                      )
                      VALUES (
                          10,
                          1,
                          'Essen',
                          579432.0
                      );

