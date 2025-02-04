"""
Note - plain MDV - works in some consoles where terminal output fails.

Lots in common with cli displayer but risks of DRYing probably outweigh benefits
at this stage.

Makes temp MD file and displays its content.
"""
from pathlib import Path
from textwrap import dedent

from superhelp import conf, gen_utils
from superhelp.conf import Level
from superhelp.gen_utils import layout_comment as layout

MDV_CODE_START = MDV_CODE_END = "```"

def get_message(message_dets, detail_level):
    message = dedent(message_dets.message[detail_level])
    if detail_level == Level.EXTRA:
        message = dedent(message_dets.message[Level.MAIN]) + message
    message = dedent(message)
    message = (message
        .replace(conf.PYTHON_CODE_START, '\n' + MDV_CODE_START)
        .replace('\n    ' + conf.PYTHON_CODE_END, MDV_CODE_END + '\n')
    )
    return message

def _need_snippet_displayed(overall_messages_dets, block_messages_dets, *,
        multi_block=False):
    """
    Don't need to see the code snippet displayed when it is already visible:
    * because there is only one block in snippet and there is a block message
      for it (which will display the block i.e. the entire snippet) UNLESS there
      is an overall message separating them
    Otherwise we need it displayed.
    """
    mono_block_snippet = not multi_block
    if mono_block_snippet and block_messages_dets and not overall_messages_dets:
        return False
    return True

def get_formatted_help(code: str, file_path: Path, messages_dets, *,
        detail_level: Level = Level.BRIEF,
        warnings_only=False, multi_block=False) -> str:
    """
    Show by code blocks.
    """
    if warnings_only:
        options_msg = conf.WARNINGS_ONLY_MSG
    else:
        options_msg = conf.ALL_HELP_SHOWING_MSG
    intro = gen_utils.get_intro(file_path, multi_block=multi_block)
    text = [
        layout(f"""\
            # SuperHELP - Help for Humans!

            {intro}

            Currently showing {detail_level} content as requested.
            {options_msg}.

            {conf.MISSING_ADVICE_MESSAGE}

                #################################################################

                #  Help by spreading the word about SuperHELP on social media.  #

                #                Twitter: {conf.TWITTER_HANDLE}. Thanks!              #

                #################################################################
            """
        ),
    ]
    overall_messages_dets, block_messages_dets = messages_dets
    display_snippet = _need_snippet_displayed(
        overall_messages_dets, block_messages_dets, multi_block=multi_block)
    if display_snippet:
        line_numbered_snippet = gen_utils.get_line_numbered_snippet(code)
        code_desc = gen_utils.get_code_desc(file_path)
        text.append(dedent(
            f"## {code_desc}"
            f"\n{MDV_CODE_START}\n"
            + line_numbered_snippet
            + f"\n{MDV_CODE_END}"))
    for message_dets in overall_messages_dets:
        message = get_message(message_dets, detail_level)
        text.append(message)
    block_messages_dets.sort(key=lambda nt: (nt.first_line_no, nt.warning))
    prev_line_no = None
    for message_dets in block_messages_dets:
        ## display code for line number (once ;-))
        line_no = message_dets.first_line_no
        new_block = (line_no != prev_line_no)
        if new_block:
            block_has_warning_header = False
            text.append(dedent(
                f'## Code block starting line {line_no:,}'
                f"\n{MDV_CODE_START}\n"
                + message_dets.code_str
                + f"\n{MDV_CODE_END}"))
            prev_line_no = line_no
        if message_dets.warning and not block_has_warning_header:
            text.append(layout("""\
                ### Questions / Warnings

                There may be some issues with this code block you want to
                address.
                """))
            block_has_warning_header = True
        ## process message
        message = get_message(message_dets, detail_level)
        text.append(message)
    formatted_help = '\n'.join(text)
    return formatted_help
