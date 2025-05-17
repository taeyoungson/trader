from sqlalchemy import orm
from sqlalchemy.dialects import mysql


def auto_upsert_stmt(model: orm.DeclarativeBase, values: list[dict]):
    stmt = mysql.insert(model).values(values)
    update_dict = {col.name: stmt.inserted[col.name] for col in model.__table__.columns if not col.primary_key}
    return stmt.on_duplicate_key_update(**update_dict)
