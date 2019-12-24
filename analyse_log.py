import os
import sys
import re
from dotenv import load_dotenv
from modules.apache_logger import ApacheLogger
from modules import errors

load_dotenv('./.env')

# analyse_log.pyから見た読み込みディレクトリのパス
DIR_PATH = os.getenv('dir_path', '.logs')
# 読み込むファイルの拡張子
EXTENTION = os.getenv('extention', '*.log')
# ファイルを一度に何行読み込むか。数値が大きいほど処理が早くなる
CHUNKSIZE = os.getenv('chunksize', 100000)


# 引数を調整する
def ajust_argv(argv):
    option = None
    term = None
    dir_path = None
    extention = None

    # どの関数を実行するかのオプションを取得
    if (len(argv) > 1) and ('-' in argv[1]):
        if argv[1] == '--help':
            option = argv[1]
            # termがNoneのままだとエラーが出るので
            term = ''

        pattern = r'^-[a-z]$'
        repeater = re.compile(pattern)
        result = repeater.search(argv[1])
        if result:
            option = result.group()

    # 期間を入れる
    if len(argv) > 2:
        term = argv[2]

    # パスを指定しているならそれに変更する
    if len(argv) > 3:
        dir_path = argv[3]
        # パスだけでなくファイル単体を指定してきた時は最後のスラッシュでパスとファイル名を区分する
        if '.' in dir_path:
            pattern = r'.*\.[a-zA-Z]+$'
            repeater = re.compile(pattern)
            result = repeater.search(dir_path)
            if result:
                rsplit = result.group().rsplit('/', 1)
                dir_path = rsplit[0]
                extention = rsplit[1]

    return option, term, dir_path, extention


# オプション引数によってどの関数を実行するか決める
def switch_process(option, term, dir_path, extention):
    dir_path = dir_path or DIR_PATH
    extention = extention or EXTENTION
    if term is None:
        errors.not_enough_argv()

    logger = ApacheLogger(dir_path, extention, CHUNKSIZE)

    if option == '--help':
        print('Usage:\n'
              'python analyse_log.py [option] [term] [dir_name or file_name]\n'
              '\n'
              'Commands:\n'
              '-h    1時間毎のアクセス数を表示します\n'
              '-r    アクセスが多い順にリモートホスト名を表示します\n')

    # １時間毎のアクセス数を表示
    elif option == '-h':
        logger.show_hour_count(term)
    # アクセスの多いホスト順に一覧表示
    elif option == '-r':
        logger.show_host_count(term)
    # 規程以外のオプション
    else:
        errors.wrong_option()


if __name__ == '__main__':
    option, term, dir_path, extention = ajust_argv(sys.argv)
    switch_process(option, term, dir_path, extention)
