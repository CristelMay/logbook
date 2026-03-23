from django.shortcuts import render


def index(request):
    return render(request, "dashboard/admin-dashboard.html")


def lobby_dashboard(request):
    return render(request, "dashboard/lobby-dashboard.html")
