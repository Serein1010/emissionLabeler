import json, datetime
from api import config
from data_processor import DataProcessor
from utils.GCPRegions import GCP_MAPPED_REGIONS_TO_ELECTRICITY_MAPS_ZONES, GCP_REGIONS


def convert_date(o):
    if isinstance(o, datetime.date):
        return o.strftime('%Y-%m-%d')

def main(file_path):
    json_input = []  
    with open(file_path, 'r') as file:  
         for line in file:
            line = line.strip()
            if line: 
                try:
                    json_input.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON line: {line}")
                    print(e)

    processor = DataProcessor(json_input, granularity='Day')
    processor.process()
    output = processor.get_results()
   
    output_file_path = config.OUTPUT_FILE_PATH
    json_data = json.dumps(output, default=convert_date, indent=4)
    
    with open(output_file_path, 'w') as file:
        file.write(json_data)
    print(f"Data has been written to {output_file_path}")

    

if __name__ == "__main__":
    input_file_path = config.INPUT_FILE_PATH
    main(input_file_path)




