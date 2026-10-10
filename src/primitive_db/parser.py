def parse_value(val_str):
    """Разбирает строковое значение и приводит его к соответствующему типу данных."""
    val_str = val_str.strip()
    if (val_str.startswith('"') and val_str.endswith('"')) or (
        val_str.startswith("'") and val_str.endswith("'")
    ):
        return val_str[1:-1]
    if val_str.lower() == "true":
        return True
    if val_str.lower() == "false":
        return False
    try:
        return int(val_str)
    except ValueError:
        return val_str


def parse_where(where_str):
    """Разбирает строку условия после ключевого слова where."""
    if not where_str or "where" not in where_str.lower():
        return None

    parts = where_str.split(maxsplit=1)
    if len(parts) < 2:
        return None

    condition = parts[1].strip()
    if "=" not in condition:
        return None

    col, val = condition.split("=", 1)
    return {col.strip(): parse_value(val)}


def parse_set(set_str):
    """Разбирает выражение set для обновления данных в таблице."""
    if not set_str or "set" not in set_str.lower():
        return None, None

    clean_str = set_str.strip()
    if "where" in clean_str.lower():
        set_part, where_part = clean_str.split("where", 1)
        where_clause = parse_where("where " + where_part)
    else:
        set_part = clean_str
        where_clause = None

    set_part = set_part.split(maxsplit=1)[1].strip()
    if "=" not in set_part:
        return None, None

    col, val = set_part.split("=", 1)
    return {col.strip(): parse_value(val)}, where_clause


def parse_insert_values(values_str):
    if not values_str or "(" not in values_str or ")" not in values_str:
        return []

    start = values_str.find("(")
    end = values_str.rfind(")")
    content = values_str[start + 1 : end]

    import re

    raw_vals = re.split(r',\s*(?=[^"]*(?:"[^"]*"[^"]*)*$)', content)
    return [parse_value(v) for v in raw_vals]
