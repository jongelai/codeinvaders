let muted = false;

const canvas = document.getElementById("canvas");

document.getElementById("btnFS").onclick = () => {
    if (document.fullscreenElement) {
        document.exitFullscreen();
    } else {
        canvas.requestFullscreen().catch(err => {
            console.log("Error al entrar en fullscreen: " + err.message);
        });
    }
};

document.getElementById("btnMute").onclick = () => {
    muted = !muted;
    if (Module.pygame_mixer_set_muted) {
        Module.pygame_mixer_set_muted(muted);
    }
};

const Module = {
    canvas: canvas,
    // Argumentos para que el motor sepa qué archivo ejecutar
    arguments: ["game.py"],
    async onRuntimeInitialized() {
        console.log("Motor listo, iniciando sonido...");
        if (Module.pygame_mixer_init) {
            Module.pygame_mixer_init();
            Module.pygame_mixer_set_muted(false);
        }
    }
};

window.Module = Module;

// --- ESTO ES LO QUE TE FALTABA: CARGAR EL MOTOR ---
const script = document.createElement("script");
// Usamos la versión estable del motor de pygame-ce para web
script.src = "https://pygame-games.com/engine/pygame_ce.js";
script.async = true;
document.body.appendChild(script);
