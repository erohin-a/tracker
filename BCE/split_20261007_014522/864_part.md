<!-- Часть 864 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Фильтрация данных по отделу для роли manager](863_Filtratsiya_dannyh_po_otdelu_dlya_roli_manager.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](865_part.md)

---

# ============================================================
def manager_department_id(user):
    """
    Возвращает department_id если user.role == 'manager' и отдел задан.
    Иначе — None.
    Используется для фильтрации списков и отчётов.
    """
    if user and user.get("role") == "manager":
        return user.get("department_id")
    return None


def filter_employees_query(query, user, emp_col="id"):
    """
    Если user — manager с отделом: добавляет в query фильтр
    employee.department_id == его отдел.
    
    query — SQLAlchemy Query по модели Employee.
    user — dict из current_admin().
    """
    dep_id = manager_department_id(user)
    if dep_id is None:
        return query
    from .models import Employee as _Emp
    col = getattr(_Emp, emp_col, _Emp.id)
    return query.filter(_Emp.department_id == dep_id)


def filter_work_sessions_query(query, user):
    """
    Если user — manager с отделом: ограничивает WorkSession
    только сессиями сотрудников его отдела.
    """
    dep_id = manager_department_id(user)
    if dep_id is None:
        return query
    from .models import Employee as _Emp, WorkSession as _WS
    sub = db_subquery_employees_of_dept(dep_id)
    return query.filter(_WS.employee_id.in_(sub))


def db_subquery_employees_of_dept(dep_id):
    """Подзапрос: id сотрудников указанного отдела."""
    from .models import Employee as _Emp
    from sqlalchemy import select
    return select(_Emp.id).where(_Emp.department_id == dep_id)


