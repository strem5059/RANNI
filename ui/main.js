const { app, BrowserWindow, ipcMain, screen } = require("electron");
const path = require("path");

let mainWindow;

function createWindow() {
  const WIDTH = 420;
  const HEIGHT = 460;
  const { width: sw, height: sh } = screen.getPrimaryDisplay().workAreaSize;
  const x = sw - WIDTH - 20;
  const y = sh - HEIGHT - 20;

  mainWindow = new BrowserWindow({
    width: WIDTH,
    height: HEIGHT,
    x, y,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    resizable: false,
    skipTaskbar: true,
    title: "RANNI UI",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  mainWindow.setIgnoreMouseEvents(true, { forward: true });
  mainWindow.loadFile(path.join(__dirname, "renderer", "index.html"));

  if (process.argv.includes("--dev")) {
    mainWindow.webContents.openDevTools({ mode: "detach" });
  }

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

ipcMain.on("set-ignore-mouse", (event, ignore) => {
  if (mainWindow) {
    mainWindow.setIgnoreMouseEvents(ignore, { forward: true });
  }
});
