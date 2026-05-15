class ParticleBurst {
  constructor(scene) {
    this.scene = scene;
    this.particles = [];
  }

  emit(count = 50, position = { x: 0, y: 0, z: 0 }, color = 0x00f0ff) {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const velocities = [];
    const life = [];

    for (let i = 0; i < count; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const speed = 0.02 + Math.random() * 0.05;
      positions[i * 3] = position.x;
      positions[i * 3 + 1] = position.y;
      positions[i * 3 + 2] = position.z;
      velocities.push({
        x: Math.sin(phi) * Math.cos(theta) * speed,
        y: Math.sin(phi) * Math.sin(theta) * speed,
        z: Math.cos(phi) * speed,
      });
      life.push(1.0);
    }

    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));

    const material = new THREE.PointsMaterial({
      color: color,
      size: 0.02,
      transparent: true,
      opacity: 1,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });

    const points = new THREE.Points(geometry, material);
    this.scene.add(points);
    this.particles.push({ points, velocities, life, geometry, material });
  }

  update() {
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      const pos = p.geometry.attributes.position.array;
      for (let j = 0; j < pos.length / 3; j++) {
        pos[j * 3] += p.velocities[j].x;
        pos[j * 3 + 1] += p.velocities[j].y;
        pos[j * 3 + 2] += p.velocities[j].z;
        p.velocities[j].x *= 0.98;
        p.velocities[j].y *= 0.98;
        p.velocities[j].z *= 0.98;
      }
      p.geometry.attributes.position.needsUpdate = true;
      p.life = p.life.map((l) => l - 0.01);
      p.material.opacity = p.life.reduce((a, b) => a + b, 0) / p.life.length;
      if (p.life[0] <= 0) {
        this.scene.remove(p.points);
        p.geometry.dispose();
        p.material.dispose();
        this.particles.splice(i, 1);
      }
    }
  }
}

// Data flow particles (líneas de datos)
class DataFlow {
  constructor(scene) {
    this.scene = scene;
    this.flows = [];
  }

  addFlow(from, to, color = 0x00f0ff) {
    const points = [];
    const segments = 30;
    for (let i = 0; i <= segments; i++) {
      const t = i / segments;
      points.push(
        new THREE.Vector3(
          from.x + (to.x - from.x) * t + (Math.random() - 0.5) * 0.1,
          from.y + (to.y - from.y) * t + (Math.random() - 0.5) * 0.1,
          from.z + (to.z - from.z) * t + (Math.random() - 0.5) * 0.1
        )
      );
    }
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({
      color: color,
      transparent: true,
      opacity: 0.3,
    });
    const line = new THREE.Line(geometry, material);
    this.scene.add(line);
    this.flows.push({ line, life: 1.0 });
  }

  update() {
    for (let i = this.flows.length - 1; i >= 0; i--) {
      this.flows[i].life -= 0.02;
      this.flows[i].line.material.opacity = this.flows[i].life * 0.3;
      if (this.flows[i].life <= 0) {
        this.scene.remove(this.flows[i].line);
        this.flows[i].line.geometry.dispose();
        this.flows[i].line.material.dispose();
        this.flows.splice(i, 1);
      }
    }
  }
}
