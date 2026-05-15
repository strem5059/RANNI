class SphereAnimations {
  constructor(sphereGroup, binaryPoints, ringGroup) {
    this.sphereGroup = sphereGroup;
    this.binaryPoints = binaryPoints;
    this.ringGroup = ringGroup;
  }

  activate() {
    // Animación de activación: pulso brillante
    gsap.to(this.sphereGroup.scale, {
      x: 1.1,
      y: 1.1,
      z: 1.1,
      duration: 0.2,
      yoyo: true,
      repeat: 1,
      ease: "power2.out",
    });
  }

  listeningPulse() {
    // Pulso suave mientras escucha
  }

  processingSpin() {
    // Giro rápido mientras procesa
    gsap.to(this.sphereGroup.rotation, {
      y: this.sphereGroup.rotation.y + Math.PI * 2,
      duration: 0.5,
      ease: "power2.out",
    });
  }

  speakingRing() {
    // Anillos se expanden al hablar
    if (!this.ringGroup) return;
    this.ringGroup.children.forEach((ring, i) => {
      gsap.to(ring.scale, {
        x: 1.2 + i * 0.1,
        y: 1.2 + i * 0.1,
        z: 1.2 + i * 0.1,
        duration: 0.3,
        yoyo: true,
        repeat: 1,
        ease: "power2.out",
        delay: i * 0.1,
      });
    });
  }
}

// Nota: gsap no está incluido por defecto.
// Las animaciones usan interpolación nativa en el loop principal.
// Si se desea gsap: npm install gsap
