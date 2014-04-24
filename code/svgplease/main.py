from . import command, parse
import glob
def run(program_name, arguments):
    """Parses the arguments and runs the commands"""
    if len(arguments) > 0 and arguments[0] == "--complete":
        completions = parse.complete(*arguments[2:])
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
