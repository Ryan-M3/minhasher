import re
import pdb
import pickle
import sys
from copy import copy
from main import *
from tqdm import tqdm


def build_dict():
    all_entries = {}
    tag_rgx   ="(?<=<%s>).+(?=</%s>)"
    entry_rgx = tag_rgx % ("P", "P")
    key_rgx   = tag_rgx % ("B", "B")
    type_rgx  = tag_rgx % ("I", "I")


    for i in range( ord("a"), ord("z") ):
        with open("texts/dict_%s.txt" % chr(i)) as f:
            txt = f.read()
        entries = re.findall(entry_rgx, txt)

        for entry in entries:
            #pdb.set_trace()
            k = re.search(key_rgx, entry).group()
            part_of_speech = re.search(type_rgx, entry)

            if not part_of_speech:
                part_of_speech = ""
            else:
                part_of_speech = part_of_speech.group()

            print(entry)
            val = re.search("(?<=</I>\)).+", entry).group()
            all_entries[k] = part_of_speech + " " + val


    with open("engl_dict.pkl", "wb") as f:
        pickle.dump(all_entries, f)

    return all_entries


def populate_database(all_entries):
    db = Database(minhash_length = 300, db_name = "dictionary_hashes.db")
    clean = lambda s: " ".join(re.findall("[\w\ ]+", s)).strip().lower()

    for i, k in enumerate(all_entries.keys()):
        if i % 1000 == 0:
            print(str(i/len(all_entries)).ljust(5), end="\t")
            sys.stdout.flush()

        clean_k = clean(k)
        clean_v = clean(all_entries[k])

        try:
            ngrams = ngrammize( clean_v.split() )
            h = minhash(ngrams, hash_algorithms = 300)
            db.save(clean_k, h)
        except:
            # this is almost always because of a failure of the unique constraint
            pdb.set_trace()


def jaccard(A, B):
    numer = 0
    for a, b in zip(A, B):
        numer += (a == b)
    return numer / len(A)

                
def look_up(word: str, at_least_x_results = 3):
    word_h = db.get_hash(word)

    i = 1
    while True:
        similar = db.find_similar(word_h, rows_per_band = i)
        if len(similar) > at_least_x_results:
            old = copy(similar)
            i += 1
        else:
            break

    similarity_scores = []
    for word_and_hash in old:
        w = word_and_hash[0]
        h = word_and_hash[1:]
        similarity_scores.append( (jaccard(word_h, h), w) )
    
    return sorted(similarity_scores)

    
    return similar


db = Database(minhash_length = 300, db_name = "dictionary_hashes.db")
