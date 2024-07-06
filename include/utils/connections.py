import json

from airflow import settings
from airflow.models import Connection

from include.utils.settings import GCP_CONN_ID, GCP_KEYFILE, GCP_PROJECT


def add_gcp_connection():
    """Create the Airflow GCP connection, or point the existing one at the current key file."""
    extra_field = {
        "extra__google_cloud_platform__project": GCP_PROJECT,
        "extra__google_cloud_platform__key_path": GCP_KEYFILE,
    }

    session = settings.Session()
    conn = session.query(Connection).filter(Connection.conn_id == GCP_CONN_ID).one_or_none()
    if conn is None:
        conn = Connection(conn_id=GCP_CONN_ID, conn_type='google_cloud_platform')
    conn.set_extra(json.dumps(extra_field))
    session.add(conn)
    session.commit()
