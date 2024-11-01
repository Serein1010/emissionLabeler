
# Methodology

## CO2e Estimates

**Total CO2e = Operational Emissions + Embodied Emissions**

- **Operational Emissions = (Cloud provider service usage) x (Cloud energy conversion factors [kWh]) x (Cloud provider Power Usage Effectiveness (PUE)) x (grid emissions factors [metric tons CO2e])**

## Operational Emissions

### Cloud Provider Service Usage

Since Voormedia deploys most of the projects on Google Cloud, we use BigQuery to get GCP Billing Export Table, and the estimation is built on top of the GCP billing results.

One usage record example:

```json
{
    "billing_account_id": "003576-4CB9A5-BC33DB",
    "service": {
        "id": "6F81-5844-456A",
        "description": "Compute Engine"
    },
    "sku": {
        "id": "315D-05CC-A75E",
        "description": "SSD backed PD Capacity in Netherlands"
    },
    "usage_start_time": "2024-05-12 22:00:00 UTC",
    "usage_end_time": "2024-05-12 23:00:00 UTC",
    "project": {
        "id": "voormedia-187708",
        "number": "441570621172",
        "name": "Voormedia",
        "labels": [
            {
                "key": "firebase",
                "value": "enabled"
            }
        ],
        "ancestors": [
            {
                "resource_name": "projects/441570621172",
                "display_name": "Voormedia"
            }
        ]
    },
    "labels": [],
    "system_labels": [],
    "location": {
        "location": "europe-west4",
        "country": "NL",
        "region": "europe-west4"
    },
    "resource": {
        "name": "photoshop-development",
        "global_name": "//compute.googleapis.com/projects/441570621172/zones/europe-west4-a/disk/5731447681477044785"
    },
    "tags": [],
    "price": {
        "effective_price": "0.174592",
        "tier_start_amount": 0,
        "unit": "gibibyte month",
        "pricing_unit_quantity": 1
    },
    "subscription": {},
    "transaction_type": "GOOGLE",
    "export_time": "2024-05-13 01:49:02.981774 UTC",
    "cost": 0.012434,
    "currency": "EUR",
    "currency_conversion_rate": 0.93364999999987552,
    "usage": {
        "amount": 204816252928000,
        "unit": "byte-seconds",
        "amount_in_pricing_units": 0.071217891,
        "pricing_unit": "gibibyte month"
    },
    "credits": [],
    "invoice": {
        "month": "202405"
    },
    "cost_type": "regular",
    "adjustment_info": {},
    "cost_at_list": 0.012434
}
```

### Cloud Provider Power Usage Effectiveness (PUE)

We use a dictionary `GCP_CLOUD_CONSTANTS` to store all the cloud constants that might be useful for calculating. You can find it in `~/.../utils/GcpFootprintEstimationConstant.py`.

```python
'PUE_AVG': 1.1,
'PUE_TRAILING_TWELVE_MONTH': {
    'US_EAST4': 1.08,
    'US_CENTRAL1': 1.11,
    'US_CENTRAL2': 1.11,
    'EUROPE_WEST1': 1.09,
    'EUROPE_WEST4': 1.07,
    'EUROPE_NORTH1': 1.09,
    'ASIA_EAST1': 1.12,
    'ASIA_SOUTHEAST1': 1.13,
},
```

### Grid Emissions Factors

The related codes are in `~/.../emissions/getEmissionsFactors.py`. Two modes to get the emission factor:

