import os
import time
import random
import threading
import tkinter as tk
from tkinter import messagebox
from faker import Faker
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
import bcrypt
import sys

# Função para criar um Entry customizado com borda neon e cantos arredondados
def create_rounded_entry(parent, width=300, height=35, border_color="#00ffff", fill_color="black", **kwargs):
    canvas = tk.Canvas(parent, width=width, height=height, bg=fill_color, highlightthickness=0)
    radius = 10
    # Arcos para os cantos
    canvas.create_arc((0, 0, 2*radius, 2*radius), start=90, extent=90, fill=border_color, outline=border_color)
    canvas.create_arc((width-2*radius, 0, width, 2*radius), start=0, extent=90, fill=border_color, outline=border_color)
    canvas.create_arc((0, height-2*radius, 2*radius, height), start=180, extent=90, fill=border_color, outline=border_color)
    canvas.create_arc((width-2*radius, height-2*radius, width, height), start=270, extent=90, fill=border_color, outline=border_color)
    # Retângulos para preencher as laterais
    canvas.create_rectangle(radius, 0, width-radius, height, fill=fill_color, outline=border_color)
    canvas.create_rectangle(0, radius, width, height-radius, fill=fill_color, outline=border_color)
    entry = tk.Entry(canvas, bd=0, bg=fill_color, fg=border_color, font=("Helvetica Neue", 12), **kwargs)
    canvas.create_window(width/2, height/2, window=entry, width=width-10, height=height-10)
    return entry, canvas

# --- Janela de Login Customizada (Visual Futurista - Cyberpunk) ---
class CyberpunkLoginDialog:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        # Removido o overrideredirect para que o sistema gerencie os controles
        # self.top.overrideredirect(True)
        self.top.geometry("400x350+500+200")
        self.top.configure(bg="#1a1a1a")
        # Fundo futurista com borda neon
        self.canvas = tk.Canvas(self.top, width=400, height=350, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_rectangle(5, 5, 395, 345, outline="#00ffff", width=2)
        # Conteúdo centralizado
        self.content_frame = tk.Frame(self.top, bg="#1a1a1a")
        self.content_frame.place(relx=0.5, rely=0.55, anchor="center")
        tk.Label(self.content_frame, text="FLASHBOT", bg="#1a1a1a", fg="#00ffff", font=("Helvetica Neue", 28, "bold")).pack(pady=(10,10))
        tk.Label(self.content_frame, text="FLASHID", bg="#1a1a1a", fg="#00ffff", font=("Helvetica Neue", 12)).pack(pady=(10,5))
        self.username_entry, self.username_canvas = create_rounded_entry(self.content_frame, width=300, height=35, border_color="#00ffff", fill_color="black")
        self.username_canvas.pack(pady=5)
        tk.Label(self.content_frame, text="KEY", bg="#1a1a1a", fg="#00ffff", font=("Helvetica Neue", 12)).pack(pady=(20,5))
        self.password_entry, self.password_canvas = create_rounded_entry(self.content_frame, width=300, height=35, border_color="#00ffff", fill_color="black")
        self.password_entry.config(show="*")
        self.password_canvas.pack(pady=5)
        tk.Button(self.content_frame, text="Continuar", command=self.on_submit, font=("Helvetica Neue", 12), bg="#00ffff", fg="#1a1a1a", bd=0, relief="flat", padx=10, pady=5).pack(pady=20)
        self.username = None
        self.password = None
        self.top.grab_set()
        parent.wait_window(self.top)
        
    def on_submit(self):
        self.username = self.username_entry.get().strip()
        self.password = self.password_entry.get().strip()
        if not self.username or not self.password:
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos.")
        else:
            self.top.destroy()

# Cria a janela raiz oculta e exibe o diálogo de login
root = tk.Tk()
root.withdraw()
login = CyberpunkLoginDialog(root)
nome_usuario = login.username
senha = login.password
if not nome_usuario or not senha:
    messagebox.showinfo("Aviso", "Login cancelado.")
    sys.exit()

# --- Funções de Conexão e Verificação no Banco ---
def conectar_banco_de_dados():
    mydb = mysql.connector.connect(
        host="flashbot-jhoncostantine2016-5ea0.e.aivencloud.com",
        port=26475,
        user="avnadmin",
        password="senhaq",  # Substitua pela senha real
        database="flashbot",
        ssl_ca="C:/certificados/ca.pem",  # Ajuste o caminho conforme necessário
        use_pure=True
    )
    print("Conexão bem-sucedida!")
    return mydb

def verificar_acesso(nome_usuario, senha):
    try:
        mydb = conectar_banco_de_dados()
        mycursor = mydb.cursor()
        sql = "SELECT senha, ativo, tempo_acesso, credito FROM usuarios WHERE nome_usuario = %s"
        val = (nome_usuario,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()
        mydb.close()
        if not result:
            return False, "usuario incorreto", 0, 0
        senha_armazenada = result[0].strip() if isinstance(result[0], str) else result[0]
        ativo = result[1]
        tempo_acesso = result[2]
        creditos = result[3]
        print(f"DEBUG: senha inserida: {senha!r}")
        print(f"DEBUG: senha armazenada: {senha_armazenada!r}")
        if isinstance(senha_armazenada, str) and senha_armazenada.startswith("$2"):
            valid = bcrypt.checkpw(senha.encode("utf-8"), senha_armazenada.encode("utf-8"))
        else:
            valid = (senha == senha_armazenada)
        print(f"DEBUG: senha válida? {valid}")
        if not valid:
            return False, "senha incorreta", 0, 0
        if not ativo or tempo_acesso <= 0 or creditos <= 0:
            return False, "Tá Liso? Dorme!", tempo_acesso, creditos
        return True, "", tempo_acesso, creditos
    except Exception as e:
        print(f"Erro ao verificar acesso: {e}")
        return False, str(e), 0, 0

def atualizar_creditos(nome_usuario, novos_creditos):
    try:
        mydb = conectar_banco_de_dados()
        mycursor = mydb.cursor()
        sql = "UPDATE usuarios SET credito = %s WHERE nome_usuario = %s"
        val = (novos_creditos, nome_usuario)
        mycursor.execute(sql, val)
        mydb.commit()
        mydb.close()
    except Exception as e:
        print(f"Erro ao atualizar créditos: {e}")

def desativar_usuario(nome_usuario):
    try:
        mydb = conectar_banco_de_dados()
        mycursor = mydb.cursor()
        sql = "UPDATE usuarios SET ativo = FALSE WHERE nome_usuario = %s"
        val = (nome_usuario,)
        mycursor.execute(sql, val)
        mydb.commit()
        mydb.close()
    except Exception as e:
        print(f"Erro ao desativar usuário: {e}")

def atualizar_tempo_acesso(nome_usuario, novo_tempo):
    try:
        mydb = conectar_banco_de_dados()
        mycursor = mydb.cursor()
        sql = "UPDATE usuarios SET tempo_acesso = %s WHERE nome_usuario = %s"
        val = (novo_tempo, nome_usuario)
        mycursor.execute(sql, val)
        mydb.commit()
        mydb.close()
    except Exception as e:
        print(f"Erro ao atualizar tempo: {e}")

# Thread para contar e atualizar o tempo do usuário
def time_counter(nome_usuario, tempo_inicial):
    start_time = time.time()
    total_seconds = tempo_inicial * 60
    while True:
        time.sleep(10)  # Atualiza a cada 10 segundos
        elapsed = time.time() - start_time
        remaining = total_seconds - elapsed
        if remaining <= 0:
            atualizar_tempo_acesso(nome_usuario, 0)
            desativar_usuario(nome_usuario)
            print("Tempo esgotado. Encerrando automação.")
            for driver in drivers:
                driver.quit()
            sys.exit()
        remaining_minutes = remaining / 60
        atualizar_tempo_acesso(nome_usuario, remaining_minutes)
        print(f"Tempo restante: {remaining_minutes:.2f} minutos")

acesso_concedido, erro, tempo_acesso, creditos = verificar_acesso(nome_usuario, senha)
if not acesso_concedido:
    messagebox.showinfo("Aviso", erro)
    sys.exit()

# Inicia o contador de tempo em thread paralela
threading.Thread(target=time_counter, args=(nome_usuario, tempo_acesso), daemon=True).start()

# --- Código de Automação com Selenium ---
# Inicialize o Faker com um locale válido (exemplo: "en_US")
fake = Faker("en_US")
URL = "https://www.mel881.com/?eventCurrent=1&gameCategoryId=0&fixed.isSaveShort=true&fixed.isHideDomain=1"
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
MARGIN_X = 10
AVAILABLE_HEIGHT = SCREEN_HEIGHT - 50
START_Y_BOTTOM = AVAILABLE_HEIGHT // 2
WINDOW_WIDTH = 275
WINDOW_HEIGHT = 567
POSITIONS = [(i * (WINDOW_WIDTH + MARGIN_X), y) for i in range(5) for y in [0, START_Y_BOTTOM]]
drivers = []
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
    time.sleep(1)

def preencher_formulario(driver):
    try:
        celular_conta = "".join(random.choices("abcdefghijklmnopqrstuvwxyz1234567890", k=10))
        senha_registro = "J11111"
        nome_real = fake.name()
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@data-input-name='account']"))).send_keys(celular_conta)
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@data-input-name='userpass']"))).send_keys(senha_registro)
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@data-input-name='confirmPassword']"))).send_keys(senha_registro)
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@data-input-name='realName']"))).send_keys(nome_real)
        botao_registro = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[@class='ui-button__text' and text()='Registro']]")))
        botao_registro.click()
        print("Registro feito!")
        return True
    except Exception as e:
        print(f"Erro ao preencher o formulário: {e}")
        return False

def fechar_notificacao(driver):
    try:
        wait = WebDriverWait(driver, 10)
        for _ in range(3):
            botao_fechar = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='ui-dialog-close-box ui-dialog-close-box ui-dialog-close-box--occupy-space']")))
            botao_fechar.click()
            print("Notificação fechada!")
            time.sleep(1)
        botao_cancelar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[@class='ui-button__text' and text()='Cancelar']]")))
        botao_cancelar.click()
        print("Botão 'Cancelar' clicado!")
    except Exception as e:
        print(f"Erro ao fechar notificações: {e}")

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

resultados_registros = []
for driver in drivers:
    driver.get(URL)
    resultados_registros.append(preencher_formulario(driver))
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
for driver in drivers:
    driver.quit()
