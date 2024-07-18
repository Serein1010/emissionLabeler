from utils.helpers import containsAny
from utils.GcpFootprintEstimationConstant import GCP_CLOUD_CONSTANTS
from utils.GCPRegions import GCP_DUAL_REGIONS, GCP_MULTI_REGIONS
from utils.CloudConstantsType import ReplicationFactorsForService




# 函数定义：每个函数接收usageType和可选的region参数，并根据条件返回适当的复制因子。
# 字典映射：GCP_REPLICATION_FACTORS_FOR_SERVICES字典将服务名称映射到相应的函数。
# 调用示例：在实际调用时，可以传递适当的参数。例如，调用get_replication_factor_for_cloud_storage('Dual-region usage type')将返回对应的复制因子。

REPLICATION_FACTORS = GCP_CLOUD_CONSTANTS['REPLICATION_FACTORS']

SERVICES = {
    "CLOUD_STORAGE": "Cloud Storage",
    "COMPUTE_ENGINE": "Compute Engine",
    "CLOUD_FILESTORE": "Cloud Filestore",
    "CLOUD_SQL": "Cloud SQL",
    "CLOUD_MEMORYSTORE_FOR_REDIS": "Cloud Memorystore for Redis",
    "CLOUD_SPANNER": "Cloud Spanner",
    "KUBERNETES_ENGINE": "Kubernetes Engine",
    "CLOUD_COMPOSER": "Cloud Composer",
}

def get_replication_factor_for_cloud_storage(usageType: str) -> int:
    if 'Dual-region' in usageType:
        return REPLICATION_FACTORS['CLOUD_STORAGE_DUAL_REGION']
    if 'Multi-region' in usageType:
        return REPLICATION_FACTORS['CLOUD_STORAGE_MULTI_REGION']
    return REPLICATION_FACTORS['CLOUD_STORAGE_SINGLE_REGION']

def get_replication_factor_for_compute_engine(usageType: str, region: str ) -> int:
    if 'Regional' in usageType:
        return REPLICATION_FACTORS['COMPUTE_ENGINE_REGIONAL_DISKS']
    if containsAny(['Snapshot', 'Image'], usageType):
        multi_regions = list(GCP_MULTI_REGIONS.values())
        dual_regions = list(GCP_DUAL_REGIONS.values())
        if region in multi_regions:
            return REPLICATION_FACTORS['CLOUD_STORAGE_MULTI_REGION']
        if region in dual_regions:
            return REPLICATION_FACTORS['CLOUD_STORAGE_DUAL_REGION']
        return REPLICATION_FACTORS['CLOUD_STORAGE_SINGLE_REGION']
    return REPLICATION_FACTORS['DEFAULT']

def get_replication_factor_for_cloud_filestore() -> int:
    return REPLICATION_FACTORS['CLOUD_FILESTORE']

def get_replication_factor_for_cloud_sql(usageType: str) -> int:
    if 'Regional - Standard storage' in usageType or 'HA' in usageType:
        return REPLICATION_FACTORS['CLOUD_SQL_HIGH_AVAILABILITY']
    return REPLICATION_FACTORS['DEFAULT']

def get_replication_factor_for_cloud_memorystore_for_redis(usageType: str) -> int:
    if 'Standard' in usageType:
        return REPLICATION_FACTORS['CLOUD_MEMORY_STORE_REDIS']
    return REPLICATION_FACTORS['DEFAULT']

def get_replication_factor_for_cloud_spanner(usageType: str) -> int:
    if 'Regional' in usageType:
        return REPLICATION_FACTORS['CLOUD_SPANNER_SINGLE_REGION']
    if 'Multi-Region' in usageType:  # Not sure how it will come from GCP, we don't have any multi-region
        return REPLICATION_FACTORS['CLOUD_SPANNER_MULTI_REGION']
    return REPLICATION_FACTORS['DEFAULT']

def get_replication_factor_for_kubernetes_engine(usageType: str) -> int:
    if 'Clusters' in usageType and ('Regional' in usageType or 'Autopilot' in usageType):
        return REPLICATION_FACTORS['KUBERNETES_ENGINE']
    return REPLICATION_FACTORS['DEFAULT']

def get_replication_factor_for_cloud_composer(usageType: str) -> int:
    if 'Storage' in usageType or 'storage' in usageType:
        return REPLICATION_FACTORS['CLOUD_STORAGE_SINGLE_REGION']
    return REPLICATION_FACTORS['DEFAULT']

GCP_REPLICATION_FACTORS_FOR_SERVICES: ReplicationFactorsForService = {
    SERVICES["CLOUD_STORAGE"]: get_replication_factor_for_cloud_storage,
    SERVICES["COMPUTE_ENGINE"]: get_replication_factor_for_compute_engine,
    SERVICES["CLOUD_FILESTORE"]: get_replication_factor_for_cloud_filestore,
    SERVICES["CLOUD_SQL"]: get_replication_factor_for_cloud_sql,
    SERVICES["CLOUD_MEMORYSTORE_FOR_REDIS"]: get_replication_factor_for_cloud_memorystore_for_redis,
    SERVICES["CLOUD_SPANNER"]: get_replication_factor_for_cloud_spanner,
    SERVICES["KUBERNETES_ENGINE"]: get_replication_factor_for_kubernetes_engine,
    SERVICES["CLOUD_COMPOSER"]: get_replication_factor_for_cloud_composer,
}