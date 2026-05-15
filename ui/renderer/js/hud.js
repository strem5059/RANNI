class RanniHUD {
  constructor() {
    this.messages = [];
    this.container = document.getElementById("hud-container");
    this.statusEl = document.getElementById("status-text");
    this.commandEl = document.getElementById("command-text");
  }

  showMessage(text, duration = 3000) {
    this.commandEl.textContent = text;
    this.commandEl.classList.add("visible");
    clearTimeout(this._msgTimeout);
    this._msgTimeout = setTimeout(() => {
      this.commandEl.classList.remove("visible");
    }, duration);
  }

  setStatus(text) {
    this.statusEl.textContent = text.toUpperCase();
  }

  showTyping(text) {
    let i = 0;
    this.commandEl.classList.add("visible");
    this.commandEl.textContent = "";
    const interval = setInterval(() => {
      this.commandEl.textContent += text[i];
      i++;
      if (i >= text.length) clearInterval(interval);
    }, 30);
  }
}

const hud = new RanniHUD();
