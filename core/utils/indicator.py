def get_finbonacci_fallback(val_min: int, val_max: int) -> list[int]:
    diff = val_max - val_min
    assert diff > 0

    return [
        int(val_min + diff * 0.236),
        int(val_min + diff * 0.382),
        int(val_min + diff * 0.618),
        int(val_min + diff * 0.786),
    ]