1. If you have the token for the ElectricityMap API, the emission labeler will use the API to get the emissions factors in 24 hours. The token can be set in `~/.../api/config.py`.
2. Without a token, the emission labeler will use the constant stored in `~/.../utils/GcpFootprintEstimationConstant.py`, which is determined by the [emission factors of GCP](https://cloud.google.com/sustainability/region-carbon) published by Google.

```python
'US_CENTRAL1': 0.0002152373529,
'US_CENTRAL2': 0.0002152373529,
'US_EAST1': 0.0003255,
'US_EAST4': 0.00011124,
'US_EAST5': 0.00011124,
'US_WEST1': 0.0000072,
'US_WEST2': 0.0000893,
'US_WEST3': 0.00030912,
'US_WEST4': 0.00028835,
'US_SOUTH1': 0.0001776,
'ASIA_EAST1': 0.00037848,
'ASIA_EAST2': 0.0002592,
'ASIA_NORTHEAST1': 0.00038976,
'ASIA_NORTHEAST2': 0.00026496,
'ASIA_NORTHEAST3': 0.00029325,
'ASIA_SOUTH1': 0.000603,
'ASIA_SOUTH2': 0.00061732,
'ASIA_SOUTHEAST1': 0.00035712,
'ASIA_SOUTHEAST2': 0.0005046,
'AUSTRALIA_SOUTHEAST1': 0.00047242,
'AUSTRALIA_SOUTHEAST2': 0.00035949,
'EUROPE_CENTRAL2': 0.0004608,
'EUROPE_NORTH1': 0.00001143,
'EUROPE_SOUTHWEST1': 0.000121,
'EUROPE_WEST1': 0.0000198,
'EUROPE_WEST2': 0.00007396,
'EUROPE_WEST3': 0.0001076,
'EUROPE_WEST4': 0.00013301,
'EUROPE_WEST6': 0.0000129,
'EUROPE_WEST8': 0.000298,
'EUROPE_WEST9': 0.000059,
'NORTHAMERICA_NORTHEAST1': 0,  # Montreal is 100% CFE
'NORTHAMERICA_NORTHEAST2': 0.00000232,
'SOUTHAMERICA_EAST1': 0.00002838,
'SOUTHAMERICA_WEST1': 0.0000589,
'ASIA1': 0.00065472,  # Sum of asia-northeast1 + asia-northeast2
'EUR4': 0.00014444,  # Sum of europe-west4 + europe-north1
'NAM4': 0.00033732,  # Sum of us-central1 + us-east1
'ASIA': 0.00139032,  # Sum of region group data centers within Asia
'EU': 0.00121064,  # Sum of region group data centers within EU
'US': 0.00143137,  # Sum of all US data centers
'UNKNOWN': 0.0002152373529,  # Average across all regions (excluding multi and dual regions)
```

### Cloud Energy Conversion Factors

The billing data record's usage amount has different units (bytes, seconds, gigabyte-months, etc.).

The cloud energy conversion factor can translate usage amount into electricity consumption (unit in kWh).

So we need different algorithms to calculate the factor. The logic of this part is stored in `~/.../data_processor.py`.

#### Usage Type Classification

For each record, we first classify it.

##### Rough Classification

| Unit                 | Classification   |
|----------------------|------------------|
| hours or seconds     | Compute          |
| byte-seconds or gigabyte-months | Storage |
| bytes or gigabytes   | Networking       |
| Others               | Ignored          |

##### Detailed Classification

Please check `~/.../utils/UsageTypeConstants.py` and [Detailed Classification](https://docs.google.com/spreadsheets/d/1vhZNiOvkFH3oKcTV4wkjtw5KKfTFCuSBznEZGRRBdKM/edit?usp=sharing).

##### Calculation for Each Usage Type

- **Compute (CPU)**
  
  ```python
  Average Watts = Min Watts + Avg vCPU Utilization * (Max Watts - Min Watts)
  Compute Watt-Hours = Average Watts * vCPU Hours (or the amount of time servers are being used)
  ```

  | Variable              | Source                                                    |
  |-----------------------|-----------------------------------------------------------|
  | Min Watts             | from SPECPower, or using GCP average                      |
  | Max Watts             | from SPECPower, or using GCP average                      |
  | Avg vCPU Utilization  | from GCP APIs or use constant 50%                         |
  | vCPU Hours            | from cloud usage APIs or billing data                     |

  - The Min Watts/Max Watts is dependent on the CPU processor used by the Cloud provider to host the virtual machines. Based on publicly available information about which CPUs cloud providers use, we looked up the [SPECPower](https://www.spec.org/power_ssj2008/results/power_ssj2008.html) database to determine this constant per processor micro-architecture.
  - If we know the specific processor micro-architecture or group of micro-architectures used for a given cloud provider's virtual machine, we use the minimum and maximum watts for that micro-architecture or the average of the group. When a group includes Ivy Bridge or Sandy Bridge, we use the median of that group to avoid overestimating, as these micro-architectures are considered outliers due to their higher power consumption. Refer to [ProcessorMinMaxWatts](https://github.com/cloud-carbon-footprint/cloud-carbon-coefficients/tree/main/data) with the corresponding minimum and maximum wattages.
  - When the actual average vCPU utilization for a given time period isn't available from a cloud provider's API, we use a projected estimate of 50% average server utilization, based on data from the [2016 U.S. Data Center Energy Usage Report](https://eta.lbl.gov/publications/united-states-data-center-energy).

- **vCPU**
  
  The formula can be expressed as:
  `total vCPU hours = average number of vCPUs provisioned per cluster * the usage amount in hours`.

  For *GCP Kubernetes Engine Compute Estimates*, we assume the number of virtual CPUs provisioned per cluster. For each cluster, we provision a number of "nodes", each representing a Compute Engine machine type. The default machine type is set as "e2-medium". e2-medium has one vCPU provisioned.

  By default, we assume 3 vCPUs provisioned because the default number of nodes for a cluster is 3. And the default machine type 'e2-medium' has only 1 vCPU. The default configuration can be adjusted in the `~/.../api/config.py`.

  For *GCP Cloud Composer Compute Estimates*, there are a number of vCPUs provisioned based on the environment size, with GKE providing a lot of the underlying infrastructure. There are three Cloud Composer Environment sizes, each with a default number of vCPUs that can be provisioned via schedulers, workers, and a web server. In order to estimate the energy from Cloud Composer, we multiply the average number of vCPUs provisioned per environment by the usage amount in hours, to get the total vCPU Hours.

  By default, we assume 14 vCPUs provisioned because this is the default option for a median-sized work environment. The default configuration can be adjusted in the `~/.../api/config.py`.

- **Storage:**
  Basically, we divide storage records into two types: HDD and SSD. We use different coefficients to calculate the energy conversion factors.
  
  - **HDD**
    
    ```
    Watts per Terabyte = 2.14 Watt-Hours per Terabyte-Hour for HDD
    ```
  - **SSD**
    
    ```
    Watts per Terabyte = Watts per disk / Terabytes per disk: 4.35 Watt-Hours per Terabyte-Hour for SSD
    ```
  - **Replication Factors**
    Most cloud providers automatically replicate the data that users stored on cloud to achieve better data availability and durability. So the actual storage size might be multiple times more than the allocated storage sizes that users think they need. The replication factors are used to take this into account in our estimations. It is applied to the total energy and CO2 estimate for each storage or database service. Check [Replication Factors Form](https://docs.google.com/spreadsheets/d/1vhZNiOvkFH3oKcTV4wkjtw5KKfTFCuSBznEZGRRBdKM/edit?gid=1539529180#gid=1539529180) for more details.

    ```python
    if service_name in GCP_REPLICATION_FACTORS_FOR_SERVICES:
        service_function = GCP_REPLICATION_FACTORS_FOR_SERVICES[service_name]
        if service_name == SERVICES["COMPUTE_ENGINE"]:
            return service_function(usage_type, region)
        else:
            return service_function(usage_type)
    return REPLICATION_FACTORS['DEFAULT']
    ```

- **Network**
  We can confidently assume that hyper-scale cloud providers maintain highly energy-efficient networks between their data centers, utilizing their own optical fiber networks and submarine cables. Data exchanges between these centers occur at very high bitrates (~100 GbE, or 100 Gbps), representing the most efficient use case. Based on these assumptions, we have chosen to use the smallest available coefficient: 0.001 kWh/Gb. We invite feedback and contributions to further refine this coefficient.

- **Memory**
  - 0.625 W/GB, 0.000625 Kilowatt Hour / Gigabyte Hour.

Kilowatt hours = Memory usage (GB-Hours) x Memory coefficient

Overestimation exists because of the overlapping with Computing estimation using SPEC.

