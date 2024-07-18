# Import necessary modules and functions
from collections import defaultdict
from utils.helpers import containsAny
from utils.UnitConversion import convertByteSecondsToGigabyteHours
from emissions import getEmissionsFactors
from models.UsageRecord import UsageRecord
from estimators.ComputeEstimator import ComputeEstimator
from estimators.MemoryEstimator import MemoryEstimator
from models.IFootprintEstimate import getWattsByAverageOrMedian
import json

GCP_CLOUD_CONSTANTS = {
    'SSDCOEFFICIENT': 1.2,  # watt hours / terabyte hour
    'HDDCOEFFICIENT': 0.65,  # watt hours / terabyte hour
    'MIN_WATTS_MEDIAN': 0.68,
    'MIN_WATTS_BY_COMPUTE_PROCESSOR': {
        'CASCADE_LAKE': 0.64,
        'SKYLAKE': 0.65,
        'BROADWELL': 0.71,
        'HASWELL': 1,
        'COFFEE_LAKE': 1.14,
        'SANDY_BRIDGE': 2.17,
        'IVY_BRIDGE': 3.04,
        'AMD_EPYC_1ST_GEN': 0.82,
        'AMD_EPYC_2ND_GEN': 0.47,
        'AMD_EPYC_3RD_GEN': 0.45,
        'NVIDIA_K520': 26,
        'NVIDIA_A10G': 18,
        'NVIDIA_T4': 8,
        'NVIDIA_TESLA_M60': 35,
        'NVIDIA_TESLA_K80': 35,
        'NVIDIA_TESLA_V100': 35,
        'NVIDIA_TESLA_A100': 46,
        'NVIDIA_TESLA_P4': 9,
        'NVIDIA_TESLA_P100': 36,
        'AMD_RADEON_PRO_V520': 26,
    },
    'MAX_WATTS_MEDIAN': 4.11,
    'MAX_WATTS_BY_COMPUTE_PROCESSOR': {
        'CASCADE_LAKE': 3.97,
        'SKYLAKE': 4.26,
        'BROADWELL': 3.69,
        'HASWELL': 4.74,
        'COFFEE_LAKE': 5.42,
        'SANDY_BRIDGE': 8.58,
        'IVY_BRIDGE': 8.25,
        'AMD_EPYC_1ST_GEN': 2.55,
        'AMD_EPYC_2ND_GEN': 1.69,
        'AMD_EPYC_3RD_GEN': 2.02,
        'NVIDIA_K520': 229,
        'NVIDIA_A10G': 153,
        'NVIDIA_T4': 71,
        'NVIDIA_TESLA_M60': 306,
        'NVIDIA_TESLA_K80': 306,
        'NVIDIA_TESLA_V100': 306,
        'NVIDIA_TESLA_A100': 407,
        'NVIDIA_TESLA_P4': 76.5,
        'NVIDIA_TESLA_P100': 306,
        'AMD_RADEON_PRO_V520': 229,
    },
    'NETWORKING_COEFFICIENT': 0.001,  # kWh / Gb
    'MEMORY_COEFFICIENT': 0.000392,  # kWh / Gb
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
    'AVG_CPU_UTILIZATION_2020': 50,
    'REPLICATION_FACTORS': {
        'CLOUD_STORAGE_SINGLE_REGION': 2,
        'CLOUD_STORAGE_DUAL_REGION': 2,
        'CLOUD_STORAGE_MULTI_REGION': 2,
        'COMPUTE_ENGINE_REGIONAL_DISKS': 2,
        'CLOUD_FILESTORE': 2,
        'CLOUD_SQL_HIGH_AVAILABILITY': 2,
        'CLOUD_MEMORY_STORE_REDIS': 2,
        'CLOUD_SPANNER_SINGLE_REGION': 2,
        'CLOUD_SPANNER_MULTI_REGION': 2,
        'KUBERNETES_ENGINE': 3,
        'DEFAULT': 1,
    },
    'KILOWATT_HOURS_BY_SERVICE_AND_USAGE_UNIT': {
        'total': {},
    },
    'ESTIMATE_UNKNOWN_USAGE_BY': 'USAGE_AMOUNT',
    'SERVER_EXPECTED_LIFESPAN': 35040,  # 4 years in hours
}


def get_min_watts(compute_processors):
    min_watts_for_processors = [
        GCP_CLOUD_CONSTANTS['MIN_WATTS_BY_COMPUTE_PROCESSOR'].get(processor, GCP_CLOUD_CONSTANTS['MIN_WATTS_MEDIAN'])
        for processor in compute_processors
    ]
    watts_for_processors = getWattsByAverageOrMedian(compute_processors, min_watts_for_processors)
    return watts_for_processors or GCP_CLOUD_CONSTANTS['MIN_WATTS_MEDIAN']

def get_max_watts(compute_processors):
    max_watts_for_processors = [
        GCP_CLOUD_CONSTANTS['MAX_WATTS_BY_COMPUTE_PROCESSOR'].get(processor, GCP_CLOUD_CONSTANTS['MAX_WATTS_MEDIAN'])
        for processor in compute_processors
    ]
    watts_for_processors = getWattsByAverageOrMedian(compute_processors, max_watts_for_processors)
    return watts_for_processors or GCP_CLOUD_CONSTANTS['MAX_WATTS_MEDIAN']

def get_pue(region):
    region = region.upper().replace('-','_')
    return GCP_CLOUD_CONSTANTS['PUE_TRAILING_TWELVE_MONTH'].get(region, GCP_CLOUD_CONSTANTS['PUE_AVG'])

def getGcpEmissionsFactors(use_carbon_free_energy_percentage=False):
    if use_carbon_free_energy_percentage:
        return {
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
        }
    else:
        return {
            'US_CENTRAL1': 0.000456,
            'US_CENTRAL2': 0.000456,
            'US_EAST1': 0.000434,
            'US_EAST4': 0.000309,
            'US_EAST5': 0.000309,
            'US_WEST1': 0.00006,
            'US_WEST2': 0.00019,
            'US_WEST3': 0.000448,
            'US_WEST4': 0.000365,
            'US_SOUTH1': 0.000296,
            'ASIA_EAST1': 0.000456,
            'ASIA_EAST2': 0.00036,
            'ASIA_NORTHEAST1': 0.000464,
            'ASIA_NORTHEAST2': 0.000384,
            'ASIA_NORTHEAST3': 0.000425,
            'ASIA_SOUTH1': 0.00067,
            'ASIA_SOUTH2': 0.000671,
            'ASIA_SOUTHEAST1': 0.000372,
            'ASIA_SOUTHEAST2': 0.00058,
            'AUSTRALIA_SOUTHEAST1': 0.000598,
            'AUSTRALIA_SOUTHEAST2': 0.000521,
            'EUROPE_CENTRAL2': 0.000576,
            'EUROPE_NORTH1': 0.000127,
            'EUROPE_SOUTHWEST1': 0.000121,
            'EUROPE_WEST1': 0.00011,
            'EUROPE_WEST2': 0.000172,
            'EUROPE_WEST3': 0.000269,
            'EUROPE_WEST4': 0.000283,
            'EUROPE_WEST6': 0.000086,
            'EUROPE_WEST8': 0.000298,
            'EUROPE_WEST9': 0.000059,
            'NORTHAMERICA_NORTHEAST1': 0.000028,
            'NORTHAMERICA_NORTHEAST2': 0.000029,
            'SOUTHAMERICA_EAST1': 0.000129,
            'SOUTHAMERICA_WEST1': 0.00019,
            'ASIA1': 0.000848,  # Sum of asia-northeast1 + asia-northeast2
            'EUR4': 0.00041,  # Sum of europe-west4 + europe-north1
            'NAM4': 0.000828,  # Sum of us-central1 + us-east1
            'ASIA': 0.001676,  # Sum of region group data centers within Asia
            'EU': 0.001843,  # Sum of region group data centers within EU
            'US': 0.002805,  # Sum of all US data centers
            'UNKNOWN': 0.0003171470588,  # Average of the above regions (excludes multi/dual-regions)
        }


