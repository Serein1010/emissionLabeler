from models.UsageRecord import UsageRecord
from utils.GCPRegions import GCP_REGIONS
from typing import Dict, Optional, Any
from utils.CloudConstantsType import CloudConstantsEmissionsFactors
from utils.UnitConversion import convertGramsToMetricTons
import requests
import time
from datetime import datetime
from api import config

MappedRegionsToElectricityMapZones = Dict[str, Optional[str]]

def get_emissions_factors(region: str, dateTime: str, emissionsFactors: CloudConstantsEmissionsFactors, mappedRegionsToElectricityMapZones: MappedRegionsToElectricityMapZones, zoneIntensityFactors) -> CloudConstantsEmissionsFactors:
    try:
        regionInMappedDict = GCP_REGIONS(region)
    except ValueError:
        raise ValueError(f"Invalid region for GCP_REGIONS: {region}")
    region = region.upper().replace('-','_')
    electricityMapsZone =  mappedRegionsToElectricityMapZones.get(regionInMappedDict)
    electricityMapsToken = config.ELECTRICITY_MAP_TOKEN
    if (not electricityMapsToken or not electricityMapsZone):
        if (electricityMapsToken and  not electricityMapsZone):
            pass
        return emissionsFactors
    formatted_date_time = datetime.strptime(dateTime, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%dT%H:%M:%S.00Z")
    formatted_date_time_obj = datetime.strptime(formatted_date_time, "%Y-%m-%dT%H:%M:%S.00Z")
    if formatted_date_time in zoneIntensityFactors and electricityMapsZone in zoneIntensityFactors[formatted_date_time]:
        return {region: zoneIntensityFactors[formatted_date_time][electricityMapsZone]}
    else:
        for key in zoneIntensityFactors:
            key_date_time_obj = datetime.strptime(key, "%Y-%m-%dT%H:%M:%S.00Z")
            if key_date_time_obj.hour == formatted_date_time_obj.hour and electricityMapsZone in zoneIntensityFactors[key]:
                return {region: zoneIntensityFactors[key][electricityMapsZone]}
    try:
        response = get_electricity_maps_data(electricityMapsZone, formatted_date_time, electricityMapsToken, zoneIntensityFactors)
    except Exception as e:
        raise Exception(f'Failed to get data from Electricity Maps. Reason: {str(e)}.')
    if not response or 'carbonIntensity' not in response:
        return emissionsFactors
    carbon_intensity = convertGramsToMetricTons(response['carbonIntensity'])
    if formatted_date_time in zoneIntensityFactors:
        zoneIntensityFactors[formatted_date_time][electricityMapsZone] = carbon_intensity
    else:
        zoneIntensityFactors[formatted_date_time] = {electricityMapsZone: carbon_intensity}  
    return {region: zoneIntensityFactors[formatted_date_time][electricityMapsZone]}
    
   

def get_electricity_maps_data(electricityMapsZone: str, dateTime: str, electricityMapsToken, zoneIntensityFactors: Dict[str, Dict[str, float]]) -> Any:
    url = f'https://api.electricitymap.org/v3/carbon-intensity/history?zone={electricityMapsZone}'
    headers = {'auth-token': electricityMapsToken}
    
    max_retries = 5  
    backoff_factor = 1  
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            if response.status_code == 200:
                break
        except requests.RequestException as e:
            wait_time = backoff_factor * (2 ** attempt)
            print(f'Rate limit exceeded. Retrying in {wait_time} seconds...')
            time.sleep(wait_time)
            
    target_hour = datetime.strptime(dateTime, "%Y-%m-%dT%H:%M:%S.%fZ").hour 
    result_entry = []
    data = response.json()

    if isinstance(data, dict) and "history" in data:
        entries = data["history"]
        for entry in entries:
            if isinstance(entry, dict) and "datetime" in entry:
                carbon_intensity = convertGramsToMetricTons(entry["carbonIntensity"])
                entry_date_time = datetime.strptime(entry["datetime"], "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_entry_date_time = entry_date_time.strftime("%Y-%m-%dT%H:%M:%S.00Z") 
                if not (formatted_entry_date_time in zoneIntensityFactors):
                    zoneIntensityFactors[formatted_entry_date_time] = {electricityMapsZone: carbon_intensity}
                elif formatted_entry_date_time in zoneIntensityFactors and (not (electricityMapsZone in zoneIntensityFactors[formatted_entry_date_time])): 
                    zoneIntensityFactors[formatted_entry_date_time][electricityMapsZone] = carbon_intensity    
                ## match the request's hour and the usage's hour 
                entry_hour = entry_date_time.hour
                if entry_hour == target_hour:
                    print(f"Emission factor from Electricity Map found, Requesting URL: {url}")  
                    result_entry = entry
          
    return result_entry

