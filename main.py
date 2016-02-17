import re
import binascii
from database import Database
try:
    from gutenberg.acquire import load_etext
    from gutenberg.cleanup import strip_headers

    def acquire_and_process(name: str, txt_num: int):
        """
        Convenience function that minhashes a Project Gutenberg
        text given the text id number (can be found on the gutenberg.org,
        for instance in the url).
        """
        txt = strip_headers( load_etext(txt_num) )
        with open("texts/%s.txt" % name, "w") as f:
            f.write(txt)
        process_file("texts/%s.txt" % name)
except:
    pass


def load(pathname):
    """ Convenience function of questionable necessity. """
    with open(pathname) as f:
        return f.read()


def format_text(txt, to_lower = True) -> list:
    """
    Break a string into a list of words.
    """
    if to_lower:
        txt = txt.lower()
    # Regex just splits text on non alphanumeric characters;
    # it does produce incorrect results on contractions and
    # abbreviations, however.
    txt = re.split("\W", txt)
    txt = list(filter(None, txt))  # get rid of empty entries
    return txt
    

def ngrammize(words: list, ngram_size = 2, nested_list = False) -> list:
    """
    Also called "shingling" this returns a list of every
    consecutive sequence n words long. For example, this:

        The quick brown fox jumps over the lazy dog.

    Will break up into bigrams (2-grams) of:
        The quick
        quick brown
        brown fox
        fox jumps
        jumps over
        ...
    """
    if len(words) <= ngram_size:
        # Our input cannot be broken down further!
        return words

    # I like to imagine a "window" is passing over the words
    # in our text. The ngram_size is the width of our window.
    # We place our window on the far left then stop once the
    # right side of our window hits the far edge our text.
    # len(words) - ngram_size refers to the farthest toward
    # the right that the *left edge of the window* can travel.
    # We have to add one because Python's range does not
    # return the last number in that range.
    ngrams = []
    for i in range( len(words) - ngram_size + 1 ):
        j = i + ngram_size
        ngrams.append( words[i:j] )

    if not nested_list:
        ngrams = [" ".join(x) for x in ngrams]

    return ngrams


def hash_(string, num):
    """ Get the CRC32 hash for the input string with some salt, "num". """
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
    for i in range(hash_algorithms):  # i is some arbitrary numerical constant
        # find the hash for each ngram and append the smallest to hashes
        hashes.append( min([hash_(ng, i) for ng in ngrams]) )
    return hashes
        

def process_file(fname, ngram_size = 10, hash_algorithms = 200):
    """
    Convenience function that minhashes and saves an entire
    file given the file name, "fname."
    """
    data = load(fname)
    data = format_text(data)
    data = ngrammize(data, ngram_size = ngram_size)
    h = minhash(data, hash_algorithms = hash_algorithms)
    
    db = Database()
    db.save(fname, h)
    del db
