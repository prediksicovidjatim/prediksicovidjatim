from django.shortcuts import render
from django.http import HttpResponse, Http404 

from web.models import Greeting

import matplotlib.pyplot as plt
import mpld3
import numpy as np

from core.data.model import ModelDataRepo
from core import config, util, database
from core.modeling import SeicrdRlcModel, ModelPlotter

import math

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
    

def map(request):
    return render(request, "map.html")

score_headers_flat = [
    "MAE", 
    "RMSE", 
    "RMSLE", 
    "R^2 adj", 
    "SMAPE", 
    "MASE", 
    "Red Chi", 
    "AICc", 
    "BIC"
]

def _preprocess_scores_flat(scores):
    if len(scores) == 0:
        return [], []
    kabko = [s[:2] for s in scores]
    scores_1 = util.transpose_list_list([s[2:] for s in scores])
    scores_2 = util.transpose_list_list([_round(s) for s in scores_1])
    
    return [(*(kabko[i]), scores_2[i]) for i in range(0, len(kabko))]

def kabko(request):
    kabko = request.GET.getlist('kabko')
    if kabko and len(kabko) > 0 and kabko[0]:
        return grafik(request, kabko[0])
        
    with database.get_conn() as conn, conn.cursor() as cur:
        kabko_scored = ModelDataRepo.fetch_kabko_scored(cur)
        
        rata_fit, rata_test = ModelDataRepo.fetch_scores_avg(cur)
        flat_fit, flat_test = ModelDataRepo.fetch_scores_flat(cur)
    
    rata_fit = _preprocess_scores_flat(rata_fit)
    rata_test = _preprocess_scores_flat(rata_test)
    flat_fit = _preprocess_scores_flat(flat_fit)
    flat_test = _preprocess_scores_flat(flat_test)
    
    data =  {
        "kabko_scored": kabko_scored,
        "score_headers": score_headers_flat,
        "rata_fit": rata_fit,
        "rata_test": rata_test,
        "flat_fit": flat_fit,
        "flat_test": flat_test
    }
    return render(request, "kabko.html", data)
    
    
def _ma(x):
    return sum(np.abs(x))/len(x)

def _round(x):
    y = _ma(x)
    if y > 9999:
        return np.round(x, 0)
    elif y > 99:
        return np.round(x, 1)
    elif y > 9:
        return np.round(x, 2)
    elif y > 2:
        return np.round(x, 3)
    else:
        return np.round(x, 4)


score_headers = [
    "Variabel Bebas", 
    "Max Error", 
    "MAE/MAD", 
    "RMSE", 
    "RMSLE", 
    "R-squared", 
    "Adjusted R-squared", 
    "SMAPE", 
    "MASE", 
    "Reduced Chi-Square", 
    "AIC", 
    "AICc", 
    "BIC"
]


def _preprocess_scores(scores):
    if len(scores) == 0:
        return [], []
    scores = util.transpose_list_list(scores)
    sets = scores.pop(0)
    scores = [(score_headers[i], _round(scores[i])) for i in range(0, len(score_headers))]
    return sets, scores
    
def _plot_compare(plotter, kabko, d, length):
    datasets = kabko.get_datasets([d], kabko.last_outbreak_shift)
    return plotter.plot(
        plotter.plot_main_data, 
        datasets,
        length
    )
    
def grafik(request, kabko):
    with database.get_conn() as conn, conn.cursor() as cur:
        kabko_scored = ModelDataRepo.fetch_kabko_scored(cur)
        
        if kabko not in {x[0] for x in kabko_scored}:
            raise Http404
        
        kabko = ModelDataRepo.get_kabko_full(kabko, cur)
        fit_scores, test_scores = ModelDataRepo.fetch_scores(kabko.kabko, cur)
        
    mod = SeicrdRlcModel(kabko)
    params = kabko.get_params_init(extra_days=config.PREDICT_DAYS)
    model_result = mod.model(**params)
    
    plotter = ModelPlotter(model_result)
    length = kabko.data_count + kabko.last_outbreak_shift
    datasets = ["infectious_all", "critical_cared", "recovered", "dead", "infected"]
    compare = {d:mpld3.fig_to_html(_plot_compare(plotter, kabko, d, length)) for d in datasets}
    
    fit_sets, fit_scores = _preprocess_scores(fit_scores)
    test_sets, test_scores = _preprocess_scores(test_scores)
    
    fit_scores = fit_scores[1:]
    test_scores = test_scores[1:]
    
    main = {
        "main": mpld3.fig_to_html(plotter.plot(plotter.plot_main)),
        "main_lite": mpld3.fig_to_html(plotter.plot(plotter.plot_main_lite)),
        "daily_lite": mpld3.fig_to_html(plotter.plot(plotter.plot_daily_lite)),
        "mortality_rate": mpld3.fig_to_html(plotter.plot(plotter.plot_mortality_rate)),
        "over": mpld3.fig_to_html(plotter.plot(plotter.plot_over)),
        #"healthcare": plotter.plot(plotter.plot_healthcare)
    }
    
    data = {
        "kabko": kabko,
        "kabko_scored": kabko_scored,
        "main_plots": main,
        "compare_plots": compare,
        "fit_sets": fit_sets,
        "test_sets": test_sets,
        "fit_scores": fit_scores,
        "test_scores": test_scores
    }
    
    return render(request, "grafik.html", data)
    
def about(request):
    return render(request, "about.html")