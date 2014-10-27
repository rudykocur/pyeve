__author__ = 'Rudy'


from collections import namedtuple


SimpleContainerEntry = namedtuple('SimpleContainerEntry', ['name', 'quantity'])


def parseContainerEntries(containerPasteStr):
    result = []

    for line in containerPasteStr.split("\n"):
        if not line:
            continue

        name, quantity, *rest = line.split("\t")

        result.append(SimpleContainerEntry(name, (int(quantity) if quantity else 1)))

    return result


def formatWorthAsString(total):
    totalStr = str(total)

    if len(totalStr) < 5:
        return format(totalStr, ',d').replace(',', ' ')

    significant = totalStr[:3]

    roundedTotal = int(significant) * int(10 ** len(totalStr[3:]))

    return format(roundedTotal, ',d').replace(',', ' ')