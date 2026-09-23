import duckdb
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "auto_analys.duckdb"

UPLOADS_DIR = DATA_DIR / "uploads"
REPORTS_DIR = DATA_DIR / "reports"



def get_connection():
    """
    DuckDB database-ə bağlantı yaradır.
    Lazım olan qovluqları avtomatik yaradır.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    return duckdb.connect(str(DB_PATH))


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_database():
    con = get_connection()

    # -----------------------------------------------------
    # USERS
    # -----------------------------------------------------

    con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username VARCHAR UNIQUE NOT NULL,
            password_hash VARCHAR NOT NULL,
            full_name VARCHAR,
            email VARCHAR,
            role VARCHAR DEFAULT 'user',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # UPLOADED FILES
    # -----------------------------------------------------

    con.execute("""
        CREATE TABLE IF NOT EXISTS uploaded_files (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            filename VARCHAR NOT NULL,
            file_path VARCHAR NOT NULL,
            file_type VARCHAR,
            file_size BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # ANALYSES
    # -----------------------------------------------------

    con.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            file_id INTEGER NOT NULL,
            analysis_type VARCHAR,
            status VARCHAR DEFAULT 'pending',
            row_count INTEGER,
            column_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # REPORTS
    # -----------------------------------------------------

    con.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            analysis_id INTEGER NOT NULL,
            filename VARCHAR NOT NULL,
            file_path VARCHAR NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.close()


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    init_database()

    print("Database uğurla yaradıldı.")
    print(f"Database: {DB_PATH}")