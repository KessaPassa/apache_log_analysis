def not_exit_log():
    print('指定した日付のログは存在しません\n')


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