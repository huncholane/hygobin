import click
from .codegen import Codegen
from pathlib import Path


@click.command()
@click.argument("prompt")
def cli(prompt):
    codegen = Codegen()
    codegen.load_session_data(str(Path.cwd()))
    if codegen.is_new_session_data:
        codegen.init_session()
