import glob
import pandas as pd
import re
import collections
import datetime

DIR_PATH = '../log'
EXTENTION = '.log'


class ApacheLogger:
    MONTH = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
             7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

    def __init__(self):
        self.datas = self.read_files()

    def read_files(self):
        datas = pd.DataFrame()

        files = glob.glob(DIR_PATH + '/*' + EXTENTION)
        for file in files:
            df = self.create_dataframe(file)
            datas = pd.concat([datas, df])

        datas.reset_index(inplace=True, drop=True)
        return datas[0].values.tolist()

    def create_dataframe(self, file):
        df = None
        reader = pd.read_table(file, header=None, chunksize=1000)
        for r in reader:
            if df is None:
                df = r
            else:
                df = df.append(r, ignore_index=True)

        return df

    def show_access_per_hour(self, date):
        print('指定した日付にアクセスしてきた回数を1時間毎に表示します')
        target_date = self.get_access_per_date(date)
        access_dict = self.get_access_per_hour(target_date)
        for hour, count in access_dict.items():
            print('{}時: {}回'.format(hour, count))

    def show_access_per_host(self):
        print('接続してきたホスト名をアクセス数順に表示します')
        remote_hosts = self.get_remote_hosts()
        c = collections.Counter(remote_hosts)
        for name, count in c.most_common():
            print('ホスト名: {}, 接続回数: {}'.format(name, count))

    def get_access_per_date(self, date):
        date_formated = datetime.datetime.strptime(date, '%Y/%m/%d')
        year = str(date_formated.year)
        month = self.MONTH[int(date_formated.month)]
        day = str(date_formated.day)

        target_date = []
        for data in self.datas:
            # pattern = r'\[[0-9]{2}\/[A-Z][a-z]{2}\/[0-9]{4}.*\]'
            pattern = r'\[' + day + r'\/' + month + r'\/' + year + r'(:[0-9]{2}){3}.*\]'
            repeater = re.compile(pattern)
            result = repeater.search(data)
            if result:
                target_date.append(result.group().split()[0])

        if not target_date:
            print('指定した日付のログは存在しません')
            exit()

        return target_date

    def get_access_per_hour(self, _list):
        hour_dict = {'{:0>2}'.format(str(key)): 0 for key in range(24)}
        for l in _list:
            # print(l.split(':'))
            hour = l.split(':')[1]
            hour_dict[hour] += 1

        return hour_dict

    def get_remote_hosts(self):
        remote_hosts = []

        for data in self.datas:
            ip_address = r'(([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}' \
                         r'([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])'
            pattern = r'^(' + ip_address + r'|\s*-\s*){3}'
            repeater = re.compile(pattern)
            result = repeater.search(data)
            if result:
                remote_hosts.append(result.group().split()[0])

        return remote_hosts


if __name__ == '__main__':
    logger = ApacheLogger()
    logger.show_access_per_hour('2019/12/15')
    logger.show_access_per_host()
