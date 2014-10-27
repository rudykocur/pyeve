from breve.flatten import flatten

from breve.tags.html import tags as T
from breve.tags import C

from pyeve.www.core import UIModuleDescriptior, Page, JsonResponse
from pyeve.www.html import Panel, forEach, Modal
from pyeve.www.igb import IGBLayout, IGBRequest

from pyeve.signatures import parseSignatures
from pyeve.loot import parseContainerEntries, formatWorthAsString

ScanningModule = UIModuleDescriptior('Scanning', 'scanning', private=True)
ScanningModule.addPage('personal', lambda: PersonalScanningPage, 'Personal scanner')
ScanningModule.addPage('corporation', lambda: CorporationScanningPage, 'Corporation scanner')
ScanningModule.addPage('help', lambda: HelpPage, 'Help page')


class HelpPage(Page):
    def doGet(self, request):
        layout = IGBLayout()

        layout.setContent([
            Panel(heading=['How to use scanning tool'],
                  content=[
                      T.p["""
                      This tool alows you to remember all scanned signatures in given solar system. It will try
                      to automatically detect that you changed system, and always show you signatures from system
                      you are currently in
                      """],

                      T.p["""
                      Basic idea for this tool is that, you should copy-and-paste all data from scanning overview to
                      rectangular gray textarea in this tool (and submit) as often as posible. It will automatically
                      detect changes, update existing signatures with more info, delete old signatures, and add new.
                      """],

                      T.p["""
                      This tool has two modes: personal and corporation. All they differ is who sees your submitted
                      data. It might be only you, or all people from your corporation.
                      """],

                      T.p["""
                      To copy-paste signatures from scanning overview, select any signature in your "Probe scanner"
                      window. Then press ctrl+a (select all), then ctrl+c (copy). Then click in IGB window, inside
                      rectangular gray area, and press ctrl+v (paste).
                      """],

                      T.div[
                          T.img(src='/static/images/help_overview.jpg'),
                          T.img(src='/static/images/help_igb_paste.jpg')

                      ],

                      T.p["""
                      """],

                      T.hr(),

                      T.p[
                          'Back to: ',
                          T.a(href=self.getUrl('scanning/personal'))['personal scanner'],
                          ' or ',
                          T.a(href=self.getUrl('scanning/corporation'))['corporation scanner'],
                      ]
                  ])
        ])

        return layout


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

            parsed = parseSignatures(newSignatures)
            currentSignatures = self._updateSignatures(self.getDA().getSignaturesDA(), helper, parsed)

            html = flatten(self.getKnownSignaturesTable(currentSignatures))

            return JsonResponse(dict(status='save sig', html=html))

        elif operation == 'getSystem':
            return JsonResponse(dict(systemName=helper.systemName))

        elif operation == 'getLoot':
            return self.handleGetLootRequest(request)

        elif operation == 'addContainer':
            return self.handleAddContainerRequest(request)

        else:
            return JsonResponse(dict(error='invalid operation'))

    def handleGetLootRequest(self, request):
        """
        :type request: werkzeug.wrappers.Request
        """

        html = flatten(self.renderSignatureLoot(request.args['key']))

        return JsonResponse(
            dict(status='getLoot',
                 metadata=dict(

                     levels=dict(
                         trivial=dict(
                             label='Debris',
                             image='http://image.eveonline.com/Type/33254_64.png',
                         ),
                         easy=dict(
                             label='Rubble',
                             image='http://image.eveonline.com/Type/33255_64.png',
                         ),
                         medium=dict(
                             label='Remains',
                             image='http://image.eveonline.com/Type/33256_64.png',
                         ),
                         hard=dict(
                             label='Ruins',
                             image='http://image.eveonline.com/Type/33257_64.png',
                         ),
                     ),
                 ),
                 html=html)
        )

    def handleAddContainerRequest(self, request):
        """
        :type request: werkzeug.wrappers.Request
        """

        import time
        time.sleep(1)

        content = request.data.decode('utf8')
        entries = parseContainerEntries(content)

        total = self.getDA().getLootDA().calculateLootWorth(entries)

        import random

        return JsonResponse(
            dict(status='addContainer',
                 id=random.randint(1, 1000000),
                 totalWorth='%s ISK' % formatWorthAsString(total))
        )

    def renderResponse(self, helper, signatures):

        layout = IGBLayout()
        layout.addJs('common.js')
        layout.addJs('scanning.js')
        layout.addJs('loot.js')

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
                                T.button(class_='btn btn-default', id='processButton')['Submit'],
                                T.img(id='ajaxLoader', src='/static/images/ajax-loader.gif'),
                            ],

                        ]
                    ]
                ),
                Panel(heading=['Known signatures in ', T.strong[helper.systemName],
                               T.div(class_='pull-right')[
                                   T.a(href=self.getUrl('scanning/help'))['How to use this tool']
                               ]],
                      content=[
                          T.div(id='bookmarkContainer')[
                              self.getKnownSignaturesTable(signatures)
                          ],

                      ]),
                T.script[
                    """
                    $(document).ready(function() {
                        BookmarkManager.init({
                            container: document.getElementById('bookmarkContainer'),
                            processButton: document.getElementById('processButton'),
                            signaturesInput: document.getElementById('signaturesInput'),
                            ajaxLoader: document.getElementById('ajaxLoader'),

                            systemName: '%(system)s'
                        });

                        LootInterface.init();
                    });
                    """ % dict(system=helper.systemName)
                ]
            ]

            layout.setContent(content)

        return layout

    def renderSignatureLoot(self, signatureKey):
        result = Modal(
            id='lootModal',
            content=[
                T.div(id='containers')[
                    T.div(class_='buttons')[
                            T.button(type='button', class_='btn btn-success', **{'data-level': 'trivial'})['+ Debris'],
                            T.button(type='button', class_='btn btn-success', **{'data-level': 'easy'})['+ Rubble'],
                            T.button(type='button', class_='btn btn-warning', **{'data-level': 'medium'})['+ Remains'],
                            T.button(type='button', class_='btn btn-danger', **{'data-level': 'hard'})['+ Ruins'],
                    ],

                    T.div(id='contentPaste')[
                        Panel(
                            heading='Paste content of container below',
                            content=[
                                T.div(class_='row')[
                                    T.div(class_='col-xs-9')[
                                        T.textarea(class_="form-control", rows="2"),
                                    ],
                                    T.div(class_='col-xs-3')[
                                        T.button(class_='btn btn-default')['Submit'],
                                        T.div(class_='ajaxLoader', style='white-space: nowrap')[
                                            T.img(src='/static/images/ajax-loader.gif'),
                                            ' Processing'
                                        ],
                                    ],
                                ],
                            ]
                        ),
                    ],

                    T.div(class_='row container-list')[
                        T.div(class_='col-xs-3 blueprint')[
                            T.div(class_='thumbnail')[
                                T.img(src='#'),
                                T.div(class_='caption')[
                                    T.strong()['Lorem ipsum'],
                                    T.div(class_='totalWorth')['Lorem ipsum'],
                                ],

                                T.a(href='#', title='Delete', **{'data-toggle': 'tooltip', 'data-placement': 'top'})[
                                    T.span(class_='glyphicon glyphicon-remove-circle')
                                ]
                            ]

                        ]
                    ],
                ]
            ],
            heading=['Loot for signature ', T.strong[signatureKey]],
        )

        return result

    def getKnownSignaturesTable(self, signatures):

        result = [
            T.table(class_='table table-bordered')[
                T.thead[
                    T.tr[
                        T.th['Key'],
                        T.th['Group'],
                        T.th['Type'],
                        T.th['Name'],
                        T.th[''],
                    ]
                ],

                T.tbody[
                    forEach(signatures, lambda key, group, sigType, name: [
                        T.tr[
                            T.td[key],
                            T.td[group],
                            T.td[sigType],
                            T.td[name],
                            T.td[
                                C.when(sigType in ['Data Site', 'Relic Site'])[
                                    T.a(href='#', class_='lootModalToggle', **{'data-key': key})[
                                        'Loot'
                                    ]
                                ]
                            ]
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

        return signaturesDA.updateUserSignaturesInSystem(helper.charID, helper.systemID, signatures)

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

        return signaturesDA.updateCorpSignaturesInSystem(helper.corpID, helper.systemID, signatures)

    def _renderHeader(self, helper):
        """
        :type helper: pyeve.www.igb.IGBRequest
        """

        return [
            'Hello ', T.strong[helper.charName], ', from ', T.strong[helper.corpName],

            T.div(class_='pull-right')[
                T.a(href=self.getUrl('scanning/personal'))['Go to personal']
            ]
        ]