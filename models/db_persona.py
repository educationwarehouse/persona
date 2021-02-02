class NO_ROLE_OVERLAP:
    """Validator to check whether or not the selected role is overlapping with a role that is already assigned to a
    dossier in the given period of time.

    Example:
        Usage:
        Field('rol', 'list:reference rol', requires=NO_ROLE_OVERLAP())

    used for reference fields, rendered as a dropbox.
    """

    def __init__(self, multiple=True,
                 error_message='Een of meerdere rollen zijn tijdens deze periode al toegewezen aan dit dossier'):
        self.error_message = error_message
        self.roles = db(db.rol.id > 0).select()  # we're working with every role in the database for the options field
        self.multiple = multiple  # multiple=True because we're allowing for multiple roles to be selected

    def __call__(self, value):
        try:
            return self.validate(value)
        except Exception:
            raise

    def options(self):
        # creating a list of tuples, this way web2py can create a SELECT object
        items = [(_.id, _.naam) for _ in self.roles]
        # inserting an extra option, so the default field is blank, this way we make sure
        # that items will be selected properly
        items.insert(0, ("", ""))
        return items

    def validate(self, value):
        # if there is no role selected, there's nothing to validate. also, this field is not allowed to be empty.
        if not value:
            self.error_message = 'Dit veld mag niet leeg zijn'
            return value, self.error_message
        # TODO: dit moet later wellicht anders, werkt voor nu
        # this allows for editing the 'dienstverbanden', it ignores the validation
        if 'edit' in request.url:
            return value, None
        # getting all of the records that are currently active for this dossier
        dienstverbanden = current_dienstverbanden(request.vars.dossier_id)
        begin = request.vars.begindatum
        # checking the instance, because even with a field that can handle multiple inputs,
        # sometimes you just want one input.
        if isinstance(value, (tuple, list)):
            # inherit the instance if the value is already a tuple or a list
            values = value
        else:
            # creating a list of values from value
            values = [value]
        for role_id in values:
            # getting the rol record belonging to role_id
            role = db.rol[role_id]
            # appending because check_conflicts() returns either True or False
            conflicting = check_conflicts(active_dienstverbanden=dienstverbanden,
                                          role=role,
                                          begin_date=begin if begin else None)
            if conflicting:
                # showing error message if a conflict occurs
                return value, self.error_message
            else:
                pass
        return value, None
        # else:
        #     # getting selected role from the database
        #     role = db.rol[value]
        #     conflicting = check_conflicts(active_dienstverbanden=dienstverbanden,
        #                                 role=role,
        #                                 begin_date=begin if begin else None)
        #     # if there are any conflicts, show the error message
        #     if conflicting:
        #         return value, self.error_message
        #     else:
        #         return value, None


class IS_CAPITALIZED:
    """"Never returns an error, only converts string input value to a capitalized string.

    Example:
        Usage:
         Field('naam', 'string', requires=IS_CAPITALIZED()),
    """

    def __call__(self, value):
        try:
            return self.validate(value)
        except Exception:
            raise

    def validate(self, value):
        return value.capitalize(), None


db.define_table('dossier',
                Field('voornaam', 'string', required=True, requires=IS_NOT_EMPTY()),
                Field('achternaam', 'string', required=True, requires=IS_NOT_EMPTY()),
                # using both unique=True and IS_NOT_IN_DB, because IS_NOT_IN_DB enforces that the inserted value is
                # unique on a form level. unique=True enforces this on a database level. This means that if we
                # were to insert a value in any other way than by a form, the inserted value still has to be unique.
                Field('email', 'string', unique=True, requires=[IS_EMAIL(),
                                                                IS_NOT_EMPTY(),
                                                                IS_NOT_IN_DB(db, 'dossier.email')]
                      ),
                plural='dossiers',
                format=lambda r: f'{r.id} <{r.voornaam} {r.achternaam}>'
                )

db.define_table('rol',
                Field('naam', 'string', required=True, unique=True, requires=[IS_NOT_EMPTY(),
                                                                              IS_CAPITALIZED(),
                                                                              IS_ALPHANUMERIC(),
                                                                              IS_NOT_IN_DB(db, 'rol.naam')]
                      ),
                plural='rollen',
                format=lambda r: r.naam
                )

db.define_table('dienstverband',
                # rol_id has to be a list of references for it to allow multiple roles within the same
                # dienstverband record
                Field('rol_id', 'list:reference rol', requires=NO_ROLE_OVERLAP(), label='Rol(len)'),
                Field('begindatum', 'date'),
                Field('einddatum', 'date'),
                Field('dossier_id', 'reference dossier', required=True, label='Dossier'),
                plural='dienstverbanden'
                )
