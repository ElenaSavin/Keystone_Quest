#!/bin/bash
cd /home/lena/oc-files/
for file1 in *_R1_001.fastq.gz; do
  # Extract base name and remove "_R1_001.fastq.gz"
  base_name="${file1%_R1_001.fastq.gz}"
  # Find corresponding R2 file with the same base name and "_R2_001.fastq.gz" suffix
  file2="${base_name}_R2_001.fastq.gz"
  # Check if R2 file exists
  if [[ -f "$file2" ]]; then
    # Print the pair of files in your desired format (replace placeholders)
    /home/lena/bbmap/bbmerge.sh in1="/home/lena/oc-files/$file1" in2="/home/lena/oc-files/$file2" out="${base_name}.fastq"
    cd /home/lena/cdr3_finder/
    python src/main.py -f /home/lena/oc-files --filename "${base_name}" || continue
    echo $base_name >> done.txt
    rm -f ${base_name}.fastq.gz /home/lena/oc-files/$file1 /home/lena/oc-files/$file2
    cd -
  fi
  
done