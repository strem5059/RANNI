class SphereAnimations {
  constructor(sphereGroup, binaryPoints, ringGroup) {
    this.sphereGroup = sphereGroup;
    this.binaryPoints = binaryPoints;
    this.ringGroup = ringGroup;
  }

  activate() {
    if (!this.sphereGroup || typeof gsap === 'undefined') return;
    gsap.to(this.sphereGroup.scale, {
      x: 1.1, y: 1.1, z: 1.1,
      duration: 0.2, yoyo: true, repeat: 1, ease: "power2.out",
    });
  }

  listeningPulse() {}

  processingSpin() {
    if (this.sphereGroup) {
      this.sphereGroup.rotation.y += Math.PI * 2;
    }
  }

  speakingRing() {
    if (!this.ringGroup) return;
    this.ringGroup.children.forEach((ring, i) => {
      const s = 1.2 + i * 0.1;
      ring.scale.set(s, s, s);
      setTimeout(() => ring.scale.set(1, 1, 1), 300 + i * 100);
    });
  }
}
