class ImageSlider {
    constructor(container) {
        this.container = container;
        this.slider = container.querySelector('.slider');
        this.slides = container.querySelectorAll('.slide');
        this.dots = container.querySelectorAll('.slider-dot');
        this.prevButton = container.querySelector('.prev');
        this.nextButton = container.querySelector('.next');
        
        this.currentSlide = 0;
        this.slideCount = this.slides.length;
        this.isAutoPlaying = true;
        this.autoPlayInterval = null;
        
        this.init();
    }
    
    init() {
        // Add event listeners
        this.prevButton.addEventListener('click', () => this.prevSlide());
        this.nextButton.addEventListener('click', () => this.nextSlide());
        
        this.dots.forEach((dot, index) => {
            dot.addEventListener('click', () => this.goToSlide(index));
        });
        
        // Pause on hover
        this.container.addEventListener('mouseenter', () => this.pauseAutoPlay());
        this.container.addEventListener('mouseleave', () => this.startAutoPlay());
        
        // Start autoplay
        this.startAutoPlay();
        
        // Update initial state
        this.updateSlider();
    }
    
    updateSlider() {
        // Update slides position
        this.slider.style.transform = `translateX(-${this.currentSlide * 100}%)`;
        
        // Update dots
        this.dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === this.currentSlide);
        });
    }
    
    nextSlide() {
        this.currentSlide = (this.currentSlide + 1) % this.slideCount;
        this.updateSlider();
    }
    
    prevSlide() {
        this.currentSlide = (this.currentSlide - 1 + this.slideCount) % this.slideCount;
        this.updateSlider();
    }
    
    goToSlide(index) {
        this.currentSlide = index;
        this.updateSlider();
    }
    
    startAutoPlay() {
        if (!this.isAutoPlaying) {
            this.isAutoPlaying = true;
            this.autoPlayInterval = setInterval(() => this.nextSlide(), 5000); // Change slide every 5 seconds
        }
    }
    
    pauseAutoPlay() {
        if (this.isAutoPlaying) {
            this.isAutoPlaying = false;
            clearInterval(this.autoPlayInterval);
        }
    }
}

// Initialize sliders when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const sliders = document.querySelectorAll('.slider-container');
    sliders.forEach(slider => new ImageSlider(slider));
});