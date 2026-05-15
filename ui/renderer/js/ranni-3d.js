const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 0, 4);

const renderer = new THREE.WebGLRenderer({
  canvas: document.getElementById("ranni-canvas"),
  alpha: true,
  antialias: true,
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setClearColor(0x000000, 0);

const clock = new THREE.Clock();

let sphereGroup, binaryPoints, ringGroup;
let currentPulse = 0;
let targetPulse = 0;
let waveIntensity = 0.3;

// === ESFERA HOLOGRÁFICA PRINCIPAL ===
function createHoloSphere() {
  sphereGroup = new THREE.Group();

  const geo = new THREE.SphereGeometry(1.2, 64, 64);
  const mat = new THREE.ShaderMaterial({
    vertexShader: sphereVertexShader,
    fragmentShader: sphereFragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uPulse: { value: 0.5 },
      uWaveIntensity: { value: 0.3 },
      uColor: { value: new THREE.Color(0x00c8ff) },
      uGlowColor: { value: new THREE.Color(0x0066ff) },
      uOpacity: { value: 0.8 },
    },
    transparent: true,
    blending: THREE.AdditiveBlending,
    side: THREE.DoubleSide,
    depthWrite: false,
  });

  const sphere = new THREE.Mesh(geo, mat);
  sphereGroup.add(sphere);

  // Líneas de wireframe orbitando
  const wireGeo = new THREE.SphereGeometry(1.25, 24, 16);
  const wireMat = new THREE.MeshBasicMaterial({
    color: 0x00f0ff,
    wireframe: true,
    transparent: true,
    opacity: 0.15,
  });
  const wireSphere = new THREE.Mesh(wireGeo, wireMat);
  sphereGroup.add(wireSphere);

  // Anillos rotatorios
  ringGroup = new THREE.Group();
  for (let i = 0; i < 3; i++) {
    const ringGeo = new THREE.TorusGeometry(1.4 + i * 0.15, 0.008, 16, 100);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.2 - i * 0.05,
      blending: THREE.AdditiveBlending,
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = Math.PI / 3 + i * 0.5;
    ring.rotation.y = i * 0.3;
    ring.userData = { speed: 0.3 + i * 0.15, axis: i };
    ringGroup.add(ring);
  }
  sphereGroup.add(ringGroup);

  scene.add(sphereGroup);
  return { sphere, mat, wireSphere };
}

// === BITS BINARIOS (1s y 0s) ===
function createBinaryBits() {
  const count = 2048;
  const positions = new Float32Array(count * 3);
  const sizes = new Float32Array(count);
  const speeds = new Float32Array(count);
  const offsets = new Float32Array(count);
  const digits = new Float32Array(count);

  for (let i = 0; i < count; i++) {
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    const radius = 1.6 + Math.random() * 0.8;
    positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
    positions[i * 3 + 2] = radius * Math.cos(phi);
    sizes[i] = 8 + Math.random() * 16;
    speeds[i] = 0.2 + Math.random() * 0.6;
    offsets[i] = Math.random() * Math.PI * 2;
    digits[i] = Math.random() > 0.5 ? 1 : 0;
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geo.setAttribute("aSize", new THREE.BufferAttribute(sizes, 1));
  geo.setAttribute("aSpeed", new THREE.BufferAttribute(speeds, 1));
  geo.setAttribute("aOffset", new THREE.BufferAttribute(offsets, 1));
  geo.setAttribute("aDigit", new THREE.BufferAttribute(digits, 1));

  const mat = new THREE.ShaderMaterial({
    vertexShader: binarySpriteVertexShader,
    fragmentShader: binarySpriteFragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uColor: { value: new THREE.Color(0x00f0ff) },
      uPulse: { value: 0.5 },
    },
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });

  binaryPoints = new THREE.Points(geo, mat);
  scene.add(binaryPoints);
}

// === PARTÍCULAS DE FONDO ===
function createBackgroundParticles() {
  const count = 3000;
  const positions = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 20;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 20;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 20;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const mat = new THREE.PointsMaterial({
    color: 0x004488,
    size: 0.01,
    transparent: true,
    opacity: 0.5,
  });
  const particles = new THREE.Points(geo, mat);
  scene.add(particles);
}

const holo = createHoloSphere();
createBinaryBits();
createBackgroundParticles();

// === WEBSOCKET ===
let ws = null;
function connectWebSocket() {
  ws = new WebSocket("ws://127.0.0.1:9876");
  ws.onopen = () => console.log("RANNI UI: Conectado al backend");
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    handleBackendMessage(msg);
  };
  ws.onclose = () => {
    console.log("RANNI UI: Desconectado, reconectando...");
    setTimeout(connectWebSocket, 2000);
  };
}

function handleBackendMessage(msg) {
  const { type, data } = msg;
  switch (type) {
    case "state":
      setState(data);
      break;
    case "status":
      updateHUDStatus(data.status, data.text);
      break;
    case "audio_level":
      updateAudioLevel(data.level);
      break;
  }
}

function sendToBackend(msg) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(msg));
  }
}

// === ESTADOS ===
function setState(state) {
  document.getElementById("status-corner").textContent = state.toUpperCase();
  switch (state) {
    case "listening":
      setSpherePulse(1.0, 0.8);
      updateHUDStatus("listening", "ESCUCHANDO...");
      break;
    case "processing":
      setSpherePulse(1.5, 0.5);
      updateHUDStatus("processing", "PROCESANDO...");
      break;
    case "speaking":
      setSpherePulse(0.8, 0.3);
      updateHUDStatus("speaking", "HABLANDO...");
      break;
    default:
      setSpherePulse(0.5, 0.3);
      updateHUDStatus("idle", "ESPERANDO COMANDO");
  }
}

function setSpherePulse(pulse, intensity) {
  targetPulse = pulse;
  waveIntensity = intensity;
}

function updateHUDStatus(status, text) {
  const statusEl = document.getElementById("status-text");
  const cmdEl = document.getElementById("command-text");
  statusEl.textContent = text.toUpperCase();
  if (text && text !== "ESPERANDO COMANDO") {
    cmdEl.textContent = text;
    cmdEl.classList.add("visible");
  } else {
    cmdEl.textContent = "";
    cmdEl.classList.remove("visible");
  }
}

function updateAudioLevel(level) {
  document.getElementById("audio-level").style.height = `${Math.min(level * 100, 100)}%`;
}

// === RELOJ ===
function updateClock() {
  const now = new Date();
  document.getElementById("time-display").textContent =
    now.toTimeString().split(" ")[0];
}

// === RESIZE ===
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// === LOOP PRINCIPAL ===
function animate() {
  requestAnimationFrame(animate);

  const t = clock.getElapsedTime();

  currentPulse += (targetPulse - currentPulse) * 0.05;

  if (holo.sphere) {
    holo.sphere.material.uniforms.uTime.value = t;
    holo.sphere.material.uniforms.uPulse.value = currentPulse;
    holo.sphere.material.uniforms.uWaveIntensity.value = waveIntensity;
  }

  sphereGroup.rotation.y = t * 0.08;
  sphereGroup.rotation.x = Math.sin(t * 0.03) * 0.1;

  if (ringGroup) {
    ringGroup.children.forEach((ring, i) => {
      ring.rotation.z += 0.005 * ring.userData.speed;
      ring.rotation.x += 0.003 * ring.userData.speed;
    });
  }

  if (binaryPoints) {
    binaryPoints.material.uniforms.uTime.value = t;
    binaryPoints.material.uniforms.uPulse.value = currentPulse;
    binaryPoints.rotation.y = t * 0.05;
    binaryPoints.rotation.x = Math.sin(t * 0.02) * 0.05;
  }

  updateClock();
  renderer.render(scene, camera);
}

connectWebSocket();
animate();
