import csv
import re
import os
import glob
from pathlib import Path

def load_ris_standards(standards_file):
    """Load RIS standards from CSV file."""
    standards = {}
    try:
        with open(standards_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader, 1):
                if not row or len(row) < 2:
                    print(f"Skipping invalid row {i} in {standards_file}: {row}")
                    continue
                tag = row[0].strip()
                if tag:
                    standards[tag] = {
                        'description': row[1] if len(row) > 1 else '',
                        'notes': row[3] if len(row) > 3 else ''
                    }
                else:
                    print(f"Warning: Empty tag in row {i} of {standards_file}: {row}")
            
            if 'TY' not in standards:
                print("Error: TY field not found in standards. Available keys:", sorted(standards.keys()))
                raise ValueError("TY field missing in RIS_stds.csv")
            
            print("Loaded standards keys:", sorted(standards.keys()))
            return standards
    except Exception as e:
        print(f"Error loading {standards_file}: {e}")
        raise

def parse_ris_file(ris_file):
    """Parse RIS file and return list of references."""
    references = []
    current_ref = {}
    
    with open(ris_file, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('ER'):
            if current_ref and 'TY' in current_ref:
                references.append(current_ref)
                current_ref = {}
            continue
            
        match = re.match(r'^([A-Z0-9]{2})\s*-\s*(.*)$', line)
        if match:
            tag, value = match.groups()
            value = value.strip()
            if value or tag == 'TY':
                if tag in current_ref:
                    if isinstance(current_ref[tag], list):
                        current_ref[tag].append(value)
                    else:
                        current_ref[tag] = [current_ref[tag], value]
                else:
                    current_ref[tag] = value
    
    if current_ref and 'TY' in current_ref:
        references.append(current_ref)
    
    return references

def convert_ris_to_csv(ris_file, standards_file, output_csv):
    """Convert a single RIS file to CSV."""
    try:
        standards = load_ris_standards(standards_file)
        references = parse_ris_file(ris_file)
        
        fields = sorted(standards.keys())
        print(f"CSV header fields for {output_csv}: {fields}")
        
        with open(output_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(fields)
            
            for ref in references:
                row = []
                for field in fields:
                    value = ref.get(field, '')
                    if isinstance(value, list):
                        value = ';'.join(str(v) for v in value)
                    row.append(value)
                writer.writerow(row)
        
        # Validate output
        with open(output_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if 'TY' not in reader.fieldnames:
                print(f"Error: 'TY' field missing in CSV header of {output_csv}")
                return
            for i, row in enumerate(reader, 1):
                if not row['TY']:
                    print(f"Warning: Missing TY field value in reference {i} of {output_csv}")
        
        print(f"Converted {ris_file} to {output_csv}")
    
    except Exception as e:
        print(f"Error converting {ris_file} to {output_csv}: {e}")

def merge_csv_files(csv_folder, merged_output_csv, standards_file):
    """Merge all CSV files in the folder into a single CSV, removing duplicates."""
    try:
        standards = load_ris_standards(standards_file)
        fields = sorted(standards.keys())
        
        unique_rows = set()
        header_written = False
        
        csv_files = glob.glob(os.path.join(csv_folder, "*.csv"))
        if not csv_files:
            print(f"No CSV files found in {csv_folder}")
            return
        
        for csv_file in csv_files:
            if csv_file == merged_output_csv:
                continue
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                if sorted(header) != fields:
                    print(f"Warning: Header mismatch in {csv_file}. Expected: {fields}, Got: {header}")
                    continue
                for row in reader:
                    row_tuple = tuple(row)
                    unique_rows.add(row_tuple)
        
        with open(merged_output_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(fields)
            for row in unique_rows:
                writer.writerow(row)
        
        print(f"Merged {len(csv_files)} CSV files into {merged_output_csv} with {len(unique_rows)} unique rows")
    
    except Exception as e:
        print(f"Error merging CSV files into {merged_output_csv}: {e}")

def convert_csv_to_ris(csv_file, standards_file, output_ris):
    """Convert a CSV file to RIS format."""
    try:
        standards = load_ris_standards(standards_file)
        fields = sorted(standards.keys())
        
        # Identify multi-value fields based on notes in RIS_stds.csv
        multi_value_fields = {tag for tag, info in standards.items() 
                            if 'each' in info['notes'].lower() and 'line' in info['notes'].lower()}
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if sorted(reader.fieldnames) != fields:
                print(f"Error: Header mismatch in {csv_file}. Expected: {fields}, Got: {reader.fieldnames}")
                return
            
            with open(output_ris, 'w', encoding='utf-8') as ris_f:
                for i, row in enumerate(reader, 1):
                    if not row['TY']:
                        print(f"Warning: Skipping reference {i} in {csv_file} due to missing TY field")
                        continue
                    
                    # Write TY first
                    ris_f.write(f"TY  - {row['TY']}\n")
                    
                    # Write other fields
                    for field in fields:
                        if field in ('TY', 'ER') or not row[field]:
                            continue
                        # Handle multi-value fields
                        if field in multi_value_fields:
                            values = row[field].split(';')
                            for value in values:
                                if value.strip():
                                    ris_f.write(f"{field}  - {value.strip()}\n")
                        else:
                            ris_f.write(f"{field}  - {row[field]}\n")
                    
                    # Write ER to end reference
                    ris_f.write("ER  - \n\n")
        
        print(f"Converted {csv_file} to {output_ris}")
    
    except Exception as e:
        print(f"Error converting {csv_file} to {output_ris}: {e}")

def main():
    # Define paths
    ris_folder = '.\RIS'
    standards_file = '.\RIS_stds.csv'
    csv_output_folder = '.\CSV'
    merged_output_csv = '.\merged_output.csv'
    merged_output_ris = '.\merged_output.ris'
    
    # Create output folder if it doesn't exist
    os.makedirs(csv_output_folder, exist_ok=True)
    
    # Check if standards file exists
    if not os.path.exists(standards_file):
        print(f"Error: {standards_file} not found")
        return
    
    # Process each RIS file
    ris_files = glob.glob(os.path.join(ris_folder, "*.ris"))
    if not ris_files:
        print(f"No RIS files found in {ris_folder}")
        return
    
    for ris_file in ris_files:
        ris_filename = Path(ris_file).stem
        output_csv = os.path.join(csv_output_folder, f"{ris_filename}.csv")
        convert_ris_to_csv(ris_file, standards_file, output_csv)
    
    # Merge all CSV files
    merge_csv_files(csv_output_folder, merged_output_csv, standards_file)
    
    # Convert merged CSV to RIS
    if os.path.exists(merged_output_csv):
        convert_csv_to_ris(merged_output_csv, standards_file, merged_output_ris)
    else:
        print(f"Error: Merged CSV file {merged_output_csv} not found")

if __name__ == '__main__':
    main()