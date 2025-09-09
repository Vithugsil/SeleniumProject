from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import pandas as pd

# item = input("Enter Item Name: ")

most_relevant_products = []
lowest_price_products = []
biggest_price_products = []

zoom_url = "https://www.zoom.com.br/"
driver = webdriver.Edge()
driver.get(zoom_url)
driver.maximize_window()

# clicando no span dos cookies
cookie_span = driver.find_element(By.XPATH, "//span[contains(text(), 'Concordar')]")
cookie_span.click()

# inserindo item a ser pesquisado
search_input = driver.find_element(By.ID, "searchInput")
search_input.send_keys('teclado')
search_input.send_keys(Keys.ENTER)

#modal
sleep(1)
modal_close_button = driver.find_element(By.XPATH, "//span[@class='ModalCampaign_CloseButton__LDTLX']/button")
modal_close_button.click()

# modificanco a quantidade de items por pagina
hits_per_page = driver.find_element(By.XPATH, "//select[@data-testid='hits-per-page-select']")
hits_per_page.click()

# colocando o maximo de items por pagina
options = hits_per_page.find_elements(By.XPATH, ".//option")
last_option = options[-1]
last_option.click()

for option in range(3):
    # sao tres por que representa as paginas
    select_order_by = driver.find_element(By.XPATH, "//select[@data-testid='select-order-by']")
    select_order_by.click()
    order_by_options = select_order_by.find_elements(By.XPATH, ".//option")
    order_by_options[option].click()
    sleep(1)
    for idx in range(3):
        products_details = driver.find_elements(By.XPATH, ".//div[@data-testid='product-card::description']")

        for product in products_details:
            product_name = product.find_element(By.XPATH, ".//h2[@data-testid='product-card::name']").text
            product_price = product.find_element(By.XPATH, ".//p[@data-testid='product-card::price']").text

            match idx:
                case 0:
                    most_relevant_products.append({'product_name': product_name, 'product_price': product_price})
                case 1:
                    lowest_price_products.append({'product_name': product_name, 'product_price': product_price})
                case 2:
                    biggest_price_products.append({'product_name': product_name, 'product_price': product_price})

        # tempo pra carregar os elementos
        sleep(1)
        # botao de proxima pagina
        next_page = driver.find_element(By.XPATH, "//li[@data-testid='page-next']/a")
        # Acao para scrollar ate o elemento e ai entao clicar nele, se nao fizer isso ele nao encontra o elemento
        ActionChains(driver).scroll_to_element(next_page).perform()
        next_page.click()

    sleep(0.5)
    go_to_first_page = driver.find_element(By.XPATH, "//li[@data-testid='page-1']/a")
    ActionChains(driver).click(go_to_first_page).perform()
    go_to_first_page.click()

driver.quit()

# parte do pandas
dt_most_relevant_products = pd.DataFrame(most_relevant_products)
dt_lowest_price_products = pd.DataFrame(lowest_price_products)
dt_biggest_price_products = pd.DataFrame(biggest_price_products)

dt_intersection = dt_most_relevant_products.merge(dt_lowest_price_products, how='inner').merge(dt_biggest_price_products, how='inner')

dt_most_relevant_products.to_csv('most_relevant_products.csv', index=False, encoding='utf-8-sig', sep=";")
dt_lowest_price_products.to_csv('lowest_price_products.csv', index=False, encoding='utf-8-sig', sep=";")
dt_biggest_price_products.to_csv('biggest_price_products.csv', index=False, encoding='utf-8-sig', sep=";")
dt_intersection.to_csv('intersection.csv', index=False, encoding='utf-8-sig', sep=";")
