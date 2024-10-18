import json
import csv

# Path to the JSON and CSV files
json_file_path = 'query_logs.json'
csv_file_path = 'queries.csv'

# Function to convert JSON to CSV
def json_to_csv():
    try:
        # Open the JSON file and load data
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
        
        # Open the CSV file for writing
        with open(csv_file_path, mode='w', newline='') as csv_file:
            # Define the column names
            fieldnames = ['timestamp', 'query', 'response']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            
            # Write the header (column names)
            writer.writeheader()
            
            # Write the data rows
            writer.writerows(data)
        
        print(f"Successfully converted '{json_file_path}' to '{csv_file_path}'")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

# Call the function to convert JSON to CSV
if __name__ == "__main__":
    json_to_csv()
