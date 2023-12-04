
def match_all_in_list(collection:list, **kwargs) -> list:
    """
    Queries a list collection for objects with attributes in the given keyword parameters.

    collection: A list of objects
    kwargs: Keyword arguments to match object attributes to values. Falsy values will be ignored. No args will return all in the collection.
    Returns: List of objects that match given criteria
    """
    # Only query given parameters
    query_attrs =  {k:v for k,v in kwargs.items() if v}
    # Match all given parameters
    if query_attrs:
        match = [entry for entry in collection
                if all(value in [getattr(entry, query_attr) for query_attr in query_attrs] for value in query_attrs.values())]
    else:
        match = collection
    return match

def ensure_one(func):
    def wrapper(*args, **kwargs):
        return_list = func(*args, **kwargs)
        if return_list and len(return_list) > 1:
            raise RuntimeError(f"More than one object returned when calling {func}")
        
        if not return_list:
            return None
        
        return return_list[0]
    return wrapper
