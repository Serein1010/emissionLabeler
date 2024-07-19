from models.IFootprintEstimate import IFootprintEstimate, estimateCo2
from models.UsageRecord import UsageRecord



class UnknownEstimator(IFootprintEstimate):
    def __init__(self):
        pass 
    
    def estimate(self, UnknownUsage, region, emissionsFactors, unknown_dic):     
        estimatedKilowattHours = self.estimate_kilowatt_hours(UnknownUsage, unknown_dic) 
        estimatedCO2Emissions = estimateCo2(estimatedKilowattHours, region, emissionsFactors)
        footprint_estimate = IFootprintEstimate(
            timestamp = UnknownUsage['timestamp'], 
            energy_estimate = estimatedKilowattHours,
            co2_estimate = estimatedCO2Emissions,
            region = region,
            usesAverageCPUConstant = False
        )
        return footprint_estimate
    
    def estimate_kilowatt_hours(self, UnknownUsage, unknown_dic) -> float:
        if UnknownUsage['serviceName'] in unknown_dic:
            if UnknownUsage['usageUnit'] in unknown_dic[UnknownUsage['serviceName']]:
                serviceAndUsageUnit = unknown_dic[UnknownUsage['serviceName']][UnknownUsage['usageUnit']]
                return ((serviceAndUsageUnit['kilowattHours'] /
                        serviceAndUsageUnit['UsageAmount']) *
                        UnknownUsage['usageAmount'])
        if 'total' in unknown_dic:   
            
            if UnknownUsage['usageUnit'] in unknown_dic['total']:
                serviceAndUsageUnit = unknown_dic['total'][UnknownUsage['usageUnit']]
                return ((serviceAndUsageUnit['kilowattHours'] /
                            serviceAndUsageUnit['UsageAmount']) *
                            UnknownUsage['usageAmount'])
        return 0
