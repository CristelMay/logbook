from django.shortcuts import render

from authentication.decorators import role_required


@role_required('admin')
def index(request):
    return render(request, "dashboard/admin-dashboard.html")


@role_required('guard')
def lobby_dashboard(request):
    return render(request, "dashboard/lobby-dashboard.html")
