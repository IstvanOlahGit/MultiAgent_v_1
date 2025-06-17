def normalize_deadline_field(d):
    if isinstance(d, dict):
        for key, value in d.items():
            if isinstance(value, dict) and "$date" in value:
                d[key] = value["$date"]
            else:
                normalize_deadline_field(value)
    elif isinstance(d, list):
        for item in d:
            normalize_deadline_field(item)