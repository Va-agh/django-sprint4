from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPage(TemplateView):
    """The view reterns About page"""

    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    """The view reterns Rules page"""

    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """The view always returns a response with a status code of 404."""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """The view always returns a response with a status code of 403."""
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    """The view always returns a response with a status code of 500."""
    return render(request, 'pages/500.html', status=500)
