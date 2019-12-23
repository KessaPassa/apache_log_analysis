from apache_logger import ApacheLogger

if __name__ == '__main__':
    logger = ApacheLogger()
    logger.show_access_count_per_hour('2019/12/15')
    logger.show_access_count_per_host()
