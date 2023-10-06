import asyncio
import datetime
import os, sys
from django.contrib.auth import get_user_model
from django.db import DatabaseError
from telegram.handlers import send_message_to_admin


proj = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(proj)
os.environ["DJANGO_SETTINGS_MODULE"] = "scraping_service.settings"

import django

django.setup()

from scraping.parsers import *
from scraping.models import Vacancy, Location, Search, Errors





parsers = (
    work_ua, rabota_ua, djinni, dou
)

jobs, errors = [], []


def get_settings(user):
    qs = user.objects.filter(newsletter=True, search__isnull=False).values()
    settings_lst = set((q['search_id'], q['location_id']) for q in qs)
    print(settings_lst)
    search_query = set()
    for i in settings_lst:
        search = Search.objects.get(id=i[0])
        try:
            location = Location.objects.get(id=i[1])
        except:
            location = None
        search_query.add((search, location))
    return search_query


async def main(value):
    func, location, search = value
    job, err = await loop.run_in_executor(None, func, location, search)
    errors.extend(err)
    jobs.extend(job)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.run(send_message_to_admin('start scraping'))
    User = get_user_model()
    settings = get_settings(User)
    tmp_tasks = [(func, data[0], data[1])
                 for data in settings
                 for func in parsers]
    print(tmp_tasks)
    if tmp_tasks:

        tasks = asyncio.wait([loop.create_task(main(f)) for f in tmp_tasks])
        loop.run_until_complete(tasks)
        loop.close()
    asyncio.run(send_message_to_admin(f'jobs:{len(jobs)}'))
    for job in jobs:
        v = Vacancy(**job)
        try:
            v.save()
            print('save job')
        except DatabaseError:
            pass
    if errors:
        qs = Errors.objects.filter(timestamp=datetime.date.today())
        if qs.exists():
            print('we in error')
            err = qs.first()
            err.data.update({'errors': errors})
            asyncio.run(send_message_to_admin(f'jobs:{err.data}'))
            err.save()
        else:
            er = Errors(data=f'errors:{errors}').save()

    ten_days_ago = datetime.date.today() - datetime.timedelta(10)
    Vacancy.objects.filter(timestamp__lte=ten_days_ago).delete()

    asyncio.run(send_message_to_admin(f'scraping end'))
