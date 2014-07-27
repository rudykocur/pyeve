
from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData
from sqlalchemy.sql import select

# from db import meta

meta = MetaData()

accounts = Table(
    'account', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('email', String(100), nullable=False, unique=True),
)

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