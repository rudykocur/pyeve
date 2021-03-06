from pyeve.www.html import Panel, LayoutBase

__author__ = 'Rudy'


from werkzeug.wrappers import Response

from breve.flatten import flatten
from breve.tags.html import tags as T
from breve.tags import invisible, C


class IGBRequest(object):
    def __init__(self, request):
        """
        :type request: werkzeug.wrappers.Request
        """

        self._request = request

        self.isDevel = (request.remote_addr == '127.0.0.1')

    @property
    def isTrusted(self):
        if self.isDevel:
            return True

        return self._request.headers.get('EVE_TRUSTED', 'No') == 'Yes'

    @property
    def charName(self):
        return self._request.headers.get('EVE_CHARNAME', 'ANON')

    @property
    def charID(self):
        return int(self._request.headers.get('EVE_CHARID', '666'))

    @property
    def systemName(self):
        return self._request.headers.get('EVE_SOLARSYSTEMNAME', 'SOL001')

    @property
    def systemID(self):
        return int(self._request.headers.get('EVE_SOLARSYSTEMID', '777'))

    @property
    def corpName(self):
        return self._request.headers.get('EVE_CORPNAME', 'CORPO666')

    @property
    def corpID(self):
        return int(self._request.headers.get('EVE_CORPID', '888'))


class IGBLayout(LayoutBase):

    def render(self, request, url):
        """
        :type url: werkzeug.routing.MapAdapter
        :type request: werkzeug.wrappers.Request
        """

        # ifLogged = lambda fun: fun if self.isLogged else ''
        isTrusted = IGBRequest(request).isTrusted

        layout = (
            T.html(lang='en')[
                T.head[
                    T.meta(charset='utf-8'),
                    T.meta(content='IE=Edge', **{'http-equiv': "X-UA-Compatible"}),
                    T.meta(name='viewport', content='width=device-width, initial-scale=1'),

                    T.title['PyEve IGB'],

                    T.link(href='/static/css/bootstrap-black.min.css', rel='stylesheet'),
                    T.link(href='/static/css/igb.css', rel='stylesheet'),

                    T.script(src='https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js'),
                    T.script(src='/static/js/bootstrap.js'),
                    T.script(src='/static/js/igbCore.js'),

                    self.getAdditionalJs()
                ],

                T.body[
                    # 'HOWDY',
                    # request.headers.get('EVE_TRUSTED', 'alo'),
                    T.div(class_='container-fluid')[
                        C.switch(isTrusted)[
                            C.case(True)[self.content],
                            C.case(False)[self.renderRequestTrust()]
                        ],

                        T.div(class_='text-center')[
                            T.small[
                                'PyEVE. Created by ',
                                T.a(href="#", onclick="CCPEVE.showInfo(1377, 93747896); return false")[
                                    'Rudykocur Maxwell'
                                ]
                            ]
                        ]
                    ],
                ]
            ]
        )

        return Response(flatten(layout), mimetype='text/html')

    def renderRequestTrust(self):
        result = [

            Panel(heading='Untrusted',
                  content=[
                      T.p(id='untrusted')[
                          T.a(href='#', onclick='return IGBManager.requestTrust()')['Please trust me!']
                      ],

                      T.p()[
                          T.a(href='#', onclick='return IGBManager.reload()')['Reload page'],
                          ' when you accepted trust request'
                      ]
                  ])


        ]

        return result