let muted = false;
const canvas = document.getElementById("canvas");

document.getElementById("btnFS").onclick = () => {
    if (document.fullscreenElement) document.exitFullscreen();
    else canvas.requestFullscreen().catch(e => console.log(e));
};

document.getElementById("btnMute").onclick = () => {
    muted = !muted;
    if (Module.pygame_mixer_set_muted) Module.pygame_mixer_set_muted(muted);
};

const Module = {
    canvas: canvas,
    arguments: ["game.py"],
    async onRuntimeInitialized() {
        if (Module.pygame_mixer_init) {
            Module.pygame_mixer_init();
            Module.pygame_mixer_set_muted(false);
        }
    }
};

window.Module = Module;
const script = document.createElement("script");
script.src = "https://pygame-games.com/engine/pygame_ce.js";
script.async = true;
document.body.appendChild(script);
