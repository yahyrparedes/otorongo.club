from django.core.paginator import Paginator as DjangoPaginator


PAGINATOR_DIVIDER_THRESHOLD = 10


class Paginator(DjangoPaginator):
    """Everything should work as in django.core.paginator.Paginator, except
    this class provides additional generator for nicer set of pages."""

    _page_number = None

    def page(self, number):
        """Overridden to store retrieved page number somewhere."""
        self._page_number = number
        return super().page(number)

    def paginate_sections(self):
        """Divide pagination range into 3 sections.
        Each section should contain approx. 5 links.  If sections are
        overlapping, they're merged.
        The results might be:
        * L…M…R
        * LM…R
        * L…MR
        * LMR
        where L - left section, M - middle section, R - right section, and "…"
        stands for a separator.
        """
        index = int(self._page_number) or 1
        items = self.page_range

        # The number of pages is low, so we don't need to divide them.
        if items and items[-1] <= PAGINATOR_DIVIDER_THRESHOLD:
            return list(items)

        L = items[0:5]
        M = items[index-3:index+4] or items[0:index+1]
        R = items[-5:]
        L_s = set(L)
        M_s = set(M)
        R_s = set(R)

        D1 = L_s.isdisjoint(M_s)
        D2 = M_s.isdisjoint(R_s)

        if D1 and D2:
            # L…M…R
            pagination = list(L) + [None] + list(M) + [None] + list(R)
        elif not D1 and D2:
            # LM…R
            pagination = sorted(L_s | M_s) + [None] + list(R)
        elif D1 and not D2:
            # L…MR
            pagination = list(L) + [None] + sorted(M_s | R_s)
        else:
            # LMR
            pagination = sorted(L_s | M_s | R_s)

        return pagination
