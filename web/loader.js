let muted = false;

const canvas = document.getElementById("canvas");

document.getElementById("btnFS").onclick = () => {
  if (document.fullscreenElement) document.exitFullscreen();
  else canvas.requestFullscreen();
};

document.getElementById("btnMute").onclick = () => {
  muted = !muted;
  Module.pygame_mixer_set_muted(muted);
};

const Module = {
  canvas: canvas,
  async onRuntimeInitialized() {
    // Enable mixer at start (muted if browser blocks)
    Module.pygame_mixer_init();
    Module.pygame_mixer_set_muted(false);
  }
};

window.Module = Module;
