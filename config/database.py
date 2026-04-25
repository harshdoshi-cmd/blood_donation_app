import streamlit as st
import psycopg2
import pandas as pd
from sqlalchemy import create_engine

# Use the 'Pooled connection' string from Neon (the one with '-pooler')
# This is stored in Streamlit Cloud Secrets

DB_URL = st.secrets["connections"]["neon"]["url"]

try:
    DB_URL = st.secrets["connections"]["neon"]["url"]
except Exception as e:
    st.error(f"Secret Access Error: {e}")
    st.write("Available Secret Keys:", st.secrets.to_dict().keys())

def get_connection():
    """Returns a PEP 249 connection object."""
    try:
        return psycopg2.connect(DB_URL)
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

def get_engine():
    """Returns a SQLAlchemy engine for pandas integration."""
    # Append sslmode if not present (Neon requires SSL)
    url = DB_URL
    if "sslmode" not in url:
        url += "?sslmode=require"
    return create_engine(url)

st.write("### 🔍 Debugging Connection")
try:
    engine = get_engine()
    with engine.connect() as conn:
        # This lists all tables the app can actually see
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        st.write(f"✅ Connection Successful!")
        st.write(f"Tables found in DB: {tables}")
        
        if not tables:
            st.warning("⚠️ The database is connected, but it is EMPTY (no tables found).")
except Exception as e:
    st.error(f"❌ Connection Failed: {e}")
    
engine = get_engine()
st.write("Tables actually in DB:", pd.read_sql("SELECT table_name FROM information_schema.tables WHERE table_schema='public'", engine))

# DB_CONFIG = {
#     "host": "ep-noisy-rain-amuwipxs-pooler.c-5.us-east-1.aws.neon.tech",
#     "database": "neondb",
#     "user": "neondb_owner",
#     "password": "npg_PzJVteDQI0g3",
#     "port": "5432"
# }

# def get_connection():
#     try:
#         conn = psycopg2.connect(**DB_CONFIG)
#         return conn
#     except Exception as e:
#         st.error(f"Database Connection Error: {e}")
#         return None

# def get_engine():
#     url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
#     return create_engine(url)


def load_data():
    try:
        engine = get_engine()
        df = pd.read_sql("SELECT * FROM bd_master", engine)
        # obj_cols = df.select_dtypes(include=["object"]).columns
        # df[obj_cols] = df[obj_cols].fillna("").replace({"None": "", "nan": "", "NaN": "", "null": ""})
        obj_cols = df.select_dtypes(include=["object"]).columns
        df[obj_cols] = df[obj_cols].fillna("").replace({"None": "", "nan": "", "NaN": ""})

        num_cols = df.select_dtypes(include=["float64", "int64"]).columns
        if 'year' in df.columns:
            df['year'] = df['year'].replace(0, pd.NA).astype('Int64')
        df[num_cols] = df[num_cols].fillna(0)

        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def load_online_registration_2026_data():
    try:
        engine = get_engine()
        df = pd.read_sql("SELECT * FROM online_registration_2026", engine)
        # obj_cols = df.select_dtypes(include=["object"]).columns
        # df[obj_cols] = df[obj_cols].fillna("").replace({"None": "", "nan": "", "NaN": "", "null": ""})
        
        obj_cols = df.select_dtypes(include=["object"]).columns
        df[obj_cols] = df[obj_cols].fillna("").replace({"None": "", "nan": "", "NaN": ""})

        num_cols = df.select_dtypes(include=["float64", "int64"]).columns
        if 'year' in df.columns:
            df['year'] = df['year'].replace(0, pd.NA).astype('Int64')
        df[num_cols] = df[num_cols].fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def load_combined_data():
    try:
        df_master = load_data()
        df_online = load_online_registration_2026_data()

        if df_master.empty and df_online.empty:
            return pd.DataFrame()
        if df_master.empty:
            return df_online
        if df_online.empty:
            return df_master

        combined = pd.concat([df_master, df_online], ignore_index=True, join='outer')

        obj_cols = combined.select_dtypes(include=["object"]).columns
        combined[obj_cols] = combined[obj_cols].fillna("").replace({"None": "", "nan": "", "NaN": ""})

        # num_cols = combined.select_dtypes(include=["float64", "int64"]).columns
        # combined[num_cols] = combined[num_cols].fillna(0)
        
        num_cols = combined.select_dtypes(include=["float64", "int64"]).columns
        combined[num_cols] = combined[num_cols].fillna(0)
        if 'year' in combined.columns:
            combined['year'] = combined['year'].replace(0, pd.NA).astype('Int64')

        return combined
    except Exception as e:
        st.error(f"Error combining data: {e}")
        return pd.DataFrame()


def explorar_data():
    try:
        df_master = load_data()
        df_online = load_online_registration_2026_data()
        df_todays = load_2026_data()
        
        if df_master.empty and df_online.empty and df_todays.empty:
            return pd.DataFrame()
        if df_master.empty:
            return df_online
        if df_online.empty:
            return df_master
        if df_todays.empty:
            return df_todays

        combined = pd.concat([df_master, df_online, df_todays], ignore_index=True, join='outer')

        obj_cols = combined.select_dtypes(include=["object"]).columns
        combined[obj_cols] = combined[obj_cols].fillna("").replace({"None": "", "nan": "", "NaN": ""})

        num_cols = combined.select_dtypes(include=["float64", "int64"]).columns
        combined[num_cols] = combined[num_cols].fillna(0)

        return combined
    except Exception as e:
        st.error(f"Error combining data: {e}")
        return pd.DataFrame()


def load_2026_data():
    try:
        engine = get_engine()
        df = pd.read_sql("SELECT * FROM registration_2026", engine)
        # obj_cols = df.select_dtypes(include=["object"]).columns
        # df[obj_cols] = df[obj_cols].fillna("").replace({"None": "", "nan": "", "NaN": "", "null": ""})
        
        obj_cols = df.select_dtypes(include=["object"]).columns
        df[obj_cols] = df[obj_cols].fillna("").replace({"None": "", "nan": "", "NaN": ""})

        num_cols = df.select_dtypes(include=["float64", "int64"]).columns
        if 'year' in df.columns:
            df['year'] = df['year'].replace(0, pd.NA).astype('Int64')
        df[num_cols] = df[num_cols].fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()



def run_query(query, params=None):
    """Executes Write/Update/Delete operations."""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
            return True
        except Exception as e:
            st.error(f"Query Error: {e}")
            return False
        finally:
            conn.close()
    return False
