import datetime


def NO_MEMBERSHIP_PERIOD_OVERLAP(form):
    """Validator to check whether or not a new role_membership period is overlapping with the active role_membership
    period assigned to a person.

    Meaning, if the begin date of a new role_membership is within the range of the begin- and end date of the active
    role_membership, an error message will be shown.

    Example:
        Usage:
            form = SQLFORM()
            if form.process(onvalidation=NO_MEMBERSHIP_OVERLAP).accepted

    this should only be used with a SQLFORM that's based on the db.role_membership table
    """
    if not form.vars.role_ids:
        form.errors.role_ids = T('Select a role to assign to this role membership')

    # form.vars.person_id doesn't work here. as the person_id doesn't get submitted with the form vars.
    active_role_membership = active_role_membership_record(request.vars['person'])

    # if the person does not have any active role memberships, accept validation.
    if not active_role_membership:
        return True

    # form.record indicates that a record is being edited.
    if form.record:
        # if the record we're trying to edit is the same as the active role_membership record, accept validation.
        if form.record.id == active_role_membership.id:
            return True

    begin_date = form.vars.begin_date
    end_date = form.vars.end_date

    if begin_date is not None and end_date is not None:
        #  a membership can't end sooner than it begins, so if begin_date > end_date, show error message.
        if begin_date > end_date:
            form.errors.end_date = T("Membership can't end sooner than it begins. "
                                     "Please change the end date to a later date")

    conflict = is_date_within_active_membership_record(active_role_membership_record=active_role_membership,
                                                       begin_date=begin_date)

    if conflict:
        form.errors.end_date = T('New membership period overlaps with the currently active membership period. If '
                                 'you want to split the active period, change the end date of the active membership '
                                 'and start a new period with the new set of roles.')

    # if form has errors, show all of the errors at once.
    if form.errors:
        return


def active_role_membership_record(person_id):
    """Gets the currently active role_membership record assigned to a person.

    :param person_id: id of the person you want the active role_membership record of
    :return: active role_membership record
    """
    today = datetime.date.today()
    query = (db.role_membership.person_id == person_id) & (db.role_membership.begin_date <= today)
    query &= (db.role_membership.end_date >= today) | (db.role_membership.end_date == None)
    rows = db(query).select()
    # raise a ValueError if there is more than one row, since we only allow one role_membership to be active at a time.
    if len(rows) > 1:
        raise ValueError(T('There can only be 1 active role_membership record at a time.'))
    return rows.first()


def is_date_within_active_membership_record(active_role_membership_record, begin_date=None):
    """Checks if the given date is in the role_membership that's currently active.

    :param active_role_membership_record: an active role_membership record, use active_role_membership_record()
    :param begin_date: the starting date of the new role_membership record.
    :return: boolean
    """
    if begin_date:

        if active_role_membership_record.end_date:
            return bool(
                active_role_membership_record.begin_date <= begin_date <= active_role_membership_record.end_date)

        else:
            # we do not allow different role memberships to start on the same day, even when they have no ending
            # date. if we were to allow the same begin date on different records, we would at one point get multiple
            # active role memberships.
            return bool(active_role_membership_record.begin_date == begin_date)

    # obviously, if no begin date has been given, this membership can't overlap
    else:
        return False
