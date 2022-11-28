from datetime import datetime
from tabulate import tabulate
import numpy as np
import re
import pandas as pd

def set_epicenter_coord(str_epicenter):
    pattern = r"([\d\.]+)°([SN])[^\d]+([\d\.]+)°([EW])"
    result = re.search(pattern, str_epicenter)

    grp1 = result[1]  # value of longitude
    grp2 = result[2]  # letter or longitude
    grp3 = result[3]  # value of latitude
    grp4 = result[4]  # letter or latitude

    lat = float(grp1)
    long = float(grp3)
    lat *= -1 if "S" in grp2 else 1
    long *= -1 if "W" in grp4 else 1
    coord = (lat, long)
    # there is also the information on the country and region, do we need this ? its stored in grp5 if needed.
    return coord

def energy_release(e):
    result = re.search(r"([\d.]+) x 10(\d+)", e)
    mantis = float(result[1])
    exponent = int(result[2])
    return mantis * np.power(10, exponent)
#============================================================================


def test_set_datatype_status(df):
    d = df.copy()
    set_datatype_status(d)
    print(df['Status'])
    print(d['Status'])

if __name__ == '__main__':
    df = pd.read_csv('earthquake.csv')

    columns_to_drop = ["Local time at epicenter"]
    df.drop(columns_to_drop, axis=1)

    # Status
    df['Status'] = df['Status'] == "Confirmed"

    #Date & time
    df['Date & time'] = df['Date & time'].apply(lambda x: datetime.strptime(re.sub('UTC.*', 'UTC', x),'%b %d, %Y %H:%M:%S UTC'))

    #Magnitude
    df['Magnitude'] = df['Magnitude'].where(~df['Magnitude'].str.startswith("unknown"), np.nan)
    df['Magnitude']= df['Magnitude'].astype(float)


    # Depth
    df['Depth']= df['Depth'].str.replace(" km", '')  # just to get rid of the km str at the end
    df['Depth']= df['Depth'].astype(float)

    #Epicenter latitude / longitude
    df["Epicenter latitude / longitude"] = df["Epicenter latitude / longitude"].apply(set_epicenter_coord)

    #Antipode
    df["Antipode"] = df["Antipode"].apply(set_epicenter_coord)

    # Shaking intensity
    intensity_str_to_nbr = {'Not felt':0,
                            'Very weak shaking':1,
                            'Weak shaking near epicenter':1,
                            'Light shaking near epicenter':1,
                            'Light shaking':1,
                            'Weak shaking':2,
                            'Moderate shaking near epicenter':3,
                            'Strong shaking near epicenter':4}
    df["Shaking intensity"] = df["Shaking intensity"].apply(lambda x: intensity_str_to_nbr[x])

    # Felt
    df["Felt"] = df["Felt"].where(df["Felt"].notnull(), "0")
    df["Felt"] = df["Felt"].apply(lambda x: int(re.search(r'^\d*', x)[0]))

    #Estimated seismic energy released
    df["Estimated seismic energy released"] = df["Estimated seismic energy released"].where(df["Estimated seismic energy released"].notnull(), np.nan)
    df["Estimated seismic energy released"][df["Estimated seismic energy released"].notnull()] = df["Estimated seismic energy released"][df["Estimated seismic energy released"].notnull()].apply(energy_release)


    # tests
    # print(df['Date & time'])
    # print(df['Magnitude'])
    # print(df['Depth'])
    # print(df["Epicenter latitude / longitude"])
    # print(df["Antipode"])
    # print(df["Shaking intensity"])
    # print(df["Felt"])
    print(df["Estimated seismic energy released"])

