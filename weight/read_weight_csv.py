import csv
import datetime
import dateutil.tz
import dateutil.parser
from dateutil import zoneinfo

# Modify those if needed, timezone must match the times in the CSV
# Default CSV assumes datetime in the first column, weight in the second one.
TIME_ZONE = zoneinfo.gettz("Europe/Berlin")
DATA_IN_POUNDS = False

DAWN_TIME = datetime.datetime(1970, 1, 1, tzinfo=dateutil.tz.tzutc())
POUNDS_PER_KILOGRAM = 2.20462


def nano(val):
    """Converts a number to nano (str)."""
    return '%d' % (int(val) * 1e9)


def epoch_of_time_str(dateTimeStr, tzinfo):
    log_time = dateutil.parser.parse(dateTimeStr).replace(tzinfo=tzinfo)
    return (log_time - DAWN_TIME).total_seconds()


def read_weights_csv():
    print("Reading Weights")
    is_header = True
    weights = []
    with open('weights.csv', 'r') as csvfile:
        weights_reader = csv.reader(csvfile, delimiter=',')
        for row in weights_reader:
            if is_header:
                is_header = False
                continue
            row[1] = row[1].strip("kg")
            weights.append(dict(
                seconds_from_dawn=epoch_of_time_str(row[0], TIME_ZONE),
                weight=float(row[1])
            ))
    return weights


def read_weights_csv_with_gfit_format():
    weights = read_weights_csv()
    gfit_weights = []
    for weight in weights:
        weight_number = weight["weight"]
        if DATA_IN_POUNDS:
            weight_number = weight["weight"] / POUNDS_PER_KILOGRAM
        gfit_weights.append(dict(
            dataTypeName='com.google.weight',
            endTimeNanos=nano(weight["seconds_from_dawn"]),
            startTimeNanos=nano(weight["seconds_from_dawn"]),
            value=[dict(fpVal=weight_number)],
        ))
    return gfit_weights


if __name__ == "__main__":
    gfit_weights = read_weights_csv_with_gfit_format()
    print(gfit_weights)
