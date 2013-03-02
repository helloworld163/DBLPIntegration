import os
from demo import DBLPQuery
from supquery import get_publications_by_u
import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['html'])

class Root(object):

    @cherrypy.expose
    def ww(self):
        tmpl = lookup.get_template('ww.html')
        return tmpl.render()

    @cherrypy.expose
    def index(self):
        tmpl = lookup.get_template('index.html')
        return tmpl.render()

    @cherrypy.expose
    def query(self, query_type, author1, author2, cdblp_venue, dblp_venue, submit):

        tmpl = lookup.get_template('query.html')

        cached_author_list = DBLPQuery.get_cached_authors()
        name_set = set(map(lambda a: a['full_name'], cached_author_list)).union(set(map(lambda a: a['zh'], cached_author_list)))

        if query_type == 'pub':
            result = get_publications_by_u(cached_author_list, name_set, author1)
            return tmpl.render(type=query_type, data=result, author=author1)

        elif query_type == 'coauthor':
            result = DBLPQuery.get_coauthors_by_author(cached_author_list, name_set, author1)
            return tmpl.render(type=query_type, data=result, author=author1)

        elif query_type == 'venue':
            result = DBLPQuery.get_venues_by_author(cached_author_list, name_set, author1)
            l = []
            for k, v in result.items():
                l.append({ 'venue': k, 'type': v.get('type'), 'count': v.get('count') })
            l.sort(key=lambda i: i['count'], reverse=True)

            return tmpl.render(type=query_type, data=l, author=author1)

        elif query_type == 'coauthor-pub':
            result = DBLPQuery.get_coauthored_publications_by_authors(cached_author_list, name_set, author1, author2)
            return tmpl.render(type=query_type, data=result, author1=author1, author2=author2)

        elif query_type == 'join-venue':
            d = DBLPQuery.get_authors_by_venue(cached_author_list, name_set, { 'title': cdblp_venue }, { 'title': dblp_venue })
            l = []

            for k, v in d.items():
                l.append({ 'name': v['zh'], 'name_en': k, 'count': v['count'] })

            #l.sort(key=lambda i: i['count'], reverse=True)
            return tmpl.render(type=query_type, data=l, cdblp_venue=cdblp_venue, dblp_venue=dblp_venue)

        return tmpl.render()


if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Set up site-wide config first so we get a log if errors occur.
    cherrypy.config.update({'environment': 'production',
                            'log.error_file': 'site.log',
                            'log.screen': True})

    conf = {'/stylesheets': {'tools.staticdir.on': True,
                      'tools.staticdir.dir': os.path.join(current_dir, 'css'),
                      'tools.staticdir.content_types': {'css': 'text/css'}}}
    cherrypy.quickstart(Root(), '/', config=conf)