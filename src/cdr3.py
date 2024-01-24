import logging
from fastq_parser import translate_all_orfs_optimized, chunked_file_reader, read_fastq_in_chunks
import time, os
import ahocorasick
import multiprocessing

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

def process_fastq_file(file_path, chunk_size, target_hashed):
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
