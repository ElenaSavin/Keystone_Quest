import csv
import pandas as pd
import logging
from upload import upload_file

logger = logging.getLogger('main')

def output_csv(file_path, rows):
    """Creates a CSV file with column headers and rows as lists.

    Args:
        file_path (str): The name of the CSV file to create.
        rows (list): A list of lists representing the data rows.
    """
    headers = ["aaCDR3", "readID", "frame", "nCDR3"]
    with open(f"{file_path}_output.csv", 'a') as csvfile:
        csv_writer = csv.writer(csvfile)
        if csvfile.tell() == 0:  # Check file position
            csv_writer.writerow(headers)  # Write the header row
        csv_writer.writerow(rows)   # Write the data rows
    upload_file(f"{file_path}_output.csv")

def output_summery(file_path):
    # Read the CSV file into a DataFrame
    try:
        df = pd.read_csv(f"{file_path}_output.csv")

        # Count the occurrences of each sequence in the "aaCDR3" column
        sequence_counts = df["aaCDR3"].value_counts()

        # Create a new DataFrame with the summarized data
        summary_df = pd.DataFrame({"aaCDR3": sequence_counts.index, "count": sequence_counts.values})

        # Save the summarized data to a new CSV file
        summary_df.to_csv(f"{file_path}_summary.csv", index=False)

        logger.info(f"Summary data saved to {file_path}_summary.csv")
        upload_file(f"{file_path}_summary.csv")
    except FileNotFoundError:
        logger.warning(f"file {file_path} does not have any of the sequences.")