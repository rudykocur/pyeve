import json

from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData, Text
from sqlalchemy.orm import mapper

meta = MetaData()

accounts = Table(
    'account', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('email', String(100), nullable=False, unique=True),
)

userSignatures = Table(
    'userSignatures', meta,
    Column('id', Integer, primary_key=True, autoincrement=False),
    Column('systemId', Integer, primary_key=True, autoincrement=False),
    Column('data', Text, nullable=False),
)

corpSignatures = Table(
    'corpSignatures', meta,
    Column('id', Integer, primary_key=True, autoincrement=False),
    Column('systemId', Integer, primary_key=True, autoincrement=False),
    Column('data', Text, nullable=False),
)


class SignaturesBase(object):
    def getSignatures(self):
        if self.data is None:
            return None

        return json.loads(self.data)

    def setSignatures(self, signatures):
        self.data = json.dumps(signatures)


class UserSignature(SignaturesBase):

    def __init__(self, userId, systemId, signatures):
        self.id = userId
        self.systemId = systemId

        self.data = None
        if signatures is not None:
            self.setSignatures(signatures)


class CorpSignature(SignaturesBase):

    def __init__(self, corpId, systemId, signatures):
        self.id = corpId
        self.systemId = systemId

        self.data = None
        if signatures is not None:
            self.setSignatures(signatures)


mapper(UserSignature, userSignatures)
mapper(CorpSignature, corpSignatures)

# =================================================================================
# Tables from static export below
# =================================================================================

types = Table(
    'invTypes', meta,
    Column('typeID', Integer, primary_key=True),
    Column('typeName', String))

mapRegions = Table(
    'mapRegions', meta,
    Column('regionID', Integer, primary_key=True),
    Column('regionName', String))

mapConstellations = Table(
    'mapConstellations', meta,
    Column('constellationID', Integer, primary_key=True),
    Column('constellationName', String),
    Column('regionID', Integer, ForeignKey('mapRegions.regionID')))

mapSolarSystems = Table(
    'mapSolarSystems', meta,
    Column('solarSystemID', Integer, primary_key=True),
    Column('solarSystemName', String),
    Column('regionID', Integer, ForeignKey('mapRegions.regionID')),
    Column('constellationID', Integer, ForeignKey('mapConstellations.constellationID')))

mapDenormalize = Table(
    'mapDenormalize', meta,
    Column('itemID', Integer, primary_key=True),
    Column('itemName', String),
    Column('regionID', Integer, ForeignKey('mapRegions.regionID')),
    Column('constellationID', Integer, ForeignKey('mapConstellations.constellationID')),
    Column('solarSystemID', Integer, ForeignKey('mapSolarSystems.solarSystemID')))