
import sys
import urllib
import urllib2

from bs4 import BeautifulSoup
from flask import Flask, render_template

app = Flask(__name__)

# url_for('static', filename="style.css")

global TITLE, JOBS


@app.route("/")
def prettify():
    global TITLE, JOBS
    return render_template('jobs.html', title=TITLE, jobs=JOBS)


def comment_or_job(tag):
    return int(tag.find('img')['width']) == 0


if __name__ == "__main__":
    global TITLE, JOBS
    if len(sys.argv) < 2:
        raise Exception("You must provide the URL post id number.")

    # request the page and parse
    base_url = "https://news.ycombinator.com/"
    post_id = urllib.urlencode({"id": sys.argv[1]})
    request = urllib2.Request(base_url + "item?" + post_id)
    request.add_header('User-Agent:',
                       'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')
    response = urllib2.urlopen(request)
    page_soup = BeautifulSoup(response.read(), 'lxml')
    TITLE = unicode(page_soup.title.string)

    # split self post and responses from the outer table
    thread = page_soup.body.center.table.find_all('tr', recursive=False)

    if len(thread) < 3:
        raise Exception("Outer table parse parse error on page.")

    comments = thread[2].td.find_all("table")[1]
    tr_posts = comments.find_all(comment_or_job, recursive=False)
    td_posts = [p.td.table.tr.find("td", "default") for p in tr_posts if p]

    JOBS = []
    for td in td_posts:
        link = td.find("a", text="link")
        if link:
            JOBS.append({'link': base_url + link['href'],
                         'content': td.find("span", "comment")})

    app.run(host='0.0.0.0')
