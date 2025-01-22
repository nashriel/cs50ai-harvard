import nltk
import sys

# Define the grammar for the parser
TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
s -> s Conj s | NP VP | s Conj VP
NP -> N | DP | P NP | AP | N PP
VP -> V | V NP | V NP PP | Adv VP | VP Adv
PP -> P NP
AP -> Adj NP | Adj AP
DP -> Det N | Det AP
"""

# Download NLTK tokenizer data if not already available
nltk.download('punkt')

# Create a context-free grammar and chart parser
grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():
    """
    Main function to handle input, parsing, and output of syntax trees.
    """
    # Check if a filename is provided as a command-line argument
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()
    else:
        # Otherwise, get a sentence as input from the user
        s = input("Sentence: ")

    # Preprocess the input sentence into tokens
    s = preprocess(s)

    # Attempt to parse the tokenized sentence using the grammar
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return

    if not trees:
        print("Could not parse sentence.")
        return

    # Print each parse tree and its noun phrase chunks
    for tree in trees:
        tree.pretty_print()
        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Preprocess the input sentence.

    Converts the sentence to lowercase, tokenizes it into words, and filters out
    any tokens that do not contain at least one alphabetic character.

    Args:
        sentence (str): The input sentence.

    Returns:
        list: A list of cleaned, lowercase word tokens.
    """
    return [
        word.lower() for word in nltk.word_tokenize(sentence)
        if any(c.isalpha() for c in word)
    ]


def np_chunk(tree):
    """
    Extract noun phrase (NP) chunks from a syntax tree.

    A noun phrase chunk is defined as a subtree of the tree labeled "NP"
    that does not contain any other NP subtrees.

    Args:
        tree (Tree): A parsed sentence tree.

    Returns:
        list: A list of noun phrase subtrees.
    """
    chunks = []
    for subtree in tree.subtrees(lambda t: t.label() == 'NP'):
        # Check if this NP subtree contains no other NP subtrees
        if sum(1 for _ in subtree.subtrees(lambda t: t.label() == 'NP')) == 1:
            chunks.append(subtree)
    return chunks


if __name__ == "__main__":
    main()
