__author__ = 'Rudy'

from collections import namedtuple
import json

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound

from werkzeug.contrib.sessions import SessionStore

from breve.flatten import flatten
from breve.tags.html import tags as T


ModulePageInfo = namedtuple('ModulePageInfo', ['endpoint', 'url', 'name', 'clazzFactory'])


class JsonResponse(Response):
    def __init__(self, data):
        super().__init__(json.dumps(data), mimetype='application/json')


class UIModuleDescriptior(object):
    def __init__(self, name, root, private=False):
        self.name = name
        self.root = root
        #: :type: list of pyeve.www.core.ModulePageInfo
        self.pages = []
        #: :type: list of pyeve.www.core.ModulePageInfo
        self.internalPages = []

        self.private = private

    def addPage(self, endpoint, classFactory, name=None):
        self.pages.append(ModulePageInfo(
            endpoint='%s/%s' % (self.root, endpoint),
            url='/%s/%s' % (self.root, endpoint),
            name=name,
            clazzFactory=classFactory))

    @property
    def publicPages(self):
        return [x for x in self.pages if x.name]

    @property
    def endpoints(self):
        return [x.endpoint for x in self.pages]


class Page(object):

    def __init__(self, wsgiApp, urlAdapter):
        """
        :type urlAdapter: werkzeug.routing.MapAdapter
        :type wsgiApp: pyeve.www.core.PyEveWsgiApp
        """
        self._wsgiApp = wsgiApp
        self._urlAdapter = urlAdapter

    def getUrl(self, endpoint, **params):
        return self._urlAdapter.build(endpoint, params)

    def handleRequest(self, request, params):
        methodName = 'do%s' % request.method.lower().capitalize()

        result = getattr(self, methodName)(request, **params)

        if hasattr(result, 'render'):
            return result.render(request, self._urlAdapter)

        return result

    def doGet(self, request):
        """
        :type request: werkzeug.wrappers.Request
        """

    def breveLayout(self, content):

        html = (
            T.html(lang='en')[
                T.head[
                    T.meta(charset='utf-8'),
                    T.meta(content='IE=Edge', **{'http-equiv': "X-UA-Compatible"}),
                    T.meta(name='viewport', content='width=device-width, initial-scale=1'),

                    T.title['PyEve WSGI App'],

                    T.link(href='/static/css/bootstrap.min.css', rel='stylesheet')
                ],

                T.body[
                    T.div(class_="container-fluid")[
                        T.h1['Howdy!!'],
                        content
                    ]
                ]
            ]
        )

        return Response(flatten(html), mimetype='text/html')


class InMemorySessionStore(SessionStore):

    def __init__(self):
        super().__init__()
        self.sessionCache = {}

    def save(self, session):
        self.sessionCache[session.sid] = session

    def delete(self, session):
        del self.sessionCache[session.sid]

    def get(self, sid):
        if not self.is_valid_key(sid):
            return self.new()

        if sid in self.sessionCache:
            return self.sessionCache[sid]

        newSession = self.new()
        self.sessionCache[newSession.sid] = newSession
        return newSession


class PyEveWsgiApp(object):

    def __init__(self, config):
        self.urlMap = Map()
        self.handlerMap = {}

        self.sessionStore = InMemorySessionStore()

    def registerPage(self, url, endpoint, handlerCls):
        self.urlMap.add(Rule(url, endpoint=endpoint))
        self.handlerMap[endpoint] = handlerCls

    def error_404(self):
        response = Response('4-oh-4!!')
        response.status_code = 404
        return response

    def dispatch_request(self, request):
        adapter = self.urlMap.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()

            handlerCls = self.handlerMap[endpoint]
            handler = handlerCls(self, adapter)

            return handler.handleRequest(request, values)
            # methodName = 'do%s' % request.method.lower().capitalize()
            #
            # return getattr(handler, methodName)(request, **values)
        except NotFound as e:
            return self.error_404()
        except HTTPException as e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)

        sid = request.cookies.get('pyeve_sid')
        if sid is None:
            request.session = self.sessionStore.new()
        else:
            request.session = self.sessionStore.get(sid)

        response = self.dispatch_request(request)

        if request.session.should_save:
            self.sessionStore.save(request.session)
            response.set_cookie('pyeve_sid', request.session.sid)

        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)