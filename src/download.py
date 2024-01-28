import logging
import requests
import json
from os import remove, system
import os

logger = logging.getLogger('main')

def download(data_endpt, token_string, file_path):
  """Downloading BAM file from tcga data portal using the TCGA api.
  Converting to fastq using samtools.

  Args:
      data_endpt (str): url with endpoint to specific file.
      token_string (str): TCGA NIH token
      file_path (str): path to download the file to.
  """
  params = {"gencode": ["BRCA1", "BRCA2"]}
  response = requests.post(data_endpt, 
                          data = json.dumps(params), 
                          headers = {
                            "Content-Type": "application/json",
                            "X-Auth-Token": token_string
                            })
  
  with open(f"{file_path}.bam", "wb") as output_file:
    output_file.write(response.content)
      
  system(f"samtools bam2fq {file_path}.bam > ${file_path}.fastq")
  
#read the file ids from file
def import_files(file_id, file_path, token_file):
  """Creating all data for download.

  Args:
    file_id (str): file id from TCGA.
    file_path (str): path of the fastq.
    token_file (str): token file path. use for restricted data.
  """
  data_endpt = f"https://api.gdc.cancer.gov/slicing/view/{file_id}"
  file = f"{file_path}.fastq"
  if os.path.exists(file):
    logging.info(f"File: {file_id} exists, Skipping Download")
  else:
    logging.info(f"Downloading file id: {file_id}")
    with open(token_file,"r") as token:
      token_string = str(token.read().strip())
    try:
      download(data_endpt, token_string, file_path)
    except requests.exceptions.ConnectionError as e:
      if "Temporary failure in name resolution" in str(e):
        logging.warning(f"Temporary DNS resolution error. File {file_id} was not downloaded")
      # Code to retry the operation (e.g., call the function again)
      else:
        logging.warning("A different connection error occurred:", e) 
    logging.info(f"Downloaded file id: {file_id} successfully to path {file_path}")
 