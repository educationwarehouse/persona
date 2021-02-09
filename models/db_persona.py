class CAPITALIZE:
    """"Never returns an error, only converts string input value to a capitalized string.

    Example:
        Usage:
         Field('naam', 'string', requires=IS_CAPITALIZED()),
    """

    def __call__(self, value):
        return self.validate(value)

    def validate(self, value):
        if isinstance(value, str):
            return value.capitalize(), None
        else:
            return value, 'Value has to be a string'


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
                                                                              CAPITALIZE(),
                                                                              IS_ALPHANUMERIC(),
                                                                              IS_NOT_IN_DB(db, 'rol.naam')]
                      ),
                plural='rollen',
                format=lambda r: r.naam
                )

db.define_table('dienstverband',
                # rol_id has to be a list of references for it to allow multiple roles within the same
                # dienstverband record
                Field('rol_id', 'list:reference rol', label='Rol(len)'),
                Field('begindatum', 'date', requires=IS_EMPTY_OR(IS_DATE())),
                Field('einddatum', 'date', requires=IS_EMPTY_OR(IS_DATE())),
                Field('dossier_id', 'reference dossier', required=True, label='Dossier'),
                plural='dienstverbanden'
                )
