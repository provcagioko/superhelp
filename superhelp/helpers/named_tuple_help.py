from collections import namedtuple

from ..helpers import all_blocks_help
from .. import ast_funcs, conf
from ..gen_utils import layout_comment as layout

NTDets = namedtuple('NamedTupleDetails', 'name, label, fields_str, fields_list')

def get_named_tuple_dets(named_tuple_el):
    """
    Get name, label, fields.
    """
    assign_block_el = named_tuple_el.xpath('ancestor-or-self::Assign')[-1]
    name = assign_block_el.xpath('targets/Name')[0].get('id')
    label, fields_list = ast_funcs.get_nt_lbl_flds(assign_block_el)
    fields_str = ', '.join(fields_list)
    named_tuple_dets = NTDets(name, label, fields_str, fields_list)
    return named_tuple_dets

def get_named_tuples_dets(blocks_dets):
    all_named_tuples_dets = []
    for block_dets in blocks_dets:
        func_name_els = block_dets.element.xpath(
            'descendant-or-self::value/Call/func/Name')
        if not func_name_els:
            continue
        named_tuple_els = [func_name_el for func_name_el in func_name_els
            if func_name_el.get('id') == 'namedtuple']
        named_tuples_dets = [
            get_named_tuple_dets(named_tuple_el)
            for named_tuple_el in named_tuple_els]
        all_named_tuples_dets.extend(named_tuples_dets)
    return all_named_tuples_dets

@all_blocks_help()
def named_tuple_overview(blocks_dets, *, repeat=False, **_kwargs):
    """
    Look for named tuples and explain how they can be enhanced.
    """
    named_tuples_dets = get_named_tuples_dets(blocks_dets)
    if not named_tuples_dets:
        return None
    if repeat:
        return None

    example_dets = named_tuples_dets[0]
    first_field = example_dets.fields_list[0]
    enhancement = (
            layout("""\
            ### Named Tuple Enhancements

            Named tuples can be enhanced to make them even more useful -
            especially when debugging. The label can be expanded beyond the
            variable name; and the entire named tuple or individual fields can
            be given their own doc strings.

            For example:
            """)
            +
            layout(f"""\
            {example_dets.name} = namedtuple("{example_dets.label}",
                "{example_dets.fields_str}")
            {example_dets.name}.__doc__ += "\\n\\nExtra comments"
            {example_dets.name}.{first_field}.__doc__ = "Specific comment for {first_field}"
            ## etc
            """, is_code=True)
        )
    defaults = (
        layout("""\

        Default arguments are another nice option (added in Python 3.7). For
        example the following named tuple has a default IQ of 100:
        """)
        +
        layout("""\
        People = namedtuple('PeopleDets', 'name, IQ', defaults=(100, ))
        """, is_code=True)
        +
        layout("""\
        The official documentation has more details.
        """)
    )

    message = {
        conf.Level.BRIEF: enhancement,
        conf.Level.MAIN: enhancement + defaults,
    }
    return message
    