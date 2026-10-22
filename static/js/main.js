// Lenis smooth scroll + GSAP ScrollTrigger entegrasyonu
const lenis = new Lenis({ duration: 1.1, smoothWheel: true });
gsap.registerPlugin(ScrollTrigger);
lenis.on("scroll", ScrollTrigger.update);
gsap.ticker.add((time) => lenis.raf(time * 1000));
gsap.ticker.lagSmoothing(0);

// Mobil menü
const toggle = document.getElementById("menu-toggle");
const menu = document.getElementById("mobile-menu");
toggle?.addEventListener("click", () => {
  const open = menu.classList.toggle("hidden") === false;
  toggle.setAttribute("aria-expanded", String(open));
  document.getElementById("icon-open").classList.toggle("hidden", open);
  document.getElementById("icon-close").classList.toggle("hidden", !open);
});

// Anchor linkleri Lenis ile kaydır
document.querySelectorAll('a[href^="#"]').forEach((a) => {
  a.addEventListener("click", (e) => {
    const id = a.getAttribute("href");
    if (id.length > 1 && document.querySelector(id)) {
      e.preventDefault();
      lenis.scrollTo(id, { offset: -80 });
      if (!menu.classList.contains("hidden")) toggle.click();
    }
  });
});

// Header kapsül gölge efekti (Scroll anında hafif derinleşme)
const headerPill = document.getElementById("header-pill");
window.addEventListener("scroll", () => {
  headerPill?.classList.toggle("shadow-2xl", window.scrollY > 20);
});

// Sayfa yüklendiğinde Hero ve Header akıcı giriş animasyonu
window.addEventListener("DOMContentLoaded", () => {
  // Hero dikey metal plakalar (Vertical Slices) akıcı iniş animasyonu
  const slices = gsap.utils.toArray(".hero-slice-col");
  const dividers = gsap.utils.toArray(".hero-slice-divider");
  const baseImg = document.getElementById("hero-base-img");
  const sliceGroup = document.querySelector(".hero-slice-group");

  if (slices.length > 0) {
    // 4 metal levha sırayla yukarıdan ritmik ve güçlü bir ivmeyle oturur
    gsap.from(slices, {
      yPercent: -100,
      duration: 0.85,
      stagger: 0.12,
      ease: "power3.out",
      onComplete: () => {
        // Plakalar birleşince orijinal net görsel kalıcı olarak devreye girer
        if (baseImg) baseImg.style.opacity = "1";
        if (dividers.length) gsap.to(dividers, { opacity: 0, duration: 0.35 });
        gsap.to(sliceGroup, {
          opacity: 0,
          duration: 0.4,
          delay: 0.25,
          onComplete: () => {
            if (sliceGroup) sliceGroup.style.display = "none";
          }
        });
      }
    });

    // Olası yavaş bağlantılarda arka planın boş kalmaması için güvenlik zamanlayıcısı
    setTimeout(() => {
      if (baseImg && baseImg.style.opacity !== "1") {
        baseImg.style.opacity = "1";
      }
    }, 1600);
  }

  // Header yumuşak iniş
  gsap.from("#site-header", {
    y: -30,
    opacity: 0,
    duration: 0.9,
    ease: "power3.out",
    delay: 0.2
  });

  // Hero metinleri ve butonları kademeli akıcı yükseliş (Staggered Fade-Up)
  gsap.from("#hero [data-reveal]", {
    y: 35,
    opacity: 0,
    duration: 1.1,
    stagger: 0.15,
    ease: "power3.out",
    delay: 0.4
  });
});

// Sayfa kaydırıldıkça beliren diğer elemanlar: [data-reveal]
gsap.utils.toArray("section:not(#hero) [data-reveal]").forEach((el) => {
  gsap.from(el, {
    y: 40,
    opacity: 0,
    duration: 0.9,
    ease: "power3.out",
    scrollTrigger: {
      trigger: el,
      start: "top 88%",
      toggleActions: "play none none none"
    },
  });
});

/* ==========================================================================
   3D WEAREWILD COVERFLOW & PARALLAX GYRO ENGINE (AWWWARDS / APPLE TIER)
   ========================================================================== */
(function init3DCoverflow() {
  const stage = document.getElementById("coverflow-stage");
  if (!stage) return;

  const cards = Array.from(stage.querySelectorAll(".coverflow-card"));
  const prevBtn = document.getElementById("coverflow-prev");
  const nextBtn = document.getElementById("coverflow-next");
  const dots = Array.from(document.querySelectorAll("#coverflow-dots button"));
  const total = cards.length;
  let currentIndex = 0;
  let isHovered = false;
  let autoTimer = null;

  // Parallax Gyro Fizik Durumu (Lerp için)
  let mouseTargetX = 0;
  let mouseTargetY = 0;
  let currentTiltX = 0;
  let currentTiltY = 0;
  let rafId = null;

  function getStepOffset() {
    const w = window.innerWidth;
    if (w < 640) return 210;
    if (w < 1024) return 290;
    return 360;
  }

  function updateCards() {
    const step = getStepOffset();

    cards.forEach((card, i) => {
      let diff = (i - currentIndex) % total;
      if (diff > total / 2) diff -= total;
      if (diff < -total / 2) diff += total;

      const innerImg = card.querySelector("img");

      if (diff === 0) {
        // AKTİF MERKEZ KART
        card.style.transform = `translate3d(0px, 0px, 0px) rotateY(0deg) scale(1.05)`;
        card.style.zIndex = "40";
        card.style.opacity = "1";
        card.style.filter = "none";
        card.style.pointerEvents = "auto";
        card.style.cursor = "default";
      } else if (diff === 1) {
        // SAĞ KANAT KART
        card.style.transform = `translate3d(${step}px, 0px, -90px) rotateY(-15deg) scale(0.88)`;
        card.style.zIndex = "20";
        card.style.opacity = "0.72";
        card.style.filter = "brightness(0.96) saturate(0.92)";
        card.style.pointerEvents = "auto";
        card.style.cursor = "pointer";
        if (innerImg) innerImg.style.transform = "none";
      } else if (diff === -1) {
        // SOL KANAT KART
        card.style.transform = `translate3d(${-step}px, 0px, -90px) rotateY(15deg) scale(0.88)`;
        card.style.zIndex = "20";
        card.style.opacity = "0.72";
        card.style.filter = "brightness(0.96) saturate(0.92)";
        card.style.pointerEvents = "auto";
        card.style.cursor = "pointer";
        if (innerImg) innerImg.style.transform = "none";
      } else {
        // UZAK ARKA KART
        const dir = diff > 0 ? 1 : -1;
        card.style.transform = `translate3d(${dir * (step * 1.5)}px, 0px, -180px) rotateY(${dir * -24}deg) scale(0.72)`;
        card.style.zIndex = "10";
        card.style.opacity = "0";
        card.style.filter = "blur(1px)";
        card.style.pointerEvents = "none";
        if (innerImg) innerImg.style.transform = "none";
      }
    });

    // Sayfalama Çizgi Göstergeleri
    dots.forEach((dot, idx) => {
      const active = idx === currentIndex;
      dot.className = active
        ? "h-2 rounded-full transition-all duration-300 w-8 bg-[#1c2d26]"
        : "h-2 rounded-full transition-all duration-300 w-2.5 bg-[#1c2d26]/30 hover:bg-[#1c2d26]/60";
    });
  }

  function goTo(index) {
    currentIndex = ((index % total) + total) % total;
    mouseTargetX = 0;
    mouseTargetY = 0;
    currentTiltX = 0;
    currentTiltY = 0;
    updateCards();
  }

  function next() {
    goTo(currentIndex + 1);
  }

  function prev() {
    goTo(currentIndex - 1);
  }

  // Buton ve Dot Olayları
  prevBtn?.addEventListener("click", () => {
    prev();
    resetAuto();
  });

  nextBtn?.addEventListener("click", () => {
    next();
    resetAuto();
  });

  dots.forEach((dot, idx) => {
    dot.addEventListener("click", () => {
      goTo(idx);
      resetAuto();
    });
  });

  // Kartlara Tıklama (Yan karttaysa merkeze getir; merkezdeyse linke git)
  cards.forEach((card, idx) => {
    card.addEventListener("click", (e) => {
      // Eğer doğrudan "Hakkımızda" butonuna basılmadıysa ve kart aktif değilse merkeze al
      if (idx !== currentIndex && !e.target.closest("a")) {
        e.preventDefault();
        goTo(idx);
        resetAuto();
      }
    });
  });

  // Klavye Navigasyonu
  window.addEventListener("keydown", (e) => {
    if (stage.getBoundingClientRect().top < window.innerHeight && stage.getBoundingClientRect().bottom > 0) {
      if (e.key === "ArrowLeft") {
        prev();
        resetAuto();
      } else if (e.key === "ArrowRight") {
        next();
        resetAuto();
      }
    }
  });

  // Dokunmatik ve Fare Sürükleme (Swipe & Drag)
  let startX = 0;
  let isDragging = false;

  stage.addEventListener("touchstart", (e) => {
    startX = e.touches[0].clientX;
    isDragging = true;
  }, { passive: true });

  stage.addEventListener("touchend", (e) => {
    if (!isDragging) return;
    const diffX = e.changedTouches[0].clientX - startX;
    if (Math.abs(diffX) > 40) {
      if (diffX > 0) prev();
      else next();
      resetAuto();
    }
    isDragging = false;
  }, { passive: true });

  // 60fps Lerp 3D Parallax Tilt (Aktif Kartta Canlı Derinlik)
  function renderParallax() {
    currentTiltX += (mouseTargetX - currentTiltX) * 0.1;
    currentTiltY += (mouseTargetY - currentTiltY) * 0.1;

    const activeCard = cards[currentIndex];
    if (activeCard) {
      const rotY = currentTiltX * 7;
      const rotX = -currentTiltY * 7;
      activeCard.style.transform = `translate3d(0px, 0px, 0px) rotateX(${rotX}deg) rotateY(${rotY}deg) scale(1.05)`;

      // Kartın içindeki 3D objeyi z-uzayında daha güçlü kaydır (Stereoscopic Parallax)
      const innerImg = activeCard.querySelector("img");
      if (innerImg) {
        innerImg.style.transform = `translate3d(${currentTiltX * 16}px, ${currentTiltY * 16}px, 40px)`;
      }
    }

    rafId = requestAnimationFrame(renderParallax);
  }

  stage.addEventListener("mousemove", (e) => {
    const activeCard = cards[currentIndex];
    if (!activeCard) return;

    const rect = activeCard.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (x >= 0 && x <= rect.width && y >= 0 && y <= rect.height) {
      // -1 ile +1 arasında normalize et
      mouseTargetX = ((x / rect.width) - 0.5) * 2;
      mouseTargetY = ((y / rect.height) - 0.5) * 2;
    } else {
      mouseTargetX = 0;
      mouseTargetY = 0;
    }
  });

  stage.addEventListener("mouseenter", () => {
    isHovered = true;
    if (autoTimer) clearInterval(autoTimer);
  });

  stage.addEventListener("mouseleave", () => {
    isHovered = false;
    mouseTargetX = 0;
    mouseTargetY = 0;
    startAuto();
  });

  function startAuto() {
    if (autoTimer) clearInterval(autoTimer);
    autoTimer = setInterval(() => {
      if (!isHovered) next();
    }, 5500);
  }

  function resetAuto() {
    startAuto();
  }

  window.addEventListener("resize", () => {
    updateCards();
  });

  // Başlat
  updateCards();
  renderParallax();
  startAuto();
})();

