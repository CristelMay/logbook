from django.shortcuts import render

from authentication.decorators import role_required


@role_required('admin', 'guard')
def index_view(request):
    """
    Sample view for the app index page.
    
    Template: my_app/templates/my_app/index.html
    URL: /my-app/
    """
    context = {
        'page_title': 'My App Home',
    }
    return render(request, 'my_app/index.html', context)


@role_required('admin', 'guard')
def detail_view(request, item_id):
    """
    Sample detail view with URL parameter.
    
    Template: my_app/templates/my_app/detail.html
    URL: /my-app/detail/<item_id>/
    """
    context = {
        'item_id': item_id,
    }
    return render(request, 'my_app/detail.html', context)

