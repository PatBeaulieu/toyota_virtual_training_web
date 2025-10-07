// Configuration
const TRAINING_TIMEZONE = 'America/Toronto'; // EST/EDT
const LINK_EXPIRY_MINUTES = 30;
const UPDATE_INTERVAL = 30000; // 30 seconds

// Cache for performance optimization
let cachedTrainingSessions = [];
let cachedDOMElements = {
    estDisplay: null,
    localDisplay: null
};

// Utility functions
function formatCountdown(ms) {
    const totalMinutes = Math.floor(ms / 60000);
    const days = Math.floor(totalMinutes / (60 * 24));
    const hours = Math.floor((totalMinutes % (60 * 24)) / 60);
    const minutes = totalMinutes % 60;

    const parts = [];
    if (window.IS_QUEBEC) {
        if (days > 0) parts.push(`${days}j`);
        if (hours > 0) parts.push(`${hours}h`);
        if (minutes > 0 || parts.length === 0) parts.push(`${minutes}m`);
        return parts.join(' ');
    } else {
        if (days > 0) parts.push(`${days}d`);
        if (hours > 0) parts.push(`${hours}h`);
        if (minutes > 0 || parts.length === 0) parts.push(`${minutes}m`);
        return parts.join(' ');
    }
}

// Reliable Eastern DateTime creation using ISO strings
function createEasternDateTime(dateStr, timeStr) {
    try {
        const [hour, minute = 0] = timeStr.split(':').map(Number);

        // For September 2025, Eastern is in EDT (UTC-4)
        // Create ISO string with EDT offset
        const isoString = `${dateStr}T${hour.toString().padStart(2,'0')}:${minute.toString().padStart(2,'0')}:00-04:00`;

        return new Date(isoString);

    } catch (error) {
        console.error('Error creating Eastern date:', error);
        return null;
    }
}

// Cache training data on initialization for better performance
function cacheTrainingData() {
    const rows = document.querySelectorAll('tr[data-date]');

    cachedTrainingSessions = Array.from(rows).map((row) => {
        const dateStr = row.getAttribute('data-date');
        const timeStr = row.getAttribute('data-time');
        const trainingStart = createEasternDateTime(dateStr, timeStr);

        // Cache DOM elements for each row
        const statusCell = row.querySelector('.status-cell');
        const linkCell = row.querySelector('.link-cell');
        const localTimeCell = row.querySelector('.local-time');

        // Store original link if it exists
        const originalLink = linkCell?.querySelector('a')?.href || '';
        if (originalLink) {
            linkCell.setAttribute('data-original-link', originalLink);
        }

        return {
            row,
            dateStr,
            timeStr,
            trainingStart,
            trainingEnd: trainingStart ? new Date(trainingStart.getTime() + LINK_EXPIRY_MINUTES * 60000) : null,
            statusCell,
            linkCell,
            localTimeCell,
            originalLink,
            localTimeFormatted: null // Will cache this after first calculation
        };
    });

    console.log(`Cached ${cachedTrainingSessions.length} training sessions`);
}

// Update each training row using cached data
function updateTrainingStatus() {
    const now = new Date();

    cachedTrainingSessions.forEach((session) => {
        try {
            const {
                row, trainingStart, trainingEnd, statusCell,
                linkCell, localTimeCell, originalLink
            } = session;

            if (!trainingStart || !statusCell || !linkCell || !localTimeCell) {
                if (statusCell) statusCell.innerHTML = '<span class="error-message">Data error</span>';
                return;
            }

            // Cache local time formatting (only calculate once)
            if (!session.localTimeFormatted) {
                // Convert Eastern time to user's actual local timezone
                const locale = window.IS_QUEBEC ? 'fr-CA' : 'en-US';
                const opts = {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    timeZoneName: 'short'
                };
                if (window.IS_QUEBEC) {
                    // Force 24-hour in French locale
                    opts.hour12 = false;
                    opts.hourCycle = 'h23';
                }
                session.localTimeFormatted = trainingStart.toLocaleString(locale, opts);
                localTimeCell.textContent = session.localTimeFormatted;
            }

            // Remove all training-related classes efficiently
            row.className = row.className.replace(/\btraining-\w+\b/g, '');

            if (now < trainingStart) {
                const countdown = formatCountdown(trainingStart - now);
                statusCell.textContent = window.IS_QUEBEC ? `Commence dans ${countdown}` : `Starts in ${countdown}`;
                row.classList.add('training-upcoming');

                // Restore link if it was removed
                if (originalLink && linkCell.innerHTML.includes('expired')) {
                    const lbl = window.IS_QUEBEC ? 'Joindre la Réunion' : 'Link';
                    linkCell.innerHTML = `<a href="${originalLink}" target="_blank">${lbl}</a>`;
                }
            } else if (now >= trainingStart && now <= trainingEnd) {
                const remainingTime = formatCountdown(trainingEnd - now);
                statusCell.textContent = window.IS_QUEBEC ? `En cours - reste ${remainingTime}` : `Active - ${remainingTime} remaining`;
                row.classList.add('training-active');
            } else {
                statusCell.textContent = window.IS_QUEBEC ? 'Session terminée' : 'Session ended';
                row.classList.add('training-ended');
                if (!linkCell.innerHTML.includes('expired')) {
                    linkCell.innerHTML = window.IS_QUEBEC ? '<span class="link-expired">Lien expiré</span>' : '<span class="link-expired">Link expired</span>';
                }
            }
        } catch (error) {
            console.error('Error processing training session:', error);
            if (session.statusCell) {
                session.statusCell.innerHTML = '<span class="error-message">Processing error</span>';
            }
        }
    });
}

// Update top clock displays with cached DOM elements
function updateDateTime() {
    const now = new Date();

    // Cache DOM elements on first run
    if (!cachedDOMElements.estDisplay) {
        cachedDOMElements.estDisplay = document.getElementById('dateTimeDisplay');
        cachedDOMElements.localDisplay = document.getElementById('localTime');
    }

    // Eastern time display
    if (cachedDOMElements.estDisplay) {
        const estOptions = {
            timeZone: TRAINING_TIMEZONE,
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        };
        const estLocale = window.IS_QUEBEC ? 'fr-CA' : 'en-US';
        const tzLabel = window.IS_QUEBEC ? 'HAE' : 'EST/EDT';
        cachedDOMElements.estDisplay.textContent = now.toLocaleString(estLocale, estOptions) + ` (${tzLabel})`;
    }

    // Local browser time display
    if (cachedDOMElements.localDisplay) {
        const localOptions = {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            timeZoneName: 'short'
        };
        const localLocale = window.IS_QUEBEC ? 'fr-CA' : 'en-US';
        cachedDOMElements.localDisplay.textContent = now.toLocaleString(localLocale, localOptions);
    }
}

function initialize() {
    console.log('Initializing Eastern Time training website...');

    try {
        // Cache all training data once
        cacheTrainingData();

        // Initial updates
        updateDateTime();
        updateTrainingStatus();

        // Set up intervals
        setInterval(updateDateTime, 1000);
        setInterval(updateTrainingStatus, UPDATE_INTERVAL);

        console.log('Training website initialized successfully (Eastern Time)');
    } catch (error) {
        console.error('Initialization error:', error);
    }
}

// Optimized DOM ready check
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}