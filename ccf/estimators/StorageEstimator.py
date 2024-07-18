from models.IFootprintEstimate import IFootprintEstimate, estimateCo2
from models.UsageRecord import UsageRecord



class StorageEstimator(IFootprintEstimate):
    def __init__(self, coefficient: float):
        self.coefficient = coefficient

    def estimate(self, StorageUsage, record:UsageRecord, powerUsageEffectiveness, emissionsFactors, replicationFactor):

        estimatedKilowattHours = self.estimate_kilowatt_hours(StorageUsage, powerUsageEffectiveness, replicationFactor)
        estimatedCO2Emissions = estimateCo2(estimatedKilowattHours,record.region, emissionsFactors)
        footprint_estimate = IFootprintEstimate(
            timestamp = record.groupByDay,  
            energy_estimate = estimatedKilowattHours,
            co2_estimate = estimatedCO2Emissions,
            region = record.region,
            usesAverageCPUConstant = False
        )

        return footprint_estimate
    


    def estimate_kilowatt_hours(self, StorageUsage, powerUsageEffectiveness, replicationFactor = 1) -> float:
       
        return ((StorageUsage * self.coefficient * powerUsageEffectiveness * replicationFactor) / 1000)



