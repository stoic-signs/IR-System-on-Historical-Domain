from search import search_query, search_tag, fetch



if __name__ == "__main__":
    switcher = {
        1: search_query,
        2: search_tag,
        3: fetch,
        4: exit
    }

    while True:
        try:
            print('-------------------------------------------\n')
            key = int(input("What do you want to search today?\n1. Query\n2. Tag\n3. Fetch\n4.Exit\n"))
            print('-------------------------------------------')
            # assert key in switcher.keys()
        except (TypeError, KeyError):
            print('Invalid Input. Try again!\n')

        func = switcher[key]
        func()
