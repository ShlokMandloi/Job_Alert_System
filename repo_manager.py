from git import Repo
import os

 #Repository URL
REPO_URL = 'https://github.com/SimplifyJobs/New-Grad-Positions.git'

# Use the current working directory to set the LOCAL_PATH
LOCAL_PATH = os.path.join(os.getcwd(), 'repo_clone')
# Directory where the repository will be cloned

# Clone the repository if it doesn't exist locally
def clone_repository():
    if not os.path.exists(LOCAL_PATH):
        print("Cloning repository...")
        Repo.clone_from(REPO_URL, LOCAL_PATH)
        print("Repository cloned successfully.")
    else:
        print("Repository already exists.")

# Function to pull latest changes
def update_repository():
    if os.path.exists(LOCAL_PATH):
        print("Updating repository...")
        repo = Repo(LOCAL_PATH)
        origin = repo.remotes.origin
        origin.pull()
        print("Repository updated successfully.")
    else:
        print("Repository not found. Please clone it first.")

if __name__ == '__main__':
    clone_repository()
    update_repository()
