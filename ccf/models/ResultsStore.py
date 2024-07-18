from collections import defaultdict
from datetime import datetime, timezone
from models.UsageRecord import UsageRecord
from models.IFootprintEstimate import IFootprintEstimate
class ResultsStore:
    def __init__(self, granularity='Day'):
        self.granularity = granularity
        self.dataset = defaultdict(list)
    
    def result_granularity(self, record:UsageRecord, footprint_estimate:IFootprintEstimate):
        if self.granularity == 'Day':
            timestamp = record.groupByDay
        elif self.granularity == 'Hour':
            timestamp = record.usage_start_time
        result = {
            'cloudProvider': "GCP",
            'kilowattHours': footprint_estimate.energy_estimate,
            'co2e': footprint_estimate.co2_estimate,
            'usesAverageCPUConstant': footprint_estimate.usesAverageCPUConstant,
            'serviceName': record.serviceName,
            'accountId': record.accountId,
            'accountName': record.accountName,
            'region': record.region,
            'cost': record.cost,
        }
        return result

    
    def add_result(self, record:UsageRecord, footprint_estimate:IFootprintEstimate):
        if self.granularity == 'Day':
            timestamp = record.groupByDay
        elif self.granularity == 'Hour':
            timestamp = record.usage_start_time
        
        result = {
            'cloudProvider': "GCP",
            'kilowattHours': footprint_estimate.energy_estimate,
            'co2e': footprint_estimate.co2_estimate,
            'usesAverageCPUConstant': footprint_estimate.usesAverageCPUConstant,
            'serviceName': record.serviceName,
            'accountId': record.accountId,
            'accountName': record.accountName,
            'region': record.region,
            'cost': record.cost,
        }

        self.dataset[timestamp].append(result)

        aggregated_result = {
            'timestamp': timestamp,
            'serviceEstimates': self.dataset[timestamp],
            'groupBy': self.granularity.lower(),
        }

        return aggregated_result

    def get_results(self):
        return list(self.dataset.values())
