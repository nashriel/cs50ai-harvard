import os
import random
import re
import sys
from collections import defaultdict

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse HTML pages in the specified directory and extract links to other pages.
    Returns a dictionary where each key is a page, and each value is a set of pages
    linked from the key page within the corpus.
    """
    pages = dict()

    # Process all HTML files in the given directory to extract hyperlinks
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Filter out links that don't refer to other pages in the corpus
    for filename in pages:
        pages[filename] = {link for link in pages[filename] if link in pages}

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Generate a probability distribution of the next page to visit from the current page.

    With probability `damping_factor`, a link from the current page is chosen.
    With probability `1 - damping_factor`, a random page from the entire corpus is selected.
    """
    result = {}
    N = len(corpus)
    if page not in corpus:
        return result

    # Initial probability distribution for each page
    for p in corpus:
        result[p] = (1 - damping_factor) / N

    # Adjust the probability for pages linked by the current page
    num_links = len(corpus[page])
    for p in corpus[page]:
        result[p] += damping_factor / num_links

    return result


def sample_pagerank(corpus, damping_factor, n):
    """
    Estimate the PageRank values for each page by randomly sampling `n` pages
    based on the transition model, starting from a randomly chosen page.

    Returns a dictionary with page names as keys and their estimated PageRank values
    (between 0 and 1). The sum of all PageRank values will be 1.
    """
    pages = list(corpus.keys())
    visited = {page: 0 for page in pages}
    models = {}

    # Create transition models for each page
    for page in pages:
        models[page] = transition_model(corpus=corpus, page=page, damping_factor=damping_factor)

    # Start by randomly selecting the first sample
    next_sample = random.choice(pages)
    visited[next_sample] += 1
    count = n
    while count - 1 > 0:
        next_model = models[next_sample]
        # Get the next sample based on the current model
        next_sample = generate_next_sample(next_model)
        count -= 1
        # Track the visited page
        visited[next_sample] += 1

    # Normalize the results and return estimated PageRank values
    return {page: visited[page] / n for page in visited}


def generate_next_sample(model):
    """
    Select the next page based on the probability distribution in the model.
    """
    pages = []
    counts = []
    for page, prob in model.items():
        pages.append(page)
        counts.append(int(prob * 1000))

    return random.choices(pages, weights=counts, k=1)[0]


def iterate_pagerank(corpus, damping_factor):
    """
    Compute the PageRank values iteratively by updating the values until they converge.

    Returns a dictionary with page names as keys and their PageRank values (between 0 and 1).
    The sum of the PageRank values will be 1.
    """
    pages = list(corpus.keys())
    N = len(pages)

    # Initialize the PageRank values for all pages to be the same
    pageranks = {page: 1 / N for page in pages}

    # Build backlinks for later calculations
    backlinks = defaultdict(set)
    for page in pages:
        for source, targets in corpus.items():
            if not targets or page in targets:
                backlinks[page].add(source)

    # Continue iterating until PageRank values converge (less than 0.001 change)
    converged = False
    while not converged:
        new_pageranks = defaultdict(float)
        for page in pages:
            new_pageranks[page] = (1 - damping_factor) / N
            sigma = 0
            for link in backlinks.get(page, []):
                num_links = N if not corpus[link] else len(corpus[link])
                sigma += pageranks[link] / num_links
            new_pageranks[page] += damping_factor * sigma

        # Check for convergence by comparing the previous and current PageRank values
        converged = all(abs(new_pageranks[page] - pageranks[page]) <= 0.001 for page in pages)

        # Update the PageRank values
        pageranks = new_pageranks

    return pageranks


if __name__ == "__main__":
    main()
