document.addEventListener('DOMContentLoaded', function () {
  function initializeSegmentedBars() {
    const bars = document.querySelectorAll('.segmented-bar');
    bars.forEach(bar => {
      const steps = parseInt(bar.getAttribute('data-steps') || '10', 10);
      const percent = parseFloat(bar.getAttribute('data-percent') || '0');
      const filledCount = Math.round((percent / 100) * steps);

      // Clear existing segments
      bar.innerHTML = '';

      // Create segments
      for (let i = 0; i < steps; i++) {
        const segment = document.createElement('div');
        segment.className = 'segment';
        bar.appendChild(segment);
      }

      // Animate segments filling
      const segments = Array.from(bar.children);
      requestAnimationFrame(() => {
        segments.forEach((segment, idx) => {
          if (idx < filledCount) {
            setTimeout(() => {
              segment.classList.add('filled');
              segment.classList.add('pulse');
              setTimeout(() => segment.classList.remove('pulse'), 260);
            }, idx * 60);
          }
        });
      });
    });
  }

  function initializeProgressRings() {
    const rings = document.querySelectorAll('.progress-ring');
    rings.forEach(ring => {
      const percent = parseFloat(ring.getAttribute('data-percent') || '0');
      const fill = ring.querySelector('.progress-ring-fill');
      ring.style.setProperty('--progress-percent', percent + '%');
      
      requestAnimationFrame(() => {
        fill.classList.add('animate');
      });
    });
  }

  // Initialize both types of progress indicators
  initializeSegmentedBars();
  initializeProgressRings();
});