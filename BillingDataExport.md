# How to Get Google's Billing Data

## 1. Export Cloud Billing Data to BigQuery
Check [this guide](https://cloud.google.com/billing/docs/how-to/export-data-bigquery-setup) for detailed instructions.

### Required Setup Steps:
1. **Create a project** where the Cloud Billing data will be stored, and enable billing on the project (if you have not already done so).
2. **Configure permissions** on the project and on the Cloud Billing account.
3. **Enable the BigQuery Data Transfer Service API** (required to export your pricing data).
4. **Create a BigQuery dataset** in which to store the data.
5. **Enable Cloud Billing export** of cost data and pricing data to be written into the dataset.

### 1.1 Grant Roles to Accounts
- **Account 1**
  - **Roles:** `Billing Account Costs Manager`, `Billing Account Administrator`
  - **Function:** Enable and configure the export of Google Cloud billing usage expense data to BigQuery datasets.

- **Account 2**
  - **Roles:** `BigQuery User`, `BigQuery Admin` on the target project
  - **Function:** The `BigQuery User` role is used to access the BigQuery dataset where Cloud Billing data is stored. The `BigQuery Admin` role is used to manage and configure BigQuery datasets and tables.

### 1.2 Select or Create a Project
Google suggests creating a Google Cloud project to contain all of your billing administration needs, as well as the dataset to store the billing data. The Google Cloud project you select to contain your dataset should be linked to the same Cloud Billing account that contains the data that you plan to export to the BigQuery dataset.

### 1.3 Verify that Billing is Enabled
Check [this guide](https://cloud.google.com/billing/docs/how-to/modify-project#confirm_billing_is_enabled_on_a_project) to confirm billing is enabled on a project.

### 1.4 Enable the BigQuery Data Transfer Service API
Follow the instructions [here](https://cloud.google.com/bigquery/docs/enable-transfer-service).

### 1.5 Create a BigQuery Dataset
It is strongly suggested to create the dataset under the specific project which is used to collect all the billing cost data. Remember to choose `multi-region-europe` for the integrity of data, as once you select the region when creating the dataset, you cannot change it later.

Check more details [here](https://cloud.google.com/bigquery/docs/samples/bigquery-create-dataset).

### 1.6 Enable Cloud Billing Export to the BigQuery Dataset
Select the detailed usage report when you export, because the EmissionLabeler only supports analyzing detailed usage reports. After several hours, you should see the results in the selected dataset.

## 2. Export the Billing Data to Google Cloud Storage
Check [this guide](https://cloud.google.com/bigquery/docs/exporting-data) for instructions.

### Steps:
1. Export the billing data in JSON format.
2. Download and store it on your local PC.

## 3. Configure the File Path in `config.py` and Analyze Your Google Cloud Usage Data
Once you have downloaded the billing data, you can configure the file path in `config.py` and start analyzing your Google Cloud usage data.
