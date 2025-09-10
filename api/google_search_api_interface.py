# Install the library before: pip install googlesearch-python

from googlesearch import search


def find_instagram_url(name, address, num_results=5):
    # Build the query
    query = f"site:instagram.com/*/ {name} {address}"

    # Perform the search
    results = search(query, num_results=num_results)

    # Take the first result
    for url in results:
        return url  # return first match

    return None


if __name__ == "__main__":
    name = "bar roxy"
    address = "Montecchia di crosara"
    url = find_instagram_url(name, address)

    if url:
        print("Found Instagram URL:", url)
    else:
        print("No result found.")
