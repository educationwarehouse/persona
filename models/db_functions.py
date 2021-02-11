import datetime


def NO_MEMBERSHIP_OVERLAP(form):
    """Validator to check whether or not the selected role is overlapping with a role that is already assigned to a
    dossier in the given period of time.

    Example:
        Usage:
            form = SQLFORM()
            if form.process(onvalidation=NO_MEMBERSHIP_OVERLAP).accepted

    this should only be used with a form that interacts with the db.role_membership table
    """
    if not form.vars.role_ids:
        form.errors.role_ids = T('Select a role to assign to this role membership')
        return
    # form.vars.person_id doesn't work here. as the person_id doesn't get submitted with the form vars.
    if form.record:
        role_memberships = active_role_memberships(form.record.person_id)
    else:
        role_memberships = active_role_memberships(request.vars['person'])

    begin_date = form.vars.begin_date
    current_role_membership = form.record.id if form.record else []
    exclude = None

    if current_role_membership:
        # selecting the record, because check_conflicts() creates a list of conflicting records
        # we use this to remove the current record from that list.
        exclude = db(db.role_membership.id == current_role_membership).select().first()

    conflicting = check_conflicts(active_role_memberships=role_memberships,
                                  begin_date=begin_date,
                                  exclude=exclude)
    if conflicting:
        form.errors.begin_date = T('This membership overlaps with another membership')
        return


def active_role_memberships(person_id):
    """Gets the currently active role_membership records assigned to a person.

    :param person_id: id of the person you want the role_membership records of
    :return: list of role_membership records
    """
    today = datetime.date.today()
    query = (db.role_membership.person_id == person_id) & (db.role_membership.begin_date <= today)
    query &= (db.role_membership.end_date >= today) | (db.role_membership.end_date == None)
    rows = db(query).select()
    # creating list of all rows given by the select statement
    memberships = [r for r in rows]
    return memberships


def check_conflicts(active_role_memberships, exclude, begin_date=None):
    """Checks if there are any duplicate roles in the given period of time.

    :param active_role_memberships: the role_membership records you need to check, use active_role_memberships() for this.
    :param exclude: the record that's allowed to be overridden
    :param begin_date: the starting date of the new role_membership record.
    :return: either True or False
    """
    if begin_date:
        # creating a list of conflicting records. we do not allow any role membership to overlap
        conflicts = [r for r in active_role_memberships if r.begin_date <= begin_date <= r.end_date if
                     not r.end_date is None or not r.begin_date is None]
        # override is the current record we're trying to edit, so it will be removed from the list of conflicts.
        if exclude:
            conflicts.remove(exclude) if exclude in conflicts else []
        return bool(conflicts)
    # obviously, if no begin date has been given, this role can't overlap
    else:
        return False
