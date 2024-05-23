import requests
from bs4 import BeautifulSoup
import sqlite3
from urllib.parse import urljoin, urlparse
from collections import deque
import threading
import time

TARGET_SITES = [
    'https://dp.la/',
    'https://www.dataversity.net/',
    'https://stackoverflow.com/',
    'https://www.w3schools.com/',
    'https://twitter.com/',
]

TARGET_KEYWORDS = [
    'technology',
    'science',
    'innovation',
    'gadgets',
    'startups',
    'space',
]

# Initialize the SQLite database
conn = sqlite3.connect('crawler.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE VIRTUAL TABLE IF NOT EXISTS pages USING fts5(url, title, content)''')
conn.commit()

def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def is_target_content(content):
    for keyword in TARGET_KEYWORDS:
        if keyword.lower() in content.lower():
            return True
    return False

def crawl(start_url, visited, queue, event):
    while not event.is_set():
        if not queue:
            for site in TARGET_SITES:
                queue.append((site, 0))
        
        url, depth = queue.popleft()
        if url in visited or depth > 3:
            continue

        print(f"Crawling: {url}")  # Print the URL being crawled
        visited.add(url)

        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print(f"Failed to retrieve {url}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else 'No Title'
            content = ' '.join([p.get_text() for p in soup.find_all('p')])

            if is_target_content(content):
                print(f"Indexing: {url}")  # Print the URL being indexed
                print(f"Title: {title}")
                print(f"Content: {content[:200]}...")  # Print a preview of the content
                # Save to database
                c.execute('INSERT INTO pages (url, title, content) VALUES (?, ?, ?)', (url, title, content))
                conn.commit()

            # Find and enqueue links
            for link in soup.find_all('a', href=True):
                next_url = link['href']
                next_url = urljoin(url, next_url)  # Handle relative URLs
                if is_valid(next_url) and next_url not in visited:
                    queue.append((next_url, depth + 1))

        except requests.RequestException as e:
            print(f"Failed to crawl {url}: {e}")

if __name__ == '__main__':
    visited = set()
    queue = deque()
    stop_event = threading.Event()
    crawler_thread = threading.Thread(target=crawl, args=(None, visited, queue, stop_event))
    crawler_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
        crawler_thread.join()
    finally:
        conn.close()
