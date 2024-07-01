from datetime import datetime

from include.utils.connections import add_gcp_connection
from include.utils.dataset import add_dataset

from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

@dag(
    start_date=datetime(2024, 7, 1),
    schedule=None,
    catchup=False,
    tags=['uniswap_v3_positions'],
)

def uniswap_v3_positions():
    begin = EmptyOperator(task_id="begin")
    end = EmptyOperator(task_id="end", trigger_rule="none_failed")

    _add_gcp_connection = PythonOperator(
        task_id='add_gcp_connection',
        python_callable=add_gcp_connection,
        provide_context=True,
        trigger_rule='all_done',
    )

    _add_dataset = add_dataset()

    begin >> _add_gcp_connection >> _add_dataset >> end

uniswap_v3_positions()
