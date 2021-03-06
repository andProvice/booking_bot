from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import datetime

days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

def create_calendar(year=None, month=None):
    now = datetime.datetime.now()
    if not year: year = now.year
    if not month: month = now.month

    keyboard = []

    #First row - Month and Year
    row=[]
    row.append(
        InlineKeyboardButton(
            datetime.date(year, month, 1).strftime('%B') + ' ' + str(year),
            callback_data=create_callback_data('IGNORE')
        )
    )
    keyboard.append(row)

    #Second row - Week Days
    row=[]
    for day in days:
        row.append(InlineKeyboardButton(day, callback_data=create_callback_data('IGNORE')))
    keyboard.append(row)

    month_weeks = get_weeks(year, month)
    for week in month_weeks:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data=create_callback_data('IGNORE')))
            else:
                row.append(
                    InlineKeyboardButton(
                        str(day),
                        callback_data=create_callback_data('DAY', year, month, day)
                    )
                )
        keyboard.append(row)

    #Last row - Buttons
    row = []
    if month != now.month:
        row.append(
            InlineKeyboardButton(
                '<',
                callback_data=create_callback_data('PREV-MONTH', year, month, day)
            )
        )
    else:
        row.append(InlineKeyboardButton(' ', callback_data=create_callback_data('IGNORE')))
    row.append(
        InlineKeyboardButton(
            '>',
            callback_data=create_callback_data('NEXT-MONTH', year, month, day)
        )
    )
    keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)

def get_weeks(year=datetime.datetime.today().year, month=datetime.datetime.today().month):
    start_day_week_day = datetime.date(year, month, 1).weekday()
    weeks = []
    weeks.append([0] * start_day_week_day + list(range(1, 8 - start_day_week_day)))
    days_to_end_mount = (
        datetime.date(year + int(month / 12), (month % 12) + 1, 1) - datetime.timedelta(days=1)).day \
        - weeks[0][-1]

    for i in range(days_to_end_mount // 7):
        weeks.append(list(range(weeks[i][-1] + 1, weeks[i][-1] + 8)))

    if days_to_end_mount % 7:
        weeks.append(list(range(weeks[-1][-1] + 1, weeks[-1][-1] + 1
                                + (days_to_end_mount % 7))) + [0] * (7 - days_to_end_mount % 7))

    # remove days before today
    if datetime.date.today().month == month and \
            datetime.date.today().year == year:
        today = datetime.date.today().day
        for week in weeks:
            for i in range(7):
                if week[i] <= today:
                    week[i] = 0
                else:
                    break
            else:
                continue
            break

    return weeks

def process_calendar_selection(bot, update):
    out = (False, None)
    query = update.callback_query
    (action, year, month, day) = separate_callback_data(query.data)
    curr = datetime.datetime(int(year), int(month), 1)
    if action == 'IGNORE':
        bot.answer_callback_query(callback_query_id=query.id)
    elif action == 'DAY':
        bot.edit_message_text(
            text=query.message.text,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        out = True, datetime.datetime(int(year), int(month), int(day)).strftime('%A %d %B %Y')
    elif action == 'PREV-MONTH':
        pre = curr - datetime.timedelta(days=1)
        bot.edit_message_text(text=query.message.text,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=create_calendar(int(pre.year), int(pre.month)))
    elif action == 'NEXT-MONTH':
        ne = curr + datetime.timedelta(days=31)
        bot.edit_message_text(text=query.message.text,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=create_calendar(int(ne.year), int(ne.month)))
    else:
        bot.answer_callback_query(callback_query_id= query.id, text=CALLBACK_ERROR)

    return out

def create_callback_data(action, year=0, month=0, day=0):
    return ';'.join([action, str(year), str(month), str(day)])


def separate_callback_data(data):
    return data.split(';')