from download import import_files
import os
from cdr3 import process_fastq_file
from fastq_parser import read_sequences_from_csv
import argparse
import logging

if __name__ == "__main__":
  """
  This Python script is designed to efficiently search for target protein sequences within a large FASTQ file.
  The main is parsing arguments from commandline, setting loggging config and initialise the proccess.
  This proccess is set to run in a parallel environment therfore accepts only one file at a time.
  """
  # Parser
  parser = argparse.ArgumentParser(description="This Python script is designed to efficiently search for target protein sequences within a large FASTQ file.")
  parser.add_argument("-f", "--filepath", metavar="", required=True, type=str, help="Path to the FASTQ files")
  parser.add_argument("-n", "--filename", metavar="", required=True, type=str, help="File id to download/proccess without ending. mandatory")
  parser.add_argument("-fi", "--filter", metavar="", required=False, default=True, type=bool, help="Filter the reads before proccessing. true by default.")
  parser.add_argument("-lp", "--logpath", metavar="", required=False, default="proccess.log", help="specify custom path for logs. Will be the directory of the script by default")
  parser.add_argument("-d", "--downloadfiles", metavar="", required=False, default=False, help="feature flag for downloading files from tcga. false by default, will take files specified in filespath flag")
  parser.add_argument("-p", "--project", metavar="", required=False, default="brca", help="TCGA Project to download files from")
  parser.add_argument("-t", "--tokenpath", metavar="", required=False, default="token.txt", help="TCGA token file path for restricted data acccess. using token.txt in main folder as default")
  parser.add_argument("-m", "--manifestpath", metavar="", required=False, default="manifest.txt", help="manifest text file containing a list of all file ids to download. using manifest.txt in main folder as default.")
  parser.add_argument("-o", "--output", metavar="", required=False, help="path for the output file with results. default will be results directory.")

  # Set varibles from parser
  args = parser.parse_args()
  filter = args.filter
  logpath = args.logpath
  download = args.downloadfiles
  global project 
  project = args.project
  file_id = args.filename
  output = args.output
  
  # Set path to all config/fastq files
  os.makedirs(f"{args.filepath}/{project}", exist_ok=True)  # Create directory only if needed
  file_path = f"{args.filepath}/{project}/{file_id}"
  token_path = args.tokenpath
  manifest = args.manifestpath
  
  # Initialise and configure logger
  logging.basicConfig(
  level=logging.INFO, 
  format='%(asctime)s - %(levelname)s - %(message)s',
  filename=logpath,
  filemode='w'
  )
  
  # if download flag set to true will download from tcga,  otherwisw will go streight to proccess
  if download:    
    import_files(file_path, token_path)
  process_fastq_file(f"{file_path}.fastq", 4000, filter)
  