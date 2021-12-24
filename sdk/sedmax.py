import json
import requests
import pandas as pd


class Sedmax:

    def __init__(self, host='http://127.0.0.1'):
        self.host = host
        self.token = None

    def login(self, username, password):
        r = requests.post(
            self.host + '/sedmax/auth/login',
            data=json.dumps({'Login': username, 'Password': password})
        )
        self.token = r.cookies.get_dict()["jwt"]

    def get_token(self):
        return self.token

    def get_url(self):
        return self.host

    def categories(self):

        r = requests.post(
            self.host + '/sedmax/web/archive/categories',
            json={},
            cookies={'jwt': self.token}
        )
        if r.status_code != 200:
            return print(f'Status code: {r.status_code}, {r.json()["message"]}')

        return r.json()['categories']

    def devices_tree(self):

        url = self.host + '/sedmax/web/archive/devices_tree'
        df = pd.DataFrame()
        for category in ['electro', 'energy', 'emission']:
            data = requests.post(url, json={'category': category}, cookies={'jwt': self.token})
            if data.status_code != 200:
                return print(f'Status code: {data.status_code}, {data.json()["message"]}')
            data = pd.DataFrame(data.json()['treeObject'])
            data['category'] = category
            df = pd.concat([df, data]).reset_index(drop=True)

        return df

 #s.electro.get_electro_data([{'device': 101, 'channel': "ea_imp"}],period="30min",begin='2021-01-24',end='2021-01-26')
 #s.electro.get_data(["dev-101_ea_imp"],period=["30min"],begin='2021-01-24',end='2021-01-26')


