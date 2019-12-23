import sys
from modules.apache_logger import ApacheLogger

# analyse_log.pyから見た読み込みディレクトリのパス
DIR_PATH = './logs'
# 読み込むファイルの拡張子
EXTENTION = '.log'


if __name__ == '__main__':
    for argv in sys.argv:
        print(argv)

    logger = ApacheLogger(DIR_PATH, EXTENTION)
    logger.show_access_count_per_hour('2019/12/13-2019/12/17')
    # logger.show_access_count_per_hour('2019/12/15')
    # logger.show_access_count_per_host()