/* ==========================================================================
   APPLE "GET THE HIGHLIGHTS" INTERACTIVE SLIDER ENGINE (AWWWARDS / APPLE TIER)
   ========================================================================== */
(function initAppleHighlights() {
  const stage = document.getElementById("apple-highlights-stage");
  const track = document.getElementById("apple-highlights-track");
  if (!stage || !track) return;

  const slides = Array.from(track.querySelectorAll(".apple-slide"));
  const dots = Array.from(document.querySelectorAll("#apple-progress-dots .apple-dot"));
  const prevBtn = document.getElementById("apple-prev-btn");
  const nextBtn = document.getElementById("apple-next-btn");
  const playPauseBtn = document.getElementById("apple-play-pause-btn");
  const playIcon = document.getElementById("apple-play-icon");
  const pauseIcon = document.getElementById("apple-pause-icon");

  const total = slides.length;
  let currentIndex = 0;
  let isPlaying = true;
  let isHovered = false;
  let progress = 0; // 0 to 100
  const duration = 6000; // 6 seconds per slide
  let lastTime = performance.now();
  let rafId = null;

  // Center positioning calculation
  function updateTrack() {
    const stageWidth = stage.offsetWidth;
    const activeSlide = slides[currentIndex];
    if (!activeSlide) return;

    const slideWidth = activeSlide.offsetWidth;
    const slideLeft = activeSlide.offsetLeft;
    const targetOffset = (stageWidth - slideWidth) / 2 - slideLeft;

    track.style.transform = `translate3d(${targetOffset}px, 0px, 0px)`;

    // Update active/inactive classes on slides
    slides.forEach((slide, idx) => {
      if (idx === currentIndex) {
        slide.classList.remove("apple-card-inactive");
        slide.classList.add("apple-card-active");
      } else {
        slide.classList.remove("apple-card-active");
        slide.classList.add("apple-card-inactive");
      }
    });

    // Update Apple pill dots
    dots.forEach((dot, idx) => {
      const fill = dot.querySelector(".apple-dot-fill");
      if (idx === currentIndex) {
        dot.className = "apple-dot group relative h-2.5 rounded-full transition-all duration-300 w-12 bg-white/20 overflow-hidden cursor-pointer";
        if (fill) fill.style.width = `${progress}%`;
      } else {
        dot.className = "apple-dot group relative h-2.5 rounded-full transition-all duration-300 w-2.5 bg-white/30 hover:bg-white/60 overflow-hidden cursor-pointer";
        if (fill) fill.style.width = idx < currentIndex ? "100%" : "0%";
      }
    });
  }

  function goTo(index) {
    currentIndex = ((index % total) + total) % total;
    progress = 0;
    updateTrack();
  }

  function next() {
    goTo(currentIndex + 1);
  }

  function prev() {
    goTo(currentIndex - 1);
  }

  // Animation Loop for Smooth Progress Bar & Auto-Advance
  function loop(now) {
    const delta = now - lastTime;
    lastTime = now;

    if (isPlaying && !isHovered) {
      progress += (delta / duration) * 100;
      if (progress >= 100) {
        progress = 0;
        next();
      } else {
        const activeDot = dots[currentIndex];
        const fill = activeDot?.querySelector(".apple-dot-fill");
        if (fill) fill.style.width = `${progress}%`;
      }
    }

    rafId = requestAnimationFrame(loop);
  }

  // Controls
  prevBtn?.addEventListener("click", () => {
    prev();
  });

  nextBtn?.addEventListener("click", () => {
    next();
  });

  dots.forEach((dot, idx) => {
    dot.addEventListener("click", () => {
      goTo(idx);
    });
  });

  slides.forEach((slide, idx) => {
    slide.addEventListener("click", (e) => {
      if (idx !== currentIndex && !e.target.closest("a")) {
        e.preventDefault();
        goTo(idx);
      }
    });
  });

  // Play / Pause toggle
  playPauseBtn?.addEventListener("click", () => {
    isPlaying = !isPlaying;
    if (isPlaying) {
      playIcon?.classList.add("hidden");
      pauseIcon?.classList.remove("hidden");
      playPauseBtn.setAttribute("aria-label", "Otomatik Oynatmayı Durdur");
    } else {
      pauseIcon?.classList.add("hidden");
      playIcon?.classList.remove("hidden");
      playPauseBtn.setAttribute("aria-label", "Otomatik Oynatmayı Başlat");
    }
  });

  // Hover detection to pause autoplay gracefully
  stage.addEventListener("mouseenter", () => {
    isHovered = true;
  });

  stage.addEventListener("mouseleave", () => {
    isHovered = false;
  });

  // Touch Swipe & Pointer Drag Mechanics
  let isDragging = false;
  let startX = 0;
  let currentDragOffset = 0;

  stage.addEventListener("pointerdown", (e) => {
    if (e.button !== 0 && e.pointerType === "mouse") return;
    isDragging = true;
    startX = e.clientX;
    currentDragOffset = 0;
  });

  window.addEventListener("pointermove", (e) => {
    if (!isDragging) return;
    const dx = e.clientX - startX;
    currentDragOffset = dx;
  });

  window.addEventListener("pointerup", () => {
    if (!isDragging) return;
    isDragging = false;
    if (currentDragOffset < -45) {
      next();
    } else if (currentDragOffset > 45) {
      prev();
    }
    currentDragOffset = 0;
  });

  // Keyboard navigation
  window.addEventListener("keydown", (e) => {
    // Only if target is not an input or textarea
    if (["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName)) return;
    if (e.key === "ArrowLeft") {
      prev();
    } else if (e.key === "ArrowRight") {
      next();
    }
  });

  window.addEventListener("resize", () => {
    updateTrack();
  });

  // Wait for initial layout rendering
  setTimeout(() => {
    updateTrack();
    lastTime = performance.now();
    rafId = requestAnimationFrame(loop);
  }, 100);
})();


