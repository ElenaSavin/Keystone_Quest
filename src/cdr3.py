from fastq_parser import *
import time, os
import ahocorasick
import multiprocessing
import concurrent.futures
import logging

logger = logging.getLogger('main')
target_cdr3 = read_sequences_from_csv("top_1000.csv")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   Initialize process worker
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def init_worker():
  """initialisung worker, creating a list for the automaton.
  """
  global automaton_protein
  automaton_protein = ahocorasick.Automaton()
  for idx, value in enumerate(target_cdr3.keys()):
    automaton_protein.add_word(value, (idx, value))
  automaton_protein.make_automaton()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  End
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   Process worker
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def process_chunk(read):
  """Searching for the Keystone sequences in the read.

  Args:
    read (Seq object): one string object obtained from fastq

  Returns:
    list: If a sequence is found it will add the read details to results list, 
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
  """callback function for the worker proccess.

  Args:
      chunks (list): list of chuncks resulted from worker.
  """
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
def process_fastq_file(file_path, chunk_size, filter = True):
  """This is the main execution af the search.

  Args:
    file_path (str): fastq file path
    chunk_size (int): size of the chunck
    filter (bool, optional): weather to use filter. Defaults to True.
  """
  start_time = time.time()
  total_size = os.path.getsize(file_path)
  bytes_processed = 0
  num_processes = max(os.cpu_count() - 1, 1)
  chunksize = 100
  callback_executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

  if filter == True:
    # ----- Aho–Corasick algorithm init for first parse ------------------------------
    automaton = ahocorasick.Automaton()

    for seq, info in target_cdr3.items():
      for idx, key in enumerate(info['reverse_translate']):
        automaton.add_word(key, (idx, key))

    automaton.make_automaton()
    # --------------------------------------------------------------------------------
  
  # PHASE 2
  
  
  with multiprocessing.Pool(initializer=init_worker) as pool:
    for chunk_str in chunked_file_reader(file_path, chunk_size):
      try:
        bytes_processed += len(chunk_str.encode('ascii'))
        percentage_read = (bytes_processed / total_size) * 100
        logging.info(f"Processed {percentage_read:.2f}% of the file.")
      except UnicodeDecodeError as e:
        logging.warning(f"UnicodeDecodeError encountered: {e}") 
      
      filtered_chunk = read_fastq_in_chunks(chunk_str, automaton) #reads from fastq
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
