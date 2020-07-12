import unittest, transaction
from pyramid import testing


def _initTestingDB():
    from sqlalchemy import create_engine
    from .models import DBSession, Page, Base

    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    with transaction.manager:
        model = Page(title="FrontPage", body="This is the front page")
        DBSession.add(model)
    return DBSession


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_recipe_view(self):
        # from .views import RecipeViews
        # inst = RecipeViews(request)
        # response = inst.hello_world()
        pass

    def test_home_view(self):
        from .views import RecipeViews

        request = testing.DummyRequest()
        inst = RecipeViews(request)
        response = inst.home_view()
        self.assertEqual(response["name"], "Home View")


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from pyramid.paster import get_app

        app = get_app("development.ini")
        from webtest import TestApp

        self.testapp = TestApp(app)

    def tearDown(self):
        from .models import DBSession

        DBSession.remove()

    def test_hello_world(self):
        res = self.testapp.get("/hello/", status=200)
        self.assertIn(b"<h1>Hi Hello View</h1>", res.body)

    def test_home_view(self):
        res = self.testapp.get("/", status=200)
        self.assertIn(b"<h1>Hi Home View</h1>", res.body)

    def test_get_users(self):
        res = self.testapp.get("/get_users/", status=200)
        self.assertIn(b"<h1>All Users</h1>", res.body)

    def test_get_users_without_trailing_slash_should_redirect(self):
        res = self.testapp.get("/get_users", status=307)
        self.assertTrue(res.location.endswith("/get_users/"))
