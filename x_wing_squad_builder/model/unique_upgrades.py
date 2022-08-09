def get_root(name: str):
    """returns the root of a name, example:
    'gar saxon (crew)' becomes 'gar saxon'
    """
    name_arr = name.split()
    idx = None
    for i, part in enumerate(name_arr):
        if ('(') in part:
            idx = i

    return ' '.join(name_arr[:idx])

UNIQUE_UPGRADES = [
    "general grievous",
    "asajj ventress",
    "sabine wren",
    "^chopper^",
    "r2-d2",
    "boba fett",
    "dengar",
    "bossk",
    "finn",
    "han solo",
    "rey",
    "ahsoka tano",
    "fifth brother",
    "luke skywalker",
    "zeb orrelios",
    "4-lom",
    "lando calrissian",
    "the mandalorian",
    "unkar plutt",
    "zuckuss",
    "cad bane",
    "chewbacca",
    "ig-88d",
    "ciena ree",
    "hera syndulla",
    "ketsu onyo",
    "l3-37",
    "captain phasma",
    "cassian andor",
    "latts razzi",
    "magva yarro",
    "nien numb",
    "bo-katan kryze",
    "commander malarus",
    "gar saxon",
    "gamut key",
    "jango fett",
    "k-2so",
    "leia organa",
    "fenn rau",
    "maul",
    "kylo ren",
    "obi-wan kenobi",
    "plo koon",
    "pre vizsla",
    "rook kast",
    "rose tico",
    "saw gerrera",
    "seventh sister",
    "zam wesell",
    "kanan jarrus",
    "yoda",
    "grand inquisitor",
    "count dooku",
    "darth vader"
]