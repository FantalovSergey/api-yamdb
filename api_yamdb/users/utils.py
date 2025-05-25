from random import choice

from django.conf import settings
from django.core.mail import send_mail

INVALID_SYMBOLS_ASCII = {34, 92}  # символы " \
VALID_SYMBOLS_ASCII = tuple(set(range(33, 127)) - INVALID_SYMBOLS_ASCII)


def send_confirmation_code(user):
    """Отправка кода подтверждения и его запись в БД."""
    code = ''.join(chr(choice(VALID_SYMBOLS_ASCII))
                   for _ in range(settings.CONFIRMATION_CODE_LENGTH))
    user.confirmation_code = code
    user.save()
    send_mail(
        subject='Confirmation code',
        message=(f'\t{user.username},\nВаш код подтверждения '
                 f'для получения токена YaMDb: {code}'),
        from_email=None,
        recipient_list=[user.email],
    )
