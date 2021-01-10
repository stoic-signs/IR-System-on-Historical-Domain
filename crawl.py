import wikipediaapi
import random, time

def read_exclude_cats(filename='exclude_cats.txt'):
    with open(filename) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content

EXCLUDE = []

def exclude(tags):
    global EXCLUDE
    for t in EXCLUDE:
        if t in tags.keys():
            tags.pop(t)
    return tags

count=0
documents_collected = []
categories_covered = []
def print_categorymembers(categorymembers, level=0, max_level=4):
    global count, documents_collected, categories_covered, EXCLUDE
    if categorymembers:
        for c in categorymembers.values():
            if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
                if (c not in categories_covered) and (c not in EXCLUDE):
                    categories_covered.append(c)
                    time.sleep(2)
                    print_categorymembers(exclude(c.categorymembers), level=level + 1, max_level=max_level)
            elif c.ns == 0:
                if c.title not in documents_collected:
                    print("%s: %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
                    count += 1
                    documents_collected.append(c.title)
    
if __name__ == "__main__":
    documents_collected = read_exclude_cats(filename='rand.txt')
    EXCLUDE = read_exclude_cats()
    wiki_wiki = wikipediaapi.Wikipedia(
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI
    )
    start_page = wiki_wiki.page("World War II")
    tags = exclude(start_page.categories)
    for j in tags.keys():
        current_tag = wiki_wiki.page(j)
        print_categorymembers(current_tag.categorymembers)
        time.sleep(2)
        print('-----------------------------------------------------------------------------------------------------------------')
    print(categories_covered)