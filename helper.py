from urlextract import URLExtract
from wordcloud import WordCloud
extractor = URLExtract()
from collections import Counter
import pandas as pd
import emoji
import re

def fetch_stats(selected_user, df):
    if selected_user != 'over all':
        df = df[df['users'] == selected_user]
    # 1. fetch number of message
    num_messages = df.shape[0]
    # 2. number of words
    words = []
    for message in df['messages']:
        words.extend(message.split())

    num_media_messages = df[df['messages'] == '<Media omitted>\n'].shape[0]

    links = []
    for message in df['messages']:
        urls = extractor.find_urls(message)
        links.extend(urls)
    # len(links)

    return num_messages, len(words), num_media_messages, len(links)

def most_busy_user(df):
    x = df['users'].value_counts().head()
    df = round(df['users'].value_counts()/df.shape[0]*100, 2).reset_index().rename(columns={'index':'users', 'users':'percentage'})
    return x, df

def creates_word(selected_user, df):

    f = open('stop_Chinglish.txt', 'r')
    stop_word = f.read().splitlines()

    if selected_user != 'over all':
        df = df[df['users'] == selected_user]

    temp = df[df['users'] != 'group_notification']
    temp = temp[temp['messages'] != '<Media omitted>\n']

    def remove_stop_words(words):
        y = []
        for word in words.lower().split():
            if word not in stop_word:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    temp['messages'] = temp['messages'].apply(remove_stop_words)
    df_wc = wc.generate(temp['messages'].str.cat(sep=' '))
    return df_wc


def most_common_words(selected_user, df):

    with open('stop_Chinglish.txt', 'r') as f:
        stop_words = f.read().splitlines()

    if selected_user != 'over all':
        df = df[df['users'] == selected_user]

    temp = df[df['users'] != 'group_notification']
    temp = temp[temp['messages'] != '<Media omitted>\n']

    # Filter out messages starting with a number
    pattern = r'^\d+.*'
    temp = temp[~temp['messages'].str.match(pattern)]

    words = []

    for message in temp['messages']:
        message_words = re.findall(r'\b\w+\b', message.lower())

        for word in message_words:
            if word not in stop_words:
                words.append(word)

    # Count the most common words
    counter_dict = Counter(words)
    most_common_df = pd.DataFrame(counter_dict.most_common(20), columns=['Word', 'Count'])

    return most_common_df

def emoji_helper(selected_user, df):

    if selected_user != 'over all':
        df = df[df['users'] == selected_user]

    emojis = []
    for message in df['messages']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])

    emoji_counts = Counter(emojis)
    emoji_df = pd.DataFrame(emoji_counts.items(), columns=['emoji', 'count'])

    emoji_df = emoji_df.sort_values(by='count', ascending=False).reset_index(drop=True)

    return emoji_df

def month_timeline(selected_user, df):
    if selected_user != 'over all':
        df = df[df['users'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['messages'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time'] = time

    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'over all':
        df = df[df['users'] == selected_user]

    daily_timelines = df.groupby('only_date').count()['messages'].reset_index()

    return daily_timelines

def week_activity_map(selected_user, df):
    if selected_user != 'over all':
        df = df[df['users'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'over all':
        df = df[df['users'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user, df):

    if selected_user != 'over all':
        df = df[df['users'] == selected_user]

    df['period'] = pd.Categorical(df['period'], ordered=True, categories=[f"{i}-{i + 1}" for i in range(24)])
    user_heatmap = df.pivot_table(index='day_name', columns='period', values='messages', aggfunc='count').fillna(0)

    return user_heatmap


