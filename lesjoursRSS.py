#!/usr/bin/env python
# vim:fileencoding=utf-8

__license__ = 'GPL v3'
__copyright__ = '2012'

'''
lesjours.fr
'''

from calibre.web.feeds.news import BasicNewsRecipe

class AdvancedUserRecipe1672311212(BasicNewsRecipe):
    title          = 'Les jours RSS'
    __author__ = 'RoBSPRR'
    description = 'Les flux RSS de lesjours.fr'
    publisher = 'Les Jours'
    publication_type = 'newspaper'
    needs_subscription = 'optional'
    language = 'fr'

    oldest_article = 7
    max_articles_per_feed = 50
    no_stylesheets = True
    remove_empty_feeds = True
    ignore_duplicate_articles = {'title', 'url'}

    
    conversion_options = {
        'publisher': publisher
    }

    
    auto_cleanup   = True

    masthead_url = 'https://upload.wikimedia.org/wikipedia/fr/4/4c/Les_Jours.svg'


    feeds          = [
        ('Les jours', 'https://lesjours.fr/rss.xml'),
    ]

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