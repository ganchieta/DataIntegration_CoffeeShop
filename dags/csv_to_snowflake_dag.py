from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

from datetime import datetime
import os
import pandas as pd
from sqlalchemy.types import Integer, Float, String

CSV_FOLDER_PATH = "/opt/airflow/aux_files"
TABLE_NAME = "LANDING_COFFEE_SHOP"
SNOWFLAKE_CONN_ID = "snowflake_default"

col_types = {
    "transaction_id": Integer(),
    "transaction_date": String(),
    "transaction_time": String(),
    "store_id": Integer(),
    "store_location": String(),
    "product_id": Integer(),
    "transaction_qty": Integer(),
    "unit_price": Float(),
    "product_category": String(),
    "product_type": String(),
    "product_detail": String(),
    "Size": String(),
    "Total_bill": Float(),
    "Month Name": String(),
    "Day Name": String(),
    "Hour": Integer(),
    "Day of Week": Integer(),
    "Month": Integer()
}

def upload_csvs_to_snowflake():
    print(f"📁 Lendo arquivos de: {CSV_FOLDER_PATH}")
    csv_files = [f for f in os.listdir(CSV_FOLDER_PATH) if f.endswith(".csv")]

    if not csv_files:
        raise FileNotFoundError("Nenhum arquivo CSV encontrado.")

    hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    engine = hook.get_sqlalchemy_engine()

    for idx, file_name in enumerate(csv_files):
        file_path = os.path.join(CSV_FOLDER_PATH, file_name)
        print(f"🔍 Lendo: {file_path}")

        try:
            df = pd.read_csv(file_path, sep=";")
        except Exception as e:
            print(f"❌ Falha ao ler CSV '{file_name}': {e}")
            raise

        print(f"📊 Linhas: {len(df)}")
        print(f"🧾 Colunas: {df.columns.tolist()}")
        print(f"🔎 Tipos das colunas:\n{df.dtypes}")

        if idx == 0:
            print(f"🧱 Criando tabela '{TABLE_NAME}' (substituindo caso exista)...")
            try:
                df.to_sql(
                    TABLE_NAME,
                    engine,
                    index=False,
                    if_exists="replace",
                    method="multi",
                    dtype=col_types
                )
            except Exception as e:
                print(f"❌ Falha ao criar tabela: {e}")
                raise

        print(f"⬆️ Enviando dados de '{file_name}' para Snowflake...")
        try:
            df.to_sql(
                TABLE_NAME,
                engine,
                index=False,
                if_exists="append",
                method="multi"
            )
        except Exception as e:
            print(f"❌ Falha ao inserir dados: {e}")
            raise

    print(f"✅ Todos os arquivos foram processados e carregados para '{TABLE_NAME}'.")

with DAG(
    dag_id="csv_to_snowflake_landing",
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["csv", "snowflake", "landing"],
) as dag:

    upload_task = PythonOperator(
        task_id="upload_csvs_to_landing",
        python_callable=upload_csvs_to_snowflake,
    )

    upload_task
