from typing import Callable, Dict, Optional

class CloudConstants:
    def __init__(self,
                 minWatts: Optional[float] = None,
                 maxWatts: Optional[float] = None,
                 powerUsageEffectiveness: Optional[float] = None,
                 avgCpuUtilization: Optional[float] = None,
                 replicationFactor: Optional[int] = None,
                 kilowattHoursByServiceAndUsageUnit: Optional[Dict[str, Dict[str, float]]] = None,
                 averageWatts: Optional[float] = None):
        self.minWatts = minWatts
        self.maxWatts = maxWatts
        self.powerUsageEffectiveness = powerUsageEffectiveness
        self.avgCpuUtilization = avgCpuUtilization
        self.replicationFactor = replicationFactor
        self.kilowattHoursByServiceAndUsageUnit = kilowattHoursByServiceAndUsageUnit
        self.averageWatts = averageWatts

class CloudConstantsByProvider:
    def __init__(self,
                 SSDCOEFFICIENT: Optional[float] = None,
                 HDDCOEFFICIENT: Optional[float] = None,
                 MEMORY_AVG: Optional[float] = None,
                 MEMORY_BY_COMPUTE_PROCESSOR: Optional[Dict[str, float]] = None,
                 getMemory: Optional[Callable[[Optional[list]], float]] = None,
                 MIN_WATTS_AVG: Optional[float] = None,
                 MIN_WATTS_MEDIAN: Optional[float] = None,
                 MIN_WATTS_BY_COMPUTE_PROCESSOR: Dict[str, float] = None,
                 getMinWatts: Callable[[Optional[list]], float] = None,
                 MAX_WATTS_AVG: Optional[float] = None,
                 MAX_WATTS_MEDIAN: Optional[float] = None,
                 MAX_WATTS_BY_COMPUTE_PROCESSOR: Dict[str, float] = None,
                 getMaxWatts: Callable[[Optional[list]], float] = None,
                 PUE_AVG: float = None,
                 NETWORKING_COEFFICIENT: Optional[float] = None,
                 MEMORY_COEFFICIENT: Optional[float] = None,
                 PUE_TRAILING_TWELVE_MONTH: Optional[Dict[str, float]] = None,
                 getPUE: Callable[[Optional[str]], float] = None,
                 AVG_CPU_UTILIZATION_2020: float = None,
                 REPLICATION_FACTORS: Optional[Dict[str, int]] = None,
                 KILOWATT_HOURS_BY_SERVICE_AND_USAGE_UNIT: Optional[Dict[str, Dict[str, float]]] = None,
                 ESTIMATE_UNKNOWN_USAGE_BY: Optional[str] = None,
                 SERVER_EXPECTED_LIFESPAN: Optional[int] = None):
        self.SSDCOEFFICIENT = SSDCOEFFICIENT
        self.HDDCOEFFICIENT = HDDCOEFFICIENT
        self.MEMORY_AVG = MEMORY_AVG
        self.MEMORY_BY_COMPUTE_PROCESSOR = MEMORY_BY_COMPUTE_PROCESSOR
        self.getMemory = getMemory
        self.MIN_WATTS_AVG = MIN_WATTS_AVG
        self.MIN_WATTS_MEDIAN = MIN_WATTS_MEDIAN
        self.MIN_WATTS_BY_COMPUTE_PROCESSOR = MIN_WATTS_BY_COMPUTE_PROCESSOR
        self.getMinWatts = getMinWatts
        self.MAX_WATTS_AVG = MAX_WATTS_AVG
        self.MAX_WATTS_MEDIAN = MAX_WATTS_MEDIAN
        self.MAX_WATTS_BY_COMPUTE_PROCESSOR = MAX_WATTS_BY_COMPUTE_PROCESSOR
        self.getMaxWatts = getMaxWatts
        self.PUE_AVG = PUE_AVG
        self.NETWORKING_COEFFICIENT = NETWORKING_COEFFICIENT
        self.MEMORY_COEFFICIENT = MEMORY_COEFFICIENT
        self.PUE_TRAILING_TWELVE_MONTH = PUE_TRAILING_TWELVE_MONTH
        self.getPUE = getPUE
        self.AVG_CPU_UTILIZATION_2020 = AVG_CPU_UTILIZATION_2020
        self.REPLICATION_FACTORS = REPLICATION_FACTORS
        self.KILOWATT_HOURS_BY_SERVICE_AND_USAGE_UNIT = KILOWATT_HOURS_BY_SERVICE_AND_USAGE_UNIT
        self.ESTIMATE_UNKNOWN_USAGE_BY = ESTIMATE_UNKNOWN_USAGE_BY
        self.SERVER_EXPECTED_LIFESPAN = SERVER_EXPECTED_LIFESPAN

CloudConstantsEmissionsFactors = Dict[str, float]

ReplicationFactorsForService = Dict[str, Callable[[Optional[str], Optional[str]], int]]
