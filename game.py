import pygame
import random
import sys
import os

# --- INICIALIZACIÓN ---
pygame.init()
pygame.mixer.init()

# --- PANEL DE CONTROL ---
CONFIG = {
    "ANCHO": 960,  # Ajustado a 16:9 para mejor compatibilidad móvil
    "ALTO": 540,
    "VIDAS_INICIALES": 3,
    "VEL_JUGADOR": 8,
    "VEL_MI_BALA": 12,
    "VEL_BALA_ENEMIGA": 5,
    "VEL_OVNI": 4,
    "VEL_CAIDA_ALIENS": 15,
    "VEL_BASE_ALIENS": 1.0,
    "ARCHIVO_RECORDS": "records.txt",
    "NUM_ESTRELLAS": 60,
    "VOL_MUSICA": 0.4,
    "VOL_DISPARO": 0.2,
    "VOL_EXPLOSION": 0.3,
    "VOL_UFO": 0.3
}

pantalla = pygame.display.set_mode((CONFIG["ANCHO"], CONFIG["ALTO"]))
pygame.display.set_caption("Space Invaders Mobile")
clock = pygame.time.Clock()

# --- CLASE PARA EL FONDO ESTELAR ---
class FondoEstrellas:
    def __init__(self):
        self.estrellas = []
        for _ in range(CONFIG["NUM_ESTRELLAS"]):
            self.estrellas.append([
                random.randint(0, CONFIG["ANCHO"]),
                random.randint(0, CONFIG["ALTO"]),
                random.uniform(1.0, 3.0)
            ])

    def actualizar_y_dibujar(self, superficie):
        for e in self.estrellas:
            e[1] += e[2]
            if e[1] > CONFIG["ALTO"]:
                e[1] = 0
                e[0] = random.randint(0, CONFIG["ANCHO"])
            pygame.draw.circle(superficie, (150, 150, 200), (int(e[0]), int(e[1])), 1)

fondo_espacial = FondoEstrellas()

# --- CARGA DE RECURSOS (Rutas relativas para GitHub) ---
def cargar_img(nombre, alpha=True):
    ruta = os.path.join("assets", nombre)
    try:
        # Forzamos que Pygame cargue la ruta relativa correctamente
        img = pygame.image.load(ruta)
        return img.convert_alpha() if alpha else img.convert()
    except:
        # Si falla (ej. error de mayúsculas), crea un cuadrado de repuesto
        s = pygame.Surface((40, 40))
        s.fill((0, 255, 0))
        return s

alien_imgs = [cargar_img(f"alien{i}.png") for i in range(1, 5)]
jugador_img = cargar_img("nave.png")
logo_img = cargar_img("logo.png")
ovni_img = cargar_img("help.png") # Cambiado .gif por .png para evitar errores de carga en web
escudo_img = cargar_img("escudo.png")

# --- SONIDOS ---
try:
    pygame.mixer.music.load(os.path.join("assets", "music.mp3"))
    pygame.mixer.music.set_volume(CONFIG["VOL_MUSICA"])
    pygame.mixer.music.play(-1)
    sonido_disparo = pygame.mixer.Sound(os.path.join("assets", "fire.mp3"))
    sonido_explosion = pygame.mixer.Sound(os.path.join("assets", "bomb.mp3"))
    sonido_ufo = pygame.mixer.Sound(os.path.join("assets", "ufosound.mp3"))
except:
    sonido_disparo = sonido_explosion = sonido_ufo = None

fuente = pygame.font.Font(None, 30)
fuente_grande = pygame.font.Font(None, 60)

# --- SISTEMA DE RÉCORDS (Simplificado para Web) ---
def obtener_top_cinco():
    return [{"nombre": "PLAYER", "puntos": 1000}] # En web el guardado en TXT es limitado

