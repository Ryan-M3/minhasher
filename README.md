# minhasher

This project contains functions for implementing minhashing. In particular,
I wanted to see if minhashing dictionary definitions could return synonyms
for a particular word. It turns out not really. While the results returned
weren't quite as bad as random, they were still really bad so I won't be
continuing the experiment in the foreseeable future.

Most functions directly realted to minhashing are located in main.py, with
the notable exception being the Database class which acts as a front-end to
a SQLite database.

This project also contains some of the functions I used to break the dict-
ionary down into definitions for the purpose of minhashing. This is located
in dict_parser.py.
