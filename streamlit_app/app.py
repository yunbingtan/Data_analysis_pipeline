import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
import dotenv

dotenv.load_dotenv()  # Load .env file for local development

st.set_page_config(page_title="dbt Postgres Explorer", layout="wide")

def get_db_settings():
    return {
        "host": os.getenv("_DBT_DB_HOST"),
        "port": os.getenv("_DBT_DB_PORT"),
        "user": os.getenv("_DBT_DB_USERNAME"),
        "password": os.getenv("_DBT_DB_PASSWORD"),
        "database": os.getenv("_DBT_DB_NAME"),
    }

@st.cache_resource
def get_engine():
    settings = get_db_settings()
    conn_str = (
        f"postgresql+psycopg://{settings['user']}:{settings['password']}"
        f"@{settings['host']}:{settings['port']}/{settings['database']}"
    )
    return create_engine(conn_str)

def load_schemas():
    query = text(
        """
        select distinct table_schema
        from information_schema.tables
        where table_schema not in ('pg_catalog', 'information_schema')
        order by table_schema
        """
    )
    with get_engine().connect() as conn:
        rows = conn.execute(query).fetchall()
    return [row.table_schema for row in rows]

def load_tables(selected_schema):
    query = text(
        f"""
        select table_schema, table_name
        from information_schema.tables
        where table_schema = '{selected_schema}'
        order by table_schema, table_name
        """
    )
    with get_engine().connect() as conn:
        rows = conn.execute(query).fetchall()
    return [f"{row.table_name}" for row in rows]


def load_preview(schema_name, table_name, limit):
    query = text(
        f'SELECT * FROM "{schema_name}"."{table_name}" LIMIT :limit'
    )
    with get_engine().connect() as conn:
        return pd.read_sql(query, conn, params={"limit": limit})


def run_custom_query(sql):
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn)


st.title("dbt Postgres Explorer")
st.caption("Connects to the `dbt-postgres` service using credentials from `.env`.")

settings = get_db_settings()

with st.sidebar:
    st.subheader("Connection")
    st.write(f"Host: `{settings['host']}`")
    st.write(f"Port: `{settings['port']}`")
    st.write(f"Database: `{settings['database']}`")
    st.write(f"User: `{settings['user']}`")

try:
    with get_engine().connect() as conn:
        conn.execute(text("SELECT 1"))
    st.success("Connected to dbt-postgres.")
except Exception as exc:
    st.error("Could not connect to dbt-postgres.")
    st.exception(exc)
    st.stop()

schemas = load_schemas()
selected_schema = st.selectbox("Choose a schema", schemas)

try:
    tables = load_tables(selected_schema)
except Exception as exc:
    st.error("Failed to load tables for the selected schema.")
    st.exception(exc)
    st.stop()

if not tables:
    st.info("No user tables found yet. Run your dbt seeds or models first.")
    st.stop()

selected_table = st.selectbox("Choose a table", tables)
row_limit = st.slider("Preview row limit", min_value=5, max_value=200, value=25, step=5)

st.subheader("Table preview")
preview_df = load_preview(selected_schema, selected_table, row_limit)
st.dataframe(preview_df, use_container_width=True)

st.subheader("Data visualization")
numeric_columns = preview_df.select_dtypes(include="number").columns.tolist()
x_axis = st.selectbox("Choose x-axis column", preview_df.columns, index=0)

if not numeric_columns:
    st.info("This preview has no numeric columns available for charting.")
else:
    y_axis = st.multiselect("Choose y-axis column", numeric_columns, default=numeric_columns[:1])
    if st.button("Visualize preview data"):
        if preview_df.empty:
            st.warning("No data to visualize.")
        else:
            st.bar_chart(preview_df, x=x_axis, y=y_axis)

st.subheader("Custom SQL")
default_sql = f"SELECT * FROM {selected_table} LIMIT 50"
sql = st.text_area("Run a read-only query", value=default_sql, height=140)
if st.button("Run query"):
    try:
        result_df = run_custom_query(sql)
        st.dataframe(result_df, use_container_width=True)
    except Exception as exc:
        st.error("Query failed.")
        st.exception(exc)
