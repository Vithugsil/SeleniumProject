from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait

# item = input("Enter Item Name: ")

most_relevant_products = []
lowest_price_products = []
best_rated_products = []

zoom_url = "https://www.zoom.com.br/"

# Configurações para evitar detecção de bot
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
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

# Função para delay inteligente
def smart_delay(min_seconds=3, max_seconds=7):
    delay = random.uniform(min_seconds, max_seconds)
    print(f"Aguardando {delay:.1f} segundos para evitar detecção...")
    sleep(delay)

print(f"\n🔍 Coletando informações detalhadas de {len(products_in_at_least_two_tables)} produtos comuns...")

detailed_products = []
failed_products = []

for index, row in products_in_at_least_two_tables.iterrows():
    try:
        print(f"\n📦 Processando produto {index + 1}/{len(products_in_at_least_two_tables)}: {row['product_name'][:50]}...")
        
        # Delay inteligente entre requisições
        smart_delay()

        # Verificar se a janela ainda está aberta
        if not driver.window_handles:
            print("❌ Janela do navegador foi fechada! Reabrindo...")
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.get(zoom_url)
            driver.maximize_window()
            smart_delay(3, 5)

        # Aguardar o elemento existir antes de tentar usar
        search_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )

        # Limpar o input completamente usando múltiplas estratégias
        search_input.click()  # Focar no input
        search_input.clear()  # Método padrão
        search_input.send_keys(Keys.CONTROL + "a")  # Selecionar tudo
        search_input.send_keys(Keys.DELETE)  # Deletar seleção
        smart_delay(1, 2)  # Pequeno delay após limpar
        
        # Verificar se realmente limpou
        current_value = search_input.get_attribute("value")
        if current_value:
            print(f"⚠️ Input ainda tem valor '{current_value}', tentando limpar novamente...")
            search_input.clear()
            search_input.send_keys(Keys.CONTROL + "a")
            search_input.send_keys(Keys.BACKSPACE)
            smart_delay(0.5, 1)
        
        search_input.send_keys(row['product_name'])
        smart_delay(2, 4)  # Delay após digitar
        search_input.send_keys(Keys.ENTER)

        # Aguardar resultados carregarem
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='product-card::description']"))
        )
        
        smart_delay(2, 3)  # Delay antes de clicar

        # Aguardar o card aparecer antes de tentar clicar
        card = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@data-testid='product-card::card']"))
        )
        
        # Scroll até o elemento antes de clicar
        ActionChains(driver).scroll_to_element(card).perform()
        smart_delay(1, 2)
        card.click()
        
        print(f"✅ Produto {index + 1} processado com sucesso!")
        
        # Delay maior a cada 5 produtos para ser mais cauteloso
        if (index + 1) % 5 == 0:
            print("🛡️ Pausa extra para evitar detecção...")
            smart_delay(8, 12)
            
    except Exception as e:
        print(f"❌ Erro ao processar produto {index + 1}: {str(e)}")
        failed_products.append({
            'product_name': row['product_name'],
            'product_price': row['product_price'],
            'error': str(e)
        })
        
        # Se a janela foi fechada, tentar reabrir
        if "target window already closed" in str(e) or "no such window" in str(e):
            print("🔄 Tentando reabrir o navegador...")
            try:
                driver.quit()
            except:
                pass
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.get(zoom_url)
            driver.maximize_window()
            
            # Aceitar cookies novamente
            try:
                smart_delay(2, 3)
                cookie_span = driver.find_element(By.XPATH, "//span[contains(text(), 'Concordar')]")
                cookie_span.click()
            except:
                pass
                
        # Em caso de erro, aguardar mais tempo
        print("⏱️ Aguardando mais tempo devido ao erro...")
        smart_delay(10, 15)
        
        # Se for erro 429 ou similar, aguardar ainda mais
        if "429" in str(e) or "rate limit" in str(e).lower():
            print("🚫 Detectado rate limiting! Aguardando 30 segundos...")
            sleep(30)

# Salvar produtos que falharam para análise
if failed_products:
    df_failed = pd.DataFrame(failed_products)
    df_failed.to_csv('failed_products.csv', index=False, encoding='utf-8-sig', sep=";")
    print(f"\n⚠️ {len(failed_products)} produtos falharam e foram salvos em 'failed_products.csv'")

print(f"\n🎉 Processo concluído!")
print(f"✅ {len(products_in_at_least_two_tables) - len(failed_products)} produtos processados com sucesso")
print(f"❌ {len(failed_products)} produtos falharam")

# Fechar o navegador de forma segura
try:
    driver.quit()
    print("🔒 Navegador fechado.")
except Exception as e:
    print(f"⚠️ Erro ao fechar navegador: {e}")



