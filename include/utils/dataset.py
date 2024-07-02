from include.utils.connections import gcp_conn_id

from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryExecuteQueryOperator

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

def add_reference_tables():
    query = f"""
        CREATE OR REPLACE VIEW `{dataset_id}.blocks` AS
        SELECT *
        FROM `bigquery-public-data.crypto_ethereum.blocks`;

        CREATE OR REPLACE VIEW `{dataset_id}.transactions` AS
        SELECT *
        FROM `bigquery-public-data.crypto_ethereum.transactions`;

        CREATE OR REPLACE VIEW `{dataset_id}.logs` AS
        SELECT *
        FROM `bigquery-public-data.crypto_ethereum.logs`;

        CREATE OR REPLACE VIEW `{dataset_id}.traces` AS
        SELECT *
        FROM `bigquery-public-data.crypto_ethereum.traces`;
        
        CREATE OR REPLACE VIEW `{dataset_id}.tokens` AS
        SELECT *
        FROM `bigquery-public-data.crypto_ethereum.tokens`;

    """

    return BigQueryExecuteQueryOperator(
        task_id ='add_reference_tables',
        sql = query,
        use_legacy_sql = False,
        gcp_conn_id = 'gcp',
        trigger_rule='all_done',  
    )