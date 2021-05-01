from search import Search


def main():
    running = True
    print(1)
    search = Search('some', 'thing')
    while running:
        sites = list()
        sites_prompt = input('Enter site: ')
        sites.append(sites_prompt)
        sites_submitted = False
        while not sites_submitted:
            submit = input('Add another site? (site name, n or empty): ')
            if submit == 'n' or '':
                sites_submitted = True
            else:
                sites.append(submit)
        run_mode = input('Run mode: ').upper()
        run_mode_confirm = input('Run mode ' + run_mode + '? (y/n/empty for default): ').lower()
        if run_mode_confirm == 'y':
            articles = search.news(sites, 'news', run_mode)
            for article in articles:
                article.print()
        exit_prompt = input("Scrape again? (y/n): ")
        if exit_prompt == 'n':
            running = False
            print(1)


if __name__ == '__main__':
    main()
