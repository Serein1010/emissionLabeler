def convertByteSecondsToTerabyteHours(usage_amount):
    return usage_amount / 1099511627776 / 3600

def convertBytesToGigabytes(usage_amount):
    return usage_amount / 1073741824

def convertByteSecondsToGigabyteHours(usage_amount):
    return usage_amount / 1073741824 / 3600

def convertBytesToTerabytes(usage_amount):
    return usage_amount / 1099511627776

def convertGigabyteHoursToTerabyteHours(usage_amount):
    return usage_amount / 1000

def convertTerabytesToGigabytes(usage_amount):
    return usage_amount * 1000

def convertMegabytesToGigabytes(usage_amount):
    return usage_amount / 1024

def convertGigabytesToTerabyteHours(usage_amount):
    return (usage_amount / 1000) * 24

def convertGramsToMetricTons(amount):
    return amount / 1000000
