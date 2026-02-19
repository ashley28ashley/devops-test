import pytest

try:
    import psycopg2
except ImportError:
    psycopg2 = None

@pytest.mark.skipif(psycopg2 is None, reason="psycopg2 non installé")
def test_sql_connection():
    conn = psycopg2.connect("dbname=events user=postgres password=postgres")
    assert conn is not None