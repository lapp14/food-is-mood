import unittest

from pyramid import testing

class TutorialViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_hello_world(self):
        from .views import TutorialViews
        request = testing.DummyRequest()
        inst = TutorialViews(request)
        response = inst.hello_world()
        self.assertEqual(response['name'], 'Hello View')

    def test_home_view(self):
        from .views import TutorialViews
        request = testing.DummyRequest()
        inst = TutorialViews(request)
        response = inst.home_view()
        self.assertEqual(response['name'], 'Home View')

class TutorialFunctionalTests(unittest.TestCase):
    def setUp(self):
        from recipes import main
        app = main({})
        from webtest import TestApp

        self.testapp = TestApp(app)

    def test_hello_world(self):
        res = self.testapp.get('/hello', status=200)
        self.assertIn(b'<h1>Hi Hello View</h1>', res.body)

    def test_home_view(self):
        res = self.testapp.get('/', status=200)
        self.assertIn(b'<h1>Hi Home View</h1>', res.body)

    def test_get_users(self):
        res = self.testapp.get('/get_users', status=200)
        self.assertIn(b'<h1>All Users</h1>', res.body)
