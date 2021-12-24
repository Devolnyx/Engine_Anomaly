import json
import requests
import pandas as pd
import datetime


def build_request2(channels, period, begin, end):

    select = [{"entity": "device", "id": str(channel['device']),
               "channel": channel['channel']} for channel in channels]

    request = {
        "select": select,
        "periods": [period],
        "mult": 1,
        "begin": begin,
        "end": end,
    }
    return request


def request_electro(channels, period, begin, end, multiplier):

    if type(period) is not list:
        raise Exception(f'Period expected to be a "list" type, got {type(period)} instead')

    request = {
        "channels": channels,
        "periods": period,
        "multiplier": multiplier,
        "begin": begin,
        "end": end,
    }
    return request


class ElectricalArchive:

    def __init__(self, sedmax_object):
        self.host = sedmax_object.get_url()
        self.token = sedmax_object.get_token()

    def get_data(self, channels, period, begin, end, multiplier=1):
        if self.token is None:
            raise Exception('Authentication required!')
        if type(channels) is not list:
            raise Exception(f'Channels expected to be a "list" type, got {type(channels)} instead')

        channels = sorted(channels)
        request = request_electro(channels, period, begin, end, multiplier)

        url = self.host + '/sedmax/web/archive/electro/archive'

        data = requests.post(url, json=request, cookies={'jwt': self.token})
        if data.status_code != 200:
            return print(f'Status code: {data.status_code}, {data.json()["message"]}')

        df = pd.DataFrame(data.json()['rows'])
        df.set_index('dt', inplace=True)
        df.index = pd.to_datetime(df.index)

        for i, channel in enumerate(channels):
            df[channel] = df.cells.map(lambda x: x[i]['value'])
            df[channel] = pd.to_numeric(df[channel], errors='coerce')
        df.drop('cells', axis=1, inplace=True)
        return df

    def devices_tree(self):
        url = self.host + '/sedmax/web/archive/devices_tree'

        data = requests.post(url, json={'category':'electro'}, cookies={'jwt': self.token})
        if data.status_code != 200:
            return print(f'Status code: {data.status_code}, {data.json()["message"]}')

        df = pd.DataFrame(data.json()['treeObject'])
        return df

    def integrity(self, devices, days=1):
        if type(devices) is not list:
            raise Exception(f'Devices expected to be a "list" type, got {type(devices)} instead')

        now = datetime.datetime.now()
        past = now - datetime.timedelta(days=days)

        params = {
            "begin": past.strftime("%Y-%m-%d %H:%M:%S"),
            "end": now.strftime("%Y-%m-%d %H:%M:%S"),
            "category": "electro",
            "sort": "id",
            "sources": devices
        }

        url = self.host + '/sedmax/web/archive/integrity'
        data = requests.post(url, json=params, cookies={'jwt': self.token})
        if data.status_code != 200:
            return print(f'Status code: {data.status_code}, {data.json()["message"]}')
        return data.json()

    def get_electro_data(self, channels, period, begin, end):
        if self.token is None:
            raise Exception('Authentication required!')

        request = build_request2(channels, period, begin, end)

        url = self.host + '/sedmax/web/archive/electro/v2/data/'
        url += json.dumps(request)

        data = requests.get(url, cookies={'jwt': self.token})
        if data.status_code != 200:
            return print(f'Status code: {data.status_code}, {data.json()["message"]}')

        df = pd.DataFrame(data.json()['rows'])
        df.set_index('dt', inplace=True)
        df.index = pd.to_datetime(df.index)

        return df


#el.get_data(['dev-4_ea_exp', 'dev-3_ea_exp', 'dev-2_ea_exp'], ['30min'], '2021-11-30','2021-12-01')  SDK server
