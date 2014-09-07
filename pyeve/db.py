from sqlalchemy import select, and_

from pyeve.schema import types, mapDenormalize, mapRegions, mapSolarSystems, mapConstellations, userSignatures
from pyeve.schema import UserSignature, CorpSignature

from pyeve.signatures import combineSignatures


class DataAccessRepository(object):
    def __init__(self, session):
        self._session = session

    def getSignaturesDA(self):
        return SignaturesDA(self._session)


class SignaturesDA(object):
    def __init__(self, session):
        self._session = session

    def getUserSignaturesInSystem(self, userId, systemId):
        #: :type: pyeve.schema.UserSignature
        sig = self._session.query(UserSignature).filter(and_(
            userSignatures.c.id == userId,
            userSignatures.c.systemId == systemId
        )).first()

        if sig is None:
            return []

        return sig.getSignatures()

    def updateUserSignaturesInSystem(self, userId, systemId, signatures):
        #: :type: pyeve.schema.UserSignature
        sig = self._session.query(UserSignature).filter(and_(
            userSignatures.c.id == userId,
            userSignatures.c.systemId == systemId
        )).first()

        if sig is None:
            sig = UserSignature(userId, systemId, signatures)
            self._session.add(sig)
        else:
            oldSig = sig.getSignatures()
            newSig = combineSignatures(oldSig, signatures)
            sig.setSignatures(newSig)

        return sig.getSignatures()

    def getCorpSignaturesInSystem(self, corpId, systemId):
        #: :type: pyeve.schema.CorpSignature
        sig = self._session.query(CorpSignature).filter(and_(
            userSignatures.c.id == corpId,
            userSignatures.c.systemId == systemId
        )).first()

        if sig is None:
            return []

        return sig.getSignatures()

    def updateCorpSignaturesInSystem(self, corpId, systemId, signatures):
        #: :type: pyeve.schema.CorpSignature
        sig = self._session.query(CorpSignature).filter(and_(
            userSignatures.c.id == corpId,
            userSignatures.c.systemId == systemId
        )).first()

        if sig is None:
            sig = UserSignature(corpId, systemId, signatures)
            self._session.add(sig)
        else:
            oldSig = sig.getSignatures()
            newSig = combineSignatures(oldSig, signatures)
            sig.setSignatures(newSig)

        return sig.getSignatures()


class DBCache(object):
    def __init__(self, engine):

        self.itemCache = None
        self.celestalCache = None

        with engine.connect() as conn:
            self.itemCache = self._loadItems(conn)
            self.celestalCache = self._loadCelestals(conn)

    def getItem(self, id):
        return self.itemCache[id]

    def getCelestal(self, id):
        return self.celestalCache[id]

    def _loadItems(self, conn):
        rs = conn.execute(select([types]))

        result = {}

        try:
            for row in rs:
                result[row.typeID] = row

            return result
        finally:
            rs.close()

    def _loadCelestals(self, conn):

        columns = [
            mapDenormalize.c.itemID,
            mapDenormalize.c.itemName,
            mapSolarSystems.c.solarSystemName,
            mapConstellations.c.constellationName,
            mapRegions.c.regionName,
        ]

        query = select(columns).select_from(
            mapDenormalize.join(mapSolarSystems, mapSolarSystems.c.solarSystemID == mapDenormalize.c.solarSystemID)
                        .join(mapConstellations, mapConstellations.c.constellationID == mapDenormalize.c.constellationID)
                        .join(mapRegions, mapRegions.c.regionID == mapDenormalize.c.regionID)
        )

        rs = conn.execute(query)

        result = {}

        try:
            for row in rs:
                result[row.itemID] = row

            return result
        finally:
            rs.close()


# def init_db(databaseUrl):
#
#     # if databaseUrl is None:
#     #     with open('config.yaml') as f:
#     #         config = yaml.load(f)
#     #
#     #     databaseUrl = config['database']
#
#     engine = create_engine(databaseUrl, convert_unicode=True)
#     db_session.configure(bind=engine)
#
#     # import all modules here that might define models so that
#     # they will be registered properly on the metadata. Otherwise
#     # you will have to import them first before calling init_db()
#     #import yourapplication.models
#     # import quickbudget.schema