from django.core.paginator import Paginator

from yatube.settings import POSTS_ON_PAGE


def pagination(request, object_list):
    paginator = Paginator(object_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
