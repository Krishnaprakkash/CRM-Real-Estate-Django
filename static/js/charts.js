// ===== CHART ANIMATIONS FOR HOME PAGE =====

document.addEventListener('DOMContentLoaded', function () {
    animateSemiCircleProgressBars();
    animateHalfDonutChart();
});

// Animate semi-circle progress bars
function animateSemiCircleProgressBars() {
    document.querySelectorAll('.semi-circle-wrapper').forEach(wrapper => {
        const percentage = parseFloat(wrapper.dataset.percentage) || 0;
        const progressBar = wrapper.querySelector('.progress-bar');
        const percentageValue = wrapper.querySelector('.percentage-value');

        if (progressBar) {
            // Total arc length for semi-circle
            const totalLength = 251.2;
            const dashLength = (percentage / 100) * totalLength;

            // Start with stroke hidden
            progressBar.style.strokeDasharray = `0 ${totalLength}`;

            // Animate after a short delay
            setTimeout(() => {
                progressBar.style.transition = 'stroke-dasharray 1.5s ease-out';
                progressBar.style.strokeDasharray = `${dashLength} ${totalLength}`;

                // Animate the percentage text
                animateValue(percentageValue, 0, percentage, 1500, '%');
            }, 200);
        }
    });
}

// Animate half donut chart
function animateHalfDonutChart() {
    const donutContainer = document.getElementById('listings-donut');
    if (!donutContainer) return;

    const leads = parseInt(donutContainer.dataset.leads) || 0;
    const opps = parseInt(donutContainer.dataset.opportunities) || 0;
    const sales = parseInt(donutContainer.dataset.sales) || 0;
    const total = leads + opps + sales;

    if (total === 0) return;

    const circumference = 251.2;

    const leadsPercent = leads / total;
    const oppsPercent = opps / total;
    const salesPercent = sales / total;

    const leadsArc = leadsPercent * circumference;
    const oppsArc = oppsPercent * circumference;
    const salesArc = salesPercent * circumference;

    const leadsPath = document.getElementById('leads-arc');
    const oppsPath = document.getElementById('opps-arc');
    const salesPath = document.getElementById('sales-arc');

    setTimeout(() => {
        // Leads: starts at 0
        if (leadsPath) {
            leadsPath.style.strokeDasharray = `${leadsArc} ${circumference}`;
            leadsPath.style.strokeDashoffset = '0';
        }

        // Opps: starts after leads
        if (oppsPath) {
            oppsPath.style.strokeDasharray = `${oppsArc} ${circumference}`;
            oppsPath.style.strokeDashoffset = `-${leadsArc}`;
        }

        // Sales: starts after leads + opps
        if (salesPath) {
            salesPath.style.strokeDasharray = `${salesArc} ${circumference}`;
            salesPath.style.strokeDashoffset = `-${leadsArc + oppsArc}`;
        }
    }, 100);
}

// Generic value animation function
function animateValue(element, start, end, duration, suffix) {
    const startTime = performance.now();
    const hasDecimal = end % 1 !== 0;

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Ease-out cubic for smooth deceleration
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = start + (end - start) * easeOut;

        if (hasDecimal) {
            element.textContent = current.toFixed(1) + suffix;
        } else {
            element.textContent = Math.round(current) + suffix;
        }

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}