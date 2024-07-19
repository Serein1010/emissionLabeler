# GCP Emissions Estimator

This project is designed to estimate the carbon emissions associated with the usage of various Google Cloud Platform (GCP) services. The tool processes GCP usage data, calculates the corresponding energy consumption and CO2 emissions, and outputs the results in a structured JSON format. 

## Table of Contents

- [GCP Emissions Estimator](#gcp-emissions-estimator)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Features](#features)
  - [Project Structure](#project-structure)
  - [Installation](#installation)
  - [Configuration](#configuration)


## Introduction

The GCP Emissions Estimator is a tool that helps users understand the environmental impact of their cloud usage on GCP. By processing usage data and applying various estimation techniques, the tool provides insights into energy consumption and CO2 emissions.

## Features

- Processes GCP billing data in JSON format. (Check details in `BillingDataExport.md`)
- Supports various GCP services and usage types.
- Estimates energy consumption (in kilowatt-hours) and CO2 emissions (in metric tons). (Check the `methodology.md`)
- Outputs the results in a structured JSON format.

## Project Structure
```plaintext
.
├── Methodology.md
├── BillingDataExport.md
├── README.md
├── requirements.txt
├── .gitignore
├── ccf/
│   ├── main.py
│   ├── data_processor.py
│   ├── models/
│   │   ├── UsageRecord.py
│   │   ├── IFootprintEstimate.py
│   │   └── ResultStore.py
│   ├── emissions/
│   │   └── getEmissionsFactors.py
│   ├── estimators/
│   │   ├── ComputeEstimator.py
│   │   ├── EmbodiedEmissionsEstimator.py
│   │   ├── MemoryEstimator.py
│   │   ├── NetworkingEstimator.py
│   │   └── StorageEstimator.py
│   ├── utils/
│   │   ├── GCPRegions.py
│   │   ├── helpers.py
│   │   ├── MachineTypes.py
│   │   ├── ReplicationFactors.py
│   │   ├── UnitConversion.py
│   │   └── UsageTypeConstants.py
│   ├── api/
│   │   └── config.py
```

## Installation

To run the project, follow these steps:

1. Clone the repository, make sure your PC works with Python, Python 3.8.10 is recommended
1. Clone the repository, make sure your PC works with Python, Python 3.8.10 is recommended
1. Clone the repository, make sure your PC works with Python, Python 3.8.10 is recommended
2. Install the required dependencies
`pip install -r requirements.txt`
1. Configure the input and output file paths(possibly with the ElectricityMapToken) in api/config.py
2. Run the main script
`python3 ccf/main.py`
1. The processed data will be written to the output file specified in the configuration

## Configuration
`INPUT_FILE_PATH`: Path to the JSON file containing the GCP usage data.

`OUTPUT_FILE_PATH`: Path where the processed output JSON file will be saved.

`ELECTRICITY_MAP_TOKEN`: API token for accessing electricity map data for emissions factors. If not provided, the project will use static emissions factors.