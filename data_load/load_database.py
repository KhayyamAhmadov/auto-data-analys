import pandas as pd
from sqlalchemy import create_engine, inspect, text
from urllib.parse import quote_plus


class DatabaseManager:

    def __init__(
        self,
        db_type,
        host=None,
        port=None,
        database=None,
        username=None,
        password=None,
        authentication="sql",
        service_name=None
    ):
        self.db_type = db_type.lower()
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.authentication = authentication
        self.service_name = service_name

        self.engine = None

    def connect(self):

        if self.db_type == "sql server":
            self._connect_sql_server()

        elif self.db_type == "mysql":
            self._connect_mysql()

        elif self.db_type == "postgresql":
            self._connect_postgresql()

        elif self.db_type == "oracle":
            self._connect_oracle()

        elif self.db_type == "sqlite":
            self._connect_sqlite()

        else:
            raise ValueError("Dəstəklənməyən database tipi")

        return self.engine

    def _connect_sql_server(self):

        if self.authentication == "windows":

            server = self.host

            if self.port:
                server = f"{server},{self.port}"

            connection_string = (
                f"mssql+pyodbc://@{server}/{self.database}"
                "?driver=ODBC+Driver+17+for+SQL+Server"
                "&trusted_connection=yes"
            )

        else:

            password = quote_plus(self.password)

            server = self.host

            if self.port:
                server = f"{server},{self.port}"

            connection_string = (
                f"mssql+pyodbc://"
                f"{self.username}:{password}"
                f"@{server}/{self.database}"
                "?driver=ODBC+Driver+17+for+SQL+Server"
            )

        self.engine = create_engine(connection_string)

    def _connect_mysql(self):

        password = quote_plus(self.password)

        connection_string = (
            f"mysql+pymysql://"
            f"{self.username}:{password}"
            f"@{self.host}:{self.port}"
            f"/{self.database}"
        )

        self.engine = create_engine(connection_string)

    def _connect_postgresql(self):

        password = quote_plus(self.password)

        connection_string = (
            f"postgresql+psycopg2://"
            f"{self.username}:{password}"
            f"@{self.host}:{self.port}"
            f"/{self.database}"
        )

        self.engine = create_engine(connection_string)

    def _connect_oracle(self):

        password = quote_plus(self.password)

        connection_string = (
            f"oracle+oracledb://"
            f"{self.username}:{password}"
            f"@{self.host}:{self.port}"
            f"/?service_name={self.service_name}"
        )

        self.engine = create_engine(connection_string)

    def _connect_sqlite(self):

        connection_string = f"sqlite:///{self.database}"

        self.engine = create_engine(connection_string)

    def test_connection(self):

        try:

            if self.engine is None:
                self.connect()

            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            return True, "Connection successful"

        except Exception as e:

            return False, str(e)

    def get_tables(self):

        if self.engine is None:
            self.connect()

        inspector = inspect(self.engine)

        return inspector.get_table_names()

    def get_data(self, query):

        if self.engine is None:
            self.connect()

        return pd.read_sql(query, self.engine)

    def _quote_identifier(self, name):
        """
        Db tipinə görə identifier-i düzgün dırnaqlayır.
        Bu, cədvəl/schema adlarını sorğuya təhlükəsiz əlavə etmək üçündür
        (dəyər deyil, identifier olduğu üçün parametrləşdirmə mümkün deyil).
        """
        if self.db_type == "sql server":
            return f"[{name}]"
        elif self.db_type == "mysql":
            return f"`{name}`"
        else:  # postgresql, oracle, sqlite
            return f'"{name}"'

    def get_table_data(self, table_name, schema=None):

        if self.engine is None:
            self.connect()

        table_q = self._quote_identifier(table_name)

        if schema:
            schema_q = self._quote_identifier(schema)
            query = f"SELECT * FROM {schema_q}.{table_q}"
        else:
            query = f"SELECT * FROM {table_q}"

        return pd.read_sql(query, self.engine)

    def close(self):

        if self.engine:
            self.engine.dispose()