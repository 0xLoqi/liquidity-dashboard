"""
One-time setup script to create the subscribers table in Supabase.
Run this once after setting up your Supabase project.

Usage:
  python setup_supabase.py --host db.xxx.supabase.co --password YOUR_PASSWORD
"""

import sys
import argparse

try:
    import psycopg2
except ImportError:
    print("Installing psycopg2-binary...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2

STATEMENTS = [
    # Create table
    """
    CREATE TABLE IF NOT EXISTS subscribers (
        id SERIAL PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        cadence TEXT NOT NULL DEFAULT 'daily',
        is_waitlist BOOLEAN NOT NULL DEFAULT FALSE,
        confirmed BOOLEAN NOT NULL DEFAULT FALSE,
        subscribed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    # Create index
    "CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email)",
]

SEED_DATA = """
INSERT INTO subscribers (email, cadence, confirmed, subscribed_at)
VALUES ('elijah.wbanks@gmail.com', 'daily', false, '2026-02-05T17:27:12')
ON CONFLICT (email) DO NOTHING
"""


def main():
    parser = argparse.ArgumentParser(description="Set up Supabase subscribers table")
    parser.add_argument("--host", required=True, help="Supabase DB host (e.g., db.xxx.supabase.co)")
    parser.add_argument("--password", required=True, help="Database password")
    parser.add_argument("--port", default="5432", help="Database port (default: 5432)")
    parser.add_argument("--user", default="postgres", help="Database user (default: postgres)")
    parser.add_argument("--dbname", default="postgres", help="Database name (default: postgres)")
    args = parser.parse_args()

    print("Connecting to Supabase...")
    conn = psycopg2.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        dbname=args.dbname
    )
    conn.autocommit = True
    cursor = conn.cursor()

    print("Creating subscribers table...")
    for i, statement in enumerate(STATEMENTS):
        try:
            cursor.execute(statement)
            print(f"  Step {i+1}/{len(STATEMENTS)} done")
        except Exception as e:
            print(f"  Step {i+1} error: {e}")

    print("Seeding existing subscriber...")
    cursor.execute(SEED_DATA)

    # Verify
    cursor.execute("SELECT COUNT(*) FROM subscribers")
    count = cursor.fetchone()[0]
    print(f"\nDone! Table has {count} subscriber(s).")

    cursor.close()
    conn.close()

    print("\nNext steps:")
    print("1. Get your Supabase URL and anon key from Settings -> API")
    print("2. Add SUPABASE_URL and SUPABASE_KEY to Render environment variables")
    print("3. Deploy!")


if __name__ == "__main__":
    main()
