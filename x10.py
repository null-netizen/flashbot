import os
import time
import random
from faker import Faker
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Inicializar Faker para gerar dados aleatórios
fake = Faker()

# URL do site
URL = "https://www.mel881.com/?eventCurrent=1&gameCategoryId=0&fixed.isSaveShort=true&fixed.isHideDomain=1"

# Tamanho da tela (ajuste conforme sua resolução)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
MARGIN_X = 10  # Margem entre as janelas (horizontal)
AVAILABLE_HEIGHT = SCREEN_HEIGHT - 50  # Ajuste conforme necessário
START_Y_BOTTOM = AVAILABLE_HEIGHT // 2  # Divide a altura disponível pela metade

# Tamanho da janela do iPhone SE
WINDOW_WIDTH = 275
WINDOW_HEIGHT = 567

# Calcula posições das janelas
POSITIONS = [(i * (WINDOW_WIDTH + MARGIN_X), y) for i in range(5) for y in [0, START_Y_BOTTOM]]

# Lista para armazenar os drivers
drivers = []

# Criar e armazenar os drivers
for i, pos in enumerate(POSITIONS[:1]):
    profile_dir = os.path.join(os.path.expanduser("~"), "Desktop", f"Chrome_Profile_{i+1}")
    os.makedirs(profile_dir, exist_ok=True)
    
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={profile_dir}")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument(f"--window-position={pos[0]},{pos[1]}")
    chrome_options.add_argument(f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
    chrome_options.add_argument("--app=" + URL)
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    drivers.append(driver)
    time.sleep(1)  # Pequeno atraso para evitar sobrecarga na abertura

# Função para preencher o formulário de registro
def preencher_formulario(driver):
    try:
        celular_conta = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz1234567890", k=10))
        senha = "J11111"
        nome_real = fake.name()
        wait = WebDriverWait(driver, 10)

        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@data-input-name='account']"))).send_keys(celular_conta)
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@data-input-name='userpass']"))).send_keys(senha)
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@data-input-name='confirmPassword']"))).send_keys(senha)
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@data-input-name='realName']"))).send_keys(nome_real)
        
        botao_registro = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[@class='ui-button__text' and text()='Registro']]")))
        botao_registro.click()
        
        print("Registro feito!")
        return True
    except Exception as e:
        print(f"Erro ao preencher o formulário: {e}")
        return False

# Função para fechar notificações e clicar em "Cancelar"
def fechar_notificacao(driver):
    try:
        wait = WebDriverWait(driver, 10)
        for _ in range(3):  # Fecha até 3 notificações
            botao_fechar = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='ui-dialog-close-box ui-dialog-close-box ui-dialog-close-box--occupy-space']")))
            botao_fechar.click()
            print("Notificação fechada!")
            time.sleep(1)
        
        botao_cancelar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[@class='ui-button__text' and text()='Cancelar']]")))
        botao_cancelar.click()
        print("Botão 'Cancelar' clicado!")
    except Exception as e:
        print(f"Erro ao fechar notificações: {e}")

# Funções para clicar em botões de promoção e missão
def clicar_em_promocao(driver):
    try:
        wait = WebDriverWait(driver, 10)
        botao_promocao = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='_text_g87qd_80' and text()='Promoção']")))
        botao_promocao.click()
        print("Botão 'Promoção' clicado!")
    except Exception as e:
        print(f"Erro ao clicar em 'Promoção': {e}")

def clicar_em_missao(driver):
    try:
        wait = WebDriverWait(driver, 10)
        botao_missao = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='_item-text_1bcwl_33' and text()='Missão']")))
        botao_missao.click()
        print("Botão 'Missão' clicado!")
    except Exception as e:
        print(f"Erro ao clicar em 'Missão': {e}")

# Lista para armazenar os resultados dos registros
resultados_registros = []

# Preencher os formulários nas janelas abertas
for driver in drivers:
    driver.get(URL)
    resultados_registros.append(preencher_formulario(driver))

# Se todos os registros forem bem-sucedidos, continua com notificações e promoções
if all(resultados_registros):
    time.sleep(5)
    for driver in drivers:
        fechar_notificacao(driver)
    for driver in drivers:
        clicar_em_promocao(driver)
        clicar_em_missao(driver)
else:
    print("Um ou mais registros falharam. Notificações não serão fechadas automaticamente.")

print("Registros concluídos!")
input("Pressione Enter para fechar os navegadores...")

# Fechar todos os navegadores
for driver in drivers:
    driver.quit()
