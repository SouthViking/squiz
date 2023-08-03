# Definitions of the functions that will be executed by the global scheduler.
from typing import List
from datetime import datetime
from django.conf import settings

from .models import User
from core.logger import logger
from scheduler.types import IntervalJobDefinition

def remove_expired_unverified_accounts():
    logger.info('Executing process to remove unverified accounts.')
    target_accounts = User.objects.filter(is_verified = False).values('email', 'created_at')
    logger.info(f'Found {len(target_accounts)} unverified account(s).')

    for account in target_accounts:
        account_created_at: datetime = account['created_at']
        account_created_at = account_created_at.replace(tzinfo = None)

        hours_diff = int((datetime.now() - account_created_at).total_seconds() / 3600)
        if hours_diff < settings.EMAIL_VERIFICATION_EXPIRATION_MAX_HRS:
            continue

        logger.info(f'Removing account for email: {account["email"]}. ({hours_diff} hours have elapsed since registration)')

        # TODO: Deletion of all data for the current account.


interval_jobs: List[IntervalJobDefinition] = [
    {
        'func': remove_expired_unverified_accounts,
        'id': 'remove_expired_unverified_accounts',
        'seconds': 5,
    }
]