document.addEventListener('DOMContentLoaded', () => {

    // ============================================
    // 1. EFECTO LINTERNA EN EL HERO
    // ============================================
    const heroSection = document.getElementById('hero-section');
    const dotsHoverLayer = document.getElementById('dots-hover-layer');

    if (heroSection && dotsHoverLayer) {
        const handleMouseMove = (e) => {
            const rect = heroSection.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            dotsHoverLayer.style.setProperty('--mouse-x', `${x}px`);
            dotsHoverLayer.style.setProperty('--mouse-y', `${y}px`);
        };
        const handleMouseLeave = () => {
            dotsHoverLayer.style.setProperty('--mouse-x', `-1000px`);
            dotsHoverLayer.style.setProperty('--mouse-y', `-1000px`);
        };
        heroSection.addEventListener('mousemove', handleMouseMove);
        heroSection.addEventListener('mouseleave', handleMouseLeave);
    }

    // ============================================
    // 2. TYPEWRITER (MÁQUINA DE ESCRIBIR)
    // ============================================
    const textTarget = document.getElementById('typewriter-text');
    const fullText = "Objet-X. Detector de objetos, detecta productos, analiza nombre del producto y el precio.";
    let typewriterTimeout = null;
    let isTyping = false;

    function startTypewriter() {
        if (textTarget && !isTyping) {
            if (typewriterTimeout) clearTimeout(typewriterTimeout);
            textTarget.innerHTML = "";
            let index = 0;
            isTyping = true;
            function typeEffect() {
                if (index < fullText.length) {
                    textTarget.innerHTML += fullText.charAt(index);
                    index++;
                    typewriterTimeout = setTimeout(typeEffect, 35);
                } else {
                    isTyping = false;
                }
            }
            typeEffect();
        }
    }

    // ============================================
    // 3. REVEAL ON SCROLL (APARICIÓN GRADUAL)
    // ============================================
    const revealElements = document.querySelectorAll('.reveal');
    let ticking = false;

    const revealOnScroll = () => {
        const triggerBottom = window.innerHeight * 0.88;
        revealElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            if (elementTop < triggerBottom && elementTop > -element.offsetHeight) {
                element.classList.add('active');
                if (element.classList.contains('typewriter-container') && !element.dataset.typed && !isTyping) {
                    element.dataset.typed = "true";
                    startTypewriter();
                }
            } else if (elementTop > triggerBottom + 100) {
                element.classList.remove('active');
                if (element.classList.contains('typewriter-container')) {
                    element.removeAttribute('data-typed');
                }
            }
        });
        ticking = false;
    };

    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                revealOnScroll();
                ticking = false;
            });
            ticking = true;
        }
    }, { passive: true });

    revealOnScroll();
    startTypewriter();

    // ============================================
    // 4. CARRUSEL INFINITO AUTOMÁTICO (SIN LAG)
    // ============================================
    const images = [
        { url: "/static/image/numpy.png", title: "NumPy", tech: "Data Science" },
        { url: "/static/image/pandas.png", title: "Pandas", tech: "Análisis de Datos" },
        { url: "/static/image/python.jfif", title: "Python", tech: "Visión Artificial" },
        { url: "/static/image/cv2.jfif", title: "OpenCV", tech: "Procesamiento de Video" },
        { url: "/static/image/Pillow.jfif", title: "Pillow", tech: "Backend Web" },
        { url: "/static/image/streamlit.png", title: "Streamlit", tech: "Lenguaje Core" },
        { url: "/static/image/ultralytics.jfif", title: "Ultralytics", tech: "Maquetación UI" }
    ];

    const container = document.getElementById('carousel-container');
    const indicatorsContainer = document.getElementById('carousel-indicators');
    let currentIndex = 3;
    let autoInterval = null;
    let isAutoPlaying = true;

    function renderCarousel() {
        if (!container) return;
        container.innerHTML = '';

        images.forEach((img, idx) => {
            const card = document.createElement('div');
            card.className = 'carousel-card';
            card.innerHTML = `
                <img src="${img.url}" alt="${img.title}" loading="lazy">
                <div class="card-overlay">
                    <h3>${img.title}</h3>
                    <p>${img.tech}</p>
                </div>
            `;
            container.appendChild(card);
        });
        updatePositions();
    }

    function updatePositions() {
        const cards = document.querySelectorAll('.carousel-card');
        const totalCards = cards.length;

        cards.forEach((card, idx) => {
            card.classList.remove('center', 'left-1', 'left-2', 'left-3', 'right-1', 'right-2', 'right-3', 'hidden-left', 'hidden-right');

            let offset = idx - currentIndex;
            if (offset < -Math.floor(totalCards / 2)) offset += totalCards;
            if (offset > Math.floor(totalCards / 2)) offset -= totalCards;

            if (offset === 0) {
                card.classList.add('center');
            } else if (offset === -1) {
                card.classList.add('left-1');
            } else if (offset === -2) {
                card.classList.add('left-2');
            } else if (offset === -3 || offset === 4) {
                card.classList.add('left-3');
            } else if (offset === 1) {
                card.classList.add('right-1');
            } else if (offset === 2) {
                card.classList.add('right-2');
            } else if (offset === 3 || offset === -4) {
                card.classList.add('right-3');
            } else {
                card.classList.add(offset < 0 ? 'hidden-left' : 'hidden-right');
            }
        });
        updateIndicators();
    }

    function moveCarousel(direction) {
        if (direction === 'next') {
            currentIndex = (currentIndex + 1) % images.length;
        } else if (direction === 'prev') {
            currentIndex = (currentIndex - 1 + images.length) % images.length;
        }
        updatePositions();
    }

    function createIndicators() {
        if (!indicatorsContainer) return;
        indicatorsContainer.innerHTML = '';
        images.forEach((_, idx) => {
            const indicator = document.createElement('div');
            indicator.classList.add('indicator');
            if (idx === currentIndex) indicator.classList.add('active');
            indicator.addEventListener('click', () => {
                if (autoInterval) clearInterval(autoInterval);
                isAutoPlaying = false;
                currentIndex = idx;
                updatePositions();
                setTimeout(() => {
                    isAutoPlaying = true;
                    startAutoCarousel();
                }, 5000);
            });
            indicatorsContainer.appendChild(indicator);
        });
    }

    function updateIndicators() {
        if (!indicatorsContainer) return;
        const indicators = indicatorsContainer.children;
        for (let i = 0; i < indicators.length; i++) {
            indicators[i].classList.remove('active');
        }
        if (indicators[currentIndex]) {
            indicators[currentIndex].classList.add('active');
        }
    }

    function startAutoCarousel() {
        if (autoInterval) clearInterval(autoInterval);
        autoInterval = setInterval(() => {
            if (isAutoPlaying) {
                moveCarousel('next');
            }
        }, 4000);
    }

    const carouselWrapper = document.querySelector('.carousel-wrapper');
    if (carouselWrapper) {
        carouselWrapper.addEventListener('mouseenter', () => {
            isAutoPlaying = false;
        });
        carouselWrapper.addEventListener('mouseleave', () => {
            isAutoPlaying = true;
            startAutoCarousel();
        });
    }

    renderCarousel();
    createIndicators();
    startAutoCarousel();

    // ============================================
    // 5. MODAL CONTROL OPTIMIZADO PARA LA CÁMARA
    // ============================================
    const btnProbar = document.getElementById('btn-probar');
    const cameraModal = document.getElementById('camera-modal');
    const modalCloseRed = document.getElementById('modal-close-red');
    const modalCloseX = document.getElementById('modal-close-x');
    const webcamFeed = document.getElementById('webcam-feed'); // Elemento de imagen del streaming

    function openModal() {
        if (cameraModal) {
            cameraModal.style.display = 'flex'; // Forzamos visibilidad inmediata en el DOM
            cameraModal.classList.add('open');

            // Re-inyectamos la URL para obligar al navegador a conectarse a la cámara
            if (webcamFeed) {
                webcamFeed.src = "/video_feed";
            }
        }
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        if (cameraModal) {
            cameraModal.style.display = 'none'; // Ocultamos el modal por completo
            cameraModal.classList.remove('open');

            // Apagamos la transmisión en el cliente para liberar recursos del backend
            if (webcamFeed) {
                webcamFeed.src = "";
            }
        }
        document.body.style.overflow = '';
    }

    // Eventos de click para el modal
    if (btnProbar) btnProbar.addEventListener('click', openModal);
    if (modalCloseRed) modalCloseRed.addEventListener('click', closeModal);
    if (modalCloseX) modalCloseX.addEventListener('click', closeModal);

    // Cerrar si el usuario hace clic en el fondo oscuro difuminado fuera de la ventana
    if (cameraModal) {
        cameraModal.addEventListener('click', (e) => {
            if (e.target === cameraModal) closeModal();
        });
    }

    // Soporte para cerrar la cámara presionando la tecla Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && cameraModal && cameraModal.classList.contains('open')) {
            closeModal();
        }
    });

    // ============================================
    // 6. OPTIMIZACIONES GLOBALES DE VENTANA
    // ============================================
    let resizeTimeout;
    window.addEventListener('resize', () => {
        if (resizeTimeout) clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            updatePositions();
            revealOnScroll();
        }, 150);
    });
});