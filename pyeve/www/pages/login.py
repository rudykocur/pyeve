from pyeve.www.html import HtmlLayout, FormRenderer

__author__ = 'Rudy'

from breve.tags.html import tags as T
from werkzeug.utils import redirect
from wtforms import Form, StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, EqualTo, Email

from pyeve.www.core import Page


class LoginForm(Form):
    login = StringField('Login')
    password = PasswordField('Password')
    remember = BooleanField('Remember me')


class LoginPage(Page):
    def doGet(self, request):
        form = LoginForm()

        request.session.setdefault('loginCount', 0)
        request.session['loginCount'] += 1

        return self.renderLoginForm(form, request.session['loginCount'])

    def doPost(self, request):
        """

        :type request: werkzeug.wrappers.Request
        """
        form = LoginForm(request.form)

        if form.validate():
            return redirect(self.getUrl('profile/overview'))

        return self.renderLoginForm(form, -1)

    def renderLoginForm(self, form, count):

        formView = FormRenderer()
        formView.addButton('Login')
        formView.setRenderPanel()

        content = [
            T.div(class_="row")[
                T.div(class_="col-sm-4")[
                    T.h2['Login form '],
                ],
                T.div(class_="col-sm-4 text-right")[
                    T.h2[T.a(href=self.getUrl('register'))['Register account']]
                ]
            ],

            T.div(class_="row")[
                T.div(class_="col-sm-8")[
                    formView.render(form)
                ]
            ],

        ]

        layout = HtmlLayout(isLogged=False)
        layout.setContent(content)
        return layout


class LogoutPage(Page):
    def doGet(self, request):
        request.session['loginCount'] = 0
        return redirect(self.getUrl('index'))


class NewAccountForm(Form):
    email = StringField('Email address', [InputRequired(), Email(message='Not an email address')])
    password = PasswordField('Password', [InputRequired(),
                                          EqualTo('password_repeat', message='Password does not match')])
    password_repeat = PasswordField('Repeat password')


class RegisterAccount(Page):
    def doGet(self, request):
        form = NewAccountForm()
        return self.renderRegisterForm(form)

    def doPost(self, request):
        form = NewAccountForm(request.form)

        if form.validate():
            return redirect(self.getUrl('profile/overview'))

        return self.renderRegisterForm(form)

    def renderRegisterForm(self, form):
        html = HtmlLayout(isLogged=False)

        formView = FormRenderer()
        formView.addButton('Create account')
        formView.setRenderPanel()

        content = (
            T.div(class_="row")[
                T.div(class_="col-sm-4")[
                    T.h2['Register form'],
                ],
                T.div(class_="col-sm-4 text-right")[
                    T.h2[T.a(href=self.getUrl('index'))['Back']]
                ]
            ],

            T.div(class_="row")[
                T.div(class_="col-sm-8")[
                    formView.render(form)
                ]
            ]
        )

        html.setContent(content)

        return html