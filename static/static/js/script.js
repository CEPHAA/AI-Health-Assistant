// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Form validation
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const requiredFields = this.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.style.borderColor = '#e74c3c';
                isValid = false;
            } else {
                field.style.borderColor = '#ddd';
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            alert('Please fill in all required fields');
        }
    });
});

// Auto-hide alerts
const alerts = document.querySelectorAll('.error-message');
alerts.forEach(alert => {
    setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
});

// Add loading state to buttons
document.querySelectorAll('button[type="submit"]').forEach(button => {
    button.addEventListener('click', function(e) {
        if (this.closest('form').checkValidity()) {
            const originalText = this.textContent;
            this.textContent = 'Processing...';
            this.disabled = true;
            
            setTimeout(() => {
                this.textContent = originalText;
                this.disabled = false;
            }, 2000);
        }
    });
});

// Character counter for symptom input
const symptomTextarea = document.getElementById('symptoms');
if (symptomTextarea) {
    symptomTextarea.addEventListener('input', function() {
        const count = this.value.length;
        let counter = document.querySelector('.char-count');
        
        if (!counter) {
            counter = document.createElement('small');
            counter.className = 'char-count';
            this.parentNode.appendChild(counter);
        }
        
        counter.textContent = `${count} characters`;
        
        if (count > 500) {
            counter.style.color = '#e74c3c';
        } else {
            counter.style.color = '#666';
        }
    });
}document.querySelectorAll('.confidence-fill').forEach(el => {
    const width = el.dataset.width;
    if (width) {
        el.style.width = width + '%';
        el.textContent = width + '%'; // if you want the text inside
    }
});