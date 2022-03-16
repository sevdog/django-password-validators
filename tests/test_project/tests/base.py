from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.test import TestCase


class PasswordsTestCase(TestCase):
    """
    Local varibles:
        self.UserModel - user model class
    """

    PASSWORD_TEMPLATE = 'ABCDEFGHIJKLMNOPRSTUWXYZ_%d'

    def create_user(self, number=1):
        user = self.UserModel.objects.create_user(
            'test%d' % number,
            email='test%d@example.com' % number,
        )
        user.set_password(self.PASSWORD_TEMPLATE % 1)
        user.save()
        return user

    def user_change_password(self, user_number, password_number):
        user = self.UserModel.objects.get(username='test%d' % user_number)
        user.set_password(self.PASSWORD_TEMPLATE % password_number)
        user.save()

    def assert_password_validation_True(self, user_number, password_number):
        user = self.UserModel.objects.get(username='test%d' % user_number)
        validate_password(
            self.PASSWORD_TEMPLATE % password_number,
            user
        )

    def assert_password_validation_False(self, user_number, password_number):
        user = self.UserModel.objects.get(username='test%d' % user_number)

        try:
            validate_password(
                self.PASSWORD_TEMPLATE % password_number,
                user
            )
        except ValidationError as e:
            for error in e.error_list:
                if e.error_list[0].code == 'password_used':
                    return
            else:
                raise e

    def setUp(self):
        self.UserModel = get_user_model()
        super(PasswordsTestCase, self).setUp()

    def tearDown(self):
        self.UserModel.objects.all().delete()
        super(PasswordsTestCase, self).tearDown()
