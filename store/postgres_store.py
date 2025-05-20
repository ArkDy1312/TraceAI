import os
import psycopg2
import psycopg2.sql as sql

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT", 5432)
)

def insert_feature(workspace_id, feature_id, title, description, author, commit_ID=None, test_name=None):
    # Sanitize and construct table name
    table_name = f"features"

    with conn.cursor() as cur:
        # Create table if not exists (dynamic table name)
        cur.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {} (
                team TEXT NOT NULL,
                feature_id TEXT NOT NULL,
                title TEXT,
                description TEXT,
                author TEXT,
                commit_ID TEXT,
                commit_status TEXT,
                test_name TEXT,
                test_status TEXT
            );
        """).format(sql.Identifier(table_name)))

        # Create unique index (only once)
        cur.execute(sql.SQL("""
            CREATE UNIQUE INDEX IF NOT EXISTS unique_feature_commit_test
            ON features(team, feature_id, commit_ID, test_name);
        """))

        # Insert or update
        cur.execute(sql.SQL("""
            INSERT INTO {} (team, feature_id, title, description, author, commit_ID, commit_status, test_name, test_status)
            VALUES (%s, %s, %s, %s, %s, %s, 'Pending', %s, 'Pending')
        """).format(sql.Identifier(table_name)), (workspace_id, feature_id, title, description, author, commit_ID, test_name))

        conn.commit()

def update_commit_status(workspace_id, feature_id, commit_ID, status="Done", delete=False):
    table_name = "features"
    if delete:
        commit_ID_update = None
    else:
        commit_ID_update = commit_ID

    with conn.cursor() as cur:
        # First check if the row exists
        cur.execute(sql.SQL("""
            SELECT 1 FROM {}
            WHERE team = %s AND feature_id = %s AND commit_ID = %s;
        """).format(sql.Identifier(table_name)), (workspace_id, feature_id, commit_ID))

        exists = cur.fetchone() is not None

        if exists:
            # Update existing row
            cur.execute(sql.SQL("""
                UPDATE {}
                SET commit_ID = %s,
                commit_status = %s,
                test_name = NULL,
                test_status = 'Pending'
                WHERE team = %s AND feature_id = %s AND commit_ID = %s;
            """).format(sql.Identifier(table_name)), (commit_ID_update, status, workspace_id, feature_id, commit_ID))
        else:
            # Insert row
            cur.execute(sql.SQL("""
                INSERT INTO {} (
                    team, feature_id, title, description, author,
                    commit_ID, commit_status, test_name, test_status
                )
                SELECT
                    team, feature_id, title, description, author,
                    %s, %s, %s, %s
                FROM {}
                WHERE team = %s AND feature_id = %s
                LIMIT 1;
            """).format(
                sql.Identifier(table_name),
                sql.Identifier(table_name)
            ), (
                commit_ID, status, None, 'Pending',
                workspace_id, feature_id
            ))

        conn.commit()

def update_test_status(workspace_id, feature_id, commit_ID, test_name, status="Done", delete=False):
    table_name = "features"
    if delete:
        test_name_update = None
    else:
        test_name_update = test_name

    with conn.cursor() as cur:
        # Case 1: Exact test_name match
        cur.execute(sql.SQL("""
            SELECT 1 FROM {}
            WHERE team = %s AND feature_id = %s AND commit_ID = %s 
              AND commit_status = 'Done' AND test_name = %s;
        """).format(sql.Identifier(table_name)), (workspace_id, feature_id, commit_ID, test_name))

        if cur.fetchone():
            # Update only test_status
            cur.execute(sql.SQL("""
                UPDATE {} 
                SET test_name = %s, test_status = %s
                WHERE team = %s AND feature_id = %s AND commit_ID = %s AND test_name = %s;
            """).format(sql.Identifier(table_name)), (test_name_update, status, workspace_id, feature_id, commit_ID, test_name))

        else:
            # Case 2: test_name = NULL
            cur.execute(sql.SQL("""
                SELECT 1 FROM {}
                WHERE team = %s AND feature_id = %s AND commit_ID = %s 
                  AND commit_status = 'Done' AND test_name IS NULL;
            """).format(sql.Identifier(table_name)), (workspace_id, feature_id, commit_ID))

            if cur.fetchone():
                # Update test_name and test_status
                cur.execute(sql.SQL("""
                    UPDATE {} 
                    SET test_name = %s, test_status = %s
                    WHERE team = %s AND feature_id = %s AND commit_ID = %s AND test_name IS NULL;
                """).format(sql.Identifier(table_name)), (test_name, status, workspace_id, feature_id, commit_ID))
            else:
                # Case 3: No matching row at all — insert new one
                cur.execute(sql.SQL("""
                    INSERT INTO {} (
                        team, feature_id, title, description, author,
                        commit_ID, commit_status, test_name, test_status
                    )
                    SELECT team, feature_id, title, description, author,
                        %s, 'Done', %s, %s
                    FROM {}
                    WHERE team = %s AND feature_id = %s
                    LIMIT 1;
                """).format(sql.Identifier(table_name), sql.Identifier(table_name)),
                (commit_ID, test_name, status, workspace_id, feature_id))

        conn.commit()

def feature_status(workspace_id, feature_id, require_commit_done=False, commit_ID=None):
    table_name = "features"
    print(f"Checking feature status in table: {table_name}", flush=True)

    with conn.cursor() as cur:
        if require_commit_done:
            # QA: check feature exists AND commit_status = 'Done'
            cur.execute(sql.SQL("""
                SELECT EXISTS (
                    SELECT 1 FROM {} 
                    WHERE team = %s AND feature_id = %s AND commit_ID = %s AND commit_status = 'Done'
                );
            """).format(sql.Identifier(table_name)), (workspace_id, feature_id, commit_ID))
        else:
            # Dev: check feature exists
            cur.execute(sql.SQL("""
                SELECT EXISTS (
                    SELECT 1 FROM {} 
                    WHERE team = %s AND feature_id = %s
                );
            """).format(sql.Identifier(table_name)), (workspace_id, feature_id))

        result = cur.fetchone()[0]
        return result
    
# Get "feature_id - title" pairs from the db
def get_feature_id_title_pairs(workspace):
    try:
        table_name = "features"
        with conn.cursor() as cur:
            query = sql.SQL("""
                SELECT DISTINCT ON (feature_id) feature_id, title
                FROM {}
                WHERE team = %s
                ORDER BY feature_id, title;
            """).format(sql.Identifier(table_name))
            
            cur.execute(query, (workspace,))
            return [f"{title} - {fid}" for fid, title in cur.fetchall()]
    except Exception as e:
        conn.rollback()
        return [f"No features found! ({str(e)})"]
    
def get_commits_for_feature(workspace, feature_id):
    table_name = "features"
    if feature_id is not None:
        feature_id = feature_id.split(" - ")[1]

    with conn.cursor() as cur:
        cur.execute(sql.SQL("""
            SELECT DISTINCT commit_ID
            FROM {}
            WHERE team = %s AND feature_id = %s AND commit_ID IS NOT NULL;
        """).format(sql.Identifier(table_name)), (workspace, feature_id))

        results = cur.fetchall()
        return [row[0] for row in results]

def get_tests_for_feature(workspace, feature_id):
    table_name = "features"
    if feature_id is not None:
        feature_id = feature_id.split(" - ")[1]

    with conn.cursor() as cur:
        cur.execute(sql.SQL("""
            SELECT DISTINCT test_name
            FROM {}
            WHERE team = %s AND feature_id = %s AND test_name IS NOT NULL;
        """).format(sql.Identifier(table_name)), (workspace, feature_id))

        results = cur.fetchall()
        return [row[0] for row in results]
    
def get_commits_for_single_feature(workspace, feature_id, test_name):
    table_name = "features"
    if feature_id is not None:
        feature_id = feature_id.split(" - ")[1]
    with conn.cursor() as cur:
        cur.execute(sql.SQL("""
            SELECT DISTINCT commit_ID
            FROM {}
            WHERE team = %s AND feature_id = %s AND commit_ID IS NOT NULL AND test_name = %s;
        """).format(sql.Identifier(table_name)), (workspace, feature_id, test_name))

        results = cur.fetchall()
        return [row[0] for row in results][0]
    
def get_graph_data(workspace, feature):
    table_name = "features"
    if feature is not None:
        feature_id = feature.split(" - ")[1]
    with conn.cursor() as cur:
        cur.execute(sql.SQL("""
            SELECT feature_id, title, description, commit_ID, commit_status, test_name, test_status
            FROM {}
            WHERE team = %s AND feature_id = %s;
        """).format(sql.Identifier(table_name)), (workspace, feature_id))

        results = cur.fetchall()
        return results