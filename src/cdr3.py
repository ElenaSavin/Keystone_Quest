from fastq_parser import translate_all_orfs_optimized, chunked_file_reader, read_fastq_in_chunks, read_sequences_from_csv, logging
import time, os
import ahocorasick
import multiprocessing
import concurrent.futures

target_hashed = read_sequences_from_csv("top_1000.csv")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   Initialize process worker
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def init_worker():
  global automaton_protein
  automaton_protein = ahocorasick.Automaton()
  for idx, value in enumerate(target_hashed.keys()):
    automaton_protein.add_word(value, (idx, value))
  automaton_protein.make_automaton()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  End
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   Process worker
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def process_chunk(read):
  """_summary_

  Args:
      read (Seq object): one string object obtained from fastq

  Returns:
     result list: If a sequence is found it will return the read details, 
     Otherwise will return empty list
  """
  try:
    results = []
    sequence = str(read.seq.reverse_complement())
    for frame, protein_sequence in enumerate(translate_all_orfs_optimized(sequence), start=1):
      for _, found in automaton_protein.iter(str(protein_sequence)):
        results.append((found, read.id, frame, protein_sequence))

    return results

  except Exception as e:
    logging.error(f"Error in process_chunk: {e}")
    raise  # Reraising the exception will help to identify if any worker fails
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  End
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   Callback for the thread worker
# Add lock to write to file 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def custom_callback(chunks):
  for processed_chunk in chunks:
    for chunk in processed_chunk:
      found, read_id, frame, protein_sequence = chunk
      logging.info(f"Target sequence found - {found} in read: {read_id} | Frame: {frame + 1} | Original translated sequence: {protein_sequence}")
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   End
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   Main execution 
# Add error callback to map_async
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def process_fastq_file(file_path, chunk_size, target_hashed):
  start_time = time.time()
  total_size = os.path.getsize(file_path)
  bytes_processed = 0
  num_processes = max(os.cpu_count() - 1, 1)
  chunksize = 100
  callback_executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

  # ----- Aho–Corasick algorithm init for first parse ------------------------------
  automaton = ahocorasick.Automaton()

  for seq, info in target_hashed.items():
    for idx, key in enumerate(info['reverse_translate']):
      automaton.add_word(key, (idx, key))

  automaton.make_automaton()
  # --------------------------------------------------------------------------------
  with multiprocessing.Pool(initializer=init_worker) as pool:
    for chunk_str in chunked_file_reader(file_path, chunk_size):
      try:
        bytes_processed += len(chunk_str.encode('ascii'))
        percentage_read = (bytes_processed / total_size) * 100
        logging.info(f"Processed {percentage_read:.2f}% of the file.")
      except UnicodeDecodeError as e:
        logging.warning(f"UnicodeDecodeError encountered: {e}") 
      
      filtered_chunk = read_fastq_in_chunks(chunk_str, automaton)
      if len(filtered_chunk) > 0 :
        result = results = pool.map_async(process_chunk, filtered_chunk, chunksize = chunksize, 
                                          callback=lambda chunks: callback_executor.submit(custom_callback, chunks))
      result.wait()
    
    pool.close()
    pool.join()

  callback_executor.shutdown(wait=True)
  end_time = time.time()
  elapsed_time = end_time - start_time
  logging.info(f"Total runtime: {elapsed_time} seconds")
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   End
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
