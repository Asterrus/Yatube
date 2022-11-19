from django.views.generic.base import TemplateView


class AboutAuthor(TemplateView):
    """ Creates page about author,
     using django base view class TemplateView and template """
    template_name: str = 'about/about_author.html'


class AboutTech(TemplateView):
    """ Creates page about programms and sites,
     using django base view class TemplateView and template """
    template_name: str = 'about/about_tech.html'
