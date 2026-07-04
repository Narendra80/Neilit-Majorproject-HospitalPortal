document.addEventListener('DOMContentLoaded', () => {
    // 1. Dark Mode / Light Mode Toggle with LocalStorage
    const themeToggleBtn = document.getElementById('themeToggle');
    const htmlElement = document.documentElement;

    const savedTheme = localStorage.getItem('hospital_portal_theme') || 'dark';
    htmlElement.setAttribute('data-bs-theme', savedTheme);
    updateThemeIcon(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            htmlElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('hospital_portal_theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        if (!themeToggleBtn) return;
        if (theme === 'dark') {
            themeToggleBtn.innerHTML = '<i class="bi bi-sun-fill text-warning"></i> <span>Light Mode</span>';
        } else {
            themeToggleBtn.innerHTML = '<i class="bi bi-moon-stars-fill text-primary"></i> <span>Dark Mode</span>';
        }
    }

    // 2. Dynamic Doctor Filter (Instant department filtering without reload)
    const filterButtons = document.querySelectorAll('.filter-btn[data-department]');
    const doctorCards = document.querySelectorAll('.doctor-card-item');

    if (filterButtons.length > 0 && doctorCards.length > 0) {
        filterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                // Remove active from all buttons
                filterButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                const targetDept = btn.getAttribute('data-department');

                doctorCards.forEach(card => {
                    const cardDept = card.getAttribute('data-dept');
                    if (targetDept === 'ALL' || cardDept === targetDept) {
                        card.style.display = '';
                        card.style.opacity = '0';
                        setTimeout(() => {
                            card.style.transition = 'opacity 0.3s ease';
                            card.style.opacity = '1';
                        }, 50);
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    }

    // 3. Interactive Slot Selector for Appointment Booking
    const slotContainer = document.getElementById('slotContainer');
    const doctorSelect = document.getElementById('doctorSelect');
    const dateInput = document.getElementById('dateInput');
    const hiddenSlotInput = document.getElementById('selectedTimeSlot');

    if (slotContainer && doctorSelect && dateInput) {
        const fetchBookedSlots = async () => {
            const docId = doctorSelect.value;
            const dateVal = dateInput.value;

            if (!docId || !dateVal) return;

            // Reset selection
            if (hiddenSlotInput) hiddenSlotInput.value = '';
            
            try {
                const response = await fetch(`/api/booked-slots/?doctor_id=${docId}&date=${dateVal}`);
                const data = await response.json();
                const bookedSlots = data.booked_slots || [];

                const slotButtons = slotContainer.querySelectorAll('.slot-btn');
                slotButtons.forEach(btn => {
                    const slotTime = btn.getAttribute('data-slot');
                    btn.classList.remove('selected');
                    if (bookedSlots.includes(slotTime)) {
                        btn.classList.add('booked');
                        btn.setAttribute('title', 'Slot already booked');
                    } else {
                        btn.classList.remove('booked');
                        btn.removeAttribute('title');
                    }
                });
            } catch (err) {
                console.error("Error fetching slot availability:", err);
            }
        };

        doctorSelect.addEventListener('change', fetchBookedSlots);
        dateInput.addEventListener('change', fetchBookedSlots);

        // Slot click handler
        slotContainer.addEventListener('click', (e) => {
            const btn = e.target.closest('.slot-btn');
            if (!btn || btn.classList.contains('booked')) return;

            const allSlots = slotContainer.querySelectorAll('.slot-btn');
            allSlots.forEach(s => s.classList.remove('selected'));

            btn.classList.add('selected');
            if (hiddenSlotInput) {
                hiddenSlotInput.value = btn.getAttribute('data-slot');
            }
        });

        // Initial fetch on page load if values exist
        if (doctorSelect.value && dateInput.value) {
            fetchBookedSlots();
        }
    }
});
