from datetime import datetime, date
import numpy as np

def parse_int(text):
    if not text:
        return 0
    text = text.replace(".", "").replace(",", "").replace(" ", "")
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

def parse_date(d):
    if isinstance(d, date):
        return d
    return datetime.strptime(d, "%Y-%m-%d").date()
    
def format_date(d):
    if isinstance(d, str):
        return d
    return datetime.strftime(d, "%Y-%m-%d")
    
def filter_dates_after(dates, after):
    if after is None:
        return list(dates)
    if isinstance(after, str):
        after = parse_date(after)
    new_dates = [d for d in dates if d and parse_date(d) > after]
    return new_dates
    
def filter_dict(data, keys):
    return {k:data[k] for k in keys}
    
def filter_dict_new(data, keys):
    return {v:data[k] for k, v in keys.items()}
    
def delta(arr):
    return np.array([arr[0]] + [arr[i]-arr[i-1] for i in range(1, len(arr))])
    
def post_plot(ax):
    ax.yaxis.set_tick_params(length=0)
    ax.xaxis.set_tick_params(length=0)

    ax.grid(b=True, which='major', c='w', lw=0.5, ls='-', alpha=0.25)

    ax.legend(loc='best', shadow=True)
    
    for spine in ('top', 'right', 'bottom', 'left'):
        ax.spines[spine].set_visible(False)
        
import matplotlib.dates as mdates

date_formatter = mdates.DateFormatter('%Y-%m-%d')

def date_plot(ax):
    ax.xaxis.set_major_formatter(date_formatter)
    ax.format_xdata = date_formatter
    ax.fmt_xdata = date_formatter
    ax.xaxis_date()
    
def sum_respectively(lists):
    return [sum(x) for x in zip(*lists)]

def lerp(start, end, t):
    return start + (end-start)*t
    
def lerp_many(start, end, n):
    return [lerp(start, end, i/(n+1.0)) for i in range(1, n+1)]
    
def get_missing_data(data, start, count=1):
    end = start+count-1
    return [data[i].to_db_row() for i in range(start, end+1)]
    
def days_between(start, end):
    dt = parse_date(end) - parse_date(start)
    return dt.days
    
def get_date_index(data, date):
    return days_between(data[0].tanggal, date)
    
from datetime import timedelta
def lerp_missing_data(data, start, count=1):
    end = start+count-1
    yesterday = data[start-1].to_db_row()
    tomorrow = data[end+1].to_db_row()
    return [{
        k:(
            int(lerp(v, tomorrow[k], i/(count+1.0))) if isinstance(v, int) 
            else format_date(parse_date(v) + timedelta(days=i)) if isinstance(v, str) and "2020-" in v
            else v
        )
        for k, v in yesterday.items()
    } for i in range(1, 1+count)]