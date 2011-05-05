from django.core.paginator import Paginator, EmptyPage, InvalidPage

def paginate_posts(request, posts, paginate_count = 10):
    paginator = Paginator(posts, paginate_count)
    try: 
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        posts_on_page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        posts_on_page = paginator.page(paginator.num_pages)

    return posts_on_page
