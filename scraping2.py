import os
import time
import random
import re
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv(override=True)

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
TARGET_ACCOUNT = os.getenv("IG_TARGET_ACCOUNT")

def random_sleep(min_s=3, max_s=8):
    sleep_time = random.uniform(min_s, max_s)
    print(f"(Pausa de {sleep_time:.2f}s)...")
    time.sleep(sleep_time)

def run():
    if not USERNAME or not PASSWORD or not TARGET_ACCOUNT:
        print("Error: Faltan variables de entorno. Verifica tu archivo .env")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='es-ES'
        )
        page = context.new_page()

        print("Abriendo Instagram en la pagina de Login...")
        page.goto("https://www.instagram.com/accounts/login/")
        random_sleep(4, 7)

        print("Ingresando credenciales...")
        try:
            btn_cookies = page.locator('button:has-text("Permitir")').first
            if btn_cookies.is_visible(timeout=3000):
                btn_cookies.click()
                random_sleep(2, 4)
        except Exception:
            pass

        input_usuario = page.locator('input[name="username"], input[type="text"]').first
        input_password = page.locator('input[name="password"], input[type="password"]').first

        input_usuario.wait_for(state="visible", timeout=30000)
        
        input_usuario.click()
        random_sleep(1, 2)
        input_usuario.press_sequentially(USERNAME, delay=150)
        random_sleep(2, 4)
        
        input_password.click()
        random_sleep(1, 2)
        input_password.press_sequentially(PASSWORD, delay=150)
        random_sleep(1, 2)
        input_password.press("Enter")
        
        print("Esperando validacion de inicio de sesion...")
        random_sleep(3, 5) 
        try:
            page.wait_for_selector('svg[aria-label="Inicio"], svg[aria-label="Home"], svg[aria-label="Búsqueda"], svg[aria-label="Search"]', timeout=20000)
        except Exception:
            print("Atencion: Instagram esta tardando o pidio seguridad extra. Tienes 60 segundos.")
            page.wait_for_selector('svg[aria-label="Inicio"], svg[aria-label="Home"], svg[aria-label="Búsqueda"], svg[aria-label="Search"]', timeout=60000)
            
        random_sleep(3, 5)

        print(f"Navegando al perfil: {TARGET_ACCOUNT}")
        page.goto(f"https://www.instagram.com/{TARGET_ACCOUNT}/")
        random_sleep(5, 8)

        print("Haciendo scroll para cargar el feed...")
        page.mouse.wheel(0, 800)
        random_sleep(2, 4)
        page.mouse.wheel(0, 1200)
        random_sleep(2, 5)
        page.keyboard.press('Home')
        random_sleep(2, 4)

        selector_posts = 'main a[href*="/p/"], main a[href*="/reel/"]'
        
        try:
            page.wait_for_selector(selector_posts, timeout=20000)
        except Exception:
            print("Advertencia: No se encontro la cuadricula de fotos.")
            browser.close()
            return

        posts_elements = page.locator(selector_posts).all()
        if not posts_elements:
            print("Error: No se encontraron publicaciones validas.")
            return

        resultados = []
        cantidad_a_extraer = min(10, len(posts_elements))

        print("Iniciando extraccion de metricas...")
        for i in range(cantidad_a_extraer):
            print(f"\nAnalizando publicacion {i+1}/{cantidad_a_extraer}...")
            post = posts_elements[i]

            href = post.get_attribute("href")
            url_limpia = f"https://www.instagram.com{href}".split('?')[0]

            likes = "Ocultos"
            comentarios = "0"

            post.hover()
            
            tiempo_mirando_foto = random.uniform(1.2, 3.8)
            page.wait_for_timeout(tiempo_mirando_foto * 1000) 

            items_lista = post.locator('ul li').all()

            try:
                if len(items_lista) >= 2:
                    likes = items_lista[0].inner_text().strip()
                    comentarios = items_lista[1].inner_text().strip()
                else:
                    texto_hover = post.inner_text().strip().split('\n')
                    texto_hover = [t for t in texto_hover if t.strip()]
                    if len(texto_hover) >= 2:
                        likes = texto_hover[0]
                        comentarios = texto_hover[1]
                    elif len(texto_hover) == 1:
                        likes = texto_hover[0]
            except Exception:
                pass

            likes = re.sub(r'(?i)me gusta|likes', '', likes).strip()
            comentarios = re.sub(r'(?i)comentarios|comments', '', comentarios).strip()

            resultados.append({
                "publicacion_numero": i + 1,
                "url": url_limpia,
                "likes_txt": likes,
                "comentarios_txt": comentarios
            })
            
            print(f"Extraido -> Likes: {likes} | Comentarios: {comentarios}")

            page.mouse.move(0, 0)
            random_sleep(1.5, 4.5)

        # Imprimir y guardar resultados
        encabezado = f"| {'POST':<6} | {'LIKES':<15} | {'COMENTARIOS':<15} | {'URL'}"
        
        print("\n\n" + "=" * 95)
        print("REPORTE DE METRICAS EXTRAIDAS")
        print("=" * 95)
        print(encabezado)
        print("-" * 95)
        
        # Guardamos en un archivo de texto para evitar perdidas en la terminal
        with open("reporte_instagram.txt", "w", encoding="utf-8") as f:
            f.write("REPORTE DE METRICAS EXTRAIDAS\n")
            f.write("=" * 95 + "\n")
            f.write(encabezado + "\n")
            f.write("-" * 95 + "\n")

            for res in resultados:
                linea = f"| Post {res['publicacion_numero']:02d} | {res['likes_txt']:<15} | {res['comentarios_txt']:<15} | {res['url']}"
                print(linea)
                f.write(linea + "\n")

            f.write("=" * 95 + "\n")
            
        print("=" * 95 + "\n")
        print("El reporte completo se ha guardado en 'reporte_instagram.txt'.")

        browser.close()

if __name__ == "__main__":
    run()