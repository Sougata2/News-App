from flask import Flask, render_template, request
import requests
import datetime
import re

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

app = Flask(__name__)
source_dict_everything = {
    "bbc-news": 2,
    "the-times-of-india": 4
}
source_dict_top_headlines = {
    "bloomberg": 0,
    "the-hindu": 1,
    "bbc-news": 2,
    "google-news-in": 3,
    "the-times-of-india": 4,
}
date_dict = {
    "0": (today, yesterday),
    "1": (today - datetime.timedelta(days=1), today - datetime.timedelta(days=2)),
    "2": (today - datetime.timedelta(days=2), today - datetime.timedelta(days=3))
}
sources = [
    "bloomberg",
    "the-hindu",
    "bbc-news",
    "google-news-in",
    "the-times-of-india",
]
API_KEY = '25b54fdf5989442aaa924481dddbd9c8'

global_response = {}
global_articles = []
global_pages = []
global_page_no = 0
total_pages = 0


def filter_article_everything(articles):
    filtered_articles = []
    for article in articles:
        if 'navbharattimes.indiatimes.com' in article["url"] or \
                'economictimes.indiatimes.com/markets/stocks' in article["url"] or \
                'economictimes.indiatimes.com/markets/ipos' in article["url"] or \
                'economictimes.indiatimes.com/industry' in article["url"] or \
                'economictimes.indiatimes.com/magazines' in article["url"] or \
                'economictimes.indiatimes.com/news/web-stories' in article["url"] or \
                'timesofindia.indiatimes.com/entertainment' in article["url"] or \
                'timesofindia.indiatimes.com/web-series' in article["url"]:
            continue
        filtered_articles.append(article)
    filtered_articles = content_extra_character_remover(filtered_articles)
    return filtered_articles


def content_extra_character_remover(articles):
    for article in articles:
        if article["content"]:
            pattern = r'\[\+\d+\schars\]'
            article["content"] = re.sub(pattern, "", article["content"])
        article["date"] = today
    return articles


def divide_pages(length):
    global total_pages
    total_pages = length // 10 if length % 10 > 0 else (length // 10) - 1
    page_numbers = [_ for _ in range(length)]
    page_partitions = []
    i = 0
    while i < length:
        partition = []
        for _ in range(10):
            partition.append(page_numbers[i])
            i += 1
            if i >= length:
                break
        page_partitions.append(partition)
    return page_partitions


@app.route('/', methods=['GET', 'POST'])
def index():
    global today, yesterday
    if request.method == "POST":
        option = request.form.get("date_option")
        date = date_dict.get(option)
        today, yesterday = date[0], date[1]
    return render_template('index.html', day_before_yesterday=today - datetime.timedelta(days=2))


@app.route('/everything', methods=['GET', 'POST'])
def everything():  # put application's code here
    global global_response, global_pages, global_articles, global_page_no
    ind = 4
    if request.method == 'POST':
        ind = source_dict_everything.get(request.form.get("source_name"))
    url = ('https://newsapi.org/v2/everything?'
           f'sources={sources[ind]}&'
           f'from={yesterday}&to={today}&'
           f'apiKey={API_KEY}')
    response = requests.get(url).json()
    global_response = response
    articles = filter_article_everything(response.get("articles", []))
    global_articles = articles
    pages = divide_pages(len(articles))
    global_pages = pages
    global_page_no = 0
    print(global_response)
    print(len(global_articles), global_articles)
    print(global_page_no, global_pages[global_page_no])
    return render_template('Everything/index.html', articles=global_articles,
                           page=global_pages[global_page_no],
                           page_no=global_page_no + 1, is_next_page=True)


@app.route("/top-headlines", methods=['GET', 'POST'])
def top_headlines():
    global global_response, global_pages, global_articles, global_page_no
    ind = 4
    if request.method == 'POST':
        ind = source_dict_top_headlines.get(request.form.get("source_name"))
    url = ('https://newsapi.org/v2/top-headlines?'
           f'sources={sources[ind]}&'
           f'from={yesterday}&to={today}&'
           f'apiKey={API_KEY}')
    response = requests.get(url).json()
    global_response = response
    articles = response.get("articles", [])
    global_articles = content_extra_character_remover(articles)
    print(content_extra_character_remover(articles))
    print(global_articles, len(global_articles))
    return render_template('TopHeadlines/index.html', articles=global_articles)


@app.route('/prev', methods=['GET', 'POST'])
def previous_page():
    global global_page_no
    is_previous_page = True
    if request.method == "POST":
        global_page_no -= 1
        if global_page_no <= 0:
            is_previous_page = False
    print(global_page_no, global_pages[global_page_no])
    return render_template("Everything/index.html", articles=global_articles,
                           page=global_pages[global_page_no],
                           page_no=global_page_no + 1, is_previous_page=is_previous_page, is_next_page=True)


@app.route('/next', methods=['GET', 'POST'])
def next_page():
    global global_page_no
    is_next_page = True
    if request.method == "POST":
        global_page_no += 1
        if global_page_no >= total_pages:
            is_next_page = False
    print(global_page_no, global_pages[global_page_no])
    return render_template('Everything/index.html', articles=global_articles,
                           page=global_pages[global_page_no],
                           page_no=global_page_no + 1, is_next_page=is_next_page, is_previous_page=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
