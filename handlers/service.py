def check_date(message):
    if not len(message.text.split('.')) == 3:
        return False
    try:
        d = int(message.text.split('.')[0])
        m = int(message.text.split('.')[1])
        y = int(message.text.split('.')[2])
        print(d, m, y)
        if not 1 <= d <= 31:
            return False
        if not 1 <= m <= 12:
            return False
        if not y > 2020:
            return False
    except:
        return False
    return True

