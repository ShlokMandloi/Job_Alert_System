import sqlite3
import os
# Establish a connection to the SQLite database
def create_connection():
    # Use the current working directory to set the path to the jobs.db file
    db_path = os.path.join(os.getcwd(), 'jobs.db')
    conn = sqlite3.connect(db_path)
    return conn


# Function to create the required tables
# Function to create the required tables
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Create the 'jobs' table to store job postings
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT,
        application_link TEXT UNIQUE NOT NULL,
        date_posted DATE
    )
    ''')

    # Create the 'applications' table to track application status
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS applications (
        job_id INTEGER,
        application_status TEXT,
        applied_date DATE,
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    )
    ''')

    conn.commit()
    conn.close()

# Function to insert job postings into the database
# Function to insert job postings into the database
def insert_job(job_data):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT OR IGNORE INTO jobs (
            role, company, location, application_link, date_posted
        ) VALUES (?, ?, ?, ?, ?)
        ''', (
            job_data['Role'],
            job_data['Company'],
            job_data['Location'],
            job_data['Application Link'],
            job_data.get('Date Posted', None)
        ))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting job: {e}")
    finally:
        conn.close()




# Call this function to create the tables when you run this script
if __name__ == '__main__':
    create_tables()
    print("Database and tables created successfully!")
