from sqlalchemy import asc, desc
from sqlalchemy.sql.elements import UnaryExpression


def resolve_sort(sort: str, allowed_fields: dict[str, object]) -> UnaryExpression:
    """Turn a `sort` query param like `-created_at` into an ORDER BY clause.

    Only fields present in `allowed_fields` may be sorted on, so callers
    can't pass arbitrary model attributes (relationships, methods, etc.)
    and trigger a 500 from SQLAlchemy.
    """
    field_name = sort.lstrip("-")
    column = allowed_fields.get(field_name)
    if column is None:
        valid = ", ".join(sorted(allowed_fields))
        raise ValueError(f"Invalid sort field '{field_name}'. Must be one of: {valid}")
    order_fn = desc if sort.startswith("-") else asc
    return order_fn(column)
