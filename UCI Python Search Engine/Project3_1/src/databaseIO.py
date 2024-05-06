import psycopg
import logging

logger = logging.getLogger(__name__)
class DatabaseIO:
    def __init__(self, connection_str: str):
        self.connection_str = connection_str
        # Initialize the connection
        self.connection = psycopg.connect(self.connection_str)

    def create_table(self):
        # Check that table inverted_index exist
        # If not, create it
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
            create table if not exists public.inverted_index
            (
                token           character varying(200) primary key not null,
                doc_ids         character varying[],
                frequency_array integer[],
                tfidf_array     double precision[],
                tags_array      jsonb 
            );
            """
            )
            # Commit the changes
            self.connection.commit()

    def execute_query(self, query: str, **kwargs) -> None:
        """
        :param query: The query string
        :param kwargs: The parameters for the query
        :return: The result of the query 
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, kwargs)
        except Exception as e:
            print(kwargs['tags'])
            self.connection.rollback()
            raise e
        else:
            # Determine if the query is a select query
            if cursor.description is not None:
                # If it is, return the result
                return cursor.fetchall()
            else:
                # Otherwise, commit the changes and return None
                self.connection.commit()
                return None

    def execute_many(self, query: str, params: list[dict], *args) -> None:
        """
        :param query: The query string
        :param params: The parameters for the query
        :param args: The start and end index of the chunk 
        :return None
        """
        cursor = self.connection.cursor()
        try:
            cursor.executemany(query, params)
        except Exception as e:
            self.connection.rollback()
            raise e
        else:
            logger.info(f"Executing query for chunks {args[0]} to {args[1]}")
            self.connection.commit()


    def close(self) -> None:
        """
        :return: None
        """
        self.connection.close()
