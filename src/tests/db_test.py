import os

from src.const import DB_PATH
from src.database import create_db, setup_db


def test_setup_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    cur = create_db(DB_PATH)
    assert cur.rowcount == -1

    setup_db(cur)
