from collections import defaultdict
from models.UsageRecord import UsageRecord
from models.IFootprintEstimate import IFootprintEstimate, accumulateKilowattsHours
from estimators.ComputeEstimator import ComputeEstimator
from estimators.MemoryEstimator import MemoryEstimator
from estimators.NetworkingEstimator import NetworkingEstimator
from estimators.StorageEstimator import StorageEstimator
from estimators.embodiedEmissionsEstimator import EmbodiedEmissionsEstimator
from estimators.UnknownEstimator import UnknownEstimator
from utils.UsageTypeConstants import MEMORY_USAGE_TYPES,UNKNOWN_USAGE_UNITS, UNKNOWN_USAGE_TYPES, UNKNOWN_SERVICE_TYPES, UNSUPPORTED_USAGE_TYPES, COMPUTE_STRING_FORMATS, NETWORKING_STRING_FORMATS
from utils.helpers import containsAny, startsWith
from utils.UnitConversion import convertByteSecondsToGigabyteHours, convertByteSecondsToTerabyteHours, convertBytesToGigabytes
from emissions import getEmissionsFactors
import utils.GcpFootprintEstimationConstant as GcpFootprintEstimationConstant
from utils.ReplicationFactors import GCP_REPLICATION_FACTORS_FOR_SERVICES, SERVICES, REPLICATION_FACTORS
from utils.MachineTypes import MACHINE_FAMILY_SHARED_CORE_TO_MACHINE_TYPE_MAPPING, MACHINE_FAMILY_TO_MACHINE_TYPE_MAPPING, GPU_MACHINE_TYPES, N1_SHARED_CORE_MACHINE_FAMILY_TO_MACHINE_TYPE_MAPPING, INSTANCE_TYPE_COMPUTE_PROCESSOR_MAPPING, SHARED_CORE_PROCESSORS
from utils.ComputeProcessorType import COMPUTE_PROCESSOR_TYPES
from utils.GCPRegions import GCP_MAPPED_REGIONS_TO_ELECTRICITY_MAPS_ZONES
from utils.GcpFootprintEstimationConstant import GCP_CLOUD_CONSTANTS, getGcpEmissionsFactors
import json
from typing import Dict, Optional
from datetime import datetime, timezone

