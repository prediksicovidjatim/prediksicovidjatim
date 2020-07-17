import matplotlib
import matplotlib.pyplot as plt

FONT_SMALL = 12
FONT_MEDIUM = 14
FONT_BIG = 16
FIG_SIZE = (13,8)
LINE_WIDTH = 2

FLOAT_TOLERANCE=1e-7
FIRST_TANGGAL = "2020-03-20"
PREDICT_DAYS = 30

def init_plot(font_small=None, font_medium=None, font_big=None, fig_size=None, line_width=None):
    global FONT_SMALL
    global FONT_MEDIUM
    global FONT_BIG
    global FIG_SIZE
    global LINE_WIDTH
    
    font_small = font_small or FONT_SMALL
    font_medium = font_medium or FONT_MEDIUM
    font_big = font_big or FONT_BIG
    fig_size = fig_size or FIG_SIZE
    line_width = line_width or LINE_WIDTH
    
    plt.rc('font', size=font_small)          # controls default text sizes
    plt.rc('axes', titlesize=font_small)     # fontsize of the axes title
    plt.rc('axes', labelsize=font_medium)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=font_small)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=font_small)    # fontsize of the tick labels
    plt.rc('legend', fontsize=font_medium)    # legend fontsize
    plt.rc('figure', titlesize=font_big)  # fontsize of the figure title
    plt.rc('figure', figsize=fig_size)  
    plt.rc('lines', linewidth=line_width)  
    