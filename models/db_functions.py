import datetime


def NO_ROLE_OVERLAP(form):
    """Validator to check whether or not the selected role is overlapping with a role that is already assigned to a
    dossier in the given period of time.

    Example:
        Usage:
            form = SQLFORM()
            if form.process(onvalidation=NO_ROLE_OVERLAP).accepted

    this should only be used with a form that interacts with the db.dienstverband table
    """
    if not form.vars.rol_id:
        form.errors.rol_id = 'Selecteer een rol om toe te wijzen aan dit dossier'
        return
    # form.vars.dossier_id doesn't work here. as the dossier_id doesn't get submitted with the form vars.
    if form.record:
        dienstverbanden = active_dienstverbanden(form.record.dossier_id)
    else:
        dienstverbanden = active_dienstverbanden(request.vars['dossier'])
    begin_date = form.vars.begindatum
    roles = form.vars.rol_id
    # checking the instance, because even with a field that can handle multiple inputs,
    # sometimes you just want one input.
    if isinstance(roles, (tuple, list)):
        # inherit the instance if the value is already a tuple or a list
        roles = roles
    else:
        # creating a list of values from value
        roles = [roles]

    current_dienstverband = form.record.id if form.record else []
    override = None
    if current_dienstverband:
        # selecting the record, because check_conflicts() creates a list of conflicting records
        # we use this to remove the current record from that list.
        override = db(db.dienstverband.id == current_dienstverband).select().first()

    for role in roles:
        conflicting = check_conflicts(active_dienstverbanden=dienstverbanden,
                                      role=role,
                                      begin_date=begin_date,
                                      override=override)
        if conflicting:
            form.errors.rol_id = 'Een of meerdere rollen zijn al toegewezen aan dit dossier tijdens de gekozen periode.'
            return


def active_dienstverbanden(dossier_id):
    """Gets the currently active 'dienstverband' records assigned to a dossier.

    :param dossier_id: id of the dossier you want the dienstverband records of
    :return: list of dienstverband records
    """
    today = datetime.date.today()
    query = (db.dienstverband.dossier_id == dossier_id) & (db.dienstverband.begindatum <= today)
    query &= (db.dienstverband.einddatum >= today) | (db.dienstverband.einddatum == None)
    rows = db(query).select()
    # creating list of all rows given by the select statement
    dienstverbanden = [r for r in rows]
    return dienstverbanden


def check_conflicts(active_dienstverbanden, role, override, begin_date=None):
    """Checks if there are any duplicate roles in the given period of time.

    :param active_dienstverbanden: the 'dienstverband' records you need to check, use current_dienstverbanden() for this.
    :param role: a rol_id you need to check for
    :param override: the record that's allowed to be overridden
    :param begin_date: the starting date of the new 'dienstverband' record.
    :return: either True or False
    """
    if begin_date:
        # creating a list of records that have the same role as the role we're trying to assign for the given time
        # period. we're checking if role is in r.rol_id because r.rol_id is a list of roles assigned to a
        # 'dienstverband' record. because we're allowing for multiple roles to be selected and the field is a list of
        # references, we always need to check if the value exists within the list.
        conflicts = [r for r in active_dienstverbanden if int(role) in r.rol_id if not r.einddatum == None]
        # override is the current record we're trying to edit, so it will be removed from the list of conflicts.
        if override:
            conflicts.remove(override) if override in conflicts else []
        return bool(conflicts)
    # obviously, if no begin date has been given, this role can't overlap
    else:
        return False
