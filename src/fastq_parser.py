import Bio.SeqIO as SeqIO 
from Bio.Data import CodonTable
from itertools import product
import Bio
import csv
import logging
import time
from memory_profiler import profile
from io import StringIO


def read_sequences_from_csv(csv_file):
  """
  Reads sequences from a CSV file and returns a dictionary of hashed sequences.
  """
  start_time = time.time()
  sequence_prefixes = {}

  try:
    with open(csv_file, "r") as csvfile:
        logging.info(f"Reading sequences from {csv_file}")
        csv_reader = csv.reader(csvfile)
        next(csv_reader)  # Skip header

        for row in csv_reader:
          sequence = row[0]
          sequence_prefixes[sequence] = {
            'reverse_translate': reverse_translate(sequence[:4])
          }
        
        logging.info(f"Completed reading and hashing sequences from {csv_file}")

  except IOError as e:
    logging.error(f"Error reading file {csv_file}: {e}")

  end_time = time.time()
  print(f"Execution time for reading sequences from {csv_file}: {end_time - start_time} seconds")

  return sequence_prefixes

#TODO add as feature flag with number of chars 
def filter_reads(read, automaton):
  read_sequence = str(read.seq)
  for _, found in automaton.iter(read_sequence):
    return True  # Return True if any substring is found
  return False  # Return False if no substring is found


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

def reverse_translate(amino_acid_sequence):
  """_summary_

  Args:
      amino_acid_sequence (_type_): _description_

  Returns:
      _type_: _description_
  """
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