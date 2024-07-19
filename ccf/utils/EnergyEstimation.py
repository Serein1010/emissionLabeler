
def ENERGY_ESTIMATION_FORMULA(avg_cpu_utilization, virtual_cpu_hours, constants):
    cpu_factor = constants['CPU_CONVERSION_FACTOR']
    energy_estimate = avg_cpu_utilization * virtual_cpu_hours * cpu_factor
    return energy_estimate
