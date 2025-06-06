from enum import Enum
from typing import Dict, Optional

class GCP_REGIONS(Enum):
    ASIA_EAST1 = 'asia-east1'
    ASIA_EAST2 = 'asia-east2'
    ASIA_NORTHEAST1 = 'asia-northeast1'
    ASIA_NORTHEAST2 = 'asia-northeast2'
    ASIA_NORTHEAST3 = 'asia-northeast3'
    ASIA_SOUTH1 = 'asia-south1'
    ASIA_SOUTH2 = 'asia-south2'
    ASIA_SOUTHEAST1 = 'asia-southeast1'
    ASIA_SOUTHEAST2 = 'asia-southeast2'
    AUSTRALIA_SOUTHEAST1 = 'australia-southeast1'
    AUSTRALIA_SOUTHEAST2 = 'australia-southeast2'
    EUROPE_CENTRAL2 = 'europe-central2'
    EUROPE_NORTH1 = 'europe-north1'
    EUROPE_SOUTHWEST1 = 'europe-southwest1'
    EUROPE_WEST1 = 'europe-west1'
    EUROPE_WEST2 = 'europe-west2'
    EUROPE_WEST3 = 'europe-west3'
    EUROPE_WEST4 = 'europe-west4'
    EUROPE_WEST6 = 'europe-west6'
    EUROPE_WEST8 = 'europe-west8'
    EUROPE_WEST9 = 'europe-west9'
    EUROPE_WEST10 = 'europe-west10'
    EUROPE_WEST12 = 'europe-west12'
    NORTHAMERICA_NORTHEAST1 = 'northamerica-northeast1'
    NORTHAMERICA_NORTHEAST2 = 'northamerica-northeast2'
    SOUTHAMERICA_EAST1 = 'southamerica-east1'
    SOUTHAMERICA_WEST1 = 'southamerica-west1'
    US_CENTRAL1 = 'us-central1'
    US_CENTRAL2 = 'us-central2'
    US_EAST1 = 'us-east1'
    US_EAST2 = 'us-east2' #
    US_EAST4 = 'us-east4'
    US_EAST5 = 'us-east5'
    US_SOUTH1 = 'us-south1'
    US_WEST1 = 'us-west1'
    US_WEST2 = 'us-west2' 
    US_WEST3 = 'us-west3'
    US_WEST4 = 'us-west4' #
    US_WEST8 = 'us-west8' #
    UNKNOWN = 'UNKNOWN'
    US = 'us' #
    GLOBAL = 'global' #
    EUROPE_WEST1_B = 'europe-west1-b' #
    EUROPE = 'europe' #

class GCP_DUAL_REGIONS(Enum):
    ASIA1 = 'asia1'
    EUR4 = 'eur4'
    NAM4 = 'nam4'

class GCP_MULTI_REGIONS(Enum):
    ASIA = 'asia'
    EU = 'europe'
    US = 'us'

GCP_MAPPED_REGIONS_TO_ELECTRICITY_MAPS_ZONES: Dict[GCP_REGIONS, Optional[str]] = {
    GCP_REGIONS.ASIA_EAST1: 'TW',
    GCP_REGIONS.ASIA_EAST2: None,
    GCP_REGIONS.ASIA_NORTHEAST1: 'JP-TK',
    GCP_REGIONS.ASIA_NORTHEAST2: 'JP-KN',
    GCP_REGIONS.ASIA_NORTHEAST3: 'KR',
    GCP_REGIONS.ASIA_SOUTH1: 'IN-WE',
    GCP_REGIONS.ASIA_SOUTH2: 'IN-NO',
    GCP_REGIONS.ASIA_SOUTHEAST1: 'SG',
    GCP_REGIONS.ASIA_SOUTHEAST2: 'ID',
    GCP_REGIONS.AUSTRALIA_SOUTHEAST1: 'AU-NSW',
    GCP_REGIONS.AUSTRALIA_SOUTHEAST2: 'AU-VIC',
    GCP_REGIONS.EUROPE_CENTRAL2: 'PL',
    GCP_REGIONS.EUROPE_NORTH1: 'FI',
    GCP_REGIONS.EUROPE_SOUTHWEST1: 'ES',
    GCP_REGIONS.EUROPE_WEST1: 'BE',
    GCP_REGIONS.EUROPE_WEST2: 'GB',
    GCP_REGIONS.EUROPE_WEST3: 'DE',
    GCP_REGIONS.EUROPE_WEST4: 'NL',
    GCP_REGIONS.EUROPE_WEST6: 'CH',
    GCP_REGIONS.EUROPE_WEST8: 'IT-NO',
    GCP_REGIONS.EUROPE_WEST9: 'FR',
    GCP_REGIONS.EUROPE_WEST10: 'DE',
    GCP_REGIONS.EUROPE_WEST12: 'IT-NO',
    GCP_REGIONS.NORTHAMERICA_NORTHEAST1: 'CA-QC',
    GCP_REGIONS.NORTHAMERICA_NORTHEAST2: 'CA-ON',
    GCP_REGIONS.SOUTHAMERICA_EAST1: 'BR-CS',
    GCP_REGIONS.SOUTHAMERICA_WEST1: 'CL-SEN',
    GCP_REGIONS.US_CENTRAL1: 'US-MIDW-MISO', # Midwest region of the United States
    GCP_REGIONS.US_CENTRAL2: 'US-MIDW-MISO',
    GCP_REGIONS.US_EAST1: 'US-CAR-SCEG',
    GCP_REGIONS.US_EAST4: 'US-MIDA-PJM',
    GCP_REGIONS.US_EAST5: 'US-MIDA-PJM',
    GCP_REGIONS.US_SOUTH1: 'US-TEX-ERCO',
    GCP_REGIONS.US_WEST1: 'US-NW-PACW',
    GCP_REGIONS.US_WEST2: 'US-CAL-CISO',
    GCP_REGIONS.US_WEST3: 'US-NW-PACE',
    GCP_REGIONS.US_WEST4: 'US-NW-NEVP',
    GCP_REGIONS.UNKNOWN: None,
}