document.addEventListener('DOMContentLoaded', function () {
    const inputs = document.querySelectorAll('.target-drop-input');

    inputs.forEach(input => {
        input.addEventListener('change', function () {
            const stockId = this.dataset.id;
            const newValue = this.value;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            // Visual feedback - saving
            this.style.borderColor = '#238636';
            this.style.opacity = '0.7';

            fetch(`/stock/${stockId}/update-target/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `target_drop=${newValue}`
            })
                .then(response => {
                    if (response.ok) {
                        // Success feedback
                        this.style.borderColor = '#238636';
                        this.style.opacity = '1';
                        // Optional: flash a success message
                    } else {
                        // Error feedback
                        this.style.borderColor = '#da3633';
                        alert('Failed to save. Please try again.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    this.style.borderColor = '#da3633';
                });
        });
    });
});
