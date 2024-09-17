document.addEventListener('DOMContentLoaded', () => {
    const moonImage = document.getElementById('moon-image');
    const moonDescription = document.getElementById('moon-description');

    // Map moon phases to emojis
    const moonPhaseEmojis = {
        "New Moon": "🌑",
        "Waxing Crescent": "🌒",
        "First Quarter": "🌓",
        "Waxing Gibbous": "🌔",
        "Full Moon": "🌕",
        "Waning Gibbous": "🌖",
        "Last Quarter": "🌗",
        "Waning Crescent": "🌘"
    };

    async function fetchMoonPhase(date) {
        try {
            const response = await fetch(`/api/moon-phase?date=${date}`);
            const data = await response.json();

            // Get moon phase emoji
            const moonPhase = data.current_phase || 'No moon phase available';
            const moonEmoji = moonPhaseEmojis[moonPhase] || '🌑';  // Default to New Moon if phase is unknown

            moonImage.textContent = moonEmoji;  // Display emoji
            moonDescription.innerHTML = `
                <p>Current Moon Phase: ${moonPhase}</p>
                <p>Fractional Illumination: ${data.fractional_illumination || 'N/A'}</p>
                <p>Moon Rise Time: ${data.moon_rise_time || 'N/A'}</p>
                <p>Moon Set Time: ${data.moon_set_time || 'N/A'}</p>
                <p>Moon Transit Time: ${data.moon_transit_time || 'N/A'}</p>
            `;
        } catch (error) {
            console.error('Error fetching moon phase data:', error);
            moonDescription.textContent = 'Failed to load moon phase data.';
        }
    }

    // Fetch moon phase for today's date
    const todayDate = new Date().toISOString().split('T')[0];  // Get today's date in YYYY-MM-DD format
    fetchMoonPhase(todayDate);
});
