from utils.testcases import TestCase
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile


LOGIN_URL ='/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'
USER_PROFILE_DETAIL_URL = '/api/profiles/{}/'


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


class UserProfileApiTests(TestCase):

    def test_update(self):
        user1, client1 = self.create_user_and_client('user1')
        user_profile = user1.profile
        user_profile.nickname = 'test nickname'
        user_profile.save()
        url = USER_PROFILE_DETAIL_URL.format(user1.id)

        # test authorization for update profile
        user2, client2 = self.create_user_and_client('user2')
        response = client2.put(url, {
            'nickname': 'updated nickname',
        })
        self.assertEqual(response.status_code, 403)
        user_profile.refresh_from_db()
        self.assertEqual(user_profile.nickname, 'test nickname')

        # test normal update nickname
        response = client1.put(url, {
            'nickname': 'updated nickname'
        })
        self.assertEqual(response.status_code, 200)
        user_profile.refresh_from_db()
        self.assertEqual(user_profile.nickname, 'updated nickname')

        # test update avatar
        response = client1.put(url, {
            'avatar': SimpleUploadedFile(
                name = 'test_avatar.jpg',
                # str.encode() turn the str to byte
                content=str.encode('a fake image'),
                content_type='image/jpeg',
            )
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual('test_avatar' in response.data['avatar'], True)
        user_profile.refresh_from_db()
        self.assertIsNotNone(user_profile.avatar)