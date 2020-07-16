from datetime import datetime, date, timezone
import numpy as np
import matplotlib.dates as mdates
import math
from datetime import timedelta
from operator import add
from core.data.model.entities import RtData
from sklearn.model_selection import TimeSeriesSplit
from core import config
import calendar

def chunks(lst, n):
    #https://stackoverflow.com/a/312464
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def sanity_check_init(name, y):
    if y < 0:
        if math.isclose(y, 0, abs_tol=config.FLOAT_TOLERANCE):
            return 0
        else:
            raise Exception("%s can't be negative. (%f, %f)" % (name, y, config.FLOAT_TOLERANCE))
    return y
    
def sanity_check_flow(name, flow):
    if flow < 0:
        if math.isclose(flow, 0, abs_tol=config.FLOAT_TOLERANCE):
            return 0
        else:
            raise Exception("%s can't be negative. (%f, %f)" % (name, flow, config.FLOAT_TOLERANCE))
    return flow
    
def sanity_check_y(name, y, dy):
    y1 = y+dy
    if y1 < 0:
        if math.isclose(y1, 0, abs_tol=config.FLOAT_TOLERANCE):
            pass
        else:
            raise Exception("%s can't flow more than source. (%f+%f=%f, %f)" % (name, y, dy, y1, config.FLOAT_TOLERANCE))
    
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
    
def ms_to_date(d):
    return datetime.utcfromtimestamp(d / 1e3).date()
    
def date_to_ms(d):
    d = parse_date(d) if isinstance(d, str) else d
    return int(calendar.timegm(d.timetuple()) * 1e3)
    
def shift_date(init, shift):
    return init + timedelta(days=shift)
    
def date_range(init, length, start=0):
    init = parse_date(init) if isinstance(init, str) else init
    return [shift_date(init, x) for x in range(start, length+start)]
    
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
    
def extract_dict(data, keys):
    return [data[k] for k in keys]
    
def delta(arr):
    return np.array([arr[0]] + [arr[i]-arr[i-1] for i in range(1, len(arr))])
    
def post_plot(ax):
    ax.yaxis.set_tick_params(length=0)
    ax.xaxis.set_tick_params(length=0)

    ax.grid(b=True, which='major', c='w', lw=0.5, ls='-', alpha=0.25)

    ax.legend(loc='best', shadow=True)
    
    for spine in ('top', 'right', 'bottom', 'left'):
        ax.spines[spine].set_visible(False)
        

date_formatter = mdates.DateFormatter('%Y-%m-%d')

def date_plot(ax):
    ax.xaxis.set_major_formatter(date_formatter)
    ax.format_xdata = date_formatter
    ax.fmt_xdata = date_formatter
    ax.xaxis_date()
    
def sum_respectively(lists):
    return [sum(x) for x in zip(*lists)]

def sum_element(a, b):
    return np.array(list(map(add, a, b)))

def lerp(start, end, t):
    return start + (end-start)*t
    
def lerp_many(start, end, n):
    return [lerp(start, end, i/(n+1.0)) for i in range(1, n+1)]
    
def get_missing_data(data, start, count=1):
    end = start+count-1
    return [data[i].to_db_row() for i in range(start, end+1)]
    
def days_between(start, end, non_negative=False):
    dt = parse_date(end) - parse_date(start)
    dt = dt.days
    if non_negative:
        dt = max(0, dt)
    return dt
    
def get_date_index(data, date):
    return int(days_between(data[0].tanggal, date, True))
    
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
    
def check_finite_many(retT):
    not_finite = []
    for i in range(0, len(retT)):
        if not np.isfinite(retT[i]).all():
            not_finite.append(i)
    
    if len(not_finite) > 0:
        raise Exception("Not finite: " + str(not_finite))
        
def check_finite(retT):
    not_finite = []
    for i in range(0, len(retT)):
        if not math.isfinite(retT[i]):
            not_finite.append(i)
    
    if len(not_finite) > 0:
        raise Exception("Not finite: " + str(not_finite))
        
def map_function(t, f):
    return np.array([f(ti) for ti in t])
    
def rt_delta(rt, oldest_tanggal=None):
    first = rt[0]
    if isinstance(first, RtData):
        if not oldest_tanggal:
            raise ValueError("You must specify oldest_tanggal if the rt are RtData")
        return [(days_between(oldest_tanggal, rt[i].tanggal, True), rt[i].init-rt[i-1].init) for i in range(1, len(rt))]
    elif isinstance(first, tuple):
        first = first[0]
        if isinstance(first, int):
            return [(rt[i][0], rt[i][1]-rt[i-1][1]) for i in range(1, len(rt))]
        elif isinstance(first, str) or isinstance(first, date) or isinstance(first, datetime):
            if not oldest_tanggal:
                raise ValueError("You must specify oldest_tanggal if the rt are tuples with dates")
            return [(days_between(oldest_tanggal, rt[i].tanggal, True), rt[i][1]-rt[i-1][1]) for i in range(1, len(rt))]
        raise ValueError("Invalid rt[0][0]: " + str(first))
    elif isinstance(first, int):
        return [(rt[i]-rt[i-1]) for i in range(1, len(rt))]
    raise ValueError("Invalid rt[0]: " + str(first))
    
def get_kwargs_rt(kwargs, count):
    return [kwargs["r_%d" % (i,)] for i in range(0, count)]
    
def shift_array(data, shift, preceeding_zero=True, trailing_zero=False, keep_length=False):
    shift = int(shift)
    if shift == 0:
        return np.array(data)
    elif shift > 0:
        preceeding = np.zeros(shift) if preceeding_zero else np.repeat(data[0])
        
        ret = np.concatenate((preceeding, data))
        if keep_length:
            return ret[:len(data)]
        else:
            return ret
    else:
        ret = data[-shift:]
        if keep_length:
            trailing = np.zeros(-shift) if trailing_zero else np.repeat(data[-1], -shift)
            return np.concatenate((ret, trailing))
        else:
            return ret
        
def get_if_exists(d, index):
    if index in d:
        return d[index]
    return None
    
    
def plot_single(t, data, title=None, label=None, color='blue'):
    fig, ax = plt.subplots(1, 1)
    _plot_single(ax, t, data, title, label, color)
    util.post_plot(ax)
    return fig
    
def _plot_single(ax, t, data, title=None, label=None, color='blue'):
    ax.plot(t, data, color, alpha=0.7, linewidth=2, label=label)
    
    if title:
        ax.title.set_text(title)
        
def plot_single_pred(t, pred, data=None, min=None, max=None, title=None, label=None, color='blue'):
    fig, ax = plt.subplots(1, 1)
    _plot_single(ax, t, data, pred, min, max, title, label, color)
    util.post_plot(ax)
    return fig
    
def _plot_single_pred(ax, t, pred, data=None, min=None, max=None, title=None, label=None, color='blue'):
    ax.plot(t, pred, color=color, alpha=0.7, linewidth=2, label=label + " (model)")
    if data:
        ax.plot(t, data, marker='o', linestyle='', color=color, label=label + " (data)")
    if min and max:
        ax.fill_between(t, min, max, color=color, alpha=0.1, label=label + " (interval keyakinan)")
    
    if title:
        ax.title.set_text(title)

def stdev(cov):
    return np.sqrt(np.diag(cov))
    
def np_concat_2d(train, test):
    return np.array([np.concatenate((train[i], test[i])) for i in range(0, len(train))])
    
def time_series_split(data, split):
    if split > 1:
        return TimeSeriesSplit(split).split(data)
    else:
        data_len = len(data)
        full_index = np.linspace(0, data_len - 1, data_len, dtype=int)
        empty_index = np.array([], dtype=int)
        return [(full_index, empty_index)]
        
def simple_linear(y_0, a, x):
    return a*x + y_0