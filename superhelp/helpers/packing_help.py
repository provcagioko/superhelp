from collections import defaultdict

from superhelp.helpers import (
    get_unpacking_msg, all_blocks_help, filt_block_help)
from superhelp import ast_funcs, conf, gen_utils
from superhelp.gen_utils import layout_comment as layout
from superhelp.utils import inspect_el  # @UnusedImport

ASSIGN_UNPACKING_XPATH = 'descendant-or-self::Assign/targets/Tuple'

@filt_block_help(xpath=ASSIGN_UNPACKING_XPATH)
def unpacking(block_dets, *, repeat=False, **_kwargs):
    """
    Identify name unpacking e.g. x, y = coord
    """
    unpacked_els = block_dets.element.xpath(ASSIGN_UNPACKING_XPATH)
    if not unpacked_els:
        return None

    title = layout("""\
    ### Name unpacking
    """)
    summary_bits = []
    for unpacked_el in unpacked_els:
        unpacked_names = [
            name_el.get('id') for name_el in unpacked_el.xpath('elts/Name')]
        if not unpacked_names:
            continue
        nice_str_list = gen_utils.get_nice_str_list(unpacked_names, quoter='`')
        summary_bits.append(layout(f"""\

        Your code uses unpacking to assign names {nice_str_list}
        """))
    summary = ''.join(summary_bits)
    if not repeat:
        unpacking_msg = get_unpacking_msg()
    else:
        unpacking_msg = ''

    message = {
        conf.Level.BRIEF: title + summary,
        conf.Level.EXTRA: unpacking_msg,
    }
    return message

@all_blocks_help()
def unpacking_opportunity(blocks_dets, *, repeat=False, **_kwargs):
    """
    Look for opportunities to unpack values into multiple names instead of
    repeated and un-pythonic extraction using indexes.

    Signs of an unpacking opportunity - something is repeatedly sliced with
    different slice numbers e.g.

    x, y = coord
    vs
    x = coord[0]
    y = coord[1]
    """
    source_slices = defaultdict(set)
    for block_dets in blocks_dets:
        assign_els = block_dets.element.xpath('descendant-or-self::Assign')
        for assign_el in assign_els:
            # inspect_el(assign_el)
            try:
                slice_source = assign_el.xpath(
                    'value/Subscript/value/Name')[0].get('id')
                slice_n = ast_funcs.get_slice_n(assign_el)
            except (IndexError, TypeError):
                continue
            else:
                source_slices[slice_source].add(slice_n)
    sources2unpack = [source
        for source, slice_ns in source_slices.items()
        if len(slice_ns) > 1]
    if not sources2unpack:
        return None

    title = layout("""\
    ### Unpacking opportunity
    """)
    multiple_items = len(sources2unpack) > 1
    if multiple_items:
        nice_sources_list = gen_utils.get_nice_str_list(
            sources2unpack, quoter='`')
        unpackable = layout(f"""\

        {nice_sources_list} have multiple items extracted by indexing so might
        be suitable candidates for unpacking.
        """)
    else:
        unpackable = layout(f"""\

        Name (variable) `{sources2unpack[0]}` has multiple items extracted by
        indexing so might be a suitable candidate for unpacking.
        """)
    if not repeat:
        extra_msg = get_unpacking_msg()
    else:
        extra_msg = ''

    message = {
        conf.Level.BRIEF: title + unpackable,
        conf.Level.EXTRA: extra_msg,
    }
    return message
