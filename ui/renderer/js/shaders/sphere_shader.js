const sphereVertexShader = `
  uniform float uTime;
  uniform float uPulse;
  uniform float uWaveIntensity;

  varying vec2 vUv;
  varying vec3 vPosition;
  varying float vElevation;

  void main() {
    vUv = uv;
    vec3 pos = position;

    float wave1 = sin(pos.x * 8.0 + uTime * 0.8) * cos(pos.y * 8.0 + uTime * 0.6) * sin(pos.z * 6.0 + uTime * 0.5);
    float wave2 = sin(pos.x * 12.0 + uTime * 1.2) * 0.5 + cos(pos.y * 10.0 + uTime * 0.9) * 0.5;
    float wave = (wave1 * 0.7 + wave2 * 0.3) * uWaveIntensity * uPulse;

    pos += normal * wave * 0.06;
    vElevation = wave;
    vPosition = pos;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
  }
`;

const sphereFragmentShader = `
  uniform float uTime;
  uniform float uPulse;
  uniform vec3 uColor;
  uniform vec3 uGlowColor;
  uniform float uOpacity;

  varying vec2 vUv;
  varying vec3 vPosition;
  varying float vElevation;

  void main() {
    vec2 grid = vUv * 40.0;
    vec2 gridId = floor(grid);
    float digit = mod(gridId.x + gridId.y, 2.0);

    float pulse = sin(uTime * 1.5 + vElevation * 8.0) * 0.5 + 0.5;
    float glowPulse = sin(uTime * 2.0 + gridId.x * 0.3 + gridId.y * 0.3) * 0.3 + 0.7;

    vec3 color = mix(uColor, uGlowColor, pulse * 0.4);
    color *= glowPulse * (0.8 + 0.4 * uPulse);

    float edge = 1.0 - abs(vUv.x - 0.5) * 2.0;
    edge *= 1.0 - abs(vUv.y - 0.5) * 2.0;
    float alpha = uOpacity * (0.5 + 0.5 * edge) * (0.7 + 0.3 * uPulse);

    if (digit < 0.5) {
      alpha *= 0.3;
    }

    float glow = 0.0;
    vec2 fgrid = fract(grid) - 0.5;
    float dist = length(fgrid);
    glow = exp(-dist * 8.0) * 0.5;

    color += uGlowColor * glow * (0.5 + 0.5 * uPulse);

    gl_FragColor = vec4(color, alpha);
  }
`;

const binarySpriteVertexShader = `
  uniform float uTime;
  attribute float aSize;
  attribute float aSpeed;
  attribute float aOffset;
  attribute float aDigit;
  varying float vDigit;

  void main() {
    vDigit = aDigit;
    vec3 pos = position;

    float angle = uTime * aSpeed + aOffset;
    float rad = length(pos);
    float theta = atan(pos.z, pos.x) + angle * 0.3;
    float phi = asin(pos.y / rad) + angle * 0.2;

    pos.x = rad * cos(theta) * cos(phi);
    pos.y = rad * sin(phi);
    pos.z = rad * sin(theta) * cos(phi);

    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
    gl_PointSize = aSize * (200.0 / -mvPosition.z);
    gl_Position = projectionMatrix * mvPosition;
  }
`;

const binarySpriteFragmentShader = `
  uniform float uTime;
  uniform vec3 uColor;
  uniform float uPulse;
  varying float vDigit;

  void main() {
    vec2 center = gl_PointCoord - vec2(0.5);
    float dist = length(center);
    if (dist > 0.5) discard;

    float glow = exp(-dist * 6.0);
    float pulse = 0.8 + 0.2 * sin(uTime * 3.0 + vDigit * 6.28);

    char c = vDigit > 0.5 ? '1' : '0';
    float alpha = smoothstep(0.5, 0.0, dist) * (0.6 + 0.4 * uPulse);

    vec3 color = uColor * pulse * (1.0 + glow * 0.5);

    gl_FragColor = vec4(color, alpha * 0.8);
  }
`;
