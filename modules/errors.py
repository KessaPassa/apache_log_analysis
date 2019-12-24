def not_enough_argv():
    print('日付を入力してください。引数がたりません')
    exit()


def wrong_option():
    print('オプション引数が違います')
    exit()


def not_exist_file():
    print('ファイルが存在しないパスです')
    exit()


def not_exist_log():
    print('指定した日付のログは存在しません')
    exit()


# 日付の入力間違い
def input_date():
    print('日付の入力が間違っています。2019/01/01のように入力してください')
    exit()


# 日付を期間指定で入力間違い
def input_dates():
    print('日付の入力が間違っています。2019/01/01-2019/01/10のように入力してください')
    exit()


def input_start_to_end():
    print('日付の入力が間違っています。2019/01/01-2019/01/10のように開始-終了と入力してください')
    exit()


def not_exist_type():
    print('存在しないデータ取り出そうとしています')
    exit()
