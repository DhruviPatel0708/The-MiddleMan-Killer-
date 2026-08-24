/**
 * THE MIDDLEMAN KILLER - Live Auction Simulation Engine
 */

window.MKAuction = {
    timeLeft: 161, // 00:02:41
    currentBid: 4820,
    timerInterval: null,
    bidsStream: [],

    initAuction() {
        this.bidsStream = [...window.MKData.bidsHistory];
        this.startTimer();
        this.renderBids();
        this.startAutoBiddingSimulator();
    },

    startTimer() {
        if (this.timerInterval) clearInterval(this.timerInterval);

        const minEl = document.getElementById('auctionMin');
        const secEl = document.getElementById('auctionSec');

        this.timerInterval = setInterval(() => {
            if (this.timeLeft > 0) {
                this.timeLeft--;
                const mins = Math.floor(this.timeLeft / 60).toString().padStart(2, '0');
                const secs = (this.timeLeft % 60).toString().padStart(2, '0');

                if (minEl) minEl.textContent = mins;
                if (secEl) secEl.textContent = secs;
            } else {
                clearInterval(this.timerInterval);
                if (minEl) minEl.textContent = "00";
                if (secEl) secEl.textContent = "00";
                if (window.MKApp) window.MKApp.notify('AUCTION CLOSED!', 'Final Sold Price: ₹' + this.currentBid + '/Q to Adani Wilmar');
            }
        }, 1000);
    },

    renderBids() {
        const streamContainer = document.getElementById('bidsStreamFeed');
        if (!streamContainer) return;

        streamContainer.innerHTML = this.bidsStream.map((bid, index) => `
            <div class="bid-item-row ${index === 0 ? 'pulse-bid' : ''}">
                <div>
                    <div class="bid-buyer-name">${bid.buyer}</div>
                    <small style="color: var(--text-muted);">${bid.time}</small>
                </div>
                <div class="bid-amount-tag">₹${bid.amount.toLocaleString()}/Q</div>
            </div>
        `).join('');

        const currentBidEl = document.getElementById('liveAuctionPrice');
        if (currentBidEl) {
            currentBidEl.textContent = `₹${this.currentBid.toLocaleString()}/Q`;
        }
    },

    placeUserBid(amount) {
        if (amount <= this.currentBid) {
            if (window.MKApp) window.MKApp.notify('BID ERROR', 'Your bid must be higher than ₹' + this.currentBid, 'orange');
            return false;
        }

        this.currentBid = amount;
        this.bidsStream.unshift({
            id: Date.now(),
            buyer: "Rajesh Patel (Farmer Self-Bid/Verified)",
            amount: amount,
            time: "Just now",
            status: "Leading"
        });

        this.renderBids();

        // Visual FX
        const heroBox = document.querySelector('.auction-hero-box');
        if (heroBox) {
            heroBox.classList.add('pulse-bid');
            setTimeout(() => heroBox.classList.remove('pulse-bid'), 1000);
        }

        if (window.MKApp) {
            window.MKApp.notify('BID PLACED SUCCESS!', `You lead the auction at ₹${amount.toLocaleString()}/Q`, 'green');
            window.MKApp.closeModal('bidModal');
        }
        return true;
    },

    startAutoBiddingSimulator() {
        // Randomly simulate competing bids every 15-25 seconds
        setInterval(() => {
            if (this.timeLeft > 10 && Math.random() > 0.4) {
                const inc = Math.floor(Math.random() * 4 + 1) * 20;
                this.currentBid += inc;
                const buyers = ["Patanjali Organics", "Godrej Agrovet", "CargoAgri India", "Gujarat State Coop"];
                const randomBuyer = buyers[Math.floor(Math.random() * buyers.length)];

                this.bidsStream.unshift({
                    id: Date.now(),
                    buyer: `${randomBuyer} (Buyer #${Math.floor(Math.random() * 8000 + 1000)})`,
                    amount: this.currentBid,
                    time: "Just now",
                    status: "Leading"
                });

                if (this.bidsStream.length > 8) this.bidsStream.pop();
                this.renderBids();

                if (window.MKApp) {
                    window.MKApp.notify('NEW HIGHER BID!', `₹${this.currentBid}/Q placed by ${randomBuyer}`, 'gold');
                }
            }
        }, 18000);
    }
};
