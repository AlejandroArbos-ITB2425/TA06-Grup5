import os
import pandas as pd

def check_file_format(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    formats = []
    delimiters = [',', ';', '\t', '|']

    for file in files:
        file_path = os.path.join(directory, file)
        for delimiter in delimiters:
            try:
                df = pd.read_csv(file_path, delimiter=delimiter, nrows=5)
                formats.append((file, df.columns.tolist(), df.dtypes.tolist()))
                break
            except Exception as e:
                continue
        else:
            print(f"Error reading {file}: Could not determine delimiter.")

    if not formats:
        print("No files found or all files failed to read.")
        return

    first_format = formats[0][1:]
    for file, columns, dtypes in formats:
        if (columns, dtypes) != first_format:
            print(f"File {file} has a different format.")
            return

    print("All files have the same format.")

directory = "precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
check_file_format(directory)