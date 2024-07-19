from models.IFootprintEstimate import IFootprintEstimate, estimateCo2
from models.UsageRecord import UsageRecord



class NetworkingEstimator(IFootprintEstimate):
    def __init__(self, coefficient: float):
        self.coefficient = coefficient

    def estimate(self, NetworkingUsage, record:UsageRecord, powerUsageEffectiveness, emissionsFactors):
        estimatedKilowattHours = self.estimate_kilowatt_hours(NetworkingUsage, powerUsageEffectiveness)
        estimatedCO2Emissions = estimateCo2(estimatedKilowattHours,record.region, emissionsFactors)   
        footprint_estimate = IFootprintEstimate(
            timestamp = record.groupByDay,  
            energy_estimate = estimatedKilowattHours,
            co2_estimate = estimatedCO2Emissions,
            region = record.region,
            usesAverageCPUConstant = False
        )
        return footprint_estimate
    
    def estimate_kilowatt_hours(self, NetworkingUsage, powerUsageEffectiveness) -> float:   
        return NetworkingUsage * self.coefficient * powerUsageEffectiveness



