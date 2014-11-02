from breve.flatten import flatten

from breve.tags.html import tags as T
from breve.tags import C

from pyeve.www.core import UIModuleDescriptior, Page, JsonResponse
from pyeve.www.html import Panel, forEach, Modal
from pyeve.www.igb import IGBLayout, IGBRequest

WormholeMapModule = UIModuleDescriptior('Wormhole map', 'wh_map', private=True)
WormholeMapModule.addPage('map', lambda: WormholeMapPage, 'Wormhole map')


def whSlotEmpty():
    return T.div(class_='whSlot emptySlot')

def whSlot(title, data):
    return T.div(class_='whSlot', id='sig-%s' % title)[
          T.div(class_='title')[title],
          T.div(class_='')[data]
      ]


class WormholeMapPage(Page):
    def doGet(self, request):
        layout = IGBLayout()

        layout.addJs('dom.jsPlumb-1.6.4-min.js')
        layout.addJs('whMap.js')

        layout.setContent([
            Panel(heading=['Simple map'],
                  content=T.div(id='wormholeMap')[
                      T.div(class_='whRow')[
                          whSlotEmpty(),
                          whSlotEmpty(),
                          whSlot('J123456', 'Some data'),
                          whSlot('J098654', 'Some data 2'),
                          whSlotEmpty(),
                          whSlotEmpty(),
                      ],
                      T.div(class_='whRow')[
                          whSlotEmpty(),
                          whSlotEmpty(),
                          whSlotEmpty(),
                          whSlot('J432567', 'Some data 2'),
                          whSlotEmpty(),
                          whSlotEmpty(),
                      ],
                      T.div(class_='whRow')[
                          whSlotEmpty(),
                          whSlot('J111111', 'Some data 9'),
                          whSlot('J111112', 'Some data 8'),
                          whSlot('J111113', 'Some data 7'),
                          whSlot('J111114', 'Some data 6'),
                          whSlot('J111115', 'Some data 5'),
                      ],
                  ]
            )
        ])

        return layout