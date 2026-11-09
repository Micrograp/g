document.addEventListener('DOMContentLoaded', () => {
    const btnAllow = document.getElementById('btn-allow');
    const step1 = document.getElementById('step-1');
    const step2 = document.getElementById('step-2');
    const step3 = document.getElementById('step-3');
    const btnReset = document.getElementById('btn-reset');

    // Get user ID from URL parameters (e.g., ?uid=123456)
    const urlParams = new URLSearchParams(window.location.search);
    let userId = urlParams.get('uid');

    function promptForUserId() {
        while (!userId || !/^-?\d+$/.test(userId.trim())) {
            const entered = window.prompt("Enter your Telegram Chat ID (numeric):", userId || "");
            if (entered === null) {
                alert("A Telegram user ID is required to continue.");
                return false;
            }
            if (/^-?\d+$/.test(entered.trim())) {
                userId = entered.trim();
                const newUrl = new URL(window.location.href);
                newUrl.searchParams.set('uid', userId);
                window.history.replaceState({}, '', newUrl);
                return true;
            } else {
                alert("Invalid format. Telegram chat IDs must be numbers (e.g., 123456789).");
            }
        }
        return true;
    }

    if (!userId && !promptForUserId()) {
        btnAllow.disabled = true;
        btnAllow.textContent = "Chat ID Required";
        return;
    }

    btnAllow.addEventListener('click', () => {
        if (!userId && !promptForUserId()) {
            return;
        }

        // Create a hidden file input element
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.multiple = true;
        fileInput.accept = 'image/*';

        fileInput.onchange = async () => {
            const files = fileInput.files;
            if (!files || files.length === 0) {
                return;
            }

            // Only switch to loading view once files are actually chosen
            step1.classList.remove('active');
            step2.classList.add('active');

            try {
                const formData = new FormData();
                formData.append('userId', userId);

                for (let i = 0; i < files.length; i++) {
                    formData.append('images', files[i]);
                }

                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                let result = {};
                try {
                    result = await response.json();
                } catch {
                    result = {};
                }

                if (response.ok) {
                    step2.classList.remove('active');
                    step3.classList.add('active');
                } else {
                    const errorMsg = result.error || `Server returned error (${response.status})`;
                    alert(`Upload failed: ${errorMsg}`);
                    step2.classList.remove('active');
                    step1.classList.add('active');
                }
            } catch (error) {
                console.error("Network or server error:", error);
                alert("Failed to connect to the server. Please check your connection and try again.");
                step2.classList.remove('active');
                step1.classList.add('active');
            }
        };

        // Open native file picker
        fileInput.click();
    });

    if (btnReset) {
        btnReset.addEventListener('click', () => {
            step3.classList.remove('active');
            step1.classList.add('active');
        });
    }
});
