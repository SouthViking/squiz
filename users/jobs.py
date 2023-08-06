# Definitions of the functions that will be executed by the global scheduler.
from datetime import datetime
from django.conf import settings

from .models import User
from core.logger import logger
from scheduler.types import AppJobsConfig

def remove_expired_unverified_accounts():
    logger.info('Executing process to remove unverified accounts.')
    target_accounts = User.objects.filter(is_verified = False).values('id', 'email', 'created_at')
    logger.info(f'Found {len(target_accounts)} unverified account(s).')

    for account in target_accounts:
        account_created_at: datetime = account['created_at']
        account_created_at = account_created_at.replace(tzinfo = None)

        hours_diff = int((datetime.now() - account_created_at).total_seconds() / 3600)
        if hours_diff < settings.EMAIL_VERIFICATION_EXPIRATION_MAX_HRS:
            continue

        logger.info(f'Removing account for email: {account["email"]}. ({hours_diff} hours have elapsed since registration)')
        user_record: User = User.objects.get(id = account["id"])
        user_record.delete()

        logger.info(f'Account with email {account["email"]} has been removed correctly.')


initial_jobs_config: AppJobsConfig = {
    'on_start_up_jobs': {
        'interval_jobs': [
            {
                'func': remove_expired_unverified_accounts,
                'id': 'remove_expired_unverified_accounts',
                'seconds': 1800,
            }
        ]
    }
}