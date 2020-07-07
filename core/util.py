from datetime import datetime
import numpy as np

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


