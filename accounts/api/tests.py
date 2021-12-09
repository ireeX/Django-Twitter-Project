from utils.testcases import TestCase
from rest_framework.test import APIClient

LOGIN_URL ='/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'

class AccountApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = self.create_user('admin', 'admin@twitter.com', 'correct password')

    def test_login(self):
        # test for login HTTP method, which must use GET method
        response = self.client.get(path=LOGIN_URL, data={
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 405)

        # test for invalid credentials
        response = self.client.post(path=LOGIN_URL, data={
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        # test for login status without authentication
        response = self.client.get(path=LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

        # test for login authentication
        response = self.client.post(path=LOGIN_URL, data={
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'admin@twitter.com')

        # test for login status after login authentication
        response = self.client.get(path=LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):

        # login first
        self.client.post(LOGIN_URL, {
            'username': 'admin',
            'password': 'correct password',
        })

        # confirm user logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # test HTTP method, which logout only allow POST method
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # test logout
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        # confirm user logged out
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'test_user',
            'email': 'test@twitter.com',
            'password': 'test password',
        }

        # test for HTTP method
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # test false email
        response = self.client.post(SIGNUP_URL, {
            'username': 'test_user',
            'email': 'test bad email address',
            'password': 'any password',
        })
        self.assertEqual(response.status_code, 400)

        # test short password
        response = self.client.post(SIGNUP_URL, {
            'username': 'test_user',
            'email': 'test@twitter.com',
            'password': 'test',
        })
        self.assertEqual(response.status_code, 400)

        # test long username
        response = self.client.post(SIGNUP_URL, {
            'username': 'testtesttesttesttesttesttesttesttesttesttesttesttesttest',
            'email': 'test@twitter.com',
            'password': 'test password',
        })
        self.assertEqual(response.status_code, 400)

        # test for successful sign up
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], data['username'])

        # confirm logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

