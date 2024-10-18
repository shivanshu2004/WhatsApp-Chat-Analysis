import pandas as pd
import re
from datetime import datetime

def preprocess(data):
    pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[apAPmM]{2}\s-\s|\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    #convert 24-hour format
    def convert_to_24hour_format(date_str):
        try:
            # 12-hour format
            try:
                date_time_obj = datetime.strptime(date_str, '%d/%m/%y, %I:%M %p - ')
            except ValueError:
                # 24-hour format
                date_time_obj = datetime.strptime(date_str, '%d/%m/%y, %H:%M - ')
            return date_time_obj
        except Exception as e:
            print(f"Error processing date: {date_str}")
            print(e)
            return None

    # Convert dates format (24-hour)
    df = pd.DataFrame({'users_message': messages, 'message_date': dates})
    df['message_date'] = df['message_date'].apply(convert_to_24hour_format)

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    for message in df['users_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['users'] = users
    df['messages'] = messages
    df.drop(columns=['users_message'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df
