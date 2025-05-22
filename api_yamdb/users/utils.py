from random import choice

from django.conf import settings
from django.core.mail import send_mail

INVALID_SYMBOLS_ASCII = {34, 92}  # символы " \
VALID_SYMBOLS_ASCII = tuple(set(range(33, 127)) - INVALID_SYMBOLS_ASCII)


def send_confirmation_code(user):
    code = ''.join(chr(choice(VALID_SYMBOLS_ASCII))
                   for _ in range(settings.CONFIRMATION_CODE_LENGTH))
    # user.update(confirmation_code=code)
    send_mail(
        subject='Confirmation code',
        message=(f'\t{user.username},\nВаш код подтверждения '
                 f'для получения токена YaMDb: {code}'),
        from_email=None,
        recipient_list=[user.email],
    )
