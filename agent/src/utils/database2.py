
import psycopg2

class DatabaseConnector:
    def __init__(self, dbname='postgres', user='postgres', password='', host='localhost', port='5432'):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.conn.cursor()
            print("Database connection successful")
        except psycopg2.Error as e:
            print(f"Database connection error: {e}")
            raise

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("Database connection closed")

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Query execution error: {e}")
            raise

# if __name__ == "__main__":  # Corrected the if statement
#     db_connector = DatabaseConnector()
#     try:
#         db_connector.connect()
#         print("Connected to the database!")
#     except Exception as e:
#         print(f"Failed to connect: {e}")
#     finally:
#         db_connector.disconnect()