import logging
import requests
import json
from os import remove, system
import os

logger = logging.getLogger('main')

def download_fastq(data_endpt, token_string, file_path):
  params = {"gencode": ["BRCA1", "BRCA2"]}
  response = requests.post(data_endpt, 
                          data = json.dumps(params), 
                          headers = {
                            "Content-Type": "application/json",
                            "X-Auth-Token": token_string
                            })

  file_name = f"{file_path}.bam"
  
  # Create the "files" directory if it doesn't exist

  with open(file_name, "wb") as output_file:
    output_file.write(response.content)
      
  system(f"samtools bam2fq ${file_name} > ${file_path}.fastq")
  
#read the file ids from file
def import_files(file_id, file_path, token_file):
  logger.info(f"Importing files specified in manifest from TCGA Data Portal")

  data_endpt = f"https://api.gdc.cancer.gov/slicing/view/{file_id}"
  file = f"{file_path}.fastq"
  if os.path.exists(file):
    print(f"File: {file_id} exists, Skipping Download")
  else:
    print(f"Downloading file id: {file_id}")
    with open(token_file,"r") as token:
      token_string = str(token.read().strip())
    try:
      download_fastq(data_endpt, token_string, file_path)
    except requests.exceptions.ConnectionError as e:
      if "Temporary failure in name resolution" in str(e):
        print(f"Temporary DNS resolution error. File {file_id} was not downloaded")
      # Code to retry the operation (e.g., call the function again)
      else:
        print("A different connection error occurred:", e) 
 