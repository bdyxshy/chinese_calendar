import datetime
import hashlib
from lunar_python import Solar
from lunar_python.util.HolidayUtil import HolidayUtil
from icalendar import Calendar, Event

# ================= 自定义节日扩充区 =================
# 如果发现 lunar_python 有漏掉的公历节日，加在这里 (月份, 日期): ["节日名"]
CUSTOM_SOLAR_FESTIVALS = {
    (7, 5): ["世界羽毛球日"],
    (10, 9): ["世界邮政日"],
    # (11, 1): ["举个例子：某某纪念日"],
}

# 如果发现有漏掉的农历节日，加在这里 (农历月份, 农历日期): ["节日名"]
CUSTOM_LUNAR_FESTIVALS = {
    (6, 24): ["火把节"],
}
# ===================================================

def generate_comprehensive_ics():
    cal = Calendar()
    cal.add('prodid', '-//Comprehensive Chinese Calendar//lunar_python//CN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('x-wr-calname', '中国全能日历(终极版)')
    cal.add('x-wr-timezone', 'Asia/Shanghai')
    cal.add('x-apple-calendar-color', '#E0243A')

    current_year = datetime.date.today().year
    start_year = current_year - 2
    end_year = current_year + 2

    start_date = datetime.date(start_year, 1, 1)
    end_date = datetime.date(end_year, 12, 31)
    delta = datetime.timedelta(days=1)
    
    curr_date = start_date

    while curr_date <= end_date:
        solar = Solar.fromYmd(curr_date.year, curr_date.month, curr_date.day)
        lunar = solar.getLunar()
        
        events_today = []

        # 1. 法定节假日与调休补班
        holiday = HolidayUtil.getHoliday(curr_date.year, curr_date.month, curr_date.day)
        if holiday:
            if holiday.isWork():
                events_today.append(f"💼 补班: {holiday.getName()}")
            else:
                events_today.append(f"🏖️ 休假: {holiday.getName()}")

        # 2. 二十四节气
        jieqi = lunar.getJieQi()
        if jieqi:
            events_today.append(f"🌱 {jieqi}")

        # 3. 三伏天与数九 (仅在第一天标记)
        fu = lunar.getFu()
        if fu and fu.getIndex() == 1:
            events_today.append(f"☀️ {fu.getName()}")

        jiu = lunar.getShuJiu()
        if jiu and jiu.getIndex() == 1:
            events_today.append(f"❄️ {jiu.getName()}")

        # 4. 农历节日处理 (包含南北小年区分及自定义农历节日)
        # 获取农历绝对月份 (abs是为了处理闰月，比如闰六月也算六月处理)
        lunar_month = abs(lunar.getMonth())
        lunar_day = lunar.getDay()
        
        if lunar_month == 12:
            if lunar_day == 23:
                events_today.append("🏮 北小年")
            elif lunar_day == 24:
                events_today.append("🏮 南小年")

        for f in lunar.getFestivals():
            if f == "小年": continue # 跳过自带小年
            events_today.append(f"🏮 {f}")
            
        for f in lunar.getOtherFestivals():
            events_today.append(f"🐉 {f}")

        # 注入自定义农历节日
        if (lunar_month, lunar_day) in CUSTOM_LUNAR_FESTIVALS:
            for f in CUSTOM_LUNAR_FESTIVALS[(lunar_month, lunar_day)]:
                events_today.append(f"🏮 {f}")

        # 5. 公历节日处理 (包含自带节日及自定义公历节日)
        for f in solar.getFestivals():
            events_today.append(f"🎉 {f}")
            
        for f in solar.getOtherFestivals():
            events_today.append(f"📌 {f}")

        # 注入自定义公历节日
        if (curr_date.month, curr_date.day) in CUSTOM_SOLAR_FESTIVALS:
            for f in CUSTOM_SOLAR_FESTIVALS[(curr_date.month, curr_date.day)]:
                events_today.append(f"📌 {f}")

        # 6. 生成去重且固定的 iCal 事件
        # 使用 set 去重，防止自带节日和自定义节日重复添加
        unique_events = []
        for evt in events_today:
            if evt not in unique_events:
                unique_events.append(evt)

        for evt_title in unique_events:
            event = Event()
            event.add('summary', evt_title)
            
            event.add('dtstart', curr_date)
            event.add('dtend', curr_date + datetime.timedelta(days=1))
            event.add('dtstamp', datetime.datetime.now())
            
            # 固定UID保证iOS不闪烁
            uid_str = f"{curr_date.strftime('%Y%m%d')}-{evt_title}"
            uid = hashlib.md5(uid_str.encode('utf-8')).hexdigest()
            event.add('uid', f"{uid}@comprehensive_calendar")
            
            cal.add_component(event)

        curr_date += delta

    filename = "chinese_calendar.ics"
    with open(filename, 'wb') as f:
        f.write(cal.to_ical())
    print(f"✅ 成功生成带自定义事件的终极版日历！")

if __name__ == '__main__':
    generate_comprehensive_ics()
