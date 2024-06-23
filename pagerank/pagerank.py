import os
import random
import re
import sys

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
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    # Create a dictionary to store the probability distribution
    prob_dist = {}

    # If the page has no outgoing links, return a probability distribution that chooses randomly from all pages with
    # equal probability
    if len(corpus[page]) == 0:
        for p in corpus:
            prob_dist[p] = 1 / len(corpus)
        return prob_dist

    # Otherwise, return a probability distribution that chooses randomly from all pages with probability (1 -
    # damping_factor) and chooses from the outgoing links with probability damping_factor
    for p in corpus:
        prob_dist[p] = (1 - damping_factor) / len(corpus)
    for p in corpus[page]:
        prob_dist[p] += damping_factor / len(corpus[page])

    return prob_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Create a dictionary to store the number of times each page has been visited
    visits = {}
    for page in corpus:
        visits[page] = 0

    # Choose a page at random to start
    page = random.choice(list(corpus.keys()))

    # Loop through the number of samples
    for i in range(n):
        # Update the number of times the page has been visited
        visits[page] += 1

        # Get the probability distribution for the page
        prob_dist = transition_model(corpus, page, damping_factor)

        # Choose the next page based on the probability distribution
        page = random.choices(list(prob_dist.keys()), weights=prob_dist.values(), k=1)[0]

    # Normalize the number of visits to get the PageRank values
    ranks = {}
    for page in visits:
        ranks[page] = visits[page] / n

    return ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Initialize the PageRank values
    ranks = {}
    for page in corpus:
        ranks[page] = 1 / len(corpus)

    # Loop until the PageRank values converge
    while True:
        # Create a copy of the current PageRank values
        new_ranks = ranks.copy()

        # Loop through each page and update its PageRank value
        for page in corpus:
            new_ranks[page] = (1 - damping_factor) / len(corpus)
            for p in corpus:
                # If the page has no links, assume it has links to all pages
                if len(corpus[p]) == 0:
                    new_ranks[page] += damping_factor * ranks[p] / len(corpus)
                elif page in corpus[p]:
                    new_ranks[page] += damping_factor * ranks[p] / len(corpus[p])

        # Check for convergence
        converged = True
        for page in ranks:
            if abs(new_ranks[page] - ranks[page]) > 0.001:
                converged = False
                break

        # If the PageRank values have converged, return the values
        if converged:
            return new_ranks

        # Otherwise, update the PageRank values and continue
        ranks = new_ranks

if __name__ == "__main__":
    main()
