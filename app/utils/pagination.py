from math import ceil

def paginate(items, total: int, page: int, limit: int):
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": ceil(total / limit) if limit else 1
    }
