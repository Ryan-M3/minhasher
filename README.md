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

DEPENDENCIES:
    main.py contains an optional dependency for the python package gutenberg
    which allows you to download texts from project gutenberg. It's probably
    not very important at all.

    dict_parser.py also contains a dependency for tqdm, a library which makes
    progress bars in the terminal. Since that file isn't really that import-
    ant to anyone but the curious, I've not made an effort to remove that
    dependency.
