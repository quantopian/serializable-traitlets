"""
Miscellaneous utilities.
"""


def remove_elems(dict_, to_remove):
    """
    Return a copy of ``dict_`` with elems removed.

    Parameters
    ----------
    dict_ : dict
    to_remove : iterable
    """
    out = dict_.copy()
    for k in to_remove:
        del out[k]
    return out
