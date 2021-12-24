import json
import requests
import pandas as pd
import datetime

def request_event(ID, begin, end, limit, filters):
    if type(ID) is not int:
        raise Exception(f'Channels expected to be a "int" type, got {type(ID)} instead')

    sessionFilters = True if filters != {} else False

    request = {
        "filters": filters,
        "sessionFilters": sessionFilters,
        "limit": limit,
        "configurationId": ID,
        "begin": begin,
        "end": end,
    }
    return request

class EventJournal:

    def __init__(self, sedmax_object):
        self.host = sedmax_object.get_url()
        self.token = sedmax_object.get_token()

    def get_data(self, ID, begin, end, limit=999, filters={}):
        if self.token is None:
            raise Exception('Authentication required!')

        request = request_event(ID, begin, end, limit, filters)

        url = self.host + '/sedmax/common_event_journal/archive/select'

        data = requests.post(url, json=request, cookies={'jwt': self.token})
        if data.status_code != 200:
            return print(f'Status code: {data.status_code}, {data.json()["message"]}')

        df = pd.DataFrame(data.json()['events'])
        #if response data is empty
        if len(data.json()['events']) == 0:
            return df

        df['dt'] = pd.to_datetime(df['common-tm'])
        df = df.set_index('dt').drop('common-tm', axis=1)

        return df


#j.get_data(88, '2021-11-05 00:00:00','2021-12-05 23:00:00', filters = {'common-message': ['провал']} )
#df['MTBF'] = df.groupby('common-device')['common-tm'].diff()