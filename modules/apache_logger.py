import glob
import pandas as pd
import re
import collections
import datetime
from modules import errors


class ApacheLogger:
    MONTH = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
             7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

    def __init__(self, dir_path, extention, chunksize):
        self.datas = self.read_files(dir_path, extention, chunksize)

    # ファイルを読み込む
    def read_files(self, dir_path, extention, chunksize):
        datas = pd.DataFrame()
        # EXTENTIONに指定した拡張子全てを読み込む
        files = glob.glob(dir_path + '/*' + extention)

        # 複数読み込み対応
        for file in files:
            # ファイル読み込み
            df = self.create_dataframe(file, chunksize)
            # 読み込み済と結合
            datas = pd.concat([datas, df])

        # indexが重複しているのでリセットする
        datas.reset_index(inplace=True, drop=True)
        return datas[0].values.tolist()

    # pandasを用いてログデータを読み込む
    def create_dataframe(self, file, chunksize):
        df = None
        # chunksizeを用いてメモリに載らないファイルでも分割して読み込む
        reader = pd.read_table(file, header=None, chunksize=int(chunksize))
        for r in reader:
            if df is None:
                df = r
            else:
                df = df.append(r, ignore_index=True)

        return df

    def show_hour_count(self, date_str):
        print('指定した日付にアクセスしてきた回数を1時間毎に表示します\n')
        print(date_str)
        target_list = self.get_info_per_type(date_str, 'datetime')

        # 二次元配列としてそれぞれの日時と時間帯毎に分かれているので、時間帯でまとめる
        hour_dict = self.get_access_count_per_hour(target_list)
        for hour, count in hour_dict.items():
            print('{}時: {}回'.format(hour, count))
        print('\n合計: {}回'.format(sum(hour_dict.values())))

    def show_host_count(self, date_str):
        print('接続してきたホスト名をアクセス数順に表示します\n')
        print(date_str)
        target_list = self.get_info_per_type(date_str, 'remote_host')

        # 二次元配列としてそれぞれの日時と時間帯毎に分かれているので、ホスト名でまとめる
        host_dict = {}
        for target in target_list:
            for t in target:
                if not (t in host_dict):
                    host_dict[t] = 1
                else:
                    host_dict[t] += 1

        # ホスト名と接続回数を出力する
        c = collections.Counter(host_dict)
        for name, count in c.most_common():
            print('ホスト名: {}, 接続回数: {}'.format(name, count))

    def get_info_per_type(self, date_str, _type):
        date_list = []
        # ハイフンがある時は期間指定なので分割して補完する
        if '-' in date_str:
            date_list.extend(self.get_complemented_dates(date_str))
        else:
            date_list.append(date_str)

        is_empty = True
        target_list = []
        for date in date_list:
            date_formated = self.convert_string_to_date(date)
            target = self.get_limited_logs(date_formated, _type)

            if target:
                is_empty = False
                target_list.append(target)

        # 指定した日付のログがなければ終了
        if is_empty:
            errors.not_exit_log()

        return target_list

    # 指定した日付のアクセス時間を取得する
    def get_limited_logs(self, date, _type):
        year = str(date.year)
        # apacheの月は英語3文字になっているので変換する
        month = self.MONTH[int(date.month)]
        day = str(date.day)

        ip_address = r'(([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}' \
                     r'([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])'
        # ipアドレスがない時は-になる
        remote_host = r'^(' + ip_address + r'|\s*-\s*){3}'
        pattern = remote_host + r'\[' + day + r'\/' + month + r'\/' + year + r'(:[0-9]{2}){3}.*\]'

        target_list = []
        for data in self.datas:
            repeater = re.compile(pattern)
            result = repeater.search(data)
            if result:
                if _type == 'remote_host':
                    target_list.append(result.group().split()[0])
                elif _type == 'datetime':
                    target_list.append(result.group())
                else:
                    errors.not_exist_type()

        return target_list

    # 24時間毎のアクセス回数を辞書型配列で返す
    def get_access_count_per_hour(self, date_list):
        # 0埋めで24時間毎のアクセス回数を保存するdictを作成。[日時:回数]
        hour_dict = {'{:0>2}'.format(str(key)): 0 for key in range(24)}
        for date in date_list:
            for d in date:
                # 日/月/年:時:分:秒なので1つ目の:のあとが時間となる
                hour = d.split(':')[1]
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
