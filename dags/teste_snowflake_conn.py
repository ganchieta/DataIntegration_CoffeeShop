from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from datetime import datetime

# Função com tratamento de erro
def test_conn():
    try:
        print("🔌 Tentando criar conexão com Snowflake...")
        hook = SnowflakeHook(snowflake_conn_id='snowflake_default')

        conn = hook.get_conn()
        if conn is None:
            print("❌ hook.get_conn() retornou None")
            raise Exception("Falha ao obter conexão")

        print("✅ Conexão criada. Tentando abrir cursor...")
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_TIMESTAMP;")
        result = cursor.fetchone()
        print(f"✅ Consulta executada! Timestamp: {result[0]}")

    except Exception as e:
        print(f"❌ Erro ao conectar/executar no Snowflake: {str(e)}")
        raise e

# Definição do DAG
with DAG(
    dag_id='test_snowflake_conn_debug',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['snowflake', 'debug'],
) as dag:

    test = PythonOperator(
        task_id='test_connection',
        python_callable=test_conn
    )

    test
