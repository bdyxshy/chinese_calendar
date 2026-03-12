import datetime
import hashlib
from lunar_python import Solar
from lunar_python.util.HolidayUtil import HolidayUtil
from icalendar import Calendar, Event

def generate_comprehensive_ics():
    cal = Calendar()
    cal.add('prodid', '-//Comprehensive Chinese Calendar//lunar_python//CN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('x-wr-calname', '中国全能日历(增强版)')
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

        # 1. 法定节假日与调休补班 (用文字前缀模拟角标效果)
        holiday = HolidayUtil.getHoliday(curr_date.year, curr_date.month, curr_date.day)
        if holiday:
            if holiday.isWork():
                events_today.append(f"⚠️ [班] {holiday.getName()}补班")
            else:
                events_today.append(f"🟢 [休] {holiday.getName()}假期")

        # 2. 二十四节气
        jieqi = lunar.getJieQi()
        if jieqi:
            events_today.append(f"🌱 {jieqi}")

        # 3. 三伏天 (只在初伏、中伏、末伏的第一天标记)
        fu = lunar.getFu()
        if fu and fu.getIndex() == 1:
            events_today.append(f"☀️ {fu.getName()}")

        # 4. 数九寒天 (只在一九、二九等第一天标记)
        jiu = lunar.getShuJiu()
        if jiu and jiu.getIndex() == 1:
            events_today.append(f"❄️ {jiu.getName()}")

        # 5. 区分南北小年，并过滤掉自带的统称“小年”
        if lunar.getMonth() == 12:
            if lunar.getDay() == 23:
                events_today.append("🏮 北小年 (祭灶)")
            elif lunar.getDay() == 24:
                events_today.append("🏮 南小年 (祭灶)")

        for f in lunar.getFestivals():
            if f == "小年":
                continue # 跳过默认小年，避免与上面重复
            events_today.append(f"🏮 {f}")
            
        # 6. 农历其他节日 (如龙抬头、下元节等)
        for f in lunar.getOtherFestivals():
            events_today.append(f"🐉 {f}")

        # 7. 公历主要节日
        for f in solar.getFestivals():
            events_today.append(f"🎉 {f}")
            
        # 8. 公历其他纪念日 (植树节、消费者权益日、世界读书日等)
        for f in solar.getOtherFestivals():
            events_today.append(f"📌 {f}")

        # 每日生成独立的 iCal 事件
        for evt_title in events_today:
            event = Event()
            event.add('summary', evt_title)
            
            event.add('dtstart', curr_date)
            event.add('dtend', curr_date + datetime.timedelta(days=1))
            event.add('dtstamp', datetime.datetime.now())
            
            uid_str = f"{curr_date.strftime('%Y%m%d')}-{evt_title}"
            uid = hashlib.md5(uid_str.encode('utf-8')).hexdigest()
            event.add('uid', f"{uid}@comprehensive_calendar")
            
            cal.add_component(event)

        curr_date += delta

    filename = "chinese_calendar.ics"
    with open(filename, 'wb') as f:
        f.write(cal.to_ical())
    print(f"✅ 成功生成增强版日历！")

if __name__ == '__main__':
    generate_comprehensive_ics()
