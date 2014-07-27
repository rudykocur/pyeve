import os

from werkzeug.wsgi import SharedDataMiddleware

from pyeve.www.core import PyEveWsgiApp
from pyeve.www.routing import initRouting


def create_app(with_static=True):
    app = PyEveWsgiApp({
    })

    initRouting(app)

    if with_static:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static': os.path.join(os.path.dirname(__file__), 'pyeve', 'static', 'public')
        })
    return app


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    wsgiapp = create_app()
    run_simple('0.0.0.0', 5000, wsgiapp, use_debugger=True, use_reloader=True)