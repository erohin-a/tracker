<!-- Часть 846 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Фильтрация данных по отделу для роли manager](845_Filtratsiya_dannyh_po_otdelu_dlya_roli_manager.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](847_part.md)

---

# ============================================================
def apply_manager_filter(query, user, model_for_emp_column="employee_id"):
    """
    Если пользователь — manager с привязанным отделом, добавляет в query
    фильтр по сотрудникам этого отдела.
    query — SQLAlchemy Query (например db.query(WorkSession))
    user — dict из current_admin(request)
    model_for_emp_column — имя поля в query, содержащее employee_id
    """
    if not user or user.get("role") != "manager":
        return query
    dep_id = user.get("department_id")
    if not dep_id:
        return query  # manager без отдела — видит всё (лучше так, чем ничего)
    from .models import Employee as _Emp
    emp_ids = [e.id for e in db.query(_Emp).filter(_Emp.department_id == dep_id).all()] if False else None
    # Здесь нужен доступ к db — поэтому фильтруем проще: подзапрос
    from sqlalchemy import select
    subq = select(_Emp.id).where(_Emp.department_id == dep_id)
    col = getattr(query.column_descriptions[0]["entity"], model_for_emp_column)
    return query.filter(col.in_(subq))


def manager_department_id(user):
    """Возвращает department_id для manager или None."""
    if user and user.get("role") == "manager":
        return user.get("department_id")
    return None


