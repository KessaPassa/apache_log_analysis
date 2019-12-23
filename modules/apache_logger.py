import glob
import pandas as pd
import re
import collections
import datetime
from modules import errors


class ApacheLogger:
    MONTH = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
             7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

    def __init__(self, dir_path, extention):
        self.datas = self.read_files(dir_path, extention)

    # ファイルを読み込む
    def read_files(self, dir_path, extention):
        datas = pd.DataFrame()
        # EXTENTIONに指定した拡張子全てを読み込む
        files = glob.glob(dir_path + '/*' + extention)

        # 複数読み込み対応
        for file in files:
            # ファイル読み込み
            df = self.create_dataframe(file)
            # 読み込み済と結合
            datas = pd.concat([datas, df])

        # indexが重複しているのでリセットする
        datas.reset_index(inplace=True, drop=True)
        return datas[0].values.tolist()

    # pandasを用いてログデータを読み込む
    def create_dataframe(self, file):
        df = None
        # chunksizeを用いてメモリに載らないファイルでも分割して読み込む
        reader = pd.read_table(file, header=None, chunksize=100000)
        for r in reader:
            if df is None:
                df = r
            else:
                df = df.append(r, ignore_index=True)

        return df

    def show_access_count_per_hour(self, date_str):
        print('指定した日付にアクセスしてきた回数を1時間毎に表示します\n')

        date_list = []
        # ハイフンがある時は期間指定なので分割して補完する
        if '-' in date_str:
            date_list.extend(self.get_complemented_dates(date_str))
        else:
            date_list.append(date_str)

        for date in date_list:
            print(date)
            date_formated = self.convert_string_to_date(date)
            target_date = self.get_access_limited_date(date_formated, 'datetime')
            # 指定した日付のログがなければ終了
            if not target_date:
                errors.not_exit_log()
                continue

            access_dict = self.get_access_count_per_hour(target_date)
            for hour, count in access_dict.items():
                print('{}時: {}回'.format(hour, count))
            print('合計: {}回'.format(sum(access_dict.values())))
            print('\n')

    def show_access_count_per_host(self, date_str):
        print('接続してきたホスト名をアクセス数順に表示します\n')

        date_list = []
        # ハイフンがある時は期間指定なので分割して補完する
        if '-' in date_str:
            date_list.extend(self.get_complemented_dates(date_str))
        else:
            date_list.append(date_str)

        for date in date_list:
            print(date)
            date_formated = self.convert_string_to_date(date)
            remote_host = self.get_access_limited_date(date_formated, 'remote_host')

            # 指定した日付のログがなければ終了
            if not remote_host:
                errors.not_exit_log()
                continue

            c = collections.Counter(remote_host)
            for name, count in c.most_common():
                print('ホスト名: {}, 接続回数: {}'.format(name, count))
            print('\n')

    # 指定した日付のアクセス時間を取得する
    def get_access_limited_date(self, date, _type):
        year = str(date.year)
        # apacheの月は英語3文字になっているので変換する
        month = self.MONTH[int(date.month)]
        day = str(date.day)

        pattern = None
        if _type == 'remote_host':
            ip_address = r'(([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}' \
                         r'([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])'
            # ipアドレスがない時は-になる
            pattern = r'^(' + ip_address + r'|\s*-\s*){3}'

        elif _type == 'datetime':
            pattern = r'\[' + day + r'\/' + month + r'\/' + year + r'(:[0-9]{2}){3}.*\]'

        else:
            errors.not_exist_type()

        target_list = []
        for data in self.datas:
            # 実例 [16/Dec/2019:02:02:49 -0500]
            # pattern = r'\[' + day + r'\/' + month + r'\/' + year + r'(:[0-9]{2}){3}.*\]'
            repeater = re.compile(pattern)
            result = repeater.search(data)
            if result:
                target_list.append(result.group().split()[0])

        return target_list

    # 24時間毎のアクセス回数を辞書型配列で返す
    def get_access_count_per_hour(self, _list):
        # 0埋めで24時間毎のアクセス回数を保存するdictを作成。[日時:回数]
        hour_dict = {'{:0>2}'.format(str(key)): 0 for key in range(24)}
        for l in _list:
            # 日/月/年:時:分:秒なので1つ目の:のあとが時間となる
            hour = l.split(':')[1]
            hour_dict[hour] += 1

        return hour_dict

    def get_complemented_dates(self, dates):
        date_list = []

        pattern = r'^[0-9]{4}\/[0-9]{2}\/[0-9]{2}-[0-9]{4}\/[0-9]{2}\/[0-9]{2}$'
        repeater = re.compile(pattern)
        result = repeater.search(dates)
        if result:
            # 日付がハイフンで分かれている
            _list = result.group().split('-')
            date_first = self.convert_string_to_date(_list[0])
            date_last = self.convert_string_to_date(_list[1])
            date_diff = date_last - date_first
            # マイナスになるということは2019/1/10-2019/1/1のようになっている
            if date_diff.days < 0:
                errors.input_start_to_end()

            date_list.append(date_first)
            # 差分の日にち-1が補完するべき日数
            for i in range(1, date_diff.days):
                complement = date_first + datetime.timedelta(days=i)
                date_list.append(complement)
            date_list.append(date_last)

            date_list = map(lambda x: self.convert_date_to_string(x), date_list)
            return date_list

        # 想定と違う入力のされ方をされた
        else:
            errors.input_dates()

    # 文字列から日付データに変換
    def convert_string_to_date(self, date):
        pattern = r'^[0-9]{4}\/[0-9]{2}\/[0-9]{2}$'
        repeater = re.compile(pattern)
        result = repeater.search(date)
        if result:
            date_formated = datetime.datetime.strptime(date, '%Y/%m/%d')
            return date_formated
        else:
            errors.input_date()

    # 日付データから文字列に変換
    def convert_date_to_string(self, date):
        return date.strftime('%Y/%m/%d')
