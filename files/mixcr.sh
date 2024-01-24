for file in *.fastq; do

  # Ensure the file is a regular file before processing
  if [[ -f "$file" ]]; then

    # Execute mixcr with appropriate arguments and error handling
    mixcr analyze -s hsa rnaseq-cdr3 "$file" results/"${file%.fastq}" -f || {
      echo "Error processing $file with mixcr. Skipping." >&2
      continue
    }

    echo "Successfully processed $file with mixcr."

  else
    echo "Skipping $file as it's not a regular file."
  fi

done
