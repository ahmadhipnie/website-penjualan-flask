from flask import g, current_app
import MySQLdb
from MySQLdb.cursors import DictCursor

def get_db():
    """
    Mendapatkan koneksi MySQL dari application context
    """
    if 'db' not in g:
        g.db = MySQLdb.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB'],
            cursorclass=DictCursor
        )
    return g.db
