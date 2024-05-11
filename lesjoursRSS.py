#!/usr/bin/env python

__author__= 'RoBSPRR'
__license__ = 'GPL v3'

'''
lesjours.fr
'''

from calibre.web.feeds.news import BasicNewsRecipe, classes
import re, zipfile, os
from calibre.ptempfile import PersistentTemporaryDirectory
from calibre.ptempfile import PersistentTemporaryFile


class LesJours(BasicNewsRecipe):
    title = 'Les Jours'
    __author__ = 'RoBSPRR'
    description = 'Les Jours'
    publisher = 'Les Jours'
    authors = 'Les Jours'
    publication_type = 'newspaper'
    needs_subscription = True
    language = 'fr'

    no_stylesheets = True
    ignore_duplicate_articles = {'title', 'url'}
    auto_cleanup = False

    conversion_options = {
        'publisher': publisher,
        'authors': authors
    }

    masthead_url = 'https://upload.wikimedia.org/wikipedia/fr/4/4c/Les_Jours.svg'

    keep_only_tags = [dict(attrs={'itemprop': ['image', 'name headline', 'description', 'datePublished', 'author', 'articleBody']})]

    """
    remove_tags    = [dict(name='span', attrs={'class': ['col ml-auto w-auto']}),
                      dict(name='div', attrs={'class': ['rel container fluid p-0 sm-hidden print-hidden', 'col sm-w-6c md-w-4c lg-w-4c mt-2 col-bottom text-right', 'row m-0 row-center no-wrap obsession-name']})
                      ]
    """

    preprocess_regexps = [
        (re.compile(r'(<span class="mr-2">)([^<]*)(</span>.*?itemprop="name">)([^<]*</span>)', re.DOTALL|re.IGNORECASE),
         lambda match:  match.group(3)+ ' | ' + match.group(2) + ' : ' + match.group(4)),
        (re.compile(r'(<blockquote[^<]*<p>)([^<]*)(</p>)', re.DOTALL|re.IGNORECASE),
         lambda match: match.group(1) + '«' + match.group(2) + '»' + match.group(3))
    ]

    extra_css = '''
    .aside { font-weight: bold; font-size: 1.3em; }
    .blockquote { font-style: italic; font-size: 1.3em; }
    .footer { font-style: normal; font-weight: bold; font-size: 0.7em; }
    .figcaption { font-weight: bold; font-size: 0.9em; }
    .credits { font-weight: normal; font-size: 1em; }
    '''

    def get_browser(self):
        br = BasicNewsRecipe.get_browser(self)
        if self.username is not None and self.password is not None:
            try:
                br.open('https://lesjours.fr/connexion')
                br.select_form(nr=0)
                br['login-mail'] = self.username
                br['login-password'] = self.password
                br.submit()
            except Exception as e:
                self.log('Login failed with error:', str(e))
        return br

    def get_cover_url(self):
        return 'https://lesjours.fr/ressources/res1500/image/ep144-fin-campagne-img-header.jpeg'

    def parse_index(self):
        ans = []
        soup = self.index_to_soup('https://lesjours.fr/obsessions/')
        sections = soup.find('section', {'id': 'obsessions'})
        #print(sections)
        for section in sections.find_all('a', {'class': 'card-obsession'}):
            sect_url = 'https://lesjours.fr' + section.get('href')
            sect_title = section.find(class_='lj-color-text').string
            sect_desc = section.find('div', {'class': 'subtitle'})
            articles = list(self.parse_section(sect_url))
            if articles:
                ans.append((sect_title, articles))

        # Parse "la vie des « Jours »"
        sect_url = 'https://lesjours.fr/obsessions/vie-jours/'
        sect_title = 'la vie des « Jours »'
        sect_desc = 'L’actualité des « Jours » au jour le jour.'
        articles = list(self.parse_section(sect_url))
        if articles:
            ans.append((sect_title, articles))

        return ans

    def parse_section(self, sect_url):
        soup=self.index_to_soup(sect_url)
        counter = 0
        for article in soup.find(id='episodes-list').find_all('a'):
            episodeNumber = article.get('href').split('/')[-2]
            episodeNumber = episodeNumber.split('-')[0][2:]  + ' : '
            url = 'https://lesjours.fr%s' % article.get('href')
            #url = 'https://lesjours.fr/obsessions/eoliennes-bray-dunes/ep1-opposition-parc-offshore/'
            title =  episodeNumber + article.find('h2').get_text()
            yield {'title': title, 'url': url}
            counter += 1
            if sect_url == 'https://lesjours.fr/obsessions/vie-jours/' and counter == 5:
                break

    def preprocess_raw_html(self, raw_html, url):
        #print(raw_html)
        return raw_html

    def preprocess_html(self, soup):
        # when an image is available in multiple sizes, select the 480w one
        for img in soup.find_all('img', {'srcset': True}):
            #print ("IMGDDPYL0 = ", img)
            srcset = img['srcset'].split()
            #print ("IMGDDPYL1 = ", srcset)
            if len(srcset) > 1:
                img['src'] = srcset[2]
                #print("IMGDDPYL2 = " ,img['src'])
                del img['srcset']
        for img in soup.find_all('img', {'data-srcset': True}):
            #print ("IMGDDPYL0 = ", img)
            data_srcset = img['data-srcset'].split()
            #print ("IMGDDPYL1 = ", data_srcset)
            if len(data_srcset) > 1:
                img['src'] = data_srcset[2]
                #print("IMGDDPYL2 = " ,img['src'])
                del img['data-srcset']
        return soup

    def postprocess_html(self, soup, first_fetch):
        #print(soup.prettify())
        #remove local hyperlinks
        for a in soup.find_all('a', {'href': True}):
            if 'lesjours.fr' in a['href']:
                a.replace_with(self.tag_to_string(a))
        for a in soup.find_all('a', {'data-note': True}):
            a.replace_with(self.tag_to_string(a))
        for a in soup.find_all('a', {'data-mini': True}):
            a.replace_with(self.tag_to_string(a))

        for a in soup.find_all('aside'):
            a['class']='aside'
        for a in soup.find_all('figcaption'):
            a['class']='figcaption'
        for a in soup.find_all('blockquote'):
            a['class']='blockquote'
        for a in soup.find_all('footer'):
            a['class']='footer'
        return soup
