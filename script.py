import Bio.SeqIO as SeqIO 
from Bio.Data import CodonTable
from itertools import product
import Bio
import csv
import timeit
import multiprocessing
import logging
from multiprocessing import Queue
from multiprocessing import Value, Manager
from logging.handlers import QueueHandler, QueueListener
import time
import numpy as np
from memory_profiler import profile
from io import StringIO
import os
import ahocorasick

# ----- Initialize logging --------------------------------------------------------
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='development.log',
    filemode='w'
)
# ---------------------------------------------------------------------------------


def read_sequences_from_csv(csv_file):
    """
    Reads sequences from a CSV file and returns a dictionary of hashed sequences.
    """
    start_time = time.time()
    hashed_sequences = {}

    try:
        with open(csv_file, "r") as csvfile:
            logging.info(f"Reading sequences from {csv_file}")
            csv_reader = csv.reader(csvfile)
            next(csv_reader)  # Skip header

            for row in csv_reader:
              sequence = row[0]
              hashed_sequences[sequence] = {
                'reverse_translate': reverse_translate(sequence[:4])
              }
            
            logging.info(f"Completed reading and hashing sequences from {csv_file}")

    except IOError as e:
        logging.error(f"Error reading file {csv_file}: {e}")

    end_time = time.time()
    print(f"Execution time for reading sequences from {csv_file}: {end_time - start_time} seconds")

    return hashed_sequences

def translate_all_orfs_optimized(sequence):
  """Translates all three open reading frames (ORFs) of a given sequence, optimized for speed.

  Args:
      sequence (str): The RNA sequence to translate.

  Returns:
      list: A list of three translated amino acid sequences, one for each ORF.
  """
  
  # Efficiently determine the number of padding nucleotides needed:
  padding_needed = -len(sequence) % 3

  # Pad the sequence only once for all frames:
  padded_sequence = sequence + "N" * padding_needed

  # Translate all three frames using the padded sequence:
  protein1 = Bio.Seq.Seq(padded_sequence).translate()
  protein2 = Bio.Seq.Seq(padded_sequence)[1:].translate()
  protein3 = Bio.Seq.Seq(padded_sequence)[2:].translate()

  yield protein1, protein2, protein3

def process_chunk(reads, automaton_protein):
  try:
    for read in reads:
      sequence = str(read.seq.reverse_complement())
      for frame, protein_sequence in enumerate(translate_all_orfs_optimized(sequence), start=1):
        for _, found in automaton_protein.iter(str(protein_sequence)):
          logging.info(f"Target sequence found in read: {read.id} | Target sequence: {found} |Frame: {frame + 1} | Original translated sequence: {protein_sequence}")

  except Exception as e:
    logging.error(f"Error in process_chunk: {e}")
    raise  # Reraising the exception will help to identify if any worker fails

def filter_reads(read, automaton):
  return True
  read_sequence = str(read.seq)
  for _, found in automaton.iter(read_sequence):
    return True  # Return True if any substring is found
  return False  # Return False if no substring is found

def chunked_file_reader(file_path, chunk_size):
  with open(file_path, 'r') as file:
    chunk = []
    line_count = 0
    for line in file:
      chunk.append(line)
      line_count += 1
      if line_count % 4 == 0 and line_count >= chunk_size: # Ensure that the chunk size is a multiple of 4 to align with FASTQ record boundaries
        yield ''.join(chunk)
        chunk = []
        line_count = 0
    if chunk:
      yield ''.join(chunk)

def read_fastq_in_chunks(chunk, automaton):
    handle = StringIO(chunk)  # Convert string chunk to a file-like object
    chunk_records = []
    for record in SeqIO.parse(handle, "fastq"):
      if filter_reads(record, automaton):
        chunk_records.append(record)
    return chunk_records

def process_fastq_file(file_path, chunk_size):
    start_time = time.time()
    total_size = os.path.getsize(file_path)
    bytes_processed = 0

    # Calculate total number of reads
    # total_reads = sum(1 for _ in SeqIO.parse(open(file_path), "fastq"))
    
    # ----- Aho–Corasick algorithm init for first parse ------------------------------
    automaton = ahocorasick.Automaton()

    for seq, info in target_hashed.items():
      for idx, key in enumerate(info['reverse_translate']):
        automaton.add_word(key, (idx, key))

    automaton.make_automaton() #Build tree with target seqs codons
    # --------------------------------------------------------------------------------

    # ----- Aho–Corasick algorithm init for first parse ------------------------------
    automaton_protein = ahocorasick.Automaton()

    for idx, value in enumerate(target_hashed.keys()):
      automaton_protein.add_word(value, (idx, value))

    automaton_protein.make_automaton() #Build tree with target seqs amino acids
    # --------------------------------------------------------------------------------

    with multiprocessing.Pool(processes=7) as pool:
      for chunk_str in chunked_file_reader(file_path, chunk_size):
        try:
          bytes_processed += len(chunk_str.encode('utf-8'))
          percentage_read = (bytes_processed / total_size) * 100
          logging.info(f"Processed {percentage_read:.2f}% of the file.")
        except UnicodeDecodeError as e:
          logging.warning(f"UnicodeDecodeError encountered: {e}")

        filtered_chunk = read_fastq_in_chunks(chunk_str, automaton)
        
        if len(filtered_chunk) > 0:
          pool.apply_async(process_chunk, args=(filtered_chunk, automaton_protein, ))
        
      pool.close()
      pool.join()

    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"Total runtime: {elapsed_time} seconds")


def reverse_translate(amino_acid_sequence):
    standard_table = CodonTable.unambiguous_dna_by_id[1]

    # Find all codons for each amino acid
    amino_acid_to_codons = {}
    for codon, amino_acid in standard_table.forward_table.items():
        if amino_acid not in amino_acid_to_codons:
            amino_acid_to_codons[amino_acid] = []
        amino_acid_to_codons[amino_acid].append(codon)

    # Generate all combinations of codons for the amino acid sequence
    all_codon_combinations = [amino_acid_to_codons[aa] for aa in amino_acid_sequence]
    possible_dna_sequences = [''.join(codon_combo) for codon_combo in product(*all_codon_combinations)]

    return possible_dna_sequences

# Usage
target_hashed = read_sequences_from_csv("top_1000.csv")
process_fastq_file("files/brca_CD8T_REH_4h_rep1.fastq", 4000) 
