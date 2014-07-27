from breve.tags.html import tags as T
from wtforms import Form, StringField

from pyeve.www.core import Page, UIModuleDescriptior
from pyeve.www.html import HtmlLayout, FormRenderer, forEach

__author__ = 'Rudy'


ProfileModule = UIModuleDescriptior('Profile', 'profile')
ProfileModule.addPage('overview', lambda: ProfilePage, 'My profile')
ProfileModule.addPage('apiKeys', lambda: APIKeys, 'Manage API keys')
ProfileModule.addPage('newKey', lambda: NewAPIKey)


class ProfilePage(Page):
    def doGet(self, request):
        return self.renderProfile()

    def renderProfile(self):
        html = HtmlLayout()
        html.setContent(T.h2['LOLOLOL LAYOUT'])
        return html


class APIKeys(Page):
    def doGet(self, request):

        keys = (
            # (keyId, expires, characters)
            ('123qwe', '2014-12-10 10:00:21', ['Rudykocur Maxwell', 'Zenon Koźbiał', 'Mariola Szczęsna']),
            ('DDDDD', '2014-09-10 12:11:00', ['Rudykocur Maxwell',])
        )

        return self.renderApiKeys(keys)

    def renderApiKeys(self, keys):
        content = (
            T.h2['API Keys'],

            T.p[
                T.a(href=self.getUrl('profile/newKey'))[
                    T.button(class_='btn btn-primary')['Add key']
                ],
            ],

            T.div(class_='panel panel-default')[
                T.div(class_='panel-heading')['Added keys'],

                T.table(class_='table')[
                    T.thead[
                        T.tr[
                            T.th['Key ID'],
                            T.th['Expires'],
                            T.th['Characters'],
                            T.th()
                        ]
                    ],
                    T.tbody[
                        forEach(keys, lambda keyId, expires, characters: (
                            T.tr[
                                T.td[keyId],
                                T.td[expires],
                                T.td[
                                    [
                                        T.div[char]
                                        for char in characters
                                    ]
                                ],
                                T.td[
                                    T.a(class_='glyphicon glyphicon-info-sign withTooltip', title='Detailed info',
                                        href='#',
                                        **{'data-placement': 'top', 'data-toggle': 'tooltip'}),
                                    ' ',
                                    T.a(class_='glyphicon glyphicon-trash withTooltip text-danger', title='Delete key',
                                        href='#',
                                        **{'data-placement': 'top', 'data-toggle': 'tooltip'}),
                                ]
                            ]
                        )),
                    ]
                ]
            ]
        )

        html = HtmlLayout()
        html.setContent(content)
        return html


class NewKeyForm(Form):
    keyId = StringField('Key ID')
    vCode = StringField('Verification code')


class NewAPIKey(Page):
    def doGet(self, request):

        form = NewKeyForm()

        return self.renderForm(form)

    def renderForm(self, form):
        html = HtmlLayout()

        formView = FormRenderer()
        formView.addButton('Add key')

        html.setContent(['new key form...', formView.render(form)])

        return html