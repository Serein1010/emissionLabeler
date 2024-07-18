from models.IFootprintEstimate import IFootprintEstimate, estimateKwh
from models.UsageRecord import UsageRecord

class EmbodiedEmissionsEstimator(IFootprintEstimate):
    def __init__(self, serverExpectedLifespan):
        self.serverExpectedLifespan = serverExpectedLifespan

    def estimate(self, usageTimePeriod, instancevCpu, scopeThreeEmissions, largestInstancevCpu, record:UsageRecord, emissionsFactors):
        estimatedCO2Emissions = self.estimateCo2e(usageTimePeriod, instancevCpu, largestInstancevCpu, scopeThreeEmissions)
        estimatedKilowattHours = estimateKwh(estimatedCO2Emissions, record.region, emissionsFactors) 
        footprint_estimate = IFootprintEstimate(
            timestamp = record.groupByDay,  
            energy_estimate = estimatedKilowattHours,
            co2_estimate = estimatedCO2Emissions,
            region = record.region,
            usesAverageCPUConstant=False
        )
        return footprint_estimate
    
    def estimateCo2e(self, usageTimePeriod, instancevCpu, largestInstancevCpu, scopeThreeEmissions):
        # Source: https://github.com/Green-Software-Foundation/software_carbon_intensity/blob/f8ca3cb7b3195e9d3610ec58670a0d47ea7164e5/Software_Carbon_Intensity/Software_Carbon_Intensity_Specification.md?plain=1#L131
        return (scopeThreeEmissions *(usageTimePeriod / self.serverExpectedLifespan) *(instancevCpu / largestInstancevCpu)
    )



