import unittest

from pyramid import testing

class TutorialViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_hello_world(self):
        from .views import hello_world

        request = testing.DummyRequest()
        response = hello_world(request)
        self.assertEqual(response.status_code, 200)

    def test_get_users(self):
        from .views import get_users

        request = testing.DummyRequest()
        response = get_users(request)
        self.assertEqual(response.status_code, 200)

class TutorialFunctionalTests(unittest.TestCase):
    def setUp(self):
        from recipes import main
        app = main({})
        from webtest import TestApp

        self.testapp = TestApp(app)

    def test_hello_world(self):
        res = self.testapp.get('/', status=200)
        self.assertIn(b'<h1>Hello World!</h1>', res.body)
