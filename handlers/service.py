from datetime import datetime
from dateutil.relativedelta import relativedelta


def check_date(message):
    if not len(message.text.split('.')) == 3:
        return False
    try:
        d = int(message.text.split('.')[0])
        m = int(message.text.split('.')[1])
        y = int(message.text.split('.')[2])
        if not 1 <= d <= 31:
            return False
        if not 1 <= m <= 12:
            return False
        if not y > 2020:
            return False
    except:
        return False
    return True


def calculate_expiration_date(start_date, balance):
    month_count = int(int(balance) // 100)
    finish_date = datetime.strptime(start_date, "%d.%m.%Y").date() + relativedelta(months=month_count)
    return finish_date


def is_debtor(user):
    return datetime.now().date() >= user.date_expiration
