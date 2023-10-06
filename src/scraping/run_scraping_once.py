import asyncio
import datetime

from django.db import DatabaseError

from .models import Vacancy, Errors
from .parsers import work_ua, rabota_ua, djinni, dou

parsers = (
    work_ua, rabota_ua, djinni, dou
)
jobs, errors = [], []
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def main(value):
    func, location, search = value
    job, err = await loop.run_in_executor(None, func, location, search)
    errors.extend(err)
    jobs.extend(job)


def start(*settings):
    global loop
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    tmp_tasks = [(func, settings[0], settings[1]) for func in parsers]

    if tmp_tasks:
        tasks = asyncio.wait([loop.create_task(main(f)) for f in tmp_tasks])
        loop.run_until_complete(tasks)
        loop.close()

    for job in jobs:
        v = Vacancy(**job)
        try:
            v.save()
        except DatabaseError:
            pass
    if errors:
        qs = Errors.objects.filter(timestamp=datetime.date.today())
        if qs.exists():
            err = qs.first()
            err.data.update({'errors': errors})
            err.save()
        else:
            er = Errors(data=f'errors:{errors}').save()

    ten_days_ago = datetime.date.today() - datetime.timedelta(10)
    Vacancy.objects.filter(timestamp__lte=ten_days_ago).delete()
