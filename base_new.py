import psycopg2

conn = psycopg2.connect(database="postgres", user="postgres", password="38621964")

class Baseclass:

    def delete_tables(self, conn):
        with conn.cursor() as cur:
            cur.execute("""Drop table if exists profiles;""")
            conn.commit()

    def create_db(self, conn):
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS profiles(
            id serial primary key unique,
            event_id integer NOT NULL,
            user_search_id integer UNIQUE,
            name VARCHAR NOT NULL
            );
            """)
            conn.commit()

    def insert_profiles(self, conn, event_id, user_search_id, name):
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO profiles (event_id, user_search_id, name)
                VALUES (%s, %s, %s);
            """,
                        (event_id, user_search_id, name)
            )
            conn.commit()

    def delete_db(self, conn):
        with conn.cursor() as cur:
            cur.execute("""
            DELETE from profiles;
            """)
            conn.commit()

    def select_profiles(self, conn, event_id, user_search_id):
        with conn.cursor() as cur:
            cur.execute(f"""
            SELECT user_search_id, name FROM profiles
            WHERE event_id = {event_id} and user_search_id = {user_search_id}
            """, )
            list_profiles = cur.fetchone()
            return list_profiles


base = Baseclass()