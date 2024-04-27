from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import csv

options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

def get_models_info(url):
    driver.get(url)
    time.sleep(1)

    processed_models = {}  # Diccionario para almacenar los modelos procesados
    model_counter = 0  # Contador para limitar el número de modelos procesados

    while model_counter < 100:  # Limitar modelos
        try:
            # Obtener los elementos de modelo
            models_div = driver.find_element(By.ID, "discover-models")
            model_links = models_div.find_elements(By.TAG_NAME, "a")

            model_urls = set()

            # Recorrer los elementos y agregar las URLs a un conjunto para evitar duplicados
            for link in model_links:
                model_urls.add(link.get_attribute("href"))

            # Hacer clic en shuffle y repetir
            shuffle_button = driver.find_element(By.ID, "shuffle-models-toggle")
            shuffle_button.click()

            # Esperar a que se cargue la nueva página
            time.sleep(1)

            # Obtener los elementos de modelo después de la mezcla
            models_div_shuffled = driver.find_element(By.ID, "discover-models")
            model_links_shuffled = models_div_shuffled.find_elements(By.TAG_NAME, "a")

            # Recorrer los elementos y agregar las URLs a un conjunto para evitar duplicados
            for link in model_links_shuffled:
                model_urls.add(link.get_attribute("href"))

            # Iterar sobre las URLs de los modelos
            for model_url in model_urls:
                # Ir a la URL del modelo
                driver.get(model_url)
                time.sleep(1)

                # Obtener información del modelo
                name_box = driver.find_element(By.ID, "nameBox")
                model_name = name_box.find_element(By.TAG_NAME, "h3").text

                if model_name not in processed_models:
                    # Obtener información de Instagram si no está presente
                    try:
                        instagram_link = driver.find_element(By.CSS_SELECTOR, "#socialLinks ul li a[href^='https://www.instagram.com']").get_attribute("href")
                    except:
                        instagram_link = ""

                    if instagram_link:  # Si hay un enlace de Instagram
                        processed_models[model_name] = {'instagram': instagram_link, 'agencies': set()}

                        # Obtener información de la agencia
                        agencies = driver.find_elements(By.CSS_SELECTOR, "#agencies ul li.affEnabled a.agencyRepName")
                        for agency in agencies:
                            agency_name = agency.text
                            agency_link = agency.get_attribute("href")

                            # Agregar la agencia al diccionario de modelos procesados
                            processed_models[model_name]['agencies'].add((agency_name, agency_link))

                        # Incrementar el contador de modelos procesados
                        model_counter += 1

        except:
            driver.get("https://models.com/")
            time.sleep(1)
            shuffle_button = driver.find_element(By.ID, "shuffle-models-toggle")
            shuffle_button.click()
            time.sleep(1)
            continue

    # Verificar si el archivo CSV ya existe
    try:
        with open('models_info.csv', mode='r') as file:
            reader = csv.reader(file)
            existing_models = set(row[0] for row in reader)
    except FileNotFoundError:
        existing_models = set()

    # Escribir los datos en el archivo CSV
    with open('models_info.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        for model_name, model_data in processed_models.items():
            if model_name not in existing_models:
                existing_models.add(model_name)
                agencies = ", ".join([f"{agency_name} ({agency_link})" for agency_name, agency_link in model_data['agencies']])
                writer.writerow([model_name, model_data['instagram'], agencies])

    driver.quit()

url_to_scrape = "https://models.com"
get_models_info(url_to_scrape)
