import pygame
import random
import sys
import os
# --- INICIALIZACIÓN ---
pygame.init()
pygame.mixer.init()

# --- PANEL DE CONTROL ---
CONFIG = {
    "ANCHO": 1000,
    "ALTO": 800,
    "VIDAS_INICIALES": 3,
    "VEL_JUGADOR": 8,
    "VEL_MI_BALA": 15,
    "VEL_BALA_ENEMIGA": 6,
    "VEL_OVNI": 5,
    "VEL_CAIDA_ALIENS": 20,
    "VEL_BASE_ALIENS": 1.2,
    "FRECUENCIA_OVNI": (15, 25),
    "CADENCIA_RAFAGA": 180,
    "DURACION_RAFAGA": 8000,
    "ARCHIVO_RECORDS": "records_locales.txt",
    "NUM_ESTRELLAS": 100,
    "VOL_MUSICA": 0.5,
    "VOL_DISPARO": 0.1,
    "VOL_EXPLOSION": 0.3,
    "VOL_UFO": 0.4
}

pantalla = pygame.display.set_mode((CONFIG["ANCHO"], CONFIG["ALTO"]))
pygame.display.set_caption("Space Invaders: Starfield Edition")
clock = pygame.time.Clock()

# --- CLASE PARA EL FONDO ESTELAR ---
class FondoEstrellas:
    def __init__(self):
        self.estrellas = []
        for _ in range(CONFIG["NUM_ESTRELLAS"]):
            self.estrellas.append([
                random.randint(0, CONFIG["ANCHO"]),
                random.randint(0, CONFIG["ALTO"]),
                random.uniform(0.5, 3.0),
                random.randint(1, 3)
            ])

    def actualizar_y_dibujar(self, superficie):
        for e in self.estrellas:
            e[1] += e[2]
            if e[1] > CONFIG["ALTO"]:
                e[1] = 0
                e[0] = random.randint(0, CONFIG["ANCHO"])
            color = (200, 200, 255) if e[2] > 2 else (100, 100, 150)
            pygame.draw.circle(superficie, color, (int(e[0]), int(e[1])), e[3])

fondo_espacial = FondoEstrellas()

# --- RECURSOS ---
def cargar_img(nombre, alpha=True):
    try:
        ruta = os.path.join("assets", nombre)
        img = pygame.image.load(ruta)
        return img.convert_alpha() if alpha else img.convert()
    except:
        s = pygame.Surface((50,50), pygame.SRCALPHA)
        s.fill((0, 255, 0))
        return s

alien_imgs = [cargar_img(f"alien{i}.png") for i in range(1, 5)]
jugador_img = cargar_img("nave.png")
logo_img = cargar_img("logo.png")
ovni_img = cargar_img("help.gif")
escudo_original = cargar_img("escudo.png")

# --- SONIDOS ---
try:
    pygame.mixer.music.load(os.path.join("assets","music.mp3"))
    pygame.mixer.music.set_volume(CONFIG["VOL_MUSICA"])
    pygame.mixer.music.play(-1)

    sonido_disparo = pygame.mixer.Sound(os.path.join("assets","fire.mp3"))
    sonido_disparo.set_volume(CONFIG["VOL_DISPARO"])

    sonido_explosion = pygame.mixer.Sound(os.path.join("assets","bomb.mp3"))
    sonido_explosion.set_volume(CONFIG["VOL_EXPLOSION"])

    sonido_ufo = pygame.mixer.Sound(os.path.join("assets","ufosound.mp3"))
    sonido_ufo.set_volume(CONFIG["VOL_UFO"])
except:
    sonido_disparo = sonido_explosion = sonido_ufo = None

fuente = pygame.font.Font(None, 36)
fuente_grande = pygame.font.Font(None, 80)

# --- SISTEMA DE RÉCORDS ---
def obtener_top_cinco():
    if not os.path.exists(CONFIG["ARCHIVO_RECORDS"]): return []
    records = []
    try:
        with open(CONFIG["ARCHIVO_RECORDS"], "r") as f:
            for linea in f:
                if ";" in linea:
                    n, p = linea.strip().split(";")
                    records.append({"nombre": n, "puntos": int(p)})
    except: pass
    records.sort(key=lambda x: x["puntos"], reverse=True)
    return records[:5]

def guardar_nuevo_record(nombre, puntos):
    recs = obtener_top_cinco()
    recs.append({"nombre": nombre, "puntos": puntos})
    recs.sort(key=lambda x: x["puntos"], reverse=True)
    with open(CONFIG["ARCHIVO_RECORDS"], "w") as f:
        for r in recs[:5]: f.write(f"{r['nombre']};{r['puntos']}\n")

