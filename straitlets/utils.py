
def merge(*ds):
    """
    Merge together a sequence if dictionaries.

    Later entries overwrite values from earlier entries.

    >>> merge({'a': 'b', 'c': 'd'}, {'a': 'z', 'e': 'f'})
    {'a': 'z', 'c': 'd', 'e': 'f'}
    """
    if not ds:
        raise ValueError("Must provide at least one dict to merge().")
    out = {}
    for d in ds:
        out.update(d)
    return out
