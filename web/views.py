from django.shortcuts import render
from django.http import HttpResponse

from .models import Greeting

import matplotlib.pyplot as plt
import mpld3
import numpy as np


def init_matplotlib():
    SMALL_SIZE = 12
    MEDIUM_SIZE = 14
    BIGGER_SIZE = 16
    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    plt.rc('figure', figsize=(13, 8))  
    plt.rc('lines', linewidth=2) 

init_matplotlib()

# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')
    return render(request, "index.html")


def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings})

def notebook(request, nb_path):
    return render(request, "notebook.html", {"nb_path": nb_path})
    
def test_plot(request):
    fig, ax = plt.subplots(1, 1)
    x = np.linspace(0, 49, 50)
    y = np.array([xi*xi for xi in x])

    ax.plot(x, y, 'b', alpha=0.7, label='y')

    ax.set_xlabel('Time (days)', labelpad=10)

    ax.yaxis.set_tick_params(length=0)
    ax.xaxis.set_tick_params(length=0)

    ax.grid(b=True, which='major', c='w', lw=0.5, ls='-', alpha=0.25)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.09),
              fancybox=True, shadow=True, ncol=5)


    for spine in ('top', 'right', 'bottom', 'left'):
        ax.spines[spine].set_visible(False)

        
    g = mpld3.fig_to_html(fig)
    return render(request, "test_plot.html", {"plot": g})