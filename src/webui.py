import cherrypy

class HelloWorld(object):
    def index(self):
        return "Hello World!"
    index.exposed = True

    def search(self):
        return "Hi this is the search page."
    search.exposed = True

cherrypy.quickstart(HelloWorld())