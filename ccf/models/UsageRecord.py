from datetime import datetime
from utils.GCPRegions import GCP_REGIONS
from utils.helpers import containsAny
from utils.UsageTypeConstants import SERVICES_TO_OVERRIDE_USAGE_UNIT_AS_UNKNOWN
from utils.MachineTypes import SHARED_CORE_PROCESSORS
from api import config
class UsageRecord:
    def __init__(self, data):
        self.cloudProvider = "GCP"
        self.billing_account_id = data["billing_account_id"]
        self.serviceName = data["service"]["description"]

        if "id" in data["project"]:
            self.accountId = data["project"]["id"]
        else:
            self.accountId = "UNKNOWN"
        if "name" in data["project"]:
            self.accountName = data["project"]["name"]
        else:
            self.accountName = "UNKNOWN"   

        
        # location setting
        # if "location" in data["location"]:
        #     self.location = data["location"]["location"]
        # else:
        #     self.location = "UNKNOWN"

        # if "country" in data["location"]:
        #     self.country = data["location"]["country"]
        # else:
        #     self.country = "UNKNOWN"
        
        if "region" in data["location"]:
            self.region = data["location"]["region"]
        else:
            if "location" in data["location"]:
                self.region = data["location"]["location"]
            else:
                self.region = "UNKNOWN"

        self.usage_start_time = datetime.strptime(data["usage_start_time"], "%Y-%m-%d %H:%M:%S UTC")
        self.usage_end_time = datetime.strptime(data["usage_end_time"], "%Y-%m-%d %H:%M:%S UTC")
        self.groupByDay = self.usage_start_time.date()


        self.cost = data["cost"]


        if "cost_at_list" in data:
            self.costAtList = data["cost_at_list"]
        else:
            self.costAtList = "UNKNOWN"

        # self.costAtList = data["cost_at_list"]    
        self.usageAmount = data["usage"]["amount"]
        self.usageUnit = data["usage"]["unit"]
        self.usageType= data["sku"]["description"]
        
        if "effective_price" in data["price"]:
            self.priceEffectivePrice = data["price"]["effective_price"]
        else:
            self.priceEffectivePrice ="UNKNOWN"

        if "unit" in data["price"]:
            self.priceUnit = data["price"]["unit"]
        else:
            self.priceUnit ="UNKNOWN"
            
        self.vCpuHours = self.getVCpuHours()
        self.gpuHours = self.usageAmount / 3600
        self.machineType = self.extract_machine_type(data["system_labels"])

        if containsAny(SERVICES_TO_OVERRIDE_USAGE_UNIT_AS_UNKNOWN, self.serviceName):
            self.usageUnit = 'UNKNOWN'
        if self.isCloudComposerCompute() or self.isKubernetesCompute():
            self.machineType = SHARED_CORE_PROCESSORS.E2_MEDIUM.value
        if 'Pod mCPU Requests' in self.usageType:
            self.usageAmount = self.usageAmount / 1000

    def extract_machine_type(self, system_labels):
        for label in system_labels:
            if label["key"] == "compute.googleapis.com/machine_spec":
                return label["value"]
        return None
    
    def getVCpuHours(self)->float:
        if self.isCloudComposerCompute():
            return (self.usageAmount / 3600) * config.GCP_VCPUS_PER_CLOUD_COMPOSER_ENVIRONMENT 
        if self.isKubernetesCompute():
            return (self.usageAmount / 3600) * config.GCP_VCPUS_PER_GKE_CLUSTER
        return self.usageAmount / 3600

    def isCloudComposerCompute(self)->bool:
         return (
            'Cloud Composer Compute CPUs' in self.usageType or
            'Cloud Composer vCPU' in self.usageType or
            'Cloud Composer SQL vCPU' in self.usageType
        )

    def isKubernetesCompute(self)->bool:
        return 'Kubernetes Clusters' in self.usageType
    

    
    