import typer


app = typer.Typer()


@app.command()
def test():
    """Test command"""
    import os
    print('Current dir:', os.getcwd())
    print('Working dir:', os.path.dirname(os.path.realpath(__file__)))
    print('Works!')



def cli():
    app()
