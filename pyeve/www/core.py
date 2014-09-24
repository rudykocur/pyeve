from sqlalchemy.orm import sessionmaker

__author__ = 'Rudy'

from collections import namedtuple
import json

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound

from werkzeug.contrib.sessions import SessionStore

from pyeve.db import DataAccessRepository
from sqlalchemy import create_engine


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

    def __init__(self, wsgiApp, urlAdapter, dataAccessRepo):
        """

        :type dataAccessRepo: pyeve.db.DataAccessRepository
        :type urlAdapter: werkzeug.routing.MapAdapter
        :type wsgiApp: pyeve.www.core.PyEveWsgiApp
        """
        self._wsgiApp = wsgiApp
        self._urlAdapter = urlAdapter
        self._da = dataAccessRepo

    def getUrl(self, endpoint, **params):
        return self._urlAdapter.build(endpoint, params)

    def getDA(self):
        return self._da

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

    def __init__(self, databaseUrl):
        self.urlMap = Map()
        self.handlerMap = {}

        self.sessionStore = InMemorySessionStore()

        # local.application = self
        self.database_engine = create_engine(databaseUrl, convert_unicode=True, echo=True, pool_recycle=3600)
        self.databaseSessionMaker = sessionmaker(bind=self.database_engine)

    def registerPage(self, url, endpoint, handlerCls):
        self.urlMap.add(Rule(url, endpoint=endpoint))
        self.handlerMap[endpoint] = handlerCls

    def error_404(self):
        response = Response('4-oh-4!!')
        response.status_code = 404
        return response

    def dispatch_request(self, request):
        # local.application = self

        dbSession = self.databaseSessionMaker()

        adapter = self.urlMap.bind_to_environ(request.environ)
        try:
            daRepo = DataAccessRepository(dbSession)

            endpoint, values = adapter.match()

            handlerCls = self.handlerMap[endpoint]
            handler = handlerCls(self, adapter, daRepo)

            response = handler.handleRequest(request, values)

            dbSession.commit()

            return response

        except NotFound as e:
            dbSession.rollback()
            return self.error_404()

        except HTTPException as e:
            dbSession.rollback()
            return e

        finally:
            dbSession.close()

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
