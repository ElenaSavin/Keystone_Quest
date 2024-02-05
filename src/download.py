import logging
import requests
import json
from tqdm import tqdm
from os import remove, system
import os

logger = logging.getLogger('main')
session = requests.Session()

def download(token_string, file_path, file_id):
  """Downloading BAM file from tcga data portal using the TCGA api.
  Converting to fastq using samtools.

  Args:
      data_endpt (str): url with endpoint to specific file.
      token_string (str): TCGA NIH token
      file_path (str): path to download the file to.
  """
  session = requests.Session()

  base_url = "https://api.gdc.cancer.gov/data/"
  url = base_url + file_id
  with open("token.txt","r") as token:
    token_string = str(token.read().strip())
    
  response = session.head(url)
  try:
    file_size = int(response.headers['Content-Length'])
  except KeyError:
    raise Exception("Unable to retrieve file size for ID: " + file_id)

  response = session.get(url, stream=True, headers = {
                        "Content-Type": "application/json",
                        "X-Auth-Token": token_string
                        })

  if response.status_code == 200:
    with open(f"{file_path}.bam", 'wb') as f, tqdm(
              desc=file_id,
              total=file_size,
              unit='iB',
              unit_scale=True,
              unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=1024):
          size = f.write(chunk)
          bar.update(size)
    print(f"File {file_id} downloaded successfully.")
  else:
      print(f"Failed to download file. Status code: {response.status_code}")
  
  logger.info(f"turning {file_path}.bam into {file_path}.fastq")
  system(f"samtools bam2fq {file_path}.bam > {file_path}.fastq")
  
#read the file ids from file
def import_files(file_id, file_path, token_file):
  """Creating all data for download.

  Args:
    file_id (str): file id from TCGA.
    file_path (str): path of the fastq.
    token_file (str): token file path. use for restricted data.
  """
  file = f"{file_path}.fastq"
  if os.path.exists(file):
    logging.info(f"File: {file_id} exists, Skipping Download")
  else:
    logging.info(f"Downloading file id: {file_id}")
    with open(token_file,"r") as token:
      token_string = str(token.read().strip())
    try:
      download(token_string, file_path, file_id)
    except requests.exceptions.ConnectionError as e:
      if "Temporary failure in name resolution" in str(e):
        logging.warning(f"Temporary DNS resolution error. File {file_id} was not downloaded")
      # Code to retry the operation (e.g., call the function again)
      else:
        logging.warning("A different connection error occurred:", e) 
    logging.info(f"Downloaded file id: {file_id} successfully to path {file_path}")
 