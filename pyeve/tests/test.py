from pyeve import eveapi, db
from pyeve.eveapi import cache

__author__ = 'Rudy'

eveapi.set_user_agent('pyeve-dev')
api = eveapi.EVEAPIConnection(cacheHandler=cache.MyCacheHandler(debug=True))

auth = api.auth(keyID=2510622, vCode='DenCNTsu1ObUhPZn1cIg23jCzec7OIlkRuDlhkXJkwAZkSTAzEO6STXrHZ1A8w1e')

characters = auth.account.Characters()

me = auth.character(characters.characters[0].characterID)

result = api.eve.SkillTree()
refTypes = api.eve.RefTypes()
assets = me.AssetList()

print(result)

dbCache = db.DBCache()

# assetLocations = list(set([row.locationID for row in assets.assets]))

# print('ALL Locations', [dbCache.getCelestal(a).itemName for a in assetLocations])

def assetPrinter(rowset, indent=0):
    for row in rowset:
        typeName = dbCache.getItem(id=row.typeID).typeName

        print('    ' * indent, typeName, 'quantity:', row.quantity, 'flag:', row.flag)
        subRowset = row.get('contents', None)
        if subRowset:
            assetPrinter(subRowset, indent+1)

# print('FFFF', assets.assets.GroupedBy('locationID'))

assetLocations = assets.assets.GroupedBy('locationID')

for x in assetLocations.keys():
    cel = dbCache.getCelestal(x)
    print("Location: ", cel.itemName, ', System:', cel.solarSystemName, ', Constellation:', cel.constellationName)

    assetPrinter(assetLocations[x], indent=1)

# assetPrinter(assets.assets)