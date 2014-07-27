__author__ = 'Rudy'

from werkzeug.wrappers import Response

from breve.flatten import flatten
from breve.tags.html import tags as T
from breve.tags import invisible, C

from wtforms import BooleanField

from pkg_resources import iter_entry_points


class FormRenderer(object):
    def __init__(self):
        self.buttons = []
        self.renderPanel = False

    def setRenderPanel(self):
        self.renderPanel = True

    def addButton(self, label):
        self.buttons.append(label)

    def renderStandardField(self, field):
        additionalClasses = set()

        feedbackIcon = None

        if field.flags.required:
            feedbackIcon = 'glyphicon-asterisk'

        if field.errors:
            additionalClasses.add('has-error')
            feedbackIcon = 'glyphicon-remove'

        if feedbackIcon is not None:
            additionalClasses.add('has-feedback')

        classes = ' %s' % ' '.join(additionalClasses)

        return (
            T.div(class_="form-group%s" % classes)[
                T.label(class_="col-sm-3 control-label")[field.label],
                T.div(class_="col-sm-9")[
                    field(class_='form-control'),

                    C.when(feedbackIcon)[
                        T.span(class_='glyphicon form-control-feedback %s' % feedbackIcon),
                    ],

                    C.when(field.errors)[
                        T.span(class_='help-block')[
                            T.ul[
                                [T.li[err] for err in field.errors]
                            ]
                        ]
                    ]
                ],
            ],
        )

    def renderBooleanField(self, field):

        return (
            T.div(class_="form-group")[
                T.div(class_="col-sm-offset-3 col-sm-9")[
                    T.div(class_="checkbox")[
                        T.label[
                            field(),
                            field.label
                        ]
                    ]
                ]
            ],
        )

    def renderField(self, field):

        if isinstance(field, BooleanField):
            return self.renderBooleanField(field)

        return self.renderStandardField(field)

    def render(self, form):

        formHtml = (
            T.form(class_="form-horizontal", method='POST')[

                [
                    self.renderField(field)
                    for field in form
                ],

                T.div(class_="form-group")[
                    T.div(class_="col-sm-offset-3 col-sm-9")[
                        [
                            T.button(class_="btn btn-default")[name]
                            for name in self.buttons
                        ]
                    ]
                ],
            ]
        )

        if self.renderPanel:
            formHtml = (
                T.div(class_="panel panel-default")[
                    T.div(class_="panel-body")[
                        formHtml
                    ]
                ]
            )

        return (
            formHtml
        )


class HtmlLayout(object):
    def __init__(self, isLogged=True):
        self.content = None

        #: :type: list of  pyeve.www.core.UIModuleDescriptior
        self.modules = [ep.load() for ep in iter_entry_points('UIModules')]

        self.isLogged = isLogged

    def setContent(self, content):
        self.content = content

    def renderNavbar(self, tag, data):
        """
        :type data: (werkzeug.routing.MapAdapter, None)
        """

        (url, unused) = data

        currentEndpoint = url.match()[0]

        burgerToggle = lambda targetId: (
            T.button(class_='navbar-toggle', **{'data-toggle': 'collapse', 'data-target': '#%s' % targetId})[
                T.span(class_='sr-only')['Toggle navigation'],
                T.span(class_='icon-bar'),
                T.span(class_='icon-bar'),
                T.span(class_='icon-bar'),
            ]
        )

        mainNavigation = lambda: (
            [
                T.li(class_='active' if currentEndpoint in mod.endpoints else None)[
                    T.a(href=url.build(mod.pages[0].endpoint))[mod.name]
                ]
                for mod in self.modules
            ]
        )

        html = (
            T.nav(class_='navbar navbar-default', role='navigation')[
                T.div(class_='container-fluid')[
                    T.div(class_='navbar-header')[
                        burgerToggle('mainNavCollapse'),
                        T.span(class_='navbar-brand')['Rudykocur Maxwell']
                    ],

                    T.div(class_='collapse navbar-collapse', id='mainNavCollapse')[
                        T.ul(class_="nav navbar-nav")[
                            mainNavigation()
                        ],

                        T.ul(class_="nav navbar-nav navbar-right")[
                            T.li(class_='dropdown')[
                                T.a(href='#', class_='dropdown-toggle', **{'data-toggle': 'dropdown'})[
                                    'Characters', ' ',
                                    T.span(class_='caret')
                                ],
                                T.ul(class_='dropdown-menu', role='menu')[
                                    T.li(role='presentation', class_='dropdown-header')['Account: Rudykocur'],
                                    T.li[T.a(href='#')['Rudykocur Maxwell']],
                                    T.li[T.a(href='#')['Imaginary Profile']],
                                    T.li(role='presentation', class_='divider'),
                                    T.li(role='presentation', class_='dropdown-header')['Account: Generic'],
                                    T.li[T.a(href='#')['All Skills V']],
                                ],
                            ],
                            T.li[
                                T.a(href=url.build('logout'))['Logout']
                            ]
                        ]
                    ]
                ]
            ]
        )

        return tag[html]

    def renderModuleNav(self, tag, data):
        """
        :type data: (werkzeug.routing.MapAdapter, None)
        """
        (url, unused) = data

        currentEndpoint = url.match()[0]
        currentModule = [x for x in self.modules if currentEndpoint in x.endpoints][0]

        html = (
            T.ul(class_='nav nav-pills nav-stacked')[
                [
                    T.li(class_='active' if currentEndpoint == page.endpoint else None)[
                        T.a(href=page.url)[page.name]
                    ]
                    for page in currentModule.publicPages]
            ]
        )

        return tag[html]

    def render(self, request, url):
        """
        :type url: werkzeug.routing.MapAdapter
        """

        ifLogged = lambda fun: fun if self.isLogged else ''

        layout = (
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
                        T.h1['PyEve'],
                        invisible(render=ifLogged(self.renderNavbar), data=(url, None)),
                        T.div(class_='row')[
                            T.div(class_='col-sm-3')[
                                invisible(render=ifLogged(self.renderModuleNav), data=(url, None))
                            ],
                            T.div(class_='col-sm-9')[
                                self.content
                            ]
                        ],
                    ],

                    T.script(src='https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js'),
                    T.script(src='/static/js/bootstrap.js'),
                    T.inlineJS("""
                        $(document).ready(function() {
                            $(document.body).tooltip({
                                selector: ".withTooltip"
                            })
                        })
                    """)
                ]
            ]
        )

        return Response(flatten(layout), mimetype='text/html')