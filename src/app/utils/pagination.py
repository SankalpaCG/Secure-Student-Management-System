from flask import request, url_for


class Pagination:
    def __init__(self, query, page, per_page, endpoint, **kwargs):
        self.page = max(1, page)
        self.per_page = per_page
        self.total = query.count()
        self.items = query.limit(per_page).offset((self.page - 1) * per_page).all()
        self.pages = max(1, (self.total + per_page - 1) // per_page)
        self.has_prev = self.page > 1
        self.has_next = self.page < self.pages
        self.prev_num = self.page - 1 if self.has_prev else None
        self.next_num = self.page + 1 if self.has_next else None
        self.endpoint = endpoint
        self.kwargs = kwargs

    def iter_pages(self, left=2, right=2):
        for num in range(1, self.pages + 1):
            if num <= left or num > self.pages - right or abs(num - self.page) <= right:
                yield num

    def url(self, page):
        args = request.args.to_dict()
        args.update(self.kwargs)
        args["page"] = page
        return url_for(self.endpoint, **args)
