from utils.ComputeProcessorType import COMPUTE_PROCESSOR_TYPES
from statistics import median
from models import UsageRecord
class IFootprintEstimate:
    def __init__(self, timestamp, energy_estimate, co2_estimate, region, usesAverageCPUConstant:bool):
        self.timestamp = timestamp
        self.energy_estimate = energy_estimate
        self.co2_estimate = co2_estimate
        self.region = region
        self.usesAverageCPUConstant = usesAverageCPUConstant


def accumulateKilowattsHours(unknown_dic, record:UsageRecord, kilowattHours):  
    setOrAccumulateByServiceAndUsageUnit(unknown_dic, record, kilowattHours)
    setOrAccumulateUsageUnitTotals(unknown_dic, record, kilowattHours)


   
def setOrAccumulateByServiceAndUsageUnit(unknown_dic, record: UsageRecord, kilowattHours):
    serviceName = record.serviceName
    usageUnit = record.usageUnit
    usageAmount = record.usageAmount
    # # Service doesn't exist: set service and usage unit
    # if not unknown_dic:
    #     unknown_dic[serviceName] = {
    #         usageUnit: {
    #             'UsageAmount': usageAmount,
    #             'kilowattHours': kilowattHours
    #         }
    #     }
    #     return
   # Service exists, but no usage unit for the service: set usage unit for service
    if serviceName in unknown_dic:
        if usageUnit not in unknown_dic[serviceName]:
            unknown_dic[serviceName][usageUnit] = {
                'UsageAmount': usageAmount,
                'kilowattHours': kilowattHours
            }
    # Usage unit exists for service - accumulate
        else:
            unknown_dic[serviceName][usageUnit]['UsageAmount'] += usageAmount
            unknown_dic[serviceName][usageUnit]['kilowattHours'] += kilowattHours
    else:
        unknown_dic[serviceName] = {
            usageUnit: {
                'UsageAmount': usageAmount,
                'kilowattHours': kilowattHours
            }
        }
        return

def setOrAccumulateUsageUnitTotals(unknown_dic, record: UsageRecord, kilowattHours):
    usageUnit = record.usageUnit
    usageAmount = record.usageAmount
    if 'total' in unknown_dic:
        if usageUnit in unknown_dic['total']:
            unknown_dic['total'][usageUnit]['UsageAmount'] += usageAmount
            unknown_dic['total'][usageUnit]['kilowattHours'] += kilowattHours
        else:
            unknown_dic['total'][usageUnit] = {
                'UsageAmount': usageAmount,
                'kilowattHours': kilowattHours
            }
    else:
        unknown_dic['total'] = {
            usageUnit: {
                'UsageAmount': usageAmount,
                'kilowattHours': kilowattHours
            }
        }
        return  
def estimateCo2(estimatedKilowattHours, region: str, emissionsFactors):
    region = region.upper()
    region = region.replace('-','_')
    # if region == 'EUROPE_WEST1':
    #     return estimatedKilowattHours * 57
    # elif region == 'US_CENTRAL1':
    #     return estimatedKilowattHours * 456
    # else:
    #     return estimatedKilowattHours * 57
    if region not in emissionsFactors:
        return estimatedKilowattHours * emissionsFactors['UNKNOWN']
    else:
        return estimatedKilowattHours * emissionsFactors[region] 

def estimateKwh(estimatedCo2e, region: str, emissionsFactors, replicationFactor = 1):
    region = region.upper()
    region = region.replace('-','_')
    if region not in emissionsFactors:
        return  (estimatedCo2e / 
             (emissionsFactors['UNKNOWN']) * 
             replicationFactor)
    else:
        return  (estimatedCo2e / 
             (emissionsFactors[region]) * 
             replicationFactor)


def includes(array, element):
    return element in array

def getAverage(nums):
    if not nums:
        return 0
    if len(nums) == 1:
        return nums[0]
    return sum(nums) / len(nums)

# When we have a group of compute processor types, by we default calculate the average for this group of processors.
# However when the group contains either the Sandy Bridge or Ivy Bridge processor type, we calculate the median.
# This is because those processor types are outliers with much higher min/max watts that the other types, so we
# want to take this into account to not over estimate the compute energy in kilowatts.
def getWattsByAverageOrMedian(computeProcessors, wattsForProcessors):
    if (includes(computeProcessors, COMPUTE_PROCESSOR_TYPES.SANDY_BRIDGE) or includes(computeProcessors, COMPUTE_PROCESSOR_TYPES.IVY_BRIDGE)):
        return median(wattsForProcessors)
    return getAverage(wattsForProcessors)