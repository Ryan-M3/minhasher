import sqlite3 as sql
from copy import copy


class Database:
    def __init__(self, minhash_length = 200, db_name = "minhashes.db"):
        """
        Establishes a connection to a database on file and if
        that database does not currently exist, it creates it
        with the appropriate tables.
        """
        self.cnx = sql.connect(db_name)
        self.crs = self.cnx.cursor()

        # This would be rather repetitive to write by hand;
        # basically, it just creates 200 or so columns, one
        # for each minhash.
        cols = ["col%d INTEGER" % i for i in range(minhash_length)]
        cols = ", ".join(cols)

        self.crs.execute("""
          CREATE TABLE IF NOT EXISTS hashes (filename TEXT PRIMARY KEY, %s);
          """ % cols)
        self.cnx.commit()

        # If the table already exists, we want to ensure that
        # we have recorded the correct number of minhashes
        # we're using since other functions depend on that
        # information. We do this by looking up the number of
        # columns in our database. This bit of code executes
        # even if we just created the database because it
        # doesn't take long to execute.
        self.crs.execute("""
          PRAGMA TABLE_INFO(hashes);
          """)
        self.hash_n = len(self.crs.fetchall()) - 1  # -1 because the filename field


    def save(self, name: str, minhashes: list):
        """
        Given the a name or identifier of the thing we're
        minhashing and the list of minhashes for that, save
        that info into our database.

        WARNING: will completely ignore duplicate entries
        which may be pathological behavior depending on
        what you're doing.
        """
        stringified = [str(h) for h in minhashes]
        self.crs.execute("""
          INSERT OR IGNORE INTO hashes VALUES ('%s', %s);
          """ % (name, ", ".join(stringified)))
        self.cnx.commit()


    def get_hash(self, key: str) -> list:
        self.crs.execute("""
          SELECT * FROM HASHES WHERE filename == '%s';
          """ % key)
        return list(self.crs.fetchall()[0])[1:]


    def find_similar(self, minhashes:list, rows_per_band = 4, only_keys = False):
        """
        Given a minhashing of a document, return a list of
        possible matches.

        Args
        ----
        Rows_per_band is an implementation detail, but in
        general, the higher you set that number the more
        accurate the results and the fewer results found.
        In slightly more technical language, increasing
        rows_per_band results in fewer false positives, but
        greater false negatives.

        If only_keys is set to true, only the name of the
        result will be returned and NOT it's corresponding
        minhash.
        """
        if only_keys:
            query = "SELECT name FROM hashes WHERE "
        else:
            query = "SELECT * FROM hashes WHERE "

        # All this below is very, very ugly, but I see no
        # alternative. We break the minhashes into smaller
        # groups called bands. Then we return any item in
        # our database if it has an identical band. The
        # ugliness comes in because we need to form a SQL
        # query in string format that looks through 200 cols
        # AND will adjust to our rows_per_band variable.
        
        # Get a list of the correct column names.
        cols  = ["col%d" % i for i in range(self.hash_n)]
        # Now allow us to compare the correct columns with
        # the values of our minhashes.
        cols  = [c + " = %d" for c in cols] 
        # Put in the actual minhash values.
        cols  = [c % minhashes[i] for i, c in enumerate(cols)]

        # Now break our eqality statements into distinct bands.
        bands = []
        for i in range(0, self.hash_n, rows_per_band):
            j = i + rows_per_band
            bands.append( cols[i:j] )

        # If any single band matches entirely with our hash,
        # return it. We start by going through each band and
        #  making our columns match all of them.
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
        # Not closing a connection when you're done can cause
        # problems with a database so we try to always close
        # the connection upon destruction.
        self.cnx.close()
