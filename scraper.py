import re
import sqlite3
from bs4 import BeautifulSoup
import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import requests
import schedule
import time
from repo_manager import update_repository


# Initialize the SNS client
sns_client = boto3.client('sns', region_name='us-east-1')  # Replace 'us-east-1' with your AWS region if different
TOPIC_ARN = 'arn:aws:sns:us-east-1:851725641441:JobAlert'  # Replace with your actual Topic ARN

# Import functions from database.py to store job details
from database import insert_job, create_connection

# Pushover credentials
PUSHOVER_API_TOKEN = 'awh6z1jzk5dsz7qetm2pbayycvcf36'  # Replace with your Pushover API Token
PUSHOVER_USER_KEY = 'u6qzd7qapzyv3wo79xvp3j2sarzp4z'    # Replace with your Pushover User Key

# Define the path to the locally cloned repo
REPO_PATH = r"C:\Users\Shlok Mandloi\Desktop\Shlok\Shlok - USA\Projects\Job Alert System\repo_clone"  # Update this path to your local cloned repo
README_PATH = os.path.join(REPO_PATH, "README.md")


def scrape_jobs():
    update_repository()  # Update the repo before scraping
    readme_content = read_readme_file()
    jobs = parse_jobs_from_readme(readme_content)
    update_jobs_in_database(jobs)



def send_pushover_notification(job_details):
    message = (
        f"New Job Alert!\n\n"
        f"Role: {job_details['Role']}\n"
        f"Company: {job_details['Company']}\n"
        f"Location: {job_details['Location']}\n"
        f"Application Link: {job_details['Application Link']}\n"
        f"Date Posted: {job_details['Date Posted']}"
    )
    
    try:
        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": PUSHOVER_API_TOKEN,
                "user": PUSHOVER_USER_KEY,
                "message": message,
                "title": "New Job Alert!",
                "url": job_details['Application Link'],
                "url_title": "Apply Here"
            }
        )
        if response.status_code == 200:
            print("Pushover notification sent successfully!")
        else:
            print(f"Failed to send Pushover notification: {response.text}")
    except Exception as e:
        print(f"Error sending Pushover notification: {e}")

def send_alert(job_details):
    email_message = (
        f"New Job Alert!\n\n"
        f"Role: {job_details['Role']}\n"
        f"Company: {job_details['Company']}\n"
        f"Location: {job_details['Location']}\n"
        f"Application Link: {job_details['Application Link']}\n"
        f"Date Posted: {job_details['Date Posted']}"
    )
    
    try:
        sns_response = sns_client.publish(
            TopicArn=TOPIC_ARN,
            Message=email_message,
            Subject="!!! JOB POSTED !!!"
        )
        print(f"Email alert sent! Message ID: {sns_response['MessageId']}")
    except Exception as e:
        print(f"Failed to send email alert: {e}")

    # Send Push Notification via Pushover
    send_pushover_notification(job_details)  # Use the function to send Pushover notification

def read_readme_file():
    with open(README_PATH, 'r', encoding='utf-8') as file:
        return file.read()

def parse_jobs_from_readme(content):
    table_start = "<!-- Please leave a one line gap between this and the table TABLE_START (DO NOT CHANGE THIS LINE) -->"
    table_end = "<!-- Please leave a one line gap between this and the table TABLE_END (DO NOT CHANGE THIS LINE) -->"
    
    table_content = content.split(table_start)[1].split(table_end)[0]
    rows = table_content.strip().splitlines()[2:]  # Skip header lines

    jobs = []
    for row in rows:
        columns = row.split('|')[1:-1]  # Exclude the first and last split items
        columns = [col.strip() for col in columns]

        if len(columns) >= 5:
            company_name = re.search(r'\[(.*?)\]', columns[0]).group(1) if re.search(r'\[(.*?)\]', columns[0]) else columns[0]
            job_title = columns[1]
            location = columns[2]
            date_posted = columns[4]
            url_match = re.search(r'href="(.*?)"', columns[3])
            job_url = url_match.group(1) if url_match else None
            
            jobs.append({
                "Company": company_name,
                "Role": job_title,
                "Location": location,
                "Application Link": job_url,
                "Date Posted": date_posted
            })
            
    return jobs

def update_jobs_in_database(jobs):
    """
    Inserts new job postings into the database if not already present
    and sends alerts for each new job added.
    """
    conn = create_connection()
    cursor = conn.cursor()
    
    for job in jobs:
        try:
            # Check if the job is already in the database based on its URL
            cursor.execute("SELECT 1 FROM jobs WHERE application_link = ?", (job['Application Link'],))
            existing_job = cursor.fetchone()
            
            # If job is not in the database, insert it and send notifications
            if not existing_job:
                insert_job(job)
                send_alert(job)  # Send an alert notification for the newly added job
                print(f"Added new job: {job['Role']} at {job['Company']}")

        except sqlite3.IntegrityError:
            continue  # Continue if there's any issue, ensuring the loop doesn't stop
    
    conn.commit()
    conn.close()

def scrape_jobs():
    """
    Main function to read the README.md file, parse the job postings, and update the database.
    """
    readme_content = read_readme_file()
    jobs = parse_jobs_from_readme(readme_content)
    update_jobs_in_database(jobs)

# Scheduling part
def scheduled_job():
    print("Checking for new job postings...")
    scrape_jobs()

# Schedule the job to run every 30 minutes
schedule.every(30).minutes.do(scheduled_job)

if __name__ == "__main__":
    print("Starting job scraper...")
    scrape_jobs()
    while True:
        schedule.run_pending()
        time.sleep(1)
