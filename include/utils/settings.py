import os

# Where the pipeline writes. Set GCP_PROJECT to your project; BQ_DATASET is optional.
GCP_PROJECT = os.environ.get('GCP_PROJECT', 'your-gcp-project')
BQ_DATASET = os.environ.get('BQ_DATASET', 'uniswap_v3_positions')

GCP_CONN_ID = 'gcp'
GCP_KEYFILE = '/usr/local/airflow/include/gcp/service_account.json'
