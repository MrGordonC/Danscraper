import requests
import json
import ArticleExtract
import cloudscraper
from bs4 import BeautifulSoup


class Search:
    option = dict({
        "RA": ''
    })

    def __init__(self, key, format_):
        self.key = key
        self.format = format_

    # TODO mixmag, djmag, bleep, bandcamp, pitchfork
    def news(self, sites_, request, method):
        batch = list()
        news = list()
        for site in sites_:
            if site == "RA":
                if method == 'legacy':
                    ra = 'https://www.residentadvisor.net'
                else:
                    ra = 'https://www.ra.co'
                rasupported = {
                    'news': '/news',
                    'features': '/features',
                    'reviews': '/reviews'
                }
                if method == 'legacy':
                    residentadvisorHTML = requests.get(ra + rasupported.get(request, '/news', headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '}))
                    soup = BeautifulSoup(residentadvisorHTML.content, 'html.parser')
                    articles = soup.find_all('article', {'class': ['clearfix', 'highlight-top']})
                    for article in articles:
                        aref = ra + article.find('a').get('href')
                        meta = dict()
                        meta['source'] = site
                        meta['link'] = aref
                        if method == 'F':
                            news.append(search.ra_extract(article, meta))
                        else:
                            batch.append(ArticleMeta(meta))
                else:
                    # TODO read dates
                    # print('hi')
                    #residentadvisorHTML = requests.get(ra + rasupported.get(request, '/news'))
                    scraper = cloudscraper.create_scraper()
                    residentadvisorHTML = scraper.get(ra + rasupported.get(request, '/news'))
                    soup = BeautifulSoup(residentadvisorHTML.content, 'html.parser')
                    # print(soup)
                    articles = soup.find_all('ul', class_='Grid__GridStyled-sc-1l00ugd-0 fDRfdN grid')
                    for article in articles:
                        # print(article)
                        item = article.find('span', class_='Text-sc-1t0gn2o-0 Link__StyledLink-k7o46r-0 kCKrCv')
                        link = ra + item.get('href')
                        meta = dict()
                        meta['source'] = site
                        meta['link'] = link
                        if method == 'F':
                            meta = dict()
                            meta['title'] = item.get_text()
                            meta['body'] = article.find('span', class_='Text-sc-1t0gn2o-0 CmsContent__StyledText-g7gf78-0 jgkEyZ').get_text()
                            meta['media'] = article.find_all('img')
                            meta['date'] = article.find('span', class_='Text-sc-1t0gn2o-0 bEAYGt').get_text()
                            #print([title, body, media, date, link])
                            batch.append(ArticleMeta(meta))
                        else:
                            batch.append(ArticleMeta(meta))
            elif site == "FACT":
                factmagRequsts = {  # 'news': '/category/series',
                    'series': '/category/series',
                    'residency': '/category/residency',
                    'live': '/category/live',
                    'mixes': '/category/mixes'
                }
                factHTML = requests.get('https://www.factmag.com' + factmagRequsts.get(request, '/category/series'))
                if method == 'F':
                    fact = BeautifulSoup(factHTML.content, 'html.parser')
                    articles = fact.find_all(True, {
                        'class': ['block-post-wrapper row-single', 'tv-block-thumbnail', 'spaces-post-content']})
                    for article in articles:
                        meta = {'source': site}
                        news.append(search.fact_extract(article, meta))
                elif method == 'legacy':
                    # Kinda slow, perhaps get data from content page
                    fact = BeautifulSoup(factHTML.text, 'html.parser')
                    articles = fact.find_all(class_="block-post-wrapper row-single")
                    date = ''
                    # <class 'bs4.element.Tag'>
                    for article in articles:
                        url = article.find('a')
                        img = article.find('img')
                        title = url['title']
                        tmp_date = article.select_one('span[class*=meta-date]')
                        # TODO parse date from the URL
                        # date = tmp_date.text if tmp_date is not None else ""
                        date = tmp_date.get('text')
                        faref = url['href']
                        entry = requests.get(faref)
                        articleHTML = BeautifulSoup(entry.text, 'html.parser')
                        body = articleHTML.find('strong').get('text', '')
                        thumb = img['src']
                        # news.add([title, body, faref, date, thumb])
                        print([title, body, faref, date, thumb])
                        news.append(dict({'source': site,
                                          'title': title,
                                          'body': body,
                                          'link': aref,
                                          'date': date,
                                          'img': img
                                          }))
                else:
                    fact = BeautifulSoup(factHTML.content, 'html.parser')
                    articles = fact.find_all(True, {
                        'class': ['block-post-wrapper row-single', 'tv-block-thumbnail', 'spaces-post-content']})
                    for article in articles:
                        articleref = article.find('a', {'class': ['feature', 'thumb-permalink video']}).get('href', '')
                        # batch.add(ArticleMeta(site, articleref))
                        meta = {'source': site,
                                'link': articleref}
                        batch.append(ArticleMeta(meta))
            elif site == "MIX":
                mixmagURL = 'https://mixmag.net'
                # Supported[news, features, video, music]
                mixmagRequests = {
                    "news": "/news",
                    "features": "/features",
                    "music": "/music",
                    "video": "/video"
                }
                mixmagHTML = requests.get(mixmagURL + mixmagRequests.get(request, '/news'))
                mixmag = BeautifulSoup(mixmagHTML.text, 'lxml')
                articles = mixmag.find_all('div',
                                           {'class': lambda L: L and L.startswith('grid__item') and not L.endswith(
                                               'do')})
                for article in articles:
                    # TODO fast version has no date meta info
                    if method == 'F':
                        meta = {'source': site}
                        news.append(search.mix_extract(article, meta))
                    else:
                        aref = article.find('a')
                        if aref is None:
                            continue
                        aref = mixmagURL + article.find('a')['href']
                        # batch.add(ArticleMeta(site, articleref))
                        meta = {'source': site,
                                'link': aref}
                        batch.append(ArticleMeta(meta))
                    # self.mixmagExtract(aref)
            elif site == 'DJ':
                djmagURL = 'https://djmag.com'
                djmagRequests = {'latest': '/latest',
                                 'news': '/news',
                                 'features': '/features',
                                 'tech': '/tech',
                                 'home': ''
                                 }
                # Defect [[news, tech, music]: returns all URLS twice, features: no returns]
                djmaglatestfeed = requests.get(djmagURL + djmagRequests.get(request, '/latest'))
                djmaglatest = BeautifulSoup(djmaglatestfeed.content, 'html.parser')
                if method == 'legacy':
                    # Supported [latest]
                    articles = djmaglatest.find_all('a', {
                        'href': lambda l: l and (
                                l.startswith('/music/') or l.startswith('/news/'))})  # here's your url problem
                    for article in articles:
                        aref = djmagURL + article['href']
                        if method == 'F':
                            print(article)
                        else:
                            batch.append(ArticleMeta(site, aref))
                else:
                    articles = djmaglatest.find_all('article')
                    for article in articles:
                        title = article.find(['h1', 'h2'])
                        title = title.find('a').get_text() if title.find('a') else title.get_text()
                        body = article.find('div', class_='article--standfirst')
                        if body:
                            body.get_text()
                        aref = djmagURL + article.find('a').get('href')
                        date = ''
                        img = article.find('img').get('src')
                        print([site, title, body, aref, date, img])
                        news.append(dict({'source': site,
                                          'title': title,
                                          'body': body,
                                          'link': aref,
                                          'date': date,
                                          'img': img
                                          }))
            elif site == 'PITCH':
                pitchforkURL = 'https://pitchfork.com'
                pitchforknewsHTML = requests.get(pitchforkURL + '/news')
                pitchforknews = BeautifulSoup(pitchforknewsHTML.content, 'html.parser')
                articles = pitchforknews.find_all('div', class_='article-details')
                for article in articles:
                    href = article.find('a')['href']
                    aref = pitchforkURL + href
                    if method == 'F':
                        title = article.find(class_='title').getText()
                        body = article.find('p')
                        if body:
                            body = body.getText()
                        date = article.find('time')['title']
                        sibling = article.findPrevious('img')['src']
                        img = sibling
                        print([title, body, aref, date, img])
                        news.append(dict({'source': site,
                                          'title': title,
                                          'body': body,
                                          'link': aref,
                                          'date': date,
                                          'img': img
                                          }))
                    else:
                        # batch.add(ArticleMeta(site, articleref))
                        meta = {'source': site,
                                'link': aref}
                        batch.append(ArticleMeta(meta))
                    # self.pitchforkExtract(aref)
            elif site == 'BAND':
                bandcampURL = 'https://daily.bandcamp.com'
                bandcampRequests = {'news': '/latest',
                                    'features': '/features',
                                    'lists': '/lists',
                                    'electronic': '/genres/electronic',
                                    'ambient': '/genres/ambient'}
                bandcamplatestHTML = requests.get(bandcampURL + bandcampRequests.get(request,
                                                                                     '/' + request))  # /features + /album-of-the-day also supported
                # tested genres, hidden-gems. Bandcamp feeds have highly standardised layout
                bandcampdaily = BeautifulSoup(bandcamplatestHTML.content, 'lxml')
                articles = bandcampdaily.find_all('div', class_='list-article')
                for article in articles:
                    href = article.find('a')['href']
                    aref = bandcampURL + href
                    if method == 'F':
                        title = article.find('a', class_='title').getText()
                        body = ''
                        date = str(article.find('div', class_='article-info-text').getText()).split('\n')[3].strip()
                        img = article.find('img')['src']
                        print([title, body, aref, date, img])
                        news.append(dict({'source': site,
                                          'title': title,
                                          'body': body,
                                          'link': aref,
                                          'date': date,
                                          'img': img
                                          }))
                    else:
                        # batch.add(ArticleMeta(site, articleref))
                        meta = {'source': site,
                                'link': articleref}
                        batch.append(ArticleMeta(meta))

            elif site == 'QUIET':
                quietus_url = 'https://thequietus.com'
                quietus_requests = {'news': '/news',
                                    'features': '/features',
                                    'opinion': '/opinion'}
                quietus_response = requests.get(quietus_url + quietus_requests.get(request, '/news'))
                quietus_html = BeautifulSoup(quietus_response.content, 'html.parser')
                articles = quietus_html.find_all('li', {'class': ['holder', 'first holder']})
                for article in articles:
                    link = quietus_url + article.find('a').get('href')
                    meta = {'source': site,
                            'link': link}
                    if method == 'F':
                        meta['method'] = 'F'
                        meta['title'] = article.find('h4').get_text().replace('\n', '')
                        body = str(article).split('<span class="sub"></span>')[1]
                        if body:
                            body = str(body.split('<br/>')[0].strip()).replace('\n', '')
                            meta['body'] = body
                        # date = '' # could get from previous H3
                        meta['media'] = article.find('img').get('src')
                        news.append(ArticleMeta(meta))
                    else:
                        batch.append(meta)
            else:
                print(site + " not supported")
        # TODO concatenate quick results with real
        for item in batch:
            news.append(ArticleMeta.extract_meta(item))
        return news

    @staticmethod
    def ra_extract(article, meta):
        ra = 'https://www.residentadvisor.net'
        title = article.find('h1').get_text()
        body = article.find('p', class_='copy')
        if body is None:
            body = article.find(class_='copy')
        body = body.get_text() if body else ''
        date = article.find(class_='date')
        if date:
            date = date.get('text')
        thumb = article.find('img')
        img = ra + thumb.get('src')
        meta['title'] = title
        meta['body'] = body
        meta['date'] = date
        meta['media'] = img
        # return meta
        return ArticleMeta(meta)

    @staticmethod
    def fact_extract(article, meta):
        titletag = article.find('a', {'class': ['video', 'feature', 'thumb-permalink feature'],
                                      'title': True})
        title = titletag.get('title', '')
        body = article.find_previous('h2', {'class': ['tv-cat-title secondary-font', 'meta']})
        if body:
            body = body.get_text()
        else:
            # body is auto-generated
            body1 = article.find_next('h2', class_='tv-cat-title secondary-font')
            body2 = article.find_next('p')
            # body1 = body1.get_text() + ': ' if body1 else ''
            body1 = body1.get_text()
            # body2 = body2.get_text() if body2 else ''
            body2 = body2.get_text()
            body = body1 + body2
        articleref = article.find('a', {'class': ['feature', 'thumb-permalink video']})
        aref = articleref.get('href', '')
        date = article.findNext('p', {'class': ['meta-date', 'meta', 'meta-data secondary-font']})
        # date = date.getText() if date else ''
        date = date.get_text()
        img = article.find('img').get('src')
        meta['title'] = title
        meta['body'] = body
        meta['date'] = date
        meta['media'] = img
        return ArticleMeta(meta)

    @staticmethod
    def mix_extract(article, meta):
        mixmagURL = 'https://mixmag.net'
        header = article.find('h3')
        if header is None:
            print(article)
            return None
        title = header.string
        body = article.find('p').string
        date = ''
        meta['link'] = mixmagURL + article.find('a')['href']
        img = article.find('img')['src']
        meta['title'] = title
        meta['body'] = body
        meta['date'] = date
        meta['media'] = img
        #print([title, body, aref, date, thumb])
        # news.append(dict({'source': site,
        #                   'title': title,
        #                   'body': body,
        #                   'link': aref,
        #                   'date': date,
        #                   'img': thumb,
        #                   'home': ''
        #                   }))
        return ArticleMeta(meta)

class ArticleMeta(object):
    extract = dict({"BAND": ArticleExtract.bandcampExtract,
                    "FACT": ArticleExtract.factmagExtract,
                    "DJ": ArticleExtract.djmagExtract,
                    "MIX": ArticleExtract.mixmag_extract,
                    "PITCH": ArticleExtract.pitchforkExtract,
                    "RA": ArticleExtract.raExtract
                    })

    def __init__(self, article_meta):
        self.extract = article_meta

    def getArticle(self, *method):
        source = self.extract['source']
        url = self.extract['link']
        self.extract['method'] = method
        if method == 'S':
            result = ArticleMeta.extract[source](url)
        else:
            result = self.articleMeta(source, url)
            self.update(result.extract, '')
        return result

    @classmethod
    def extract_meta(cls, meta):
        source = meta.get('source')
        url = meta.get('link')
        method = meta.get('method')
        return ArticleMeta.factory(source, url)
        # return self.getArticle()

    @classmethod
    def factory(cls, source, article_url):
        if source == 'RA':
            scraper = cloudscraper.create_scraper()
            article_response = scraper.get(article_url)
        else:
            article_response = requests.get(article_url)
        article_html = BeautifulSoup(article_response.content, 'html.parser')

        title = article_html.find('meta', property='og:title').get('content')
        body = article_html.find('meta', property='og:description').get('content')
        date = ArticleMeta.meta_date(article_html)
        img = article_html.find('meta', property='og:image').get('content')
        # print([source, title, body, article_url, date, img])
        article_meta = dict()
        article_meta['source'] = source
        article_meta['title'] = title
        article_meta['body'] = body
        article_meta['link'] = article_url
        article_meta['date'] = date
        article_meta['media'] = img
        article_meta = ArticleMeta(article_meta)
        return article_meta

    @staticmethod
    def meta_date(article_html):
        # TODO RA Date
        published_time = article_html.find('meta', property='article:published_time')
        if published_time:
            meta_date = published_time.get('content')
        else:
            header__meta = article_html.find(class_='article-header__meta')
            meta_date = ''
            if header__meta:
                meta_date = header__meta.findAll('li')[1].getText()
            else:
                payloud = article_html.find('script', type="application/ld+json")
                if payloud:
                    script = json.loads(payloud.string)
                    if script.get('dateCreated'):
                        meta_date = script.get('dateCreated')
                    elif script.get('datePublished'):
                        meta_date = script.get('datePublished')
        return meta_date

    def print(self):
        article_meta = self.extract
        source = article_meta.get('source')
        title = article_meta.get('title')
        body = article_meta.get('body')
        link = article_meta.get('link')
        date = article_meta.get('date')
        media = article_meta.get('media')
        # print(source, title, body, link, date, media)
        print(article_meta)

    def update(self, update_dict, mode):
        if mode == 'SAFE':
            self.extract = {**self.extract, **update_dict}
        else:
            self.extract = {**update_dict, **self.extract}

# search = Search('some', 'thing')
# search.news(['RA', 'PITCH', 'MIX'], 'news', 'quick')
# sites = ['RA', 'FACT', 'DJ', 'MIX', 'PITCH', 'BAND']
# articles = search.news(['QUIET'], 'news', '')
# for article in articles:
#     article.print()

# MetaUrlInfo("RA", 'https://www.residentadvisor.net/features/3782').getArticle()
# search.factmagExtract('https://www.factmag.com/2020/07/14/artist-diy-pussy-riot/')
# for site in sites:
#   search.news(site)
# MetaUrlInfo("RA", 'https://www.residentadvisor.net/reviews/22826').getArticle()
