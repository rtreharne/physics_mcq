import os
import csv

def combine_csv_files(input_folder, output_file, recursive=True):
    first_file = True
    with open(output_file, mode='w', newline='', encoding='utf-8') as out_csv:
        writer = None

        for root, _, files in os.walk(input_folder):
            for file in files:
                if file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    with open(file_path, mode='r', newline='', encoding='utf-8') as in_csv:
                        reader = csv.reader(in_csv)
                        header = next(reader)  # Read header

                        # Write header once
                        if first_file:
                            writer = csv.writer(out_csv)
                            writer.writerow(header)
                            first_file = False

                        # Write rows
                        for row in reader:
                            writer.writerow(row)

            if not recursive:
                break

    print(f"Combined CSV files written to '{output_file}'.")

# Example usage
if __name__ == "__main__":
    input_folder = "questions/"
    output_file = "combined_quiz.csv"
    combine_csv_files(input_folder, output_file)