# --- INTERFACES ---
def pedir_nombre(puntos):
    nombre = ""
    while True:
        pantalla.fill((0, 0, 0))
        fondo_espacial.actualizar_y_dibujar(pantalla)
        t1 = fuente_grande.render("¡NUEVO RÉCORD!", True, (0, 255, 0))
        txt_n = fuente_grande.render(nombre + "_", True, (255, 215, 0))
        pantalla.blit(t1, (CONFIG["ANCHO"]//2 - t1.get_width()//2, 200))
        pantalla.blit(txt_n, (CONFIG["ANCHO"]//2 - txt_n.get_width()//2, 400))
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return nombre
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and len(nombre) > 0:
                    return nombre
                elif e.key == pygame.K_BACKSPACE:
                    nombre = nombre[:-1]
                else:
                    if len(nombre) < 10 and e.unicode.isalnum(): 
                        nombre += e.unicode.upper()

def pantalla_inicio(nivel, top5):
    esperando = True
    while esperando:
        pantalla.fill((0, 0, 0))
        fondo_espacial.actualizar_y_dibujar(pantalla)
        pantalla.blit(logo_img, ((CONFIG["ANCHO"] - logo_img.get_width())//2, 50))
        tit = fuente.render(f"NIVEL {nivel} - RANKING", True, (0, 255, 255))
        pantalla.blit(tit, (CONFIG["ANCHO"]//2 - tit.get_width()//2, 280))
        for i, r in enumerate(top5):
            col = (255, 215, 0) if i == 0 else (255, 255, 255)
            txt = fuente.render(f"{i+1}. {r['nombre']} - {r['puntos']}", True, col)
            pantalla.blit(txt, (CONFIG["ANCHO"]//2 - txt.get_width()//2, 330 + i*35))
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                esperando = False

def pausa_muerte(vidas):
    for _ in range(90):
        fondo_espacial.actualizar_y_dibujar(pantalla)
        overlay = pygame.Surface((CONFIG["ANCHO"], CONFIG["ALTO"]))
        overlay.set_alpha(10); overlay.fill((0, 0, 0))
        pantalla.blit(overlay, (0, 0))
        txt_str = "¡ÚLTIMA VIDA!" if vidas == 1 else f"TE QUEDAN {vidas} VIDAS"
        txt = fuente_grande.render(txt_str, True, (255, 50, 50))
        pantalla.blit(txt, (CONFIG["ANCHO"]//2 - txt.get_width()//2, CONFIG["ALTO"]//2))
        pygame.display.update()
        clock.tick(60)

# --- NÚCLEO DEL JUEGO ---
def jugar_nivel(nivel, vidas, puntaje):
    balas_jugador, balas_enemigas = [], []
    u_disp_j, u_disp_e = 0, 0
    rafaga_activa, rafaga_fin = False, 0

    enemigos = [[alien_imgs[f%4], pygame.Rect(80+c*85, 80+f*55, 50, 50)] for f in range(5) for c in range(10)]
    j_x, j_y = CONFIG["ANCHO"] // 2, CONFIG["ALTO"] - 80
    escudos = [pygame.Rect(CONFIG["ANCHO"]//4 * (i+1) - 40, CONFIG["ALTO"]-180, 80, 40) for i in range(3)]
    ovni_rect, t_ovni = None, pygame.time.get_ticks() + random.randint(15000, 25000)

    canal_ufo = pygame.mixer.Channel(5)
    canal_ufo.set_volume(CONFIG["VOL_UFO"])

    direccion = 1

    # --- Touch Controls ---
    touch_active = False
    touch_time = 0
    last_fire = 0
    autofire_delay = 200

    while True:
        clock.tick(60)
        ahora = pygame.time.get_ticks()
        pantalla.fill((0, 0, 0))
        fondo_espacial.actualizar_y_dibujar(pantalla)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "exit", puntaje

            # TOUCH
            if e.type == pygame.FINGERDOWN:
                touch_active = True
                touch_time = ahora
                j_x = int(e.x * CONFIG["ANCHO"]) - 30

            elif e.type == pygame.FINGERMOTION and touch_active:
                j_x = int(e.x * CONFIG["ANCHO"]) - 30

            elif e.type == pygame.FINGERUP:
                dur = ahora - touch_time
                touch_active = False
                if dur < 180:
                    # tap simple
                    balas_jugador.append(pygame.Rect(j_x+28, j_y, 4,18))
                    if sonido_disparo: sonido_disparo.play()
                # si dur > 180 = autofire ya lo hace abajo

        # CONTROLES PC
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  j_x = max(0, j_x - CONFIG["VEL_JUGADOR"])
        if keys[pygame.K_RIGHT]: j_x = min(CONFIG["ANCHO"] - 60, j_x + CONFIG["VEL_JUGADOR"])
        if keys[pygame.K_SPACE]:
            if (rafaga_activa and ahora - u_disp_j > CONFIG["CADENCIA_RAFAGA"]) or (not rafaga_activa and len(balas_jugador) == 0):
                balas_jugador.append(pygame.Rect(j_x + 28, j_y, 4, 18))
                if sonido_disparo: sonido_disparo.play()
                u_disp_j = ahora

        # AUTOFIRE táctil
        if touch_active and ahora - last_fire > autofire_delay:
            balas_jugador.append(pygame.Rect(j_x+28, j_y, 4,18))
            if sonido_disparo: sonido_disparo.play()
            last_fire = ahora

        if rafaga_activa and ahora > rafaga_fin:
            rafaga_activa = False

        # OVNI
        if ovni_rect:
            ovni_rect.x += CONFIG["VEL_OVNI"]
            pantalla.blit(ovni_img, ovni_rect)
            if ovni_rect.left > CONFIG["ANCHO"]:
                ovni_rect = None; canal_ufo.stop()
                t_ovni = ahora + random.randint(15000, 25000)
        elif ahora > t_ovni:
            ovni_rect = ovni_img.get_rect(topleft=(-60, 40))
            if sonido_ufo: canal_ufo.play(sonido_ufo, loops=-1)

        vel = CONFIG["VEL_BASE_ALIENS"] + (nivel * 0.2) + (3.0 if len(enemigos) < 5 else 0)
        bajar = False
        for _, r in enemigos:
            r.x += vel * direccion
            if r.right >= CONFIG["ANCHO"] or r.left <= 0: bajar = True
        if bajar:
            direccion *= -1
            for _, r in enemigos: r.y += CONFIG["VEL_CAIDA_ALIENS"]

        # BALAS JUGADOR
        for b in balas_jugador[:]:
            b.y -= CONFIG["VEL_MI_BALA"]
            pygame.draw.rect(pantalla, (0,255,255) if rafaga_activa else (255,255,255), b)

            for esc in escudos:
                if b.colliderect(esc):
                    balas_jugador.remove(b); break

            if b.bottom < 0:
                balas_jugador.remove(b); continue

            if ovni_rect and b.colliderect(ovni_rect):
                if sonido_explosion: sonido_explosion.play()
                canal_ufo.stop()
                rafaga_activa, rafaga_fin = True, ahora + CONFIG["DURACION_RAFAGA"]
                ovni_rect = None
                puntaje += 500
                balas_jugador.remove(b)
                t_ovni = ahora + random.randint(15000, 25000)
                continue

            for item in enemigos[:]:
                if b.colliderect(item[1]):
                    enemigos.remove(item)
                    puntaje += 10
                    if sonido_explosion: sonido_explosion.play()
                    balas_jugador.remove(b)
                    break

        # BALAS ENEMIGAS
        if ahora - u_disp_e > max(400, 1300 - (nivel*150)):
            if enemigos:
                s = random.choice(enemigos)
                balas_enemigas.append(pygame.Rect(s[1].centerx, s[1].bottom, 4, 15))
                u_disp_e = ahora

        for be in balas_enemigas[:]:
            be.y += CONFIG["VEL_BALA_ENEMIGA"]
            pygame.draw.rect(pantalla, (255, 50, 50), be)

            for esc in escudos:
                if be.colliderect(esc):
                    balas_enemigas.remove(be)
                    break

            if be.colliderect(pygame.Rect(j_x, j_y, 60, 40)):
                vidas -= 1
                balas_enemigas.remove(be)
                if sonido_explosion: sonido_explosion.play()
                if vidas > 0:
                    pausa_muerte(vidas)
                    j_x = CONFIG["ANCHO"]//2
                    balas_enemigas.clear()
                    break
                else:
                    return "gameover", puntaje

        for img, r in enemigos:
            pantalla.blit(img, r.topleft)
            if r.bottom >= j_y:
                return "gameover", puntaje

        for esc in escudos:
            pantalla.blit(escudo_original, esc.topleft)

        pantalla.blit(jugador_img, (j_x, j_y))
        hud = fuente.render(f"PUNTOS: {puntaje}   VIDAS: {vidas}   NIVEL: {nivel}", True, (255, 215, 0))
        pantalla.blit(hud, (20, CONFIG["ALTO"] - 40))

        if not enemigos:
            return puntaje, vidas

        pygame.display.update()

def main():
    v, p, n = CONFIG["VIDAS_INICIALES"], 0, 1
    while True:
        top5 = obtener_top_cinco()
        pantalla_inicio(n, top5)
        res = jugar_nivel(n, v, p)
        if isinstance(res, tuple) and res[0] == "gameover":
            if len(top5) < 5 or res[1] > (top5[-1]["puntos"] if top5 else -1):
                nombre = pedir_nombre(res[1])
                guardar_nuevo_record(nombre, res[1])
            v, p, n = CONFIG["VIDAS_INICIALES"], 0, 1
        elif isinstance(res, tuple) and res[0] == "exit":
            break
        else:
            p, v = res
            n += 1

if __name__ == "__main__":
    main()
