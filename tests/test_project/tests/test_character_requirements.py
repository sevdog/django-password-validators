from django.core.exceptions import ValidationError

from django_password_validators.password_character_requirements.password_validation import PasswordCharacterValidator

from .base import PasswordsTestCase


class UniquePasswordsValidatorTestCase(PasswordsTestCase):

    def test_digit(self):
        pv = PasswordCharacterValidator(
            min_length_digit=1,
            min_length_alpha=0,
            min_length_special=0,
            min_length_lower=0,
            min_length_upper=0,
            special_characters="[]"
        )
        pv.validate('1')
        with self.assertRaises(ValidationError):
            pv.validate('abc')

    def test_alpha(self):
        pv = PasswordCharacterValidator(
            min_length_digit=0,
            min_length_alpha=1,
            min_length_special=0,
            min_length_lower=0,
            min_length_upper=0,
            special_characters="[]"
        )
        pv.validate('a')
        with self.assertRaises(ValidationError):
            pv.validate('1')

    def test_special(self):
        pv = PasswordCharacterValidator(
            min_length_digit=0,
            min_length_alpha=0,
            min_length_special=1,
            min_length_lower=0,
            min_length_upper=0,
            special_characters="[]"
        )
        pv.validate(']')
        with self.assertRaises(ValidationError):
            pv.validate('1')

    def test_lower(self):
        pv = PasswordCharacterValidator(
            min_length_digit=0,
            min_length_alpha=0,
            min_length_special=0,
            min_length_lower=1,
            min_length_upper=0,
            special_characters="[]"
        )
        pv.validate('a')
        with self.assertRaises(ValidationError):
            pv.validate('A')

    def test_upper(self):
        pv = PasswordCharacterValidator(
            min_length_digit=0,
            min_length_alpha=0,
            min_length_special=0,
            min_length_lower=0,
            min_length_upper=1,
            special_characters="[]"
        )
        pv.validate('A')
        with self.assertRaises(ValidationError):
            pv.validate('a')

    def test_all(self):
        pv = PasswordCharacterValidator(
            min_length_digit=2,
            min_length_alpha=4,
            min_length_special=2,
            min_length_lower=2,
            min_length_upper=2,
            special_characters="!@#$%[]"
        )
        pv.validate('12ab[]AB')
