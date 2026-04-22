import os
import time
import random
import re
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Cargar variables forzando la actualización
load_dotenv(override=True)

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
TARGET_ACCOUNT = os.getenv("IG_TARGET_ACCOUNT")

def random_sleep(min_s=4, max_s=9):
    """Pausa la ejecución por un tiempo aleatorio para simular comportamiento humano."""
    sleep_time = random.uniform(min_s, max_s)
    print(f" Esperando {sleep_time:.2f} segundos...")
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

        print(" Abriendo Instagram directamente en el Login...")
        page.goto("https://www.instagram.com/accounts/login/")
        random_sleep(5, 8)

        print("Ingresando credenciales...")
        
        try:
            btn_cookies = page.locator('button:has-text("Permitir")').first
            if btn_cookies.is_visible(timeout=3000):
                print("Aceptando banner de cookies...")
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
        print("Presionando 'Enter' para enviar el formulario...")
        input_password.press("Enter")
        
        print("Esperando a que los servidores de Instagram validen la cuenta...")
        random_sleep(3, 5) 
        try:
            page.wait_for_selector('svg[aria-label="Inicio"], svg[aria-label="Home"], svg[aria-label="Búsqueda"], svg[aria-label="Search"]', timeout=20000)
            print("¡Inicio de sesión confirmado!")
        except Exception:
            print("Instagram pidió seguridad extra. Tienes 60 segundos en la ventana...")
            page.wait_for_selector('svg[aria-label="Inicio"], svg[aria-label="Home"], svg[aria-label="Búsqueda"], svg[aria-label="Search"]', timeout=60000)
            print("¡Inicio de sesión confirmado tras validación de seguridad!")
            
        random_sleep(4, 6)

        try:
            btn_ahora_no = page.get_by_role("button", name="Ahora no")
            if btn_ahora_no.is_visible(timeout=4000):
                btn_ahora_no.click()
                random_sleep(2, 4)
        except Exception:
            pass

        # Ir al perfil objetivo
        print(f"Navegando al perfil objetivo: {TARGET_ACCOUNT}")
        page.goto(f"https://www.instagram.com/{TARGET_ACCOUNT}/")
        random_sleep(6, 10)

        print("Preparando para obtener métricas de las primeras 10 publicaciones...")
        
        selector_posts = 'a[href*="/p/"], a[href*="/reel/"]'
        
        try:
            page.wait_for_selector(selector_posts, timeout=20000)
        except Exception:
            print(" No se encontró la cuadrícula de fotos.")
            browser.close()
            return

        random_sleep(3, 6)

        # Capturamos la lista de todos los posts en la cuadrícula
        posts_elements = page.locator(selector_posts).all()
        
        if not posts_elements:
            print("No se encontraron publicaciones válidas en este perfil.")
            return

        resultados = []
        
        # Limitamos a un máximo de 10 o a la cantidad de fotos que existan
        cantidad_a_extraer = min(10, len(posts_elements))

        for i in range(cantidad_a_extraer):
            print(f"\n Analizando publicación {i+1}/{cantidad_a_extraer}...")
            
            # Hacemos clic en el post desde la cuadrícula
            posts_elements[i].click()
            
            # Esperamos a que la ventana flotante (modal) cargue
            try:
                page.wait_for_selector('article[role="presentation"]', timeout=15000)
                random_sleep(3, 6)
            except Exception:
                print(" El contenido tardó mucho en cargar, saltando...")
                page.keyboard.press('Escape')
                random_sleep(2, 4)
                continue

            url = page.url
            # Eliminamos el index del carrusel para tener la URL limpia
            url_limpia = url.split('?')[0] 
            
            likes = "Ocultos / No detectados"
            comentarios = "0"
            
            # Extraemos TODO el texto visible en la ventana
            try:
                texto_completo = page.locator('article[role="presentation"]').inner_text()
                
                # ESCÁNER REGEX PARA LIKES (Busca números seguidos de 'Me gusta' o 'likes')
                match_likes = re.search(r'([\d.,]+[KMBkmb]?)\s*(Me gusta|likes)', texto_completo, re.IGNORECASE)
                if match_likes:
                    likes = match_likes.group(1).strip()
                
                # ESCÁNER REGEX PARA COMENTARIOS (Busca números seguidos de 'comentarios' o 'comments')
                match_comentarios = re.search(r'([\d.,]+[KMBkmb]?)\s*(comentarios|comments)', texto_completo, re.IGNORECASE)
                if match_comentarios:
                    comentarios = match_comentarios.group(1).strip()
                    
            except Exception as e:
                print(f"Error al leer el texto: {e}")

            resultados.append({
                "publicacion_numero": i + 1,
                "url": url_limpia,
                "likes": likes,
                "comentarios": comentarios
            })
            
            print(f"Extraído -> URL: {url_limpia} | Likes: {likes} | Comentarios: {comentarios}")

            # TRUCO MAESTRO: Presionamos la tecla 'Escape' para cerrar la foto y volver a la cuadrícula
            print("Cerrando publicación...")
            page.keyboard.press('Escape')
            random_sleep(3, 6)

        print("\n Extracción completada. Resumen final de las métricas:")
        for res in resultados:
            print(res)

        print("\nCerrando el navegador...")
        browser.close()

if __name__ == "__main__":
    run()