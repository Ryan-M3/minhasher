import sqlite3 as sql
from copy import copy


class Database:
    def __init__(self, minhash_length = 200, db_name = "minhashes.db"):
        self.cnx = sql.connect(db_name)
        self.crs = self.cnx.cursor()

        # this would be rather repetitive to write by hand.
        cols = ["col%d INTEGER" % i for i in range(minhash_length)]
        cols = ", ".join(cols)

        self.crs.execute("""
          CREATE TABLE IF NOT EXISTS hashes (filename TEXT PRIMARY KEY, %s);
          """ % cols)
        self.cnx.commit()

        self.crs.execute("""
          PRAGMA TABLE_INFO(hashes);
          """)
        self.hash_n = len(self.crs.fetchall()) - 1  # -1 because the filename field


    def save(self, filename: str, minhashes: list):
        stringified = [str(h) for h in minhashes]
        self.crs.execute("""
          INSERT INTO hashes VALUES ('%s', %s);
          """ % (filename, ", ".join(stringified)))
        self.cnx.commit()


    def find_similar(self, minhashes:list, rows_per_band = 4):
        query = "SELECT * FROM hashes WHERE "
        
        # Get a list of the correct column names.
        cols  = ["col%d" % i for i in range(self.hash_n)]
        # Now allow us to compare the correct columns with the values of our minhashes
        cols  = [c + " = %d" for c in cols] 
        # Put in the actual minhash values.
        cols  = [c % minhashes[i] for i, c in enumerate(cols)]

        # Now break our eqality statements into distinct bands.
        bands = []
        for i in range(0, self.hash_n, rows_per_band):
            j = i + rows_per_band
            bands.append( cols[i:j] )

        # If any single band matches entirely with our hash, return it.
        # We start by going through each band and making our columns match all of them.
        for i, band in enumerate(copy(bands)):
            bands[i] = " AND ".join(band)

        # but only one band has to match. So we're saying either all of this band
        # OR all of this other band OR all of...
        bands = "(" + ") OR (".join(bands) + ");"
        # add that 200-col expression to our select statement and we're done.
        query = query + bands

        self.crs.execute(query)
        return self.crs.fetchall()


    def __del__(self):
        self.cnx.close()
