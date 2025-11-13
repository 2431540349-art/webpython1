from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using a dynamic key in templates.

    This function is robust to keys that are stored as int or str in the
    dictionary. It will try the key as-is, then as a string, then as an int
    (when possible). If the dictionary is falsy or the key is not found,
    return an empty list to make template loops safe.

    Usage: {{ dictionary|get_item:key }}
    """
    if not dictionary:
        return []

    # Try direct lookup first
    try:
        if key in dictionary:
            return dictionary[key]
    except Exception:
        # key might be unhashable in some edge-cases; ignore and continue
        pass

    # Try string form of key
    try:
        sk = str(key)
        if sk in dictionary:
            return dictionary[sk]
    except Exception:
        pass

    # If key looks like an integer string, try int form
    try:
        if isinstance(key, str) and key.isdigit():
            ik = int(key)
            if ik in dictionary:
                return dictionary[ik]
    except Exception:
        pass

    # Not found: return empty list so templates can iterate safely
    return []


@register.filter
def multiply(value, arg):
    """Multiply a numeric value by arg in templates.

    Usage: {{ lessons|length|multiply:45 }}
    Returns an integer when both operands are numeric. Falls back to string
    representation on error to avoid breaking templates.
    """
    try:
        # Convert both to floats to support numeric strings and ints
        v = float(value)
        a = float(arg)
        result = v * a
        # If result is an integer value, return as int to avoid .0 in templates
        if result.is_integer():
            return int(result)
        return result
    except Exception:
        # If conversion fails, return empty string so template shows nothing
        return ""