from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import json

driver = webdriver.Chrome()
subjects = ['Python', 'React', 'Java', '.NET',
            'Kotlin', 'Swift', 'Rust', 'Golang', 'Javascript']
books = dict()
for subject in subjects:
    driver.get('https://www.google.com')

    search = driver.find_element_by_xpath(
        '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input')

    search.send_keys(subject+' Books')
    search.send_keys(Keys.RETURN)

    time.sleep(1)

    book_links = []
    try:
        div_xpath = '/html/body/div[7]/div/div[6]/div/div[2]/div/div[1]/div/div[1]/g-scrolling-carousel/div[1]/div'
        for i in range(10):
            book = driver.find_element_by_xpath(div_xpath+'/a['+str(i+1)+']')
            book_links.append(book.get_attribute('href'))
    except:
        pass

    total_books = min(10, len(book_links))
    books[subject] = dict()
    for i in range(total_books):
        driver.get(book_links[i])
        time.sleep(1)

        title = driver.find_element_by_tag_name('h2[data-attrid="title"]').text
        books[subject][title] = dict()

        try:
            author = driver.find_element_by_tag_name(
                'div[data-attrid="kc:/book/written_work:author"]').text.split(':')[1].strip()
            books[subject][title]['authors'] = author
        except:
            author = None

        try:
            published = driver.find_element_by_tag_name(
                'div[data-attrid="kc:/book/written_work:published"]').text.split(':')[1].strip()
            books[subject][title]['published'] = published
        except:
            published = None

        try:
            rating_text = driver.find_element_by_tag_name(
                'div[data-attrid="kc:/book/book:reviews"]').text
            rating_rated_by = []
            if '·' in rating_text:
                rating_text = rating_text.split('·')
                rating_rated_by.append(
                    [rating_text[0].strip(), rating_text[1].strip()])
            if '\n' in rating_text:
                rating_text = rating_text.split('\n')
                n = len(rating_text)
                for j in range(0, n, 2):
                    rating_rated_by.append(
                        [rating_text[j].strip(), rating_text[j+1].strip()])
            books[subject][title]['ratings'] = dict()
            for x in rating_rated_by:
                books[subject][title]['ratings'][x[1]] = x[0]
        except:
            rating_rated_by = None

        try:
            pages = driver.find_element_by_tag_name(
                'div[data-attrid="kc:/book/book:google books preview"]').text
            pages = pages.split('\n')[1].split()[0].split('/')[1]
            books[subject][title]['pages'] = pages
        except:
            pages = None

with open('books.json', 'w') as outfile:
    json.dump(books, outfile, indent=4)

driver.close()
