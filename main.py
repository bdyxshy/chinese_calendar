import datetime
import hashlib
from lunar_python import Solar, HolidayUtil
from icalendar import Calendar, Event

def generate_comprehensive_ics():
    cal = Calendar()
    cal.add('prodid', '-//Comprehensive Chinese Calendar//lunar_python//CN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('x-wr-calname', '中国全能日历(节假/农历/节气)')
    cal.add('x-wr-timezone', 'Asia/Shanghai')
    cal.add('x-apple-calendar-color', '#E0243A') # 默认日历颜色（中国红）

    # 动态获取近五年范围：当前年份的前2年到后2年
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

        # 1. 法定节假日与调休补班 (最重要，放最前)
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

        # 3. 农历传统节日 (如春节、元宵、除夕)
        for f in lunar.getFestivals():
            events_today.append(f"🏮 {f}")
            
        # 4. 农历其他节日 (如龙抬头、下元节等)
        for f in lunar.getOtherFestivals():
            events_today.append(f"🐉 {f}")

        # 5. 公历主要节日 (如元旦、劳动节)
        for f in solar.getFestivals():
            events_today.append(f"🎉 {f}")
            
        # 6. 公历其他纪念日/节日 (植树节、消费者权益日、世界读书日等全在这里)
        for f in solar.getOtherFestivals():
            events_today.append(f"📌 {f}")

        # 每日生成独立的 iCal 事件
        for evt_title in events_today:
            event = Event()
            event.add('summary', evt_title)
            
            # 全天事件配置
            event.add('dtstart', curr_date)
            event.add('dtend', curr_date + datetime.timedelta(days=1))
            event.add('dtstamp', datetime.datetime.now())
            
            # 使用 Hash 生成固定 UID，防止 iOS 日历每次更新时重复创建或闪烁
            uid_str = f"{curr_date.strftime('%Y%m%d')}-{evt_title}"
            uid = hashlib.md5(uid_str.encode('utf-8')).hexdigest()
            event.add('uid', f"{uid}@comprehensive_calendar")
            
            cal.add_component(event)

        curr_date += delta

    # 输出为 ics 文件
    filename = "chinese_calendar.ics"
    with open(filename, 'wb') as f:
        f.write(cal.to_ical())
    print(f"✅ 成功生成 {start_year} - {end_year} 的全能日历：{filename}")

if __name__ == '__main__':
    generate_comprehensive_ics()
