def main():
    running = True
    print(1)
    while running:
        exit_prompt = input("Scrape again? (y/n): ")
        if exit_prompt == 'n':
            running = False
            print(1)


if __name__ == '__main__':
    main()
