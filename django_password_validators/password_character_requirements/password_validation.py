from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


class PasswordCharacterValidator():

    def __init__(
            self,
            min_length_digit=1,
            min_length_alpha=1,
            min_length_special=1,
            min_length_lower=1,
            min_length_upper=1,
            special_characters="[~!@#$%^&*()_+{}\":;'[]"
    ):
        self.min_length_digit = min_length_digit
        self.min_length_alpha = min_length_alpha
        self.min_length_special = min_length_special
        self.min_length_lower = min_length_lower
        self.min_length_upper = min_length_upper
        self.special_characters = special_characters

    def validate(self, password, user=None):
        validation_errors = []
        if len([char for char in password if char.isdigit()]) < self.min_length_digit:
            validation_errors.append(ValidationError(
                _('Password must contain at least %(min_length)d digit.'),
                params={'min_length': self.min_length_digit},
                code='min_length_digit',
            ))
        if len([char for char in password if char.isalpha()]) < self.min_length_alpha:
            validation_errors.append(ValidationError(
                _('Password must contain at least %(min_length)d letter.'),
                params={'min_length': self.min_length_alpha},
                code='min_length_alpha',
            ))
        if len([char for char in password if char.isupper()]) < self.min_length_upper:
            validation_errors.append(ValidationError(
                _('Password must contain at least %(min_length)d capital letter.'),
                params={'min_length': self.min_length_upper},
                code='min_length_upper_characters',
            ))
        if len([char for char in password if char.islower()]) < self.min_length_lower:
            validation_errors.append(ValidationError(
                _('Password must contain at least %(min_length)d small letter.'),
                params={'min_length': self.min_length_lower},
                code='min_length_lower_characters',
            ))
        if len([char for char in password if char in self.special_characters]) < self.min_length_special:
            validation_errors.append(ValidationError(
                _('Password must contain at least %(min_length)d special character.'),
                params={'min_length': self.min_length_special},
                code='min_length_special_characters',
            ))
        if validation_errors:
            raise ValidationError(validation_errors)

    def get_help_text(self):
        validation_req = []
        if self.min_length_alpha:
            validation_req.append(_("%s letters") % str(self.min_length_alpha))
        if self.min_length_digit:
            validation_req.append(_("%s digits") % str(self.min_length_digit))
        if self.min_length_lower:
            validation_req.append(_("%s lower case letters") % str(self.min_length_lower))
        if self.min_length_upper:
            validation_req.append(_("%s upper case letters") % str(self.min_length_upper))
        if self.special_characters:
            validation_req.append(
                _("%s special characters such as %s") % (str(self.min_length_alpha), self.special_characters))
        return _("Password must contaion at least") + ' ' + ', '.join(validation_req) + '.'
