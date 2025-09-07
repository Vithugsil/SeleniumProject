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
best_rated_products = []


zoom_url = "https://www.zoom.com.br/"
driver = webdriver.Edge()
driver.get(zoom_url)
driver.maximize_window()

#clicando no span dos cookies
cookie_span = driver.find_element(By.XPATH, "//span[contains(text(), 'Concordar')]")
cookie_span.click()

# inserindo item a ser pesquisado
search_input = driver.find_element(By.ID, "searchInput")
search_input.send_keys('teclado')
search_input.send_keys(Keys.ENTER)

# modificanco a quantidade de items por pagina
hits_per_page = driver.find_element(By.XPATH, "//select[@data-testid='hits-per-page-select']")
hits_per_page.click()

#colocando o maximo de items por pagina
options = hits_per_page.find_elements(By.XPATH, ".//option")
last_option = options[-1]
last_option.click()

# pegando o select de ordenacao, Mais relevantes, menor preco, maior preco
select_order_by = driver.find_element(By.XPATH, "//select[@data-testid='select-order-by']")
order_by_options = select_order_by.find_elements(By.XPATH, ".//option")

#TODO: Arrumar um jeito de que ao chegar na terceira pagina ele reeinicia com uma nova ordenacao porem a partir da primeira pagina

#Range 4 por que temos 4 opcoes de ordenacao
for index in range(4):
    select_order_by.click()
    order_by_options[index].click()

    # sao tres por que representa as paginas
    for i in range(3):
        products_details = driver.find_elements(By.XPATH,".//div[@data-testid='product-card::description']")

        for product in products_details:
            product_name = product.find_element(By.XPATH, ".//h2[@data-testid='product-card::name']").text
            product_price = product.find_element(By.XPATH, ".//p[@data-testid='product-card::price']").text
            most_relevant_products.append({'product_name': product_name, 'product_price': product_price})

        #tempo pra carregar os elementos
        sleep(2)
        #botao de proxima pagina
        next_page = driver.find_element(By.XPATH, "//li[@data-testid='page-next']/a")
        #Acao para scrollar ate o elemento e ai entao clicar nele, se nao fizer isso ele nao encontra o elemento
        ActionChains(driver).scroll_to_element(next_page).perform()

        #Minha ideia aqui era que no final da terceira pagina ele voltasse para a primeira
        if index == 2:
            go_to_first_page = driver.find_element(By.XPATH, "//li[@data-testid='page-1']/a")
            go_to_first_page.click()
        else:
            next_page.click()


sleep(2)

driver.quit()

#parte do pandas
dt_most_relevant_products = pd.DataFrame(most_relevant_products)
dt_most_relevant_products.to_csv('most_relevant_products.csv', index=False, encoding='utf-8-sig', sep=";")