import re
import binascii
from tqdm import tqdm
from database import Database
from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers


def load(pathname):
    with open(pathname) as f:
        return f.read()


def format_text(txt, to_lower = True) -> list:
    if to_lower:
        txt = txt.lower()
    txt = re.split("\W", txt)
    txt = list(filter(None, txt))
    return txt
    

def ngrammize(words: list, ngram_size = 2, nested_list = False) -> list:
    ngrams = []
    for i in range( len(words) - ngram_size ):
        j = i + ngram_size
        ngrams.append( words[i:j] )

    if not nested_list:
        ngrams = [" ".join(x) for x in ngrams]

    return ngrams


def hash_(string, num):
    # CRC32 used as a hash function due to a stackoverflow post
    # showing various text hashing functions by performance and
    # characteristics. CRC32 had the lowest number of collisions
    # and looked very random, and its lack of cryptographic
    # security is not important for minhashing.
    data = binascii.b2a_base64( str.encode(string) )
    return binascii.crc32(data, num)


def minhash(ngrams, hash_algorithms):
    # TODO: make this multithreaded
    hashes = []
    for i in tqdm(range(hash_algorithms)):  # i is some arbitrary numerical constant
        # find the hash for each ngram and append the smallest to hashes
        hashes.append( min([hash_(ng, i) for ng in ngrams]) )
    return hashes
        

def process_file(fname, ngram_size = 10, hash_algorithms = 200):
    data = load(fname)
    data = format_text(data)
    data = ngrammize(data, ngram_size = ngram_size)
    h = minhash(data, hash_algorithms = hash_algorithms)
    
    db = Database()
    db.save(fname, h)
    del db


def acquire_and_process(name: str, txt_num: int):
    txt = strip_headers( load_etext(txt_num) )
    with open("texts/%s.txt" % name, "w") as f:
        f.write(txt)
    process_file("texts/%s.txt" % name)
