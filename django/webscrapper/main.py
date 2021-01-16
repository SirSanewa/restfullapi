from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from webdriver_manager.chrome import ChromeDriverManager

from app.engine import create_session
from models import Article


def get_article_title(article: WebElement):
    """
    Returns article's title from given article WebElement.
    :param article: WebElement
    :return: article's title: str
    """
    return article.find_element_by_css_selector("div.post-container>h2>a").text


def open_article_in_new_tab(driver: WebDriver, article: WebElement, article_title: str):
    """
    Opens article in new tab by performing mouse clicking on link with SHIFT key pressed.
    With new tab open switches focus to it.
    :param driver: WebDriver
    :param article: WebElement
    :param article_title: str
    :return:
    """
    article_link = article.find_element_by_link_text(article_title)
    ActionChains(driver) \
        .move_to_element(article_link) \
        .key_down(Keys.SHIFT) \
        .click(article_link) \
        .key_up(Keys.SHIFT) \
        .perform()
    article_window = driver.window_handles[1]
    driver.switch_to.window(article_window)


def save_article_in_db(driver: WebDriver, article_title: str):
    """
    Creates new article in database from data retrieved from the web page.
    :param driver: WebDriver
    :param article_title: str
    :return:
    """
    article_content = driver.find_element_by_class_name("post-content").text
    article_author = driver.find_element_by_class_name("author-name").text
    new_article = Article(
        article_author=article_author,
        article_title=article_title,
        article_content=article_content
    )
    db.add(new_article)
    db.commit()


def data_mining(driver: WebDriver):
    """
    Main function providing flow to the app. Next page button is different on first page then on others so when page is
    not having the next page button the button's value is changed to boolean which means last article page. Program goes
    through last page's articles and breaks loop.
    :param driver: WebDriver
    :return:
    """
    driver.get("https://teonite.com/blog/")
    driver.maximize_window()
    next_page_button = driver.find_element_by_css_selector("ul.pagination-list>li.blog-button.post-pagination>a")

    while True:
        main_window = driver.window_handles[0]
        articles = driver.find_elements_by_class_name("post-container")
        for article in articles:
            article_title = get_article_title(article)
            open_article_in_new_tab(driver, article, article_title)
            save_article_in_db(driver, article_title)
            driver.close()
            driver.switch_to.window(main_window)
        if not isinstance(next_page_button, bool):
            next_page_button.click()
            try:
                next_page_button = driver.find_element_by_xpath("//*[@id='blog-posts']/div/ul/li[2]/a")
            except NoSuchElementException:
                next_page_button = False
        else:
            driver.close()
            break


if __name__ == "__main__":
    db = create_session()

    driver_web = webdriver.Chrome(ChromeDriverManager().install())
    data_mining(driver_web)
