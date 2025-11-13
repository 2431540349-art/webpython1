// ==== Bật tắt cờ ====
const flags = document.querySelectorAll('.language-switch .flag');
flags.forEach(flag => {
  flag.addEventListener('click', () => {
    flags.forEach(f => f.classList.remove('active'));
    flag.classList.add('active');
  });
});

// ==== CTA Nút "Khám phá ngay" ánh sáng 10 phương luôn sáng + nhảy bật ====
const cta = document.querySelector('.cta');

// Luôn bật glow
cta.classList.add('cta-glow');

// Hàm nhảy bật ngẫu nhiên
function animateCTA() {
  const xMove = (Math.random() * 6 - 3).toFixed(2);
  const yMove = (Math.random() * 6 - 3).toFixed(2);
  const scale = (1 + Math.random() * 0.05).toFixed(2);
  cta.style.transform = `translate(${xMove}px, ${yMove}px) scale(${scale})`;
}

// Chạy liên tục
setInterval(animateCTA, 300);