class DataProcessor:
    def __init__(self, json_data, granularity='Day'):
        self.records = [UsageRecord(record) for record in json_data]
        self.processed_data = defaultdict(lambda: defaultdict(list))
        self.unknown_records = []
        self.unsupported_records = []
        self.knownresults = defaultdict(list)
        self.granularity = granularity
        self.zoneIntensityFactors: Dict[str, Dict[str, float]] = {} 
        ### unknown_dic for calculating the ratio of kilowatthours and usageAmount(for different combinations of serviceName and usageUnit)
        ### then we can use unknown_dic to calculate the unknown usage records
        self.unknown_dic = {}


        # self.count_total_record = 0
        # self.count_unknown_record = 0
    def get_unsupported_records(self):
        for element in self.unsupported_records:
            print(element.serviceName, element.region, element.usageType, element.usageAmount, element.usageUnit)
        return
    
    def get_unknown_dic(self):
        for key, value in self.unknown_dic.items():
            print(key, value)
        return

    
    def process(self):
        for record in self.records:
            # ##### 调试用
            # self.count_total_record = self.count_total_record + 1
            # #####
            dt = record.usage_start_time
            dateTime = dt.strftime("%Y-%m-%dT%H:%M:%S.00Z")
            # print(f'datetime in processor {dateTime} type{type(dateTime)}')
            emissionsFactors = getEmissionsFactors.get_emissions_factors(record.region, dateTime, getGcpEmissionsFactors(),  GCP_MAPPED_REGIONS_TO_ELECTRICITY_MAPS_ZONES, self.zoneIntensityFactors) 
            # print(f'self.zoneIntensityFactors: Dict[str, Dict[str, float]] = {self.zoneIntensityFactors}')
            estimator = self.get_estimator(record, emissionsFactors)
            if estimator:
                self.knownResultGranularity(record, estimator)
        ### 遍历unknown_records,用UnknownEstimator计算energy_estimate等数值
        ### 将每一条都转换为标准result格式，加入known_results字典列表
        for record in self.unknown_records:
            unknown_record_estimate = self.getEstimateForUnknownUsage(record)
            # print(f'here{unknown_record_estimate.energy_estimate}')
            if unknown_record_estimate:
                self.knownResultGranularity(record, unknown_record_estimate)
        # for record in self.unsupported_records:
        #     unsupported_record_estimate = self.getEstimateForUnknownUsage(record)
        #     if unsupported_record_estimate:
        #         self.knownResultGranularity(record, unsupported_record_estimate)          
                
    def knownResultGranularity(self, record:UsageRecord, estimator:IFootprintEstimate):
        if self.granularity == 'Day':
            timestamp = str(record.groupByDay)
        elif self.granularity == 'Hour':
            timestamp = str(record.usage_start_time)
        result = {
            'cloudProvider': "GCP",
            'kilowattHours': estimator.energy_estimate,
            'co2e': estimator.co2_estimate,
            'usesAverageCPUConstant': estimator.usesAverageCPUConstant,
            'serviceName': record.serviceName,
            'accountId': record.accountId,
            'accountName': record.accountName,
            'region': record.region,
            'cost': record.cost,
        }
        self.knownresults[timestamp].append(result)


    def aggregate_results(self):
        aggregated_results = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        for timestamp, records in self.knownresults.items():
            for record in records:
                key = (record['serviceName'], record['accountId'], record['region'])
                if key not in aggregated_results[timestamp]:
                    aggregated_results[timestamp][key] = {
                        'cloudProvider': "GCP",
                        'kilowattHours': 0,
                        'co2e': 0,
                        'usesAverageCPUConstant': record['usesAverageCPUConstant'],
                        'serviceName': record['serviceName'],
                        'accountId': record['accountId'],
                        'accountName': record['accountName'],
                        'region': record['region'],
                        'cost': 0,
                    }
                aggregated_results[timestamp][key]['kilowattHours'] += record['kilowattHours']
                aggregated_results[timestamp][key]['co2e'] += record['co2e']
                aggregated_results[timestamp][key]['cost'] += record['cost']
        return aggregated_results    
        
    def get_results(self):
        aggregated_results = self.aggregate_results()
        final_results = []
        for timestamp, services in aggregated_results.items():
            service_estimates = list(services.values())
            aggregated_result = {
                'timestamp': timestamp,
                'serviceEstimates': service_estimates,
                'groupBy': self.granularity,
            }
            final_results.append(aggregated_result)
        return final_results


    def get_estimator(self, record:UsageRecord, emissionsFactors): 
        if self.isUnknownUsage(record):
            serviceName = record.serviceName
            usageAmount = record.usageAmount
            usageType = record.usageType            
            self.unknown_records.append(record)
            return 
        elif self.isUnsupportedUsage(record.usageType):
            self.unsupported_records.append(record)
            return 
        else:
            return self.getEstimateByUsageUnit(record, emissionsFactors)
            
        
    def isUnknownUsage(self, record:UsageRecord):
        return (
            containsAny(UNKNOWN_USAGE_TYPES, record.usageType) or 
            containsAny(UNKNOWN_SERVICE_TYPES, record.serviceName) or 
            containsAny(UNKNOWN_USAGE_UNITS, record.usageUnit)
        )

    def isUnsupportedUsage(self, usageType):
        return containsAny(UNSUPPORTED_USAGE_TYPES, usageType)

    def isComputeUsage(self, usageType):
        return containsAny(COMPUTE_STRING_FORMATS, usageType)

    def isMemoryUsage(self, usageType):
        # ##### 调试
        # print(" ")
        # print(usageType)
        # print(containsAny(MEMORY_USAGE_TYPES, usageType))
        # print(containsAny(COMPUTE_STRING_FORMATS, usageType))
        # ##### 
        return (containsAny(MEMORY_USAGE_TYPES, usageType) and (not containsAny(COMPUTE_STRING_FORMATS, usageType)))
    
    def isNetworkUsage(self, usageType):
        # ##### 调试
        # print(" ")
        # print(usageType)
        # print(containsAny(NETWORKING_STRING_FORMATS, usageType))
        # #####
        return containsAny(NETWORKING_STRING_FORMATS, usageType)

    def getReplicationFactor(self, record:UsageRecord):
        service_name = record.serviceName
        usage_type = record.usageType
        region = record.region

        if service_name in GCP_REPLICATION_FACTORS_FOR_SERVICES:
            service_function = GCP_REPLICATION_FACTORS_FOR_SERVICES[service_name]
            if service_name == SERVICES["COMPUTE_ENGINE"]:
                return service_function(usage_type, region)
            else:
                return service_function(usage_type)
        return REPLICATION_FACTORS['DEFAULT']

    def getEstimateByUsageUnit(self, record:UsageRecord, emissionsFactors):
        powerUsageEffectiveness  = GcpFootprintEstimationConstant.get_pue(region = record.region)

        ## 调试
        # print("here0")
        ## 
        if(record.usageUnit == 'seconds'):
            # # 调试
            # print("here1")
            # # 
            if (self.isComputeUsage(record.usageType)): 
                # # 调试
                # print("here2")
                # # 
                computeFootprint = self.getComputeFootprintEstimate(record, powerUsageEffectiveness,emissionsFactors)
                
                # # 调试
                # print(f'computeFootprint is : {computeFootprint.energy_estimate}') 
                # #
                
                embodiedEmissions = self.getEmbodiedEmissions(record, emissionsFactors)
                
                # # 调试
                # print(f'embodiedEmissions is : {embodiedEmissions.energy_estimate}') 
                # #
                
                if(embodiedEmissions.co2_estimate):
                    computeAndEmbodiedEmissionsFootprintEstimate = IFootprintEstimate(
                        timestamp = record.groupByDay, 
                        energy_estimate = embodiedEmissions.energy_estimate + computeFootprint.energy_estimate,
                        co2_estimate = embodiedEmissions.co2_estimate + computeFootprint.co2_estimate,
                        region = record.region,
                        usesAverageCPUConstant = computeFootprint.usesAverageCPUConstant
                    )
                    return computeAndEmbodiedEmissionsFootprintEstimate
                return computeFootprint
            else:
                self.unknown_records.append(record)

        elif(record.usageUnit == 'byte-seconds'):
            if (self.isMemoryUsage(record.usageType)): 
                return self.getMemoryFootprintEstimate(record, powerUsageEffectiveness,emissionsFactors)
            else:
                return self.getStoragefootprintEstimate(record, powerUsageEffectiveness,emissionsFactors)
        elif(record.usageUnit == 'bytes'):
            if (self.isNetworkUsage(record.usageType)): 
                return self.getNetworkingFootprintEstimate(record, powerUsageEffectiveness, emissionsFactors)
            else:
                self.unknown_records.append(record)
        else:
            ## 调试
            # print("here4")
            ## 
            print(f"Unsupported Usage unit:{record.usageUnit}, Unsupported Usage type:{record.usageType}")
    
    def getEstimateForUnknownUsage(self, record:UsageRecord):
        if self.granularity == 'Day':
            timestamp = str(record.groupByDay)
        elif self.granularity == 'Hour':
            timestamp = str(record.usage_start_time)
        unknownUsage = {
            'timestamp': timestamp,
            'usageAmount': record.usageAmount,
            'usageUnit': record.usageUnit,
            'serviceName': record.serviceName,
            'replicationFactor': self.getReplicationFactor(record),
        }
        self.unknownestimator = UnknownEstimator()
        unknownFootprint = self.unknownestimator.estimate(unknownUsage, record.region, getGcpEmissionsFactors(), self.unknown_dic)
        return unknownFootprint

    def getComputeFootprintEstimate(self, record:UsageRecord, powerUsageEffectiveness, emissionsFactors):
        if self.granularity == 'Day':
            timestamp = str(record.groupByDay)
        elif self.granularity == 'Hour':
            timestamp = str(record.usage_start_time)
        isGPUComputeUsage = 'GPU' in record.usageType
        computeUsage = {
            'cpuUtilizationAverage': GcpFootprintEstimationConstant.GCP_CLOUD_CONSTANTS['AVG_CPU_UTILIZATION_2020'],
            'vCpuHours': record.gpuHours if isGPUComputeUsage else record.getVCpuHours(),
            'usesAverageCpuConstant': True,
            'timestamp': timestamp,
        }
        if isGPUComputeUsage:
            computeProcessors = self.getGpuComputeProcessorsFromUsageType(record.usageType)
        else:
            computeProcessors = self.getComputeProcessorsFromMachineType(record.machineType)
        computeConstants = {
            'minWatts': GcpFootprintEstimationConstant.get_min_watts(computeProcessors),
            'maxWatts': GcpFootprintEstimationConstant.get_max_watts(computeProcessors),
            'powerUsageEffectiveness': powerUsageEffectiveness,
            'replicationFactor': self.getReplicationFactor(record),
            'averageWatts': None
        }
        self.computeestimator = ComputeEstimator()
        computeFootprint = self.computeestimator.estimate(computeUsage, record, emissionsFactors, computeConstants)
        
        if computeFootprint:
             accumulateKilowattsHours(self.unknown_dic, record, computeFootprint.energy_estimate)
        return computeFootprint

    def getGpuComputeProcessorsFromUsageType(self, usageType):
        gpuComputeProcessors = [processor for processor in GPU_MACHINE_TYPES if startsWith(usageType, processor)]
        return gpuComputeProcessors if gpuComputeProcessors else GPU_MACHINE_TYPES

    def getComputeProcessorsFromMachineType(self, machineType):
        
        #### 调试用
        # print(f"the type of SHARED_CORE_PROCESSORS: {type(SHARED_CORE_PROCESSORS)}" )
        # print(f"the machineType: {record.machineType}") 
        #### 
        # sharedCoreMatch = (
        #     machineType and next((core.value for core in SHARED_CORE_PROCESSORS if core.value in machineType), None)
        # )  
        sharedCoreMatch = None
        if machineType:
            for core in SHARED_CORE_PROCESSORS:
                if core.value in machineType:
                    sharedCoreMatch = core.value
                    break

        includes_prefix = machineType[:2].lower() if machineType else ''
        processor = sharedCoreMatch if sharedCoreMatch else includes_prefix

        return INSTANCE_TYPE_COMPUTE_PROCESSOR_MAPPING.get(processor, [COMPUTE_PROCESSOR_TYPES.UNKNOWN])


    def getEmbodiedEmissions(self, record:UsageRecord,  emissionsFactors):
        if self.granularity == 'Day':
            timestamp = str(record.groupByDay)
        elif self.granularity == 'Hour':
            timestamp = str(record.usage_start_time)
        data = self.getDataFromMachineType(record.machineType)
        instancevCpu = data['instancevCpu']
        if (instancevCpu == 0):
            # print(f"instancevCpu is 0 for machineType:{record.machineType}")
            embodied_zero_footprint_estimate = IFootprintEstimate(
                timestamp = timestamp,  
                energy_estimate = 0,
                co2_estimate = 0,
                region = record.region,
                usesAverageCPUConstant = False,
            )
            return embodied_zero_footprint_estimate  
        scopeThreeEmissions = data['scopeThreeEmissions']
        largestInstancevCpu = data['largestInstancevCpu']
        usageTimePeriod = record.usageAmount / instancevCpu / 3600
        self.embodiedEmissionsEstimator = EmbodiedEmissionsEstimator(GcpFootprintEstimationConstant.GCP_CLOUD_CONSTANTS["SERVER_EXPECTED_LIFESPAN"])
        return self.embodiedEmissionsEstimator.estimate(usageTimePeriod, instancevCpu, scopeThreeEmissions, largestInstancevCpu, record, emissionsFactors)

    def getDataFromMachineType(self, machineType: Optional[str]) -> Dict[str, int]:
        if not machineType:
            return {
                "instancevCpu": 0,
                "scopeThreeEmissions": 0,
                "largestInstancevCpu": 0,
            }

        machineFamily = '-'.join(machineType.split('-')[:2])
        machineFamilySharedCore = machineType.split('-')[0]

        instancevCpu = (
            MACHINE_FAMILY_TO_MACHINE_TYPE_MAPPING.get(machineFamily, {}).get(machineType, [0])[0] or
            MACHINE_FAMILY_SHARED_CORE_TO_MACHINE_TYPE_MAPPING.get(machineFamilySharedCore, {}).get(machineType, [0])[0] or
            N1_SHARED_CORE_MACHINE_FAMILY_TO_MACHINE_TYPE_MAPPING.get(machineType, [0])[0]
        )

        scopeThreeEmissions = (
            MACHINE_FAMILY_TO_MACHINE_TYPE_MAPPING.get(machineFamily, {}).get(machineType, [0, 0])[1] or
            MACHINE_FAMILY_SHARED_CORE_TO_MACHINE_TYPE_MAPPING.get(machineFamilySharedCore, {}).get(machineType, [0, 0])[1] or
            N1_SHARED_CORE_MACHINE_FAMILY_TO_MACHINE_TYPE_MAPPING.get(machineType, [0, 0])[1]
        )

        familyMachineTypes = list(
            MACHINE_FAMILY_TO_MACHINE_TYPE_MAPPING.get(machineFamily, {}).values() or
            MACHINE_FAMILY_SHARED_CORE_TO_MACHINE_TYPE_MAPPING.get(machineFamilySharedCore, {}).values() or
            N1_SHARED_CORE_MACHINE_FAMILY_TO_MACHINE_TYPE_MAPPING.values()
        )

        largestInstancevCpu = familyMachineTypes[-1][0] if familyMachineTypes else 0

        return {
            "instancevCpu": instancevCpu,
            "scopeThreeEmissions": scopeThreeEmissions,
            "largestInstancevCpu": largestInstancevCpu,
        }


    def getMemoryFootprintEstimate(self, record:UsageRecord, powerUsageEffectiveness, emissionsFactors):
        MemoryUsage = convertByteSecondsToGigabyteHours(record.usageAmount) 
        self.memoryestimator = MemoryEstimator(GcpFootprintEstimationConstant.GCP_CLOUD_CONSTANTS["MEMORY_COEFFICIENT"])
        ## Comes from TEMPLATES: 
        #   new ComputeEstimator(),
        #   new StorageEstimator(GCP_CLOUD_CONSTANTS.SSDCOEFFICIENT),
        #   new StorageEstimator(GCP_CLOUD_CONSTANTS.HDDCOEFFICIENT),
        #   new NetworkingEstimator(GCP_CLOUD_CONSTANTS.NETWORKING_COEFFICIENT),
        #   new MemoryEstimator(GCP_CLOUD_CONSTANTS.MEMORY_COEFFICIENT),
        #   new UnknownEstimator(GCP_CLOUD_CONSTANTS.ESTIMATE_UNKNOWN_USAGE_BY),
        #   new EmbodiedEmissionsEstimator(
        #     GCP_CLOUD_CONSTANTS.SERVER_EXPECTED_LIFESPAN,
        #   ),
        #   new BigQuery(),
        memoryFootprint = self.memoryestimator.estimate(MemoryUsage, record, powerUsageEffectiveness, emissionsFactors)
        if(memoryFootprint):
            memoryFootprint.usesAverageCPUConstant = False
            accumulateKilowattsHours(self.unknown_dic, record, memoryFootprint.energy_estimate)
        return memoryFootprint
    
    
    def getStoragefootprintEstimate(self, record:UsageRecord, powerUsageEffectiveness, emissionsFactors):
        StorageUsage = convertByteSecondsToTerabyteHours(record.usageAmount)
        replicationFactor = self.getReplicationFactor(record)     
        if ('SSD' in record.usageType):
            self.ssdStorageEstimator = StorageEstimator(GcpFootprintEstimationConstant.GCP_CLOUD_CONSTANTS["SSDCOEFFICIENT"])
            storageEstimator = self.ssdStorageEstimator
        else:
            self.hhdStorageEstimator = StorageEstimator(GcpFootprintEstimationConstant.GCP_CLOUD_CONSTANTS["HDDCOEFFICIENT"])
            storageEstimator = self.hhdStorageEstimator
        storageFootprint = storageEstimator.estimate(StorageUsage, record, powerUsageEffectiveness, emissionsFactors, replicationFactor)
        if(storageFootprint):
            storageFootprint.usesAverageCPUConstant = False
            accumulateKilowattsHours(self.unknown_dic, record, storageFootprint.energy_estimate)
        return storageFootprint
    
    def getNetworkingFootprintEstimate(self, record:UsageRecord, powerUsageEffectiveness, emissionsFactors):
        NetworkingUsage = convertBytesToGigabytes(record.usageAmount) 
        self.networkingestimator = NetworkingEstimator(GcpFootprintEstimationConstant.GCP_CLOUD_CONSTANTS["NETWORKING_COEFFICIENT"])
        networkingFootprint = self.networkingestimator.estimate(NetworkingUsage, record, powerUsageEffectiveness, emissionsFactors)
        if(networkingFootprint):
            networkingFootprint.usesAverageCPUConstant = False
            accumulateKilowattsHours(self.unknown_dic, record, networkingFootprint.energy_estimate)
        return networkingFootprint
    
  

    
    # #调试用的函数        
    # def print_processed_data(self):
    #     converted_data = {
    #         str(key): value for key, value in self.processed_data.items()
    #     }
    #     formatted_data = json.dumps(converted_data, default=str, indent=4)
    #     print(formatted_data)
   
  