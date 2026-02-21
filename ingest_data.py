import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click
import os

# Correct dtype model for taxi_zone_lookup
dtype_lookup = {
    "LocationID": "Int64",
    "Borough": "string",
    "Zone": "string",
    "service_zone": "string"
}

@click.command()
@click.option('--pg_user', default='root', help='PostgreSQL user')
@click.option('--pg_password', default='root', help='PostgreSQL password')
@click.option('--pg_host', default='localhost', help='PostgreSQL host')
@click.option('--pg_port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg_db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--target_table', default='taxi_zone_lookup', help='Target table name')
@click.option('--chunksize', default=50000, type=int, help='Chunk size for processing')
@click.option(
    '--csv_path',
    default='https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv',
    help='Path or URL of the CSV file'
)
def run(pg_user, pg_password, pg_host, pg_port, pg_db,
        target_table, chunksize, csv_path):

    # Only check existence if it's a local file
    if not (csv_path.startswith("http://") or csv_path.startswith("https://")):
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

    print(f"📥 Reading from: {csv_path}")

    engine = create_engine(
        f'postgresql+psycopg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}'
    )

    # Read in chunks from URL or local path
    df_iter = pd.read_csv(
        csv_path,
        dtype=dtype_lookup,
        iterator=True,
        chunksize=chunksize
    )

    first = True
    for df_chunk in tqdm(df_iter, desc="Ingesting"):
        if first:
            df_chunk.head(0).to_sql(
                name=target_table,
                con=engine,
                if_exists='replace'
            )
            first = False

        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists='append'
        )

    print(f"✅ SUCCESS — Loaded data into '{target_table}'")


if __name__ == '__main__':
    run()