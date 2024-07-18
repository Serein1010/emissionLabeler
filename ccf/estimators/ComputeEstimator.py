
from utils.EnergyEstimation import ENERGY_ESTIMATION_FORMULA
from models.UsageRecord import UsageRecord
from models.IFootprintEstimate import IFootprintEstimate, estimateCo2

def ENERGY_ESTIMATION_FORMULA(averageCPUUtilization, virtualCPUHours, minWatts, maxWatts, powerUsageEffectiveness, averageWatts=None, replicationFactor = 1):
        if averageWatts is not None:
            calculatedAverageWatts = averageWatts
        else:
            calculatedAverageWatts = minWatts + (averageCPUUtilization / 100) * (maxWatts - minWatts)
        return ((calculatedAverageWatts * virtualCPUHours * powerUsageEffectiveness * replicationFactor) / 1000)

class ComputeEstimator(IFootprintEstimate):
    def __init__(self):
        pass 
    
    def estimate(self, computeUsage, record:UsageRecord,  emissionsFactors, computeConstants):
        # ###  调试专用
        # print(f"cpuUtilizationAverage type: {type(computeUsage['cpuUtilizationAverage'])}")
        # print(f"vCpuHours type: {type(computeUsage['vCpuHours'])}")
        # print(f"minWatts type: {type(computeConstants['minWatts'])}")
        # print(f"maxWatts type: {type(computeConstants['maxWatts'])}")
        # print(f"powerUsageEffectiveness type: {type(computeConstants['powerUsageEffectiveness'])}")
        # print(f"averageWatts type: {type(computeConstants['averageWatts'])}")
        # print(f"replicationFactor type: {type(computeConstants['replicationFactor'])}")
        # ### 
        estimatedKilowattHours = ENERGY_ESTIMATION_FORMULA(
            computeUsage['cpuUtilizationAverage'],
            computeUsage['vCpuHours'],
            computeConstants['minWatts'],
            computeConstants['maxWatts'],
            computeConstants['powerUsageEffectiveness'],
            computeConstants['averageWatts'],  #为将来留出接口，如果知道averageWatts再代入
            computeConstants['replicationFactor'],
        )
        estimatedCO2Emissions = estimateCo2(estimatedKilowattHours,record.region, emissionsFactors)
        footprint_estimate = IFootprintEstimate(
            timestamp = record.groupByDay,  
            energy_estimate = estimatedKilowattHours,
            co2_estimate = estimatedCO2Emissions,
            region = record.region,
            usesAverageCPUConstant = computeUsage['usesAverageCpuConstant']
        )
        return footprint_estimate
    
    

