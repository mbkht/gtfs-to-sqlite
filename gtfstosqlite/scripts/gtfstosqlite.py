import click

from gtfstosqlite.database_builder import DatabaseBuilder


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path(exists=False))
def cli(input_file, output_file):
    builder = DatabaseBuilder()
    builder.create_database_from_gtfs(input_file, output_file)
    print("Database created successfully")
