import re
import datetime
from dateutil.relativedelta import relativedelta

# 每日凌晨00:30开始
now_dt = datetime.datetime.now()
next_dt = now_dt.replace(hour=0, minute=30, second=0, microsecond=0)
next_day_early_morning = current_time + relativedelta(days=1)
print(1)
