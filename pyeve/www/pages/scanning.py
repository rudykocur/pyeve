import os
import json
from breve.flatten import flatten

from breve.tags.html import tags as T
from breve.tags import invisible, C
from werkzeug.wrappers import Response

from pyeve.www.core import UIModuleDescriptior, Page, JsonResponse
from pyeve.www.html import Panel, forEach
from pyeve.www.igb import IGBLayout, IGBRequest

__author__ = 'Rudy'

ScanningModule = UIModuleDescriptior('Scanning', 'scanning', private=True)
ScanningModule.addPage('personal', lambda: PersonalScanningPage, 'Personal scanner')
ScanningModule.addPage('corporation', lambda: CorporationScanningPage, 'Corporation scanner')


class ScanningPageBase(Page):

    def _loadSignatures(self, signaturesDA, helper):
        """
        :type signaturesDA: pyeve.db.SignaturesDA
        :type helper: pyeve.www.igb.IGBRequest
        """

        raise Exception('Not implemented')

    def _updateSignatures(self, signaturesDA, helper, signatures):
        """
        :type signaturesDA: pyeve.db.SignaturesDA
        :type helper: pyeve.www.igb.IGBRequest
        """

        raise Exception('Not implemented')

    def _renderHeader(self, helper):
        """
        :type helper: pyeve.www.igb.IGBRequest
        """
        raise Exception('Not implemented')

    def doGet(self, request):
        """
        :type request: werkzeug.wrappers.Request
        """

        helper = IGBRequest(request)

        savedSignatures = self._loadSignatures(self.getDA().getSignaturesDA(), helper)

        return self.renderResponse(helper, savedSignatures)

    def doPost(self, request):
        """
        :type request: werkzeug.wrappers.Request
        """

        operation = request.args.get('call', None)
        helper = IGBRequest(request)

        if operation == 'saveSignatures':
            newSignatures = request.data.decode('utf8')
            newSignatures = json.loads(newSignatures)

            self._updateSignatures(self.getDA().getSignaturesDA(), helper, newSignatures)

            html = flatten(self.getKnownSignaturesTable(newSignatures))

            return JsonResponse(dict(status='save sig', html=html))

        elif operation == 'getSystem':
            return JsonResponse(dict(systemName=helper.systemName))

        else:
            return JsonResponse(dict(error='invalid operation'))

    def renderResponse(self, helper, signatures):

        layout = IGBLayout()
        layout.addJs('scanning.js')

        if helper.isTrusted:

            content = [
                Panel(
                    heading=[
                        self._renderHeader(helper),
                    ],
                    content=[
                        T.div(class_='row')[
                            T.div(class_='col-xs-8')[
                                T.textarea(class_="form-control",
                                           id="signaturesInput",
                                           rows="2",
                                           style="overflow: hidden; resize: none",
                                           placeholder="Paste scanning content here")
                            ],
                            T.div(class_='col-xs-4')[
                                T.button(class_='btn btn-default', id='processButton')['Submit']
                            ],

                        ]
                    ]
                ),
                Panel(heading=['Known signatures in ', T.strong[helper.systemName]],
                      content=[
                          T.div(id='bookmarkContainer')[
                              self.getKnownSignaturesTable(signatures)
                          ]
                      ]),
                T.script[
                    """
                    $(document).ready(function() {
                        BookmarkManager.init({
                            container: document.getElementById('bookmarkContainer'),
                            processButton: document.getElementById('processButton'),
                            signaturesInput: document.getElementById('signaturesInput'),

                            systemName: '%(system)s',
                            savedSignatures: %(signatures)s
                        });
                    });
                    """ % dict(system=helper.systemName,
                               signatures=json.dumps(signatures))
                ]
            ]

            layout.setContent(content)

        return layout

    def getKnownSignaturesTable(self, signatures):

        result = [
            T.table(class_='table table-bordered')[
                T.thead[
                    T.tr[
                        T.th['Key'],
                        T.th['Group'],
                        T.th['Type'],
                        T.th['Name'],
                        T.th['Strength'],
                        T.th['Updated'],
                    ]
                ],

                T.tbody[
                    forEach(signatures, lambda row: [
                        T.tr[
                            T.td[row['key']],
                            T.td[row['group']],
                            T.td[row['type']],
                            T.td[row['name']],
                            T.td[row['strength']],
                            T.td[row['updated']],
                        ]
                    ])
                ]
            ]
        ]

        return result


class PersonalScanningPage(ScanningPageBase):
    def _loadSignatures(self, signaturesDA, helper):
        """
        :type signaturesDA: pyeve.db.SignaturesDA
        :type helper: pyeve.www.igb.IGBRequest
        """

        return signaturesDA.getUserSignaturesInSystem(helper.charID, helper.systemID)

    def _updateSignatures(self, signaturesDA, helper, signatures):
        """
        :type signaturesDA: pyeve.db.SignaturesDA
        :type helper: pyeve.www.igb.IGBRequest
        """

        signaturesDA.updateUserSignaturesInSystem(helper.charID, helper.systemID, signatures)

    def _renderHeader(self, helper):
        return [
            'Hello ', T.strong[helper.charName],

            T.div(class_='pull-right')[
                T.a(href=self.getUrl('scanning/corporation'))['Go to corp']
            ]
        ]


class CorporationScanningPage(ScanningPageBase):
    def _loadSignatures(self, signaturesDA, helper):
        """
        :type signaturesDA: pyeve.db.SignaturesDA
        :type helper: pyeve.www.igb.IGBRequest
        """

        return signaturesDA.getCorpSignaturesInSystem(helper.corpID, helper.systemID)

    def _updateSignatures(self, signaturesDA, helper, signatures):
        """
        :type signaturesDA: pyeve.db.SignaturesDA
        :type helper: pyeve.www.igb.IGBRequest
        """

        signaturesDA.updateCorpSignaturesInSystem(helper.corpID, helper.systemID, signatures)

    def _renderHeader(self, helper):
        """
        :type helper: pyeve.www.igb.IGBRequest
        """

        return [
            'Hello ', T.strong[helper.charName], ', in the name of ', T.strong[helper.corpName],

            T.div(class_='pull-right')[
                T.a(href=self.getUrl('scanning/personal'))['Go to personal']
            ]
        ]