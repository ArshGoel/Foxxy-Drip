import psycopg2
from psycopg2 import sql

# ---------------- CONFIG ----------------
SOURCE_DB = {
    "dbname": "FoxxyDrip",
    "user": "avnadmin",
    "password": "AVNS_ZBxpNZDSgH38UEicwgp",
    "host": "url-shortner-arshgoel16-ba75.e.aivencloud.com",
    "port": "12743",
}

DEST_DB = {
    "dbname": "FoxxyDrip1",
    "user": "avnadmin",
    "password": "AVNS_ZBxpNZDSgH38UEicwgp",
    "host": "url-shortner-arshgoel16-ba75.e.aivencloud.com",
    "port": "12743",
}

SOURCE_TABLE = "Services_productdesign"
DEST_TABLE = "Services_productdesign"  # target table name

# ---------------------------------------

def copy_table():
    try:
        # Connect to source and destination (can be same DB)
        src_conn = psycopg2.connect(**SOURCE_DB, sslmode="require")
        dest_conn = psycopg2.connect(**DEST_DB, sslmode="require")

        src_cursor = src_conn.cursor()
        dest_cursor = dest_conn.cursor()

        print(f"Copying data from {SOURCE_TABLE} to {DEST_TABLE}...")

        # 1️⃣ Get all rows from source
        src_cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(SOURCE_TABLE)))
        rows = src_cursor.fetchall()

        # 2️⃣ Get column names
        colnames = [desc[0] for desc in src_cursor.description]

        # 3️⃣ Create destination table if it doesn't exist
        src_cursor.execute(sql.SQL(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name=%s)"
        ), [DEST_TABLE.lower()])
        if not src_cursor.fetchone()[0]:
            # Copy schema from source
            src_cursor.execute(sql.SQL("CREATE TABLE {} (LIKE {} INCLUDING ALL)").format(
                sql.Identifier(DEST_TABLE),
                sql.Identifier(SOURCE_TABLE)
            ))
            print(f"Destination table '{DEST_TABLE}' created.")

        # 4️⃣ Insert all rows into destination
        for row in rows:
            insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(DEST_TABLE),
                sql.SQL(', ').join(map(sql.Identifier, colnames)),
                sql.SQL(', ').join(sql.Placeholder() * len(colnames))
            )
            dest_cursor.execute(insert_query, row)

        dest_conn.commit()
        print(f"Successfully copied {len(rows)} rows!")

        # Close connections
        src_cursor.close()
        dest_cursor.close()
        src_conn.close()
        dest_conn.close()

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    copy_table()
