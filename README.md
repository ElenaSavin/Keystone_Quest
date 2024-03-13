# Keystone Quest: A Fast and Accurate RNAseq CDR3 Discovery Tool

## Project Overview

This Python script is designed to efficiently search for target protein sequences within a large FASTQ file, leveraging multiprocessing and Aho-Corasick algorithm for optimized performance. It's specifically tailored for bioinformatics applications, particularly in the context of analyzing genetic data.

## Key Features

Fast and Efficient Searching: Employs the Aho-Corasick algorithm for rapid substring matching, enabling swift identification of target sequences within the FASTQ file.
Multiprocessing: Utilizes multiprocessing to distribute the workload across multiple CPU cores, significantly accelerating the search process.
Reverse Translation: Facilitates the search for target protein sequences by reverse translating them into possible DNA sequences, enhancing the flexibility of the search.
Open Reading Frame Translation: Translates all three possible open reading frames (ORFs) of each sequence, ensuring comprehensive coverage and minimizing the risk of missing relevant matches.
Clear Logging: Provides detailed logging information, including execution time, file processing progress, target sequence matches, and any errors encountered, aiding in analysis and troubleshooting.

## Requirements

Python 3.x  
samtools  
  
    
python libraries:  
    biopython==1.81  
    pyahocorasick==2.0.0  
    numpy==1.23.5  
    pandas==1.5.3  
    tqdm==4.64.1    

## Installation

Install the required Python libraries using pip:
Bash
```
pip install -r requirments.txt
```
Use code with caution. Learn more
## Usage

Prepare a CSV file containing the target protein sequences, with one sequence per row.
Update the following variables in the script:
csv_file: Path to the CSV file containing target sequences.
fastq_file: Path to the FASTQ file to be searched.
chunk_size: Size of chunks to be processed (adjust based on system resources and file size).
Run the script:
Bash
```
usage: main.py [-h] -f  -n  [-fi] [-lp] [-d] [-p] [-t] [-m]

This Python script is designed to efficiently search for target protein sequences within a large FASTQ file.

options:
  -h, --help            show this help message and exit
  -f , --filepath       Path to the FASTQ files
  -n , --filename       File id to download/proccess without ending. mandatory
  -fi , --filter        Filter the reads before proccessing. true by default.
  -lp , --logpath       specify custom path for logs. Will be the directory of the script by default
  -d , --downloadfiles feature flag for downloading files from tcga. false by default, will take files specified in filespath flag.
  -p , --project        TCGA Project to download files from
  -t , --tokenpath      TCGA token file path for restricted data acccess. using token.txt in main folder as default
  -m , --manifestpath   manifest text file containing a list of all file ids to download. using manifest.txt in main folder as default.
```

## Output

The script outputs target sequence matches to the logging file, and debugging messages (if enabled).
Creates a output file with all sequences found and details on each, and a summery.csv.  
they will be in the same folder as the RNASeq.  
Matches include read ID, frame, and original sequence.

## Additional Notes

Consider adjusting the chunk_size and num_processes parameters to fine-tune performance for different file sizes and hardware configurations.
For large FASTQ files, ensure adequate system resources (CPU cores and RAM) to handle the multiprocessing workload.
The script employs a thread pool for callbacks using concurrent.futures to streamline the output of results.

## Adding mount
```
#!/bin/bash
curl --fail -H "Authorization: Bearer Oracle" -L0 http://169.254.169.254/opc/v2/instance/metadata/oke_init_script | base64 --decode >/var/run/oke-init.sh
bash /var/run/oke-init.sh
sudo /usr/libexec/oci-growfs -y
```