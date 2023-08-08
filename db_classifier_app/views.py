# views.py

from .utils import recommend_database_v2

from django.shortcuts import render



def index(request):
    rows = ""
    data_structure = ""
    server = ""
    top_databases = None

    if request.method == "POST":
        rows = int(request.POST["rows"])
        data_structure = int(request.POST["data_structure"])
        server = request.POST["server"]

        top_databases = recommend_database_v2(rows, data_structure, server)
        print(top_databases)

    return render(request, 'db_classifier_app/index.html', {
        'top_databases': top_databases,
        'rows': rows,
        'data_structure': data_structure,
        'server': server
    })


def recommend(request):
    if request.method == "POST":
        rows = int(request.POST["rows"])
        data_structure = int(request.POST["data_structure"])
        server = request.POST["server"]

        top_databases = recommend_database_v2(rows, data_structure, server)

        return render(
            request,
            "db_classifier_app/recommend.html",
            {
                "top_databases": top_databases,
            },
        )
    else:
        return render(request, "db_classifier_app/recommend.html")
