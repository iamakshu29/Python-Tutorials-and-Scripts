from datetime import datetime

def sort_rows(rows, sort_by, order="asc"):

    def parse_value(row):
        value = getattr(row, sort_by)

        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            return value.lower()

        return value

    return sorted(
        rows,
        key=parse_value,
        reverse=(order == "desc")
    )