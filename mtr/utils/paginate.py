from pure_pagination import Paginator as Paginator, EmptyPage


class PaginatorRedirect(Exception):
    pass


class Paginate(object):

    def __new__(
            self, request, queryset, page=1, per_page=30, max_per_page=200):
        try:
            page = int(request.GET.get('page', page))
        except ValueError:
            raise PaginatorRedirect

        try:
            per_page = int(request.GET.get('per_page', per_page))
            if per_page < 1 or per_page > max_per_page:
                raise PaginatorRedirect
        except ValueError:
            raise PaginatorRedirect

        paginator = Paginator(queryset, per_page, request=request)

        try:
            page = paginator.page(page)
            page.count = paginator.count
            return page
        except EmptyPage:
            raise PaginatorRedirect
