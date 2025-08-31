import psycopg2
from psycopg2 import sql

# ---------------- CONFIG ----------------
DB_NAME = "FoxxyDrip"
DB_USER = "avnadmin"
DB_PASSWORD = "AVNS_ZBxpNZDSgH38UEicwgp"
DB_HOST = "url-shortner-arshgoel16-ba75.e.aivencloud.com"
DB_PORT = "12743"
TABLE_NAME = "Services_productdesign"
COLUMN_NAME = "type"
# ---------------------------------------

def remove_column():
    try:
        # Connect to the Aiven PostgreSQL database with SSL
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            sslmode="require"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        print("Connected to database successfully!")

        # Print all rows from the table
        print(f"\nContents of '{TABLE_NAME}':")
        cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(TABLE_NAME)))
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]

        # Print table header
        print(" | ".join(colnames))
        print("-" * (len(colnames) * 15))

        # Print each row
        for row in rows:
            print(" | ".join(str(r) for r in row))

        # Check if the column exists
        cursor.execute(
            sql.SQL(
                "SELECT column_name FROM information_schema.columns WHERE table_name=%s AND column_name=%s"
            ),
            [TABLE_NAME.lower(), COLUMN_NAME.lower()]
        )
        if cursor.fetchone():
            # Drop the column safely
            drop_query = sql.SQL(
                "ALTER TABLE {table} DROP COLUMN {column} CASCADE"
            ).format(
                table=sql.Identifier(TABLE_NAME),
                column=sql.Identifier(COLUMN_NAME)
            )
            cursor.execute(drop_query)
            print(f"\nColumn '{COLUMN_NAME}' removed successfully from '{TABLE_NAME}'!")
        else:
            print(f"\nColumn '{COLUMN_NAME}' does not exist in '{TABLE_NAME}'.")

        cursor.close()
        conn.close()
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    remove_column()