# --- INTERFACES ---
def pantalla_inicio():
    esperando = True
    while esperando:
        pantalla.fill((0, 0, 0))
        fondo_espacial.actualizar_y_dibujar(pantalla)
        # Centrar logo
        pantalla.blit(logo_img, (CONFIG["ANCHO"]//2 - logo_img.get_width()//2, 50))
        txt = fuente.render("TOCA LA PANTALLA O ESPACIO PARA EMPEZAR", True, (255, 255, 255))
        pantalla.blit(txt, (CONFIG["ANCHO"]//2 - txt.get_width()//2, 350))
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return False
            if e.type == pygame.KEYDOWN or e.type == pygame.FINGERDOWN: esperando = False
    return True

# --- NÚCLEO DEL JUEGO ---
def jugar_nivel(nivel, vidas, puntaje):
    balas_jugador, balas_enemigas = [], []
    u_disp_e = 0
    # Posición inicial jugador
    j_x, j_y = CONFIG["ANCHO"] // 2, CONFIG["ALTO"] - 70
    enemigos = [[random.choice(alien_imgs), pygame.Rect(60+c*70, 50+f*45, 40, 40)] for f in range(4) for c in range(10)]
    direccion = 1
    
    # Touch variables
    last_fire = 0
    autofire_delay = 250 

    jugando = True
    while jugando:
        ahora = pygame.time.get_ticks()
        pantalla.fill((0, 0, 0))
        fondo_espacial.actualizar_y_dibujar(pantalla)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "exit", puntaje
            # Control Táctil: Mover nave a la posición del dedo
            if e.type in [pygame.FINGERDOWN, pygame.FINGERMOTION]:
                j_x = int(e.x * CONFIG["ANCHO"]) - 30

        # Disparo Automático Táctil
        if ahora - last_fire > autofire_delay:
            balas_jugador.append(pygame.Rect(j_x + 28, j_y, 4, 12))
            if sonido_disparo: sonido_disparo.play()
            last_fire = ahora

        # Movimiento Enemigos
        vel_actual = CONFIG["VEL_BASE_ALIENS"] + (nivel * 0.2)
        bajar = False
        for _, r in enemigos:
            r.x += vel_actual * direccion
            if r.right >= CONFIG["ANCHO"] or r.left <= 0: bajar = True
        
        if bajar:
            direccion *= -1
            for _, r in enemigos: r.y += CONFIG["VEL_CAIDA_ALIENS"]

        # Procesar Balas Jugador
        for b in balas_jugador[:]:
            b.y -= CONFIG["VEL_MI_BALA"]
            pygame.draw.rect(pantalla, (255, 255, 255), b)
            if b.bottom < 0: balas_jugador.remove(b)
            else:
                for en in enemigos[:]:
                    if b.colliderect(en[1]):
                        enemigos.remove(en)
                        balas_jugador.remove(b)
                        puntaje += 10
                        if sonido_explosion: sonido_explosion.play()
                        break

        # Balas Enemigas
        if ahora - u_disp_e > 1500 - (nivel * 100):
            if enemigos:
                sel = random.choice(enemigos)
                balas_enemigas.append(pygame.Rect(sel[1].centerx, sel[1].bottom, 4, 10))
                u_disp_e = ahora

        for be in balas_enemigas[:]:
            be.y += CONFIG["VEL_BALA_ENEMIGA"]
            pygame.draw.rect(pantalla, (255, 50, 50), be)
            if be.top > CONFIG["ALTO"]: balas_enemigas.remove(be)
            elif be.colliderect(pygame.Rect(j_x, j_y, 60, 40)):
                vidas -= 1
                balas_enemigas.remove(be)
                if vidas <= 0: return "gameover", puntaje

        # Dibujar Todo
        for img, r in enemigos: pantalla.blit(img, r)
        pantalla.blit(jugador_img, (j_x, j_y))
        
        txt = fuente.render(f"PUNTOS: {puntaje}  VIDAS: {vidas}", True, (255, 255, 0))
        pantalla.blit(txt, (10, CONFIG["ALTO"]-30))

        if not enemigos: return "win", puntaje

        pygame.display.update()
        clock.tick(60)

def main():
    if not pantalla_inicio(): return
    v, p, n = CONFIG["VIDAS_INICIALES"], 0, 1
    while True:
        res, p_final = jugar_nivel(n, v, p)
        if res == "gameover" or res == "exit": break
        n += 1
        p = p_final

if __name__ == "__main__":
    main()
