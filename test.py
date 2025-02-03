import dateutil.parser as dt


def is_correct_date(text: str) -> bool:
    try:
        x = dt.parse(text)
        print(str(x))
    except:
        return False
    return True


print(is_correct_date('05.04'))