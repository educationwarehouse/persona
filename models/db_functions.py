import datetime


def current_dienstverbanden(dossier_id):
    """Gets the currently active 'dienstverband' records assigned to a dossier.

    :param dossier_id: id of the dossier you want the dienstverband records of
    :return: list of dienstverband records
    """
    rows = db(db.dienstverband.dossier_id == dossier_id).select()
    today = datetime.date.today()
    # dienstverbanden = [_ for _ in rows if _.einddatum >= today >= _.begindatum if not None]
    dienstverbanden = [r for r in rows if r.einddatum is not None and r.einddatum >= today >= r.begindatum if not None]
    return dienstverbanden


def check_conflicts(active_dienstverbanden, role, begin_date=None):
    """Checks if there are any duplicate roles in the given period of time.

    :param active_dienstverbanden: the 'dienstverband' records you need to check, use current_dienstverbanden() for this.
    :param role: the rol record you need to check for.
    :param begin_date: the starting date of the new 'dienstverband' record.
    :return: either True or False
    """
    if begin_date:
        begin = datetime.datetime.strptime(begin_date, '%Y-%m-%d')
        # creating a list of records that have the same role as the role we're trying to assign for the given time
        # period. we're checking if role.id is in _.rol_id because _.rol_id is a list of roles assigned to a
        # 'dienstverband' record. because we're allowing for multiple roles to be selected and the field is a list of
        # references, we always need to check inside the list.
        conflicts = [_ for _ in active_dienstverbanden if role.id in _.rol_id and _.einddatum >= begin.date()]
        return True if conflicts else False
    # obviously, if no begin date has been given, this role can't overlap
    else:
        return False
