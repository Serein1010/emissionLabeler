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

# def convertGigabyteMonthsToTerabyteHours(usage_amount, timestamp):
#     days_in_month = monthrange(timestamp.year, timestamp.month)[1]
#     hours_in_month = days_in_month * 24
#     return (usage_amount / 1000) * hours_in_month

#     try:
#         date = datetime.fromisoformat(timestamp)
#         days_in_month = calendar.monthrange(date.year, date.month)[1]
#     except ValueError:
#         days_in_month = 30.42
#     return (usage_amount / 1000) * (24 * days_in_month)

def convert_terabytes_to_gigabytes(usage_amount):
    return usage_amount * 1000

def convert_megabytes_to_gigabytes(usage_amount):
    return usage_amount / 1024

def convert_gigabytes_to_terabyte_hours(usage_amount):
    return (usage_amount / 1000) * 24

def convert_grams_to_metric_tons(amount):
    return amount / 1000000
