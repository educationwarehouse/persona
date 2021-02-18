import unittest

from gluon.globals import Request
from gluon.shell import execfile

# to run test: python web2py.py -S persona -M -R applications/persona/tests/test_global_functions.py

execfile("applications/persona/controllers/default.py", globals())  # get access to global web2py variables

# ------------
# IMPORTANT!
# ------------
db = test_db  # using a test database to avoid deleting important data from production database.

execfile('applications/persona/models/db_persona.py', globals())  # get all the persona tables


def setup_test_data():
    try:
        # assigning inserts to a variable, because it returns the record ID
        person_id = db.person.insert(first_name='test',
                                     last_name='user',
                                     email='testuser@test.com')

        role_id = db.role.insert(name='testrole')

        role_membership_id = db.role_membership.insert(role_ids=role_id,
                                                       begin_date=datetime.date.today(),
                                                       end_date=datetime.date.today(),
                                                       person_id=person_id)

        db.commit()
        return person_id, role_id, role_membership_id
    except RuntimeError:
        # rollback the database, because something went wrong
        db.rollback()


def clean_db():
    """DO NOT EXECUTE ON PRODUCTION DATABASE!"""
    db.person.truncate()
    db.role.truncate()
    db.role_membership.truncate()
    db.commit()


class TestGlobalFunctions(unittest.TestCase):

    def setUp(self):
        env = {}
        request = Request(env)
        clean_db()  # making sure we always start off with a clean database during setup
        self.person_id, self.role_id, self.role_membership_id = setup_test_data()

    def test_active_role_membership_record(self):
        resp = active_role_membership_record(person_id=self.person_id)

        # testing if active_role_membership_record is returning the right record
        # in this case resp.person_id has to be 1, because self.person_id is also 1
        self.assertTrue(resp.person_id == self.person_id)

        # testing if the starting date is correct
        self.assertTrue(resp.begin_date == datetime.date.today())

    def test_is_date_within_active_membership_record(self):
        # the role_membership that's currently selected has the beginning- and end date 'datetime.date.today()'
        active = active_role_membership_record(self.person_id)

        resp = is_date_within_active_membership_record(active_role_membership_record=active,
                                                       begin_date=datetime.date.today())
        # we expect resp to be true because the begin_date of the new role_membership record falls within the active
        # period of the active role_membership
        self.assertTrue(resp)

        resp = is_date_within_active_membership_record(active_role_membership_record=active,
                                                       begin_date=None)
        # we now expect resp to be false, since we haven't given a begin_date for the role_membership
        self.assertFalse(resp)


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestGlobalFunctions))
unittest.TextTestRunner(verbosity=2).run(suite)
