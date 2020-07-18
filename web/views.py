from django.shortcuts import render
from django.http import HttpResponse, Http404 

from web.models import Greeting

import matplotlib.pyplot as plt
import mpld3
import numpy as np

from core.data.model import ModelDataRepo
from core import config
from core.modeling import SeicrdRlcModel, ModelPlotter

from django.template.defaulttags import register
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

config.init_plot(fig_size=(10,6))

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
    

def kabko(request):
    kabko = request.GET.getlist('kabko')
    if kabko and len(kabko) > 0 and kabko[0]:
        return grafik(request, kabko[0])
    kabko_dict = ModelDataRepo.fetch_kabko_dict()
    return render(request, "kabko.html", {"kabko_dict": kabko_dict})
    
def _plot_compare(plotter, kabko, d, length):
    datasets = kabko.get_datasets([d], kabko.last_outbreak_shift)
    return plotter.plot(
        plotter.plot_main_data, 
        datasets,
        length
    )
    
def grafik(request, kabko):
    kabko_dict = ModelDataRepo.fetch_kabko_dict()
    
    if kabko not in kabko_dict:
        raise Http404
    
    kabko = ModelDataRepo.get_kabko_full(kabko)
    
    mod = SeicrdRlcModel(kabko)
    params = kabko.get_params_init(extra_days=config.PREDICT_DAYS)
    model_result = mod.model(**params)
    
    plotter = ModelPlotter(model_result)
    length = kabko.data_count + kabko.last_outbreak_shift
    datasets = ["infectious_all", "critical_cared", "recovered", "dead", "infected"]
    compare = {d:mpld3.fig_to_html(_plot_compare(plotter, kabko, d, length)) for d in datasets}
    
    main = {
        "main": mpld3.fig_to_html(plotter.plot(plotter.plot_main)),
        "main_lite": mpld3.fig_to_html(plotter.plot(plotter.plot_main_lite)),
        "daily_lite": mpld3.fig_to_html(plotter.plot(plotter.plot_daily_lite)),
        "mortality_rate": mpld3.fig_to_html(plotter.plot(plotter.plot_mortality_rate)),
        "over": mpld3.fig_to_html(plotter.plot(plotter.plot_over)),
        #"healthcare": plotter.plot(plotter.plot_healthcare)
    }
    
    return render(request, "grafik.html", {
        "kabko": kabko,
        "kabko_dict": kabko_dict,
        "main_plots": main,
        "compare_plots": compare
    })
    
def about(request):
    return render(request, "about.html")