from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.test import TestCase

from django_password_validators.password_history.password_validation import UniquePasswordsValidator
from django_password_validators.password_history.hashers import (
    HistoryVeryStrongHasher,
    HistoryHasher
)
from django_password_validators.password_history.models import (
    UserPasswordHistoryConfig,
    PasswordHistory
)


class UniquePasswordsValidatorTestCase(TestCase):
    """
    Local varibles:
        self.UserModel - user model class
    """

    PASSWORD_TEMPLATE = 'ABCDEFGHIJKLMNOPRSTUWXYZ_%d'

    def create_user(self, number=1):
        return self.UserModel.objects.create_user(
            'test%d' % number,
            email='test%d@example.com' % number,
            password=self.PASSWORD_TEMPLATE % 1
        )

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
        super(UniquePasswordsValidatorTestCase, self).setUp()

    def tearDown(self):
        self.UserModel.objects.all().delete()
        super(UniquePasswordsValidatorTestCase, self).tearDown()

    def test_create_user(self):
        self.create_user(1)
        self.assertEqual(PasswordHistory.objects.all().count(), 1)
        self.assertEqual(UserPasswordHistoryConfig.objects.all().count(), 1)

    def test_none_user(self):
        dummy_user = get_user_model()
        upv = UniquePasswordsValidator()
        upv.validate('qwerty', None)
        upv.password_changed('qwerty', None)

        self.assertEqual(PasswordHistory.objects.all().count(), 0)
        self.assertEqual(UserPasswordHistoryConfig.objects.all().count(), 0)

    def test_not_saved_user(self):
        dummy_user = get_user_model()
        upv = UniquePasswordsValidator()
        upv.validate('qwerty', dummy_user)
        upv.password_changed('qwerty', dummy_user)

        dummy_user = get_user_model()()
        upv = UniquePasswordsValidator()
        upv.validate('qwerty', dummy_user)
        upv.password_changed('qwerty', dummy_user)

        self.assertEqual(PasswordHistory.objects.all().count(), 0)
        self.assertEqual(UserPasswordHistoryConfig.objects.all().count(), 0)

    def test_create_multiple_users(self):
        self.create_user(1)
        self.create_user(2)
        self.assertEqual(PasswordHistory.objects.all().count(), 2)
        self.assertEqual(UserPasswordHistoryConfig.objects.all().count(), 2)

    def test_user_changed_password(self):
        self.create_user(1)
        self.user_change_password(user_number=1, password_number=2)
        # We check that there are no duplicate hashes passwords in the database
        self.user_change_password(user_number=1, password_number=2)
        # They must be only two hashes
        self.assertEqual(PasswordHistory.objects.all().count(), 2)
        self.assert_password_validation_False(user_number=1, password_number=2)
        self.assert_password_validation_True(user_number=1, password_number=3)
        self.user_change_password(user_number=1, password_number=3)
        self.assert_password_validation_False(user_number=1, password_number=3)

    def test_change_number_hasher_iterations(self):
        self.create_user(1)
        self.user_change_password(user_number=1, password_number=2)
        with self.settings(
                DPV_DEFAULT_HISTORY_HASHER='django_password_validators.password_history.hashers.HistoryVeryStrongHasher'):
            self.assert_password_validation_False(
                user_number=1,
                password_number=1
            )
            self.assert_password_validation_False(
                user_number=1,
                password_number=2
            )
            self.assert_password_validation_True(
                user_number=1,
                password_number=3
            )
            self.user_change_password(
                user_number=1,
                password_number=3
            )
            self.assert_password_validation_False(
                user_number=1,
                password_number=3
            )

            self.assertEqual(
                PasswordHistory.objects.filter(
                    user_config__iterations=HistoryHasher.iterations).count(),
                2,
            )
            self.assertEqual(
                PasswordHistory.objects.filter(
                    user_config__iterations=HistoryVeryStrongHasher.iterations).count(),
                1,
            )
