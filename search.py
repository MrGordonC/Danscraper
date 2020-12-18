import requests
from bs4 import BeautifulSoup


class Search:
    def __init__(self, key, format_):
        self.key = key
        self.format = format_

    # TODO mixmag, djmag, bleep, bandcamp, pitchfork
    def news(self, site, option):
        batch = set()
        if site == "RA":
            ra = 'https://www.residentadvisor.net'
            # Supported [news]
            # Not supported [reviews]
            residentadvisorHTML = requests.get(ra + '/features.aspx')
            soup = BeautifulSoup(residentadvisorHTML.content, 'html.parser')
            # popularnews = 'popular-news'
            # newslisting = 'news-listing'
            articles = soup.find_all(class_="highlight-top")
            ra = 'https://www.residentadvisor.net'
            for article in articles:
                title = article.find('h1').getText()
                body = article.find(class_='copy').getText()
                date = article.find(class_='date').getText()
                aref = ra + article.find('a')['href']
                thumb = article.find('img')
                img = ra + thumb['src']
                batch.add(MetaUrlInfo('RA', aref))
                # print([title, body, date, aref, img])
                # set.add(dict(
                #     "title": title,
                #     "body" : body,
                #     "aref": aref,
                #     "date": date,
                #     "img":  img,
                # ))
        elif site == "FACT":
            # Kinda slow, perhaps get data from content page
            factHTML = requests.get('https://www.factmag.com')
            fact = BeautifulSoup(factHTML.text, 'html.parser')
            articles = fact.find_all(class_="block-post-wrapper row-single")
            date = ''
            # <class 'bs4.element.Tag'>
            for article in articles:
                # print(s)
                url = article.find('a')
                img = article.find('img')
                title = url['title']
                tmp_date = article.select_one('span[class*=meta-date]')
                # TODO parse date from the URL
                date = tmp_date.text if tmp_date is not None else ""
                faref = url['href']

                entry = requests.get(faref)
                articleHTML = BeautifulSoup(entry.text, 'html.parser')
                body = articleHTML.find('strong').getText()

                thumb = img['src']
                print([title, body, faref, date, thumb])
        elif site == "MIX":
            mixmagURL = 'https://mixmag.net'
            # Supported[news, features, video, music]
            mixmagHTML = requests.get(mixmagURL + '/video')
            mixmag = BeautifulSoup(mixmagHTML.text, 'lxml')
            articles = mixmag.find_all('div',
                                       {'class': lambda L: L and L.startswith('grid__item') and not L.endswith('do')})
            for article in articles:
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
                    continue
                aref = mixmagURL + article.find('a')['href']
                batch.add(MetaUrlInfo(site, aref))
                self.mixmagExtract(aref)
        elif site == 'DJ':
            djmagURL = 'https://djmag.com'
            # Supported [latest]
            # Defect [[news, tech, music]: returns all URLS twice, features: no returns]
            djmaglatestfeed = requests.get(djmagURL + '/latest')
            djmaglatest = BeautifulSoup(djmaglatestfeed.content, 'html.parser')
            articles = djmaglatest.findAll('a', {
                'href': lambda l: l and (l.startswith('/music/') or l.startswith('/news/'))})  # here's your url problem
            for article in articles:
                aref = djmagURL + article['href']
                batch.add(MetaUrlInfo(site, aref))
                # self.djmagExtract(aref)
        elif site == 'PITCH':
            pitchforkURL = 'https://pitchfork.com'
            pitchforknewsHTML = requests.get(pitchforkURL + '/news')
            pitchforknews = BeautifulSoup(pitchforknewsHTML.content, 'html.parser')
            articles = pitchforknews.find_all('div', class_='article-details')
            for article in articles:
                href = article.find('a')['href']
                aref = pitchforkURL + href
                batch.add(MetaUrlInfo('PITCH', aref))
                # self.pitchforkExtract(aref)
        elif site == 'BAND':
            bandcampURL = 'https://daily.bandcamp.com'
            bandcamplatestHTML = requests.get(bandcampURL + '/latest')  # /features + /album-of-the-day also supported
            # tested genres, hidden-gems. Bandcamp feeds have highly standardised layout
            bandcampdaily = BeautifulSoup(bandcamplatestHTML.content, 'lxml')
            articles = bandcampdaily.find_all('div', class_='list-article')
            for article in articles:
                href = article.find('a')['href']
                aref = bandcampURL + href
                batch.add(MetaUrlInfo("BAND", aref))
                # self.bandcampExtract(aref) # perhaps return a dictionary or tuple
        else:
            print("not supported")

        for b in batch:
            b.getArticle()

    @staticmethod
    def raExtract(articleURL):
        raurl = 'https://www.residentadvisor.net'
        print(articleURL)
        residentAdvisorArticle = requests.get(articleURL)
        ra = BeautifulSoup(residentAdvisorArticle.content, 'html.parser')
        title = ra.find('h1').getText()
        body = ra.find('p', class_='intro').getText()
        date = ra.find('aside', id='detail').find('li', class_='wide')
        if date:
            date = date.getText()
        img = ra.find('figure')
        if img:
            img = raurl + img.find('img')['src']
        print([title, body, articleURL, date, img])
        return {"title": title,
                "body": body,
                "link": articleURL,
                "date": date,
                "media": img
                }

    @staticmethod
    def mixmagExtract(articleURL):
        mixmagArticle = requests.get(articleURL)
        mixmag = BeautifulSoup(mixmagArticle.text, 'html.parser')
        title = mixmag.find('h1', class_='article-header__title').getText()
        body = mixmag.find('div', class_='article-header__excerpt').getText()
        date = mixmag.find(class_='article-header__meta').findAll('li')[1].getText()
        img = mixmag.find('img', {'class': lambda l: l and (l.startswith('media') or l.endswith('media'))})
        if img is not None:
            thumb = img['src']
        print([title, body, articleURL, date, img])
        return {"title": title,
                "body": body,
                "link": articleURL,
                "date": date,
                "media": img
                }

    @staticmethod
    def djmagExtract(articleURL):
        article = requests.get(articleURL)
        dj = BeautifulSoup(article.text, 'lxml')
        title = dj.find('h1').string
        standfirst = dj.find('div', class_='article--standfirst').find_all('p')
        body = ''
        for p in standfirst:
            if p.find(dir='ltr'):
                body = p.find(dir='ltr')
                continue
            elif p.find('span'):
                body = p.find('span')
                continue
            else:
                body = p
        body = body.string
        date = dj.find('div', class_='article--info--date').getText().strip()
        img = dj.find('figure').find('img')['src']
        print([title, body, articleURL, date, img])
        return {"title": title,
                "body": body,
                "link": articleURL,
                "date": date,
                "media": img
                }

    @staticmethod
    def pitchforkExtract(articleURL):
        articleHTML = requests.get(articleURL)
        pf = BeautifulSoup(articleHTML.content, 'html.parser')
        title = pf.find('h1').getText()
        body = pf.find('div', class_='content-header__row content-header__dek').getText()
        date = pf.find('time').getText()
        # media = pf.find('picture', class_='lead-asset__media responsive-image')
        media = pf.find('span', class_='responsive-asset lead-asset__media')
        img = media.find('img', class_='responsive-image__image')
        if img is not None:
            img = img['src']
        else:
            # TODO not in media for some reason
            vid = pf.find('video', class_='responsive-clip__video')
            if vid is not None:
                img = vid['src']

        print([title, body, articleURL, date, img])
        return {"title": title,
                "body": body,
                "link": articleURL,
                "date": date,
                "media": img
                }

    @staticmethod
    def bandcampExtract(articleURL):
        articleHTML = requests.get(articleURL)
        bcd = BeautifulSoup(articleHTML.content, 'html.parser')
        title = bcd.find('article-title').getText().strip()
        body = bcd.find('a', class_='franchise').getText()
        # date = str(article.find('div', class_='article-info-text').getText()).split('\n')[3].strip()
        # additional filtering available via body
        date = str(bcd.find('div', class_='article-info-text').getText()).split('\n')[3].strip()
        img = bcd.find('img', id='feature-image')
        if img is not None:
            img = img['src']
        # if body == 'HIDDEN GEMS':
        print([title, body, articleURL, date, img])
        return {"title": title,
                "body": body,
                "link": articleURL,
                "date": date,
                "media": img
                }


class MetaUrlInfo(object):
    extract = dict({"BAND": Search.bandcampExtract,
                    "DJ": Search.djmagExtract,
                    "MIX": Search.mixmagExtract,
                    "PITCH": Search.pitchforkExtract,
                    "RA": Search.raExtract
                    })

    def __init__(self, source, url):
        self.source = source
        self.url = url

    def getArticle(self):
        source = self.source
        url = self.url
        # print(source)

        result = MetaUrlInfo.extract[source](url)
        return result

MetaUrlInfo("RA", "https://www.residentadvisor.net/features/3782").getArticle()
search = Search('some', 'thing')
# search.news('RA', 'news')
sites = ['RA', 'FACT', 'DJ', 'MIX', 'PITCH', 'BAND']
# for site in sites:
#     search.news(site)
