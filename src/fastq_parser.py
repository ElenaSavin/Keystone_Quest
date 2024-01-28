import Bio.SeqIO as SeqIO 
import logging
from Bio.Data import CodonTable
from itertools import product
import Bio
import csv
import time
from io import StringIO

logger = logging.getLogger('main')

def read_sequences_from_csv(csv_file):
  """
  Reads sequences from a CSV file and returns a dictionary of hashed sequences.
  Args:
    csv_file(str): name of the csv file containing the Keystone sequences.
  Return:
    sequence_prefixes(dict): dictionary of sequences, and reverse translated prefixes.
    
  """
  sequence_prefixes = {}

  try:
    with open(csv_file, "r") as csvfile:
      logger.info(f"Reading sequences from {csv_file}")
      csv_reader = csv.reader(csvfile)
      next(csv_reader)  # Skip header
      
      # writing the content to a dictionary - key is the aa sequence value is a key:value pair
      # key is "reverse_translate" value is first 4 aa reverse tranlated - all options in a list.
      for row in csv_reader:
        sequence = row[0]
        sequence_prefixes[sequence] = {
          'reverse_translate': reverse_translate(sequence[:4])
        }
      
      logger.info(f"Completed reading and hashing sequences from {csv_file}")

  except IOError as e:
    logger.error(f"Error reading file {csv_file}: {e}")

  return sequence_prefixes


#TODO add as feature flag with number of chars 
#TODO if filter flag use read from here otherwise do it in workers
def filter_reads(read, automaton):
  """
  Accepts a prebuilt Trie of all X prefix letters of the target cdr3 sequence.
  I will search for this prefix in the reads provided reverse complement. 
  If it will find a match, 
  Return true will enable this read to continue in proccess as a potential sorce containg a target cdr3

  Args:
      read (read object): biopython read object.
      automaton (object): automaton object.

  Returns:
      bool: returns true if at least one keystone prefix is found in read. false otherwise
  """
  read_sequence = str(read.seq.reverse_complement())
  for _, _ in automaton.iter(read_sequence):
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
  """Creating a chunck from full fastq file.

  Args:
      file_path (str): path of the fastq file.
      chunk_size (int): number of lines that will compose a chunk.

  Yields:
      list: returns a list of chuncks.
  """
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
  """parsing fastq chunck using biopython.

  Args:
    chunk (str): string with content of fastq file by chunck size.
    automaton (object): automaton object.

  Returns:
      list: list containing all reads from the chunck
  """
  handle = StringIO(chunk)  # Convert string chunk to a file-like object
  chunk_reads = []
  for read in SeqIO.parse(handle, "fastq"):
    if filter_reads(read, automaton):
      chunk_reads.append(read)
  return chunk_reads

def reverse_translate(amino_acid_sequence):
  """reverse translate aa and return all possible codons.

  Args:
    amino_acid_sequence (str): amino acid seq to reerse translate.

  Returns:
    list: all posible codons list
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