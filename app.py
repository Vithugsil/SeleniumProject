from selenium.webdriver.support import expected_conditions as EC
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait

# item = input("Enter Item Name: ")

most_relevant_products = []
lowest_price_products = []
best_rated_products = []

zoom_url = "https://www.zoom.com.br/"
driver = webdriver.Chrome()
driver.get(zoom_url)
driver.maximize_window()

# clicando no span dos cookies
sleep(1)
cookie_span = driver.find_element(By.XPATH, "//span[contains(text(), 'Concordar')]")
cookie_span.click()

# inserindo item a ser pesquisado
search_input = driver.find_element(By.ID, "searchInput")
search_input.send_keys('teclado')
search_input.send_keys(Keys.ENTER)

#modal
# sleep(1.5)
# modal_close_button = driver.find_element(By.XPATH, "//span[@class='ModalCampaign_CloseButton__LDTLX']/button")
# modal_close_button.click()

# # modificanco a quantidade de items por pagina
# hits_per_page = driver.find_element(By.XPATH, "//select[@data-testid='hits-per-page-select']")
# hits_per_page.click()
#
# # colocando o maximo de items por pagina
# options = hits_per_page.find_elements(By.XPATH, ".//option")
# last_option = options[-1]
# last_option.click()

for option in range(3):
    # sao tres por que representa as paginas
    select_order_by = driver.find_element(By.XPATH, "//select[@data-testid='select-order-by']")
    select_order_by.click()
    order_by_options = select_order_by.find_elements(By.XPATH, ".//option")
    if option == 2:
        option += 1
    order_by_options[option].click()
    for idx in range(3):
        sleep(1.2)
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
                    best_rated_products.append({'product_name': product_name, 'product_price': product_price})

        # tempo pra carregar os elementos
        sleep(1.2)
        # botao de proxima pagina
        next_page = driver.find_element(By.XPATH, "//li[@data-testid='page-next']/a")
        # Acao para scrollar ate o elemento e ai entao clicar nele, se nao fizer isso ele nao encontra o elemento
        ActionChains(driver).scroll_to_element(next_page).perform()
        next_page.click()

    sleep(0.8)
    go_to_first_page = driver.find_element(By.XPATH, "//li[@data-testid='page-1']/a")
    ActionChains(driver).click(go_to_first_page).perform()
    go_to_first_page.click()



# parte do pandas
dt_most_relevant_products = pd.DataFrame(most_relevant_products)
dt_lowest_price_products = pd.DataFrame(lowest_price_products)
dt_best_rated_products = pd.DataFrame(best_rated_products)

dt_most_relevant_products.to_csv('most_relevant_products.csv', index=False, encoding='utf-8-sig', sep=";")
dt_lowest_price_products.to_csv('lowest_price_products.csv', index=False, encoding='utf-8-sig', sep=";")
dt_best_rated_products.to_csv('best_rated_products.csv', index=False, encoding='utf-8-sig', sep=";")

combined_df = pd.concat([dt_best_rated_products,dt_most_relevant_products, dt_lowest_price_products])
duplicated_values = combined_df[combined_df.duplicated(subset=['product_name', 'product_price'], keep=False)]
products_in_at_least_two_tables = duplicated_values.drop_duplicates(subset=['product_name', 'product_price'])

products_in_at_least_two_tables.to_csv('commom_products_tables.csv', index=False, encoding='utf-8-sig', sep=";")

for index, row in products_in_at_least_two_tables.iterrows():
    sleep(2)

    # Aguardar o elemento existir antes de tentar usar
    search_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "searchInput"))
    )

    search_input.clear()
    search_input.send_keys(row['product_name'])
    sleep(3)
    search_input.send_keys(Keys.ENTER)

    # Aguardar o card aparecer antes de tentar clicar
    card = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@data-testid='product-card::card']"))
    )
    card.click()



