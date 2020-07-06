from datetime import datetime

def parse_int(text):
    if not text:
        return 0
    try:
        val = int(text)
    except ValueError as ex:
        try:
            val = int(float(text))
        except ValueError as ex2:
            raise
    return val

def mogrify_value_template(n):
    return "("+ ",".join(n*("%s",))+")"

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()
    
def format_date(date):
    return datetime.strftime(date, "%Y-%m-%d")
    
def filter_dates_after(dates, after):
    after = parse_date(after)
    new_dates = [d for d in dates if d and parse_date(d) > after]
    return new_dates
    
def filter_dict(data, keys):
    return {k:data[k] for k in keys}
    
def filter_dict_new(data, keys):
    return {v:data[k] for k, v in keys.items()}