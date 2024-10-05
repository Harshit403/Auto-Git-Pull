from fastapi import FastAPI, Request, HTTPException
import os
import subprocess
from datetime import datetime

app = FastAPI()

# Paths
REPO_PATH = '/home/admin/web/exam60.online/public_html'  # Replace with the path to your repository
LOG_FILE_PATH = os.path.join(os.getcwd(), 'git_logs.txt')  # Log file in the root directory of the FastAPI app

@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        os.chdir(REPO_PATH)
        
        # Open the log file in append mode
        with open(LOG_FILE_PATH, 'a') as log_file:
            log_file.write(f"\n\n---- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ----\n")
            log_file.write("Starting git pull...\n")
            
            # Start the git pull process and capture the output
            process = subprocess.Popen(
                ['git', 'pull'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            while True:
                output = process.stdout.readline().decode('utf-8')
                if output == '' and process.poll() is not None:
                    break
                if output:
                    log_file.write(output.strip() + "\n")
            
            err_output = process.stderr.read().decode('utf-8')
            if err_output:
                log_file.write(f"Error: {err_output}\n")

            log_file.write("Git pull completed.\n")

        return {"status": "success", "message": "Git pull completed and logs saved"}
    
    except subprocess.CalledProcessError as e:
        with open(LOG_FILE_PATH, 'a') as log_file:
            log_file.write(f"Git pull failed: {str(e)}\n")
        raise HTTPException(status_code=500, detail=f"Git pull failed: {str(e)}")
    
    except Exception as e:
        with open(LOG_FILE_PATH, 'a') as log_file:
            log_file.write(f"An unexpected error occurred: {str(e)}\n")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/")
async def read_root():
    return {"message": "Webhook server is running"}
