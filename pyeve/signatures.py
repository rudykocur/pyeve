__author__ = 'Rudy'

from collections import namedtuple


Signature = namedtuple('Signature', ['key', 'group', 'type', 'name'])


def parseSignatures(signaturesData):
    """

    :type signaturesData: str
    :rtype: list of [pyeve.signatures.Signature]
    """
    result = []

    for row in signaturesData.split("\n"):
        if not row:
            continue

        sigKey, group, sigType, name, *other = row.split('\t')

        result.append(Signature(
            key=sigKey,
            group=group,
            type=sigType,
            name=name,
        ))

    return result


def unparseSignatures(signatures):
    """

    :type signatures: list of pyeve.signatures.Signature
    """
    result = []

    for row in signatures:
        result.append('%s\t%s\t%s\t%s' % (row.key, row.group, row.type, row.name))

    return '\n'.join(result)


def combineSignatures(old, new):
    result = []

    oldByKey = dict([(x.key, x) for x in old])
    newByKey = dict([(x.key, x) for x in new])

    allKeys = set(oldByKey.keys()) | set(newByKey.keys())

    for key in allKeys:
        if key in oldByKey and key in newByKey:
            result.append(_combineOldAndNew(oldByKey[key], newByKey[key]))
        elif key in newByKey:
            result.append(newByKey[key])

    return result


def _combineOldAndNew(old, new):
    """

    :type old: pyeve.signatures.Signature
    :type new: pyeve.signatures.Signature
    """

    return Signature(
        key=old.key,
        group=new.group or old.group,
        type=new.type or old.type,
        name=new.name or old.name,
    )