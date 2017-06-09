from django.core.exceptions import ValidationError
import datetime


def validate_policy_date(ticked, date, name):
    """Raise a ValidationError if the date is not present or is in the future.
    """
    now = datetime.datetime.now()

    if date and not ticked:
        msg = '%s must be ticked if Date present.' % name
        raise ValidationError(msg)

    if ticked:
        if not date:
            msg = 'Date must be present if %s ticked.' % name
            raise ValidationError(msg)
        elif date > now.date():
            msg = '%s date cannot be in the future.' % name
            raise ValidationError(msg)
