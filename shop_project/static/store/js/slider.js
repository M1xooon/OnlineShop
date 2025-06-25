document.addEventListener('DOMContentLoaded', () => {
    const slider = document.querySelector('.sale-slider');
    if (slider) {
        let scrollAmount = 0;
        setInterval(() => {
            scrollAmount += 220;
            if (scrollAmount >= slider.scrollWidth - slider.clientWidth) {
                scrollAmount = 0;
            }
            slider.scrollTo({ left: scrollAmount, behavior: 'smooth' });
        }, 3000);
    }

    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        const preview = card.querySelector('.preview-img');
        const thumbs = card.querySelectorAll('.thumb');
        thumbs.forEach(thumb => {
            thumb.addEventListener('mouseenter', () => {
                preview.src = thumb.src;
            });
        });
    });

    const mainImage = document.getElementById('main-image');
    if (mainImage) {
        document.querySelectorAll('.product-detail .thumb').forEach(thumb => {
            thumb.addEventListener('click', () => {
                mainImage.src = thumb.src;
            });
        });

        // Увеличение картинки по клику (простая реализация)
        mainImage.addEventListener('click', () => {
            const overlay = document.createElement('div');
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.backgroundColor = 'rgba(0,0,0,0.8)';
            overlay.style.display = 'flex';
            overlay.style.justifyContent = 'center';
            overlay.style.alignItems = 'center';
            overlay.style.cursor = 'zoom-out';
            const img = document.createElement('img');
            img.src = mainImage.src;
            img.style.maxWidth = '90%';
            img.style.maxHeight = '90%';
            overlay.appendChild(img);
            document.body.appendChild(overlay);

            overlay.addEventListener('click', () => {
                document.body.removeChild(overlay);
            });
        });
    }
});
