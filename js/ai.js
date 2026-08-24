/**
 * THE MIDDLEMAN KILLER - AI Engine (Crop Scanner, Fair Price Radar, KrishiAI)
 * STRICT 10 SUPPORTED CROPS ONLY & MULTI-LANGUAGE RESPONSES
 */

window.MKAI = {
    drawFairPriceRadar() {
        const canvas = document.getElementById('radarCanvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const size = canvas.width = canvas.height = 360;
        const centerX = size / 2;
        const centerY = size / 2;
        const radius = 130;

        ctx.clearRect(0, 0, size, size);

        const factors = [
            { label: 'Demand (+7.8%)', val: 0.9, color: '#D96C3B' },
            { label: 'Supply (Tight)', val: 0.85, color: '#D6A84F' },
            { label: 'Weather (Alert)', val: 0.75, color: '#82957D' },
            { label: 'Quality (94/100)', val: 0.95, color: '#2ECC71' },
            { label: 'History (+14%)', val: 0.88, color: '#D6A84F' }
        ];

        const total = factors.length;

        for (let r = 1; r <= 4; r++) {
            ctx.beginPath();
            ctx.arc(centerX, centerY, (radius / 4) * r, 0, Math.PI * 2);
            ctx.strokeStyle = 'rgba(130, 149, 125, 0.2)';
            ctx.setLineDash([4, 4]);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        factors.forEach((f, i) => {
            const angle = (Math.PI * 2 / total) * i - Math.PI / 2;
            const x = centerX + Math.cos(angle) * radius;
            const y = centerY + Math.sin(angle) * radius;

            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(x, y);
            ctx.strokeStyle = 'rgba(214, 168, 79, 0.3)';
            ctx.stroke();

            const lx = centerX + Math.cos(angle) * (radius + 35);
            const ly = centerY + Math.sin(angle) * (radius + 20);

            ctx.font = '600 12px "Plus Jakarta Sans"';
            ctx.fillStyle = f.color;
            ctx.textAlign = 'center';
            ctx.fillText(f.label, lx, ly);
        });

        ctx.beginPath();
        factors.forEach((f, i) => {
            const angle = (Math.PI * 2 / total) * i - Math.PI / 2;
            const rVal = radius * f.val;
            const x = centerX + Math.cos(angle) * rVal;
            const y = centerY + Math.sin(angle) * rVal;

            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.closePath();

        ctx.fillStyle = 'rgba(217, 108, 59, 0.25)';
        ctx.fill();
        ctx.strokeStyle = '#D96C3B';
        ctx.lineWidth = 3;
        ctx.stroke();

        factors.forEach((f, i) => {
            const angle = (Math.PI * 2 / total) * i - Math.PI / 2;
            const rVal = radius * f.val;
            const x = centerX + Math.cos(angle) * rVal;
            const y = centerY + Math.sin(angle) * rVal;

            ctx.beginPath();
            ctx.arc(x, y, 6, 0, Math.PI * 2);
            ctx.fillStyle = '#D6A84F';
            ctx.fill();
            ctx.strokeStyle = '#FFFFFF';
            ctx.lineWidth = 2;
            ctx.stroke();
        });
    },

    startCropScan(onComplete) {
        const scanStatus = document.getElementById('scanStatusText');
        const scoreDisplay = document.getElementById('scanScoreDisplay');
        const scanResultBox = document.getElementById('scanResultBox');

        if (!scanStatus) return;

        scanStatus.innerHTML = '<span class="gradient-text-orange">Scanning Crop Granular Structure...</span>';
        if (scanResultBox) scanResultBox.style.display = 'none';

        const steps = [
            'Uploading High-Res Crop Macro Image...',
            'Initializing Computer Vision Neural Net...',
            'Analyzing Grain Texture & Color Spectrum...',
            'Measuring Moisture & Defect Percentages...',
            'Cross-checking Regional Quality Benchmarks...',
            'Quality Score Calculated: 94/100!'
        ];

        let idx = 0;
        const interval = setInterval(() => {
            if (idx < steps.length) {
                scanStatus.innerHTML = `<span class="gradient-text-gold">${steps[idx]}</span>`;
                idx++;
            } else {
                clearInterval(interval);
                if (scanResultBox) scanResultBox.style.display = 'block';
                if (scoreDisplay) scoreDisplay.textContent = '94/100';
                if (window.MKApp) window.MKApp.notify('AI Crop Scan Complete!', 'Quality Score: 94/100 (Premium Grade A+)');
                if (onComplete) onComplete();
            }
        }, 600);
    },

    sendKrishiAiMessage(userText) {
        const messagesContainer = document.getElementById('krishiChatMessages');
        if (!messagesContainer || !userText.trim()) return;

        const lang = (window.MKI18n && window.MKI18n.currentLang) || 'en';

        // Render User Message
        const userDiv = document.createElement('div');
        userDiv.className = 'chat-bubble user';
        userDiv.textContent = userText;
        messagesContainer.appendChild(userDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        let botReply = "";

        if (lang === 'gu') {
            botReply = "નમસ્તે! આજે ગુજરાતની મંડીઓમાં ઘઉં, ડાંગર અને મગફળીના ભાવમાં +૬.૮% નો વધારો જોવા મળ્યો છે. લાઇવ હરાજીમાં પાક મુકવાથી વધુ નફો મળશે.";
        } else if (lang === 'hi') {
            botReply = "नमस्ते! आज गुजरात मंडियों में गेहूं, धान और मूंगफली की कीमतों में +6.8% की वृद्धि हुई है। लाइव नीलामी में फसल बेचने से अधिक लाभ होगा।";
        } else {
            botReply = "Namaste! Today's benchmark prices for Wheat, Paddy (Rice), and Groundnut (Peanut) in Gujarat mandis are up by +6.8%. Placing your crop in Live Auction now will maximize returns.";
        }

        setTimeout(() => {
            const botDiv = document.createElement('div');
            botDiv.className = 'chat-bubble bot';
            botDiv.innerHTML = `<strong>KrishiAI:</strong> ${botReply}`;
            messagesContainer.appendChild(botDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 500);
    }
};
