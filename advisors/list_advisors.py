from textwrap import dedent

from advisors import advisor, get_name, get_val
import conf

@advisor(conf.LIST_ELEMENT_TYPE)
def list_overview(element, safe_imports, code_str):
    name = get_name(element)
    items = get_val(safe_imports, code_str, name)
    message = {
        conf.BRIEF: dedent(f"""
            `{name}` is a list with {len(items):,} items
        """),
    }
    return message

@advisor(conf.LIST_ELEMENT_TYPE, warning=True)
def mixed_list_types(element, safe_imports, code_str):
    """
    Warns about lists with mixed types.

    NOTE: This isn't actually checking variable types, just AST node types ;-)
    """
    name = get_name(element)
    items = get_val(safe_imports, code_str, name)
    item_types = sorted(set([
        conf.CLASS2NAME[type(item).__name__] for item in items]
    ))
    if len(item_types) <= 1:
        ## No explanation needed if there aren't multiple types.
        return None
    else:
        message = {
            conf.BRIEF: dedent(f"""
                #### Risky code - has mix of different data types
                `{name}` contains more than one data type -
                which is probably a bad idea.
            """),
            conf.MAIN: dedent(f"""
                #### Risky code - has mix of different data types
                `{name}` contains more than one data type -
                which is probably a bad idea. The data types found were:
                {", ".join(item_types)}.
            """),
        }
        return message

# To add more advice, just declare more advisor functions with the @advisor decorator!
