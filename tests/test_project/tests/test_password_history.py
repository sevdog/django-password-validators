from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from django_password_validators.password_history.password_validation import UniquePasswordsValidator
from django_password_validators.password_history.hashers import (
    HistoryVeryStrongHasher,
    HistoryHasher
)
from django_password_validators.password_history.models import (
    UserPasswordHistoryConfig,
    PasswordHistory
)

from .base import PasswordsTestCase


class UniquePasswordsValidatorTestCase(PasswordsTestCase):

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

    @override_settings(AUTH_PASSWORD_VALIDATORS=[{
        'NAME': 'django_password_validators.password_history.password_validation.UniquePasswordsValidator',
        'OPTIONS': {
            'last_passwords': 0
        }
    }])
    def test_last_password__1_pass_history(self):
        user1 = self.create_user(1)
        user_config_1 = UserPasswordHistoryConfig.objects.filter(user=user1)[0]
        PasswordHistory.objects.filter(user_config=user_config_1).delete()

        # This password cannot be taken during validation. It is out of range.
        # It is the oldest so out of range.
        self.user_change_password(user_number=1, password_number=2)
        self.user_change_password(user_number=1, password_number=1)
        self.user_change_password(user_number=1, password_number=3)

        # Passwords known in the scope we are checking
        self.assert_password_validation_False(user_number=1, password_number=2)
        # Passwords known in the scope we are checking
        self.assert_password_validation_False(user_number=1, password_number=1)
        # Passwords known in the scope we are checking
        self.assert_password_validation_False(user_number=1, password_number=3)

        # New unknown password
        self.assert_password_validation_True(user_number=1, password_number=4)

        self.assertEqual(PasswordHistory.objects.filter(user_config__user=user1).count(), 3)

    @override_settings(AUTH_PASSWORD_VALIDATORS=[{
        'NAME': 'django_password_validators.password_history.password_validation.UniquePasswordsValidator',
        'OPTIONS': {
            'last_passwords': 1
        }
    }])
    def test_last_password__1_pass_history(self):
        user1 = self.create_user(1)
        user_config_1 = UserPasswordHistoryConfig.objects.filter(user=user1)[0]
        PasswordHistory.objects.filter(user_config=user_config_1).delete()

        # This password cannot be taken during validation. It is out of range.
        # It is the oldest so out of range.
        self.user_change_password(user_number=1, password_number=2)
        self.user_change_password(user_number=1, password_number=1)
        self.user_change_password(user_number=1, password_number=3)

        # Password out of scope. We interpret it as if it had never been entered.
        self.assert_password_validation_True(user_number=1, password_number=2)
        # Password out of scope. We interpret it as if it had never been entered.
        self.assert_password_validation_True(user_number=1, password_number=1)
        # Passwords known in the scope we are checking
        self.assert_password_validation_False(user_number=1, password_number=3)

        # New unknown password
        self.assert_password_validation_True(user_number=1, password_number=4)

        self.assertEqual(PasswordHistory.objects.filter(user_config__user=user1).count(), 1)

    @override_settings(AUTH_PASSWORD_VALIDATORS=[{
        'NAME': 'django_password_validators.password_history.password_validation.UniquePasswordsValidator',
        'OPTIONS': {
            'last_passwords': 2
        }
    }])
    def test_last_password__1_pass_history(self):
        user1 = self.create_user(1)
        user_config_1 = UserPasswordHistoryConfig.objects.filter(user=user1)[0]
        PasswordHistory.objects.filter(user_config=user_config_1).delete()

        # This password cannot be taken during validation. It is out of range.
        # It is the oldest so out of range.
        self.user_change_password(user_number=1, password_number=2)
        self.user_change_password(user_number=1, password_number=1)
        self.user_change_password(user_number=1, password_number=3)

        # Password out of scope. We interpret it as if it had never been entered.
        self.assert_password_validation_True(user_number=1, password_number=2)
        # Passwords known in the scope we are checking
        self.assert_password_validation_False(user_number=1, password_number=1)
        # Passwords known in the scope we are checking
        self.assert_password_validation_False(user_number=1, password_number=3)

        # New unknown password
        self.assert_password_validation_True(user_number=1, password_number=4)

        self.assertEqual(PasswordHistory.objects.filter(user_config__user=user1).count(), 2)

    @override_settings(AUTH_PASSWORD_VALIDATORS=[{
        'NAME': 'django_password_validators.password_history.password_validation.UniquePasswordsValidator',
        'OPTIONS': {
            'last_passwords': 3
        }
    }])
    def test_last_password__1_pass_history(self):
        user1 = self.create_user(1)
        user_config_1 = UserPasswordHistoryConfig.objects.filter(user=user1)[0]
        PasswordHistory.objects.filter(user_config=user_config_1).delete()

        # This password cannot be taken during validation. It is out of range.
        # It is the oldest so out of range.
        self.user_change_password(user_number=1, password_number=2)
        self.user_change_password(user_number=1, password_number=1)
        self.user_change_password(user_number=1, password_number=3)

        # Passwords known in the scope we are checking
        self.assert_password_validation_False(user_number=1, password_number=2)
        # Passwords known in the scope we are checking
        self.assert_password_validation_False(user_number=1, password_number=1)
        # Passwords known in the scope we are checking
        self.assert_password_validation_False(user_number=1, password_number=3)

        # New unknown password
        self.assert_password_validation_True(user_number=1, password_number=4)

        self.assertEqual(PasswordHistory.objects.filter(user_config__user=user1).count(), 3)

    @override_settings(AUTH_PASSWORD_VALIDATORS=[{
        'NAME': 'django_password_validators.password_history.password_validation.UniquePasswordsValidator',
        'OPTIONS': {
            'last_passwords': 4
        }
    }])
    def test_last_password__1_pass_history(self):
        user1 = self.create_user(1)
        user_config_1 = UserPasswordHistoryConfig.objects.filter(user=user1)[0]
        PasswordHistory.objects.filter(user_config=user_config_1).delete()

        # This password cannot be taken during validation. It is out of range.
        # It is the oldest so out of range.
        self.user_change_password(user_number=1, password_number=2)
        self.user_change_password(user_number=1, password_number=1)
        self.user_change_password(user_number=1, password_number=3)

        # Passwords known in the scope we are checking
        self.assert_password_validation_False(user_number=1, password_number=2)
        # Passwords known in the scope we are checking
        self.assert_password_validation_False(user_number=1, password_number=1)
        # Passwords known in the scope we are checking
        self.assert_password_validation_False(user_number=1, password_number=3)

        # New unknown password
        self.assert_password_validation_True(user_number=1, password_number=4)

        self.assertEqual(PasswordHistory.objects.filter(user_config__user=user1).count(), 3)

    @override_settings(AUTH_PASSWORD_VALIDATORS=[{
        'NAME': 'django_password_validators.password_history.password_validation.UniquePasswordsValidator',
        'OPTIONS': {
            'last_passwords': 2
        }
    }])
    def test_last_password(self):
        user1 = self.create_user(1)
        user2 = self.create_user(2)  # needed to check if we are not deleting passwords from another user
        user_config_1 = UserPasswordHistoryConfig.objects.filter(user=user1)[0]
        user_config_2 = UserPasswordHistoryConfig.objects.filter(user=user2)[0]
        PasswordHistory.objects.filter(user_config=user_config_1).delete()
        # This password cannot be taken during validation. It is out of range.
        # It is the oldest so out of range.
        self.user_change_password(user_number=1, password_number=2)
        self.user_change_password(user_number=1, password_number=1)
        self.user_change_password(user_number=1, password_number=3)
        # Password out of scope. We interpret it as if it had never been entered.
        self.assert_password_validation_True(user_number=1, password_number=2)
        # New unknown password
        self.assert_password_validation_True(user_number=1, password_number=4)
        # Passwords known in the scope we are checking
        self.assert_password_validation_False(user_number=1, password_number=1)
        self.assert_password_validation_False(user_number=1, password_number=3)

        self.assertEqual(PasswordHistory.objects.filter(user_config=user_config_1).count(), 2)
        self.assertEqual(PasswordHistory.objects.filter(user_config=user_config_2).count(), 1)

        # Two new non-existent passwords
        self.user_change_password(user_number=1, password_number=4)
        self.user_change_password(user_number=1, password_number=2)

        # Password out of scope. We interpret it as if it had never been entered.
        self.assert_password_validation_True(user_number=1, password_number=1)
        self.assert_password_validation_True(user_number=1, password_number=3)

        # Passwords known in the scope we are checking
        self.assert_password_validation_False(user_number=1, password_number=4)
        self.assert_password_validation_False(user_number=1, password_number=2)

        self.assertEqual(PasswordHistory.objects.filter(user_config=user_config_1).count(), 2)

        # We check for interaction with the other user
        self.assert_password_validation_False(user_number=2, password_number=1)
        self.assert_password_validation_True(user_number=2, password_number=2)
        self.assert_password_validation_True(user_number=2, password_number=3)
        self.assert_password_validation_True(user_number=2, password_number=4)
        self.assertEqual(PasswordHistory.objects.filter(user_config=user_config_2).count(), 1)

    def test_last_password__delete_old_passwords__one_user__infinite_passwords_hist(self):
        user1 = self.create_user(1)
        PasswordHistory.objects.filter(user_config__user=user1).delete()
        user1_uphc1 = UserPasswordHistoryConfig.objects.filter(user=user1)[0]
        ph1 = PasswordHistory(user_config=user1_uphc1, password='2 user1 hash1')  # to delete
        ph1.save()
        ph2 = PasswordHistory(user_config=user1_uphc1, password='1 user1 hash2')  # to delete
        ph2.save()
        ph3 = PasswordHistory(user_config=user1_uphc1, password='3 user1 hash3')
        ph3.save()
        upv = UniquePasswordsValidator(last_passwords=0)
        upv.delete_old_passwords(user1)
        upv = UniquePasswordsValidator(last_passwords=-1)
        upv.delete_old_passwords(user1)
        current_passwords = list(
            PasswordHistory.objects.filter(user_config__user=user1).values_list('pk', flat=True).order_by('pk'))
        self.assertEqual(
            current_passwords,
            [ph1.pk, ph2.pk, ph3.pk],
        )

    def test_last_password__delete_old_passwords__one_user__one_password_hist(self):
        user1 = self.create_user(1)
        user1_uphc1 = UserPasswordHistoryConfig.objects.filter(user=user1)[0]
        ph1 = PasswordHistory(user_config=user1_uphc1, password='2 user1 hash1')  # to delete
        ph1.save()
        ph2 = PasswordHistory(user_config=user1_uphc1, password='1 user1 hash2')  # to delete
        ph2.save()
        ph3 = PasswordHistory(user_config=user1_uphc1, password='3 user1 hash3')
        ph3.save()
        upv = UniquePasswordsValidator(last_passwords=1)
        upv.delete_old_passwords(user1)
        current_passwords = list(
            PasswordHistory.objects.filter(user_config__user=user1).values_list('pk', flat=True).order_by('pk'))
        self.assertEqual(
            current_passwords,
            [ph3.pk],
        )

    def test_last_password__delete_old_passwords__one_user__two_passwords_hist(self):
        user1 = self.create_user(1)
        user1_uphc1 = UserPasswordHistoryConfig.objects.filter(user=user1)[0]
        ph1 = PasswordHistory(user_config=user1_uphc1, password='2 user1 hash1')  # to delete
        ph1.save()
        ph2 = PasswordHistory(user_config=user1_uphc1, password='1 user1 hash2')
        ph2.save()
        ph3 = PasswordHistory(user_config=user1_uphc1, password='3 user1 hash3')
        ph3.save()
        upv = UniquePasswordsValidator(last_passwords=2)
        upv.delete_old_passwords(user1)
        current_passwords = list(
            PasswordHistory.objects.filter(user_config__user=user1).values_list('pk', flat=True).order_by('pk'))
        self.assertEqual(
            current_passwords,
            [ph2.pk, ph3.pk],
        )

    def test_last_password__delete_old_passwords__one_user__three_passwords_hist(self):
        user1 = self.create_user(1)
        user1_uphc1 = UserPasswordHistoryConfig.objects.filter(user=user1)[0]
        ph1 = PasswordHistory(user_config=user1_uphc1, password='2 user1 hash1')
        ph1.save()
        ph2 = PasswordHistory(user_config=user1_uphc1, password='1 user1 hash2')
        ph2.save()
        ph3 = PasswordHistory(user_config=user1_uphc1, password='3 user1 hash3')
        ph3.save()
        upv = UniquePasswordsValidator(last_passwords=3)
        upv.delete_old_passwords(user1)
        current_passwords = list(
            PasswordHistory.objects.filter(user_config__user=user1).values_list('pk', flat=True).order_by('pk'))
        self.assertEqual(
            current_passwords,
            [ph1.pk, ph2.pk, ph3.pk],
        )

    def test_last_password__delete_old_passwords__two_users(self):
        user1 = self.create_user(1)
        user2 = self.create_user(2)
        PasswordHistory.objects.all().delete()

        user1_uphc1 = UserPasswordHistoryConfig.objects.filter(user=user1)[0]
        user2_uphc1 = UserPasswordHistoryConfig.objects.filter(user=user2)[0]

        ph1 = PasswordHistory(user_config=user1_uphc1, password='2 user1 hash1')  # to delete
        ph1.save()
        ph1_u2 = PasswordHistory(user_config=user2_uphc1, password='2 user2 hash1')  # to delete
        ph1_u2.save()
        ph2 = PasswordHistory(user_config=user1_uphc1, password='1 user1 hash2')
        ph2.save()
        ph2_u2 = PasswordHistory(user_config=user2_uphc1, password='1 user2 hash2')
        ph2_u2.save()
        ph3 = PasswordHistory(user_config=user1_uphc1, password='3 user1 hash3')
        ph3.save()
        ph3_u2 = PasswordHistory(user_config=user2_uphc1, password='3 user2 hash3')
        ph3_u2.save()

        upv = UniquePasswordsValidator(last_passwords=2)
        upv.delete_old_passwords(user1)

        current_passwords = list(
            PasswordHistory.objects. \
                filter(user_config__user=user1). \
                values_list('pk', flat=True). \
                order_by('pk')
        )
        self.assertEqual(
            current_passwords,
            [ph2.pk, ph3.pk],
            msg='Only the passwords of the first user can be deleted'
        )

        current_passwords = list(
            PasswordHistory.objects. \
                filter(user_config__user=user2). \
                values_list('pk', flat=True). \
                order_by('pk')
        )
        self.assertEqual(
            current_passwords,
            [ph1_u2.pk, ph2_u2.pk, ph3_u2.pk],
            msg='Password history of the other user must be unchanged'
        )

    def test_last_password__delete_old_passwords__multiple_UserPasswordHistoryConfig(self):
        user1 = self.create_user(1)
        PasswordHistory.objects.all().delete()

        user1_uphc1 = UserPasswordHistoryConfig.objects.filter(user=user1)[0]
        user1_uphc2 = UserPasswordHistoryConfig(user=user1, salt='qwerty', iterations=10)
        user1_uphc2.save()

        ph1 = PasswordHistory(user_config=user1_uphc1, password='2 user1 hash1')  # to delete
        ph1.save()
        ph2 = PasswordHistory(user_config=user1_uphc2, password='1 user1 hash2')
        ph2.save()
        ph3 = PasswordHistory(user_config=user1_uphc1, password='3 user1 hash3')
        ph3.save()
        upv = UniquePasswordsValidator(last_passwords=2)
        upv.delete_old_passwords(user1)
        current_passwords = list(
            PasswordHistory.objects.filter(user_config__user=user1).values_list('pk', flat=True).order_by('pk'))
        self.assertEqual(
            current_passwords,
            [ph2.pk, ph3.pk],
            msg='Only the oldest password can be deleted = ph1'
        )
        PasswordHistory.objects.all().delete()

        ph1 = PasswordHistory(user_config=user1_uphc2, password='2 user1 hash1')  # to delete
        ph1.save()
        ph2 = PasswordHistory(user_config=user1_uphc1, password='1 user1 hash2')
        ph2.save()
        ph3 = PasswordHistory(user_config=user1_uphc1, password='3 user1 hash3')
        ph3.save()
        upv = UniquePasswordsValidator(last_passwords=2)
        upv.delete_old_passwords(user1)
        current_passwords = list(
            PasswordHistory.objects.filter(user_config__user=user1).values_list('pk', flat=True).order_by('pk'))
        self.assertEqual(
            current_passwords,
            [ph2.pk, ph3.pk],
            msg='Only the oldest password can be deleted = ph1'
        )
        PasswordHistory.objects.all().delete()

        ph1 = PasswordHistory(user_config=user1_uphc2, password='2 user1 hash1')  # to delete
        ph1.save()
        ph2 = PasswordHistory(user_config=user1_uphc1, password='1 user1 hash2')
        ph2.save()
        ph3 = PasswordHistory(user_config=user1_uphc2, password='3 user1 hash3')
        ph3.save()
        upv = UniquePasswordsValidator(last_passwords=2)
        upv.delete_old_passwords(user1)
        current_passwords = list(
            PasswordHistory.objects.filter(user_config__user=user1).values_list('pk', flat=True).order_by('pk'))
        self.assertEqual(
            current_passwords,
            [ph2.pk, ph3.pk],
            msg='Only the oldest password can be deleted = ph1'
        )
        PasswordHistory.objects.all().delete()
