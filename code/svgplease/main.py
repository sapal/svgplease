from . import command, parse
import sys
import glob

def expand(*arguments):
    """Remove qutes around each argument and backslashes before # and %."""
    def strip_quotes(argument):
        return argument.strip("'\"")
    def remove_backslashes(argument):
        return argument.replace("\\#", "#").replace("\\%", "%")
    return [remove_backslashes(strip_quotes(argument)) for argument in arguments]


def run(program_name, arguments):
    """Parses the arguments and runs the commands"""
    if len(arguments) == 0 or arguments[0] in ("-h", "--help"):
        print("Usage: {} command list\nSee the man page for details.".format(program_name))
        sys.exit(1)
    if len(arguments) > 0 and arguments[0] == "--complete":
        completions = parse.complete(*expand(*arguments[1:]))
        for key, value in sorted(completions.items()):
            if key == "file":
                value = glob.glob("*.svg")
            for item in value:
                print(item)
    else:
        command_list = parse.CommandList.parser().parse_text(
                parse.join_tokens(arguments), eof=True, matchtype="complete").command_list
        execution_context = command.ExecutionContext()
        for command_to_execute in command_list:
            command_to_execute.execute(execution_context)
