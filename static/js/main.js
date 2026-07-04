// Frontend Interactivity Helpers

document.addEventListener('DOMContentLoaded', () => {
    // 1. Dismiss Alert Functionality
    const alertCloses = document.querySelectorAll('.close-alert');
    alertCloses.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const alert = e.target.closest('.alert');
            if (alert) {
                alert.style.transition = 'all 0.3s ease';
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-10px)';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        });
    });

    // 2. Safe Delete Confirmations
    const deleteButtons = document.querySelectorAll('.btn-danger, .delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            // Check if it's a form submit button or direct link
            const confirmMsg = button.getAttribute('data-confirm') || 'Are you sure you want to delete this record? This action cannot be undone.';
            if (!confirm(confirmMsg)) {
                e.preventDefault();
            }
        });
    });

    // 3. Simple Modal Helpers (if needed)
    window.openModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
        }
    };

    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    };

    // Close modal if clicked outside content
    const modalBackdrops = document.querySelectorAll('.modal-backdrop');
    modalBackdrops.forEach(backdrop => {
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) {
                backdrop.style.display = 'none';
            }
        });
    });
});
