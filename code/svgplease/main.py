from . import command, parse
def run(program_name, arguments):
    """Parses the arguments and runs the commands"""
    command_list = parse.CommandList.parser().parse_text(
            parse.join_tokens(arguments), eof=True).command_list
    execution_context = command.ExecutionContext()
    for command_to_execute in command_list:
        command_to_execute.execute(execution_context)
