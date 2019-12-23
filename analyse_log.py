import os
import sys
from dotenv import load_dotenv
from modules.apache_logger import ApacheLogger

load_dotenv('./.env')

# analyse_log.pyから見た読み込みディレクトリのパス
DIR_PATH = os.getenv('dir_path', '../../../Downloads/logs')
# 読み込むファイルの拡張子
EXTENTION = os.getenv('extention', '.log')
# ファイルを一度に何行読み込むか。数値が大きいほど処理が早くなる
CHUNKSIZE = os.getenv('chunksize', 100000)

if __name__ == '__main__':
    for argv in sys.argv:
        print(argv)

    logger = ApacheLogger(DIR_PATH, EXTENTION, CHUNKSIZE)
    # logger.show_hour_count('2019/12/13-2019/12/17')
    logger.show_host_count('2019/12/13-2019/12/18')
