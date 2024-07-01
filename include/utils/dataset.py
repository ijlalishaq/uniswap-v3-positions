from include.utils.connections import gcp_conn_id

from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator

project = 'your-gcp-project'
dataset_id = 'uniswap_v3_positions'

def add_dataset():
    return BigQueryCreateEmptyDatasetOperator(
        task_id = 'add_dataset',
        dataset_id = dataset_id,
        gcp_conn_id = gcp_conn_id,
        if_exists = 'skip',
        trigger_rule='all_done',
    )
