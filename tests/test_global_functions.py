import unittest

from gluon.globals import Request
from gluon.shell import execfile

# to run test: python web2py.py -S persona -M -R applications/persona/tests/test_global_functions.py

execfile("applications/persona/controllers/default.py", globals())  # get access to global web2py variables
db = test_db  # using a test database to not get rid of the data stored in the production database
execfile('applications/persona/models/db_persona.py', globals())  # get all the persona tables


def setup_test_data():
    try:
        # assigning inserts to a variable, because it returns the record ID
        person_id = db.person.insert(first_name='test', last_name='user', email='testuser@test.com')
        role_id = db.role.insert(name='testrole')
        role_membership_id = db.role_membership.insert(role_ids=role_id, begin_date=datetime.date.today(),
                                                       end_date=datetime.date.today(), person_id=person_id)
        db.commit()
        return person_id, role_id, role_membership_id
    except RuntimeError:
        # rollback the database, because something went wrong
        db.rollback()


def clean_db():
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

    def test_active_role_memberships(self):
        resp = active_role_memberships(person_id=self.person_id)
        # length of resp has to be one, since we started from a clean database and
        # created one dienstverband record for this dossier_id
        # we're testing if any record even exists
        self.assertEqual(1, len(resp))

        # testing if resp is returning the right records
        # in this case resp[0].dossier_id has to be 1, because self.person_id is also 1
        self.assertTrue(resp[0].person_id == self.person_id)

    def test_check_conflicts(self):
        # the dossier that's currently selected has the beginning and end date 'datetime.date.today()'
        active = active_role_memberships(self.person_id)
        resp = check_conflicts(active_role_memberships=active, exclude=None, begin_date=datetime.date.today())
        # we expect resp to be true because the new role_membership record is conflicting with a currently active
        # role membership.
        self.assertTrue(resp)
        resp = check_conflicts(active_role_memberships=active, exclude=None, begin_date=None)
        # we now expect resp to be false, since we haven't given a begin_date for the role_membership
        self.assertFalse(resp)


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestGlobalFunctions))
unittest.TextTestRunner(verbosity=2).run(suite)
