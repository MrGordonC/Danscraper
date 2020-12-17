import requests
from bs4 import BeautifulSoup


class Search():
    def __init__(self, key, format_):
        self.key = key
        self.format = format_

    # TODO mixmag, djmag, bleep, bandcamp
    def news(self, site):
        if site == "RA":
            ra = 'https://www.residentadvisor.net'
            r = requests.get(ra + '/news')
            soup = BeautifulSoup(r.text, 'html.parser')
            popularnews = 'popular-news'
            newslisting = 'news-listing'
            articles = soup.find_all(class_="highlight-top")
            headers = soup.find_all('h1', articles)
            ra = 'https://www.residentadvisor.net'
            for article in articles:
                title = article.find('h1').getText()
                body = article.find(class_='copy').getText()
                date = article.find(class_='date').getText()
                aref = ra + article.find('a')['href']
                thumb = article.find('img')
                thumb = ra + thumb['src']
                print([title, body, date, aref, thumb])
        elif site == "FACT":
            # Kinda slow, perhaps get data from content page
            fa = requests.get('https://www.factmag.com')
            fact = BeautifulSoup(fa.text, 'html.parser')
            sm = fact.find_all(class_="block-post-wrapper row-single")
            date = ''
            # <class 'bs4.element.Tag'>
            for s in sm:
                # print(s)
                url = s.find('a')
                img = s.find('img')
                title = url['title']
                tmp_date = s.select_one('span[class*=meta-date]')
                # TODO parse date from the URL
                date = tmp_date.text if tmp_date is not None else ""
                faref = url['href']

                entry = requests.get(faref)
                mg = BeautifulSoup(entry.text, 'html.parser')
                body = mg.find('strong').getText()

                thumb = img['src']
                print([title, body, faref, date, thumb])
        elif site == "MIX":
            mixmagURL = 'https://mixmag.net'
            mi = requests.get(mixmagURL + '/news')
            mix = BeautifulSoup(mi.text, 'lxml')
            mixmag = mix.find_all('div', {'class': lambda L: L and L.startswith('grid__item') and not L.endswith('do')})
            for article in mixmag:
                # TODO fast version has no date meta info
                # header = article.find('h3')
                # if header is None continue
                # title = header.string
                # body = article.find('p').string
                # date = ''
                # aref = mixmagURL + article.find('a')['href']
                # thumb = article.find('img')['src']

                aref = article.find('a')
                if aref is None:
                    # print(article)
                    continue
                aref = mixmagURL + article.find('a')['href']
                mixmagArticle = requests.get(aref)
                mixmag = BeautifulSoup(mixmagArticle.text, 'lxml')
                title = mixmag.find('h1', class_='article-header__title').string
                body = mixmag.find('div', class_='article-header__excerpt').string
                date = mixmag.find(class_='article-header__meta').findAll('li')[1].string
                thumb = mixmag.find('img', {'class': lambda l: l and (l.startswith('media') or l.endswith('media'))})
                print([title, body, aref, date, thumb])
        elif site == 'DJ':
            djmagURL = 'https://djmag.com'
            djmaglatestfeed = requests.get(djmagURL + '/latest')
            djmaglatest = BeautifulSoup(djmaglatestfeed.content, 'html.parser')
            djmagXML = djmaglatest.findAll('a', {'href': lambda l: l and(l.startswith('/music/') or l.startswith('/news/'))})
            for href in djmagXML:
                articleURI = djmagURL + href['href']
                article = requests.get(articleURI)
                dj = BeautifulSoup(article.text, 'lxml')
                title = dj.find('h1').string
                body = dj.find('div', class_='article--standfirst').find_all('p')
                b = ''
                for p in body:
                    if p.find(dir='ltr'):
                        b = p.find(dir='ltr')
                        continue
                    elif p.find('span'):
                        b = p.find('span')
                        continue
                    else:
                        b = p
                body = b.string
                date = dj.find('div', class_='article--info--date').string.strip()
                img = dj.find('figure').find('img')['src']
                print([title, body, articleURI, date, img])
                # print(article)
        else:
            print("not supported")


s = Search('some', 'thing')
s.news("DJ")
