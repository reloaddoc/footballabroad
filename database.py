import duckdb

DB_PATH = "data/kickways.duckdb"


def read_table(table_name):
    con = duckdb.connect(DB_PATH)
    df = con.sql(f"SELECT * FROM {table_name}").df()
    con.close()
    return df


def write_table(table_name, dataframe):
    con = duckdb.connect(DB_PATH)
    dataframe_to_write = dataframe.copy()
    for column in dataframe_to_write.select_dtypes(include=["category"]).columns:
        dataframe_to_write[column] = dataframe_to_write[column].astype("object")

    con.register("dataframe_to_write", dataframe_to_write)
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM dataframe_to_write")
    con.unregister("dataframe_to_write")
    con.close()
