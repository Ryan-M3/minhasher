from main import *
from database import *
import sys, os
import random


def full_test():
    test_minhash()
    print()
    test_database()


def test_minhash():
    print("Testing minhash")
    print("\tPreparing data to be minhashed".ljust(40), end="")
    sys.stdout.flush()
    txt = load("bible.txt")
    txt = format_text(txt)
    ngrams = ngrammize(txt, ngram_size = 5)
    print("complete.")
    mh = minhash(ngrams, 10)
    mh_str = [str(n).ljust(4) for n in mh]
    mh_str = " ".join(mh_str)
    print("\tminhash: ", mh_str)


def test_database():
    print("Testing Database")
    print("\tremoving test.db")

    try:
        os.remove("test.db")
    except FileNotFoundError:
        pass

    print("\tCreating test.db")
    db = Database(db_name = "test.db")

    print("\tInserting random minhashes.")
    for i in range(100):
        minhash = [random.randint(0,999) for i in range(200)]
        name = "test" + str(i)
        db.save(name, minhash)

    print("\tAccessing minhashes.")
    results = db.find_similar(minhash)
    assert len(results) >= 1
    if len(results) != 1:
        print("\tMore than one result returned.")
        print("\toriginal: ", minhash)
        print("\tResults: ", results)
    else:
        r = list(results[0])
        r = r[1:]
        for found, saved in zip(r, minhash):
            if found != saved:
                print("\t\tdiscrepancy found between", found, "and", saved)
        print("\t\tExact match found.")

    for i in range(20):
        minhash = [random.randint(0,999) for i in range(200)]
        db.find_similar(minhash)

    print("\tComplete.")
