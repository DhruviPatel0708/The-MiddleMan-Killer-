/**
 * THE MIDDLEMAN KILLER - Auth Validation, Registration Wizard & Dashboard Logic
 * STRICT 10 SUPPORTED CROPS & I18N SUPPORT
 */

window.MKDashboard = {
    currentWizardStep: 1,
    regRole: 'farmer',
    regStep: 1,
    otpTimer: null,
    otpTimeLeft: 29,

    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    },

    validateIndianMobile(mobile) {
        const clean = String(mobile).replace(/[\s\-\+]/g, '');
        return /^(91)?[6-9]\d{9}$/.test(clean);
    },

    evaluatePasswordStrength(password) {
        let score = 0;
        if (password.length >= 8) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^A-Za-z0-9]/.test(password)) score++;

        const requirements = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            number: /[0-9]/.test(password),
            special: /[^A-Za-z0-9]/.test(password)
        };

        return { score, requirements };
    },

    selectRegRole(role) {
        this.regRole = role;
        document.querySelectorAll('.role-card-btn').forEach(btn => btn.classList.remove('active'));
        const activeBtn = document.getElementById(`roleCardBtn_${role}`);
        if (activeBtn) activeBtn.classList.add('active');

        const farmerFields = document.getElementById('farmerRegFields');
        const buyerFields = document.getElementById('buyerRegFields');

        if (farmerFields && buyerFields) {
            if (role === 'farmer') {
                farmerFields.style.display = 'block';
                buyerFields.style.display = 'none';
            } else {
                farmerFields.style.display = 'none';
                buyerFields.style.display = 'block';
            }
        }
    },

    nextRegStep() {
        if (this.regStep === 1) {
            this.regStep = 2;
            this.updateRegWizardUI();
        } else if (this.regStep === 2) {
            if (this.regRole === 'farmer') {
                const name = document.getElementById('regFarmerName')?.value.trim();
                if (!name) {
                    window.MKApp.notify('REGISTRATION ERROR', 'Please enter your full name.', 'orange');
                    return;
                }
            } else {
                const company = document.getElementById('regBuyerCompany')?.value.trim();
                if (!company) {
                    window.MKApp.notify('REGISTRATION ERROR', 'Please enter your company / business name.', 'orange');
                    return;
                }
            }
            this.regStep = 3;
            this.updateRegWizardUI();
        } else if (this.regStep === 3) {
            const email = document.getElementById('regEmail')?.value.trim();
            const mobile = document.getElementById('regMobile')?.value.trim();

            if (!email || !this.validateEmail(email)) {
                window.MKApp.notify('EMAIL ERROR', 'Please enter a valid email address.', 'orange');
                return;
            }

            if (!mobile || !this.validateIndianMobile(mobile)) {
                window.MKApp.notify('MOBILE ERROR', 'Enter a valid 10-digit Indian mobile number.', 'orange');
                return;
            }

            this.regStep = 4;
            this.updateRegWizardUI();
        } else if (this.regStep === 4) {
            const pwd = document.getElementById('regPassword')?.value;
            const confirmPwd = document.getElementById('regConfirmPassword')?.value;

            const { score } = this.evaluatePasswordStrength(pwd || '');

            if (score < 2) {
                window.MKApp.notify('PASSWORD WEAK', 'Password must be at least 8 characters with numbers & uppercase.', 'orange');
                return;
            }

            if (pwd !== confirmPwd) {
                window.MKApp.notify('PASSWORD MISMATCH', 'Passwords do not match.', 'orange');
                return;
            }

            this.regStep = 5;
            this.updateRegWizardUI();
            this.startOtpTimer();
        } else if (this.regStep === 5) {
            const otpInputs = document.querySelectorAll('.otp-digit-input');
            let otpVal = '';
            otpInputs.forEach(i => otpVal += i.value);

            if (otpVal.length < 6) {
                window.MKApp.notify('OTP ERROR', 'Please enter the 6-digit verification code.', 'orange');
                return;
            }

            this.regStep = 6;
            this.updateRegWizardUI();
            if (this.otpTimer) clearInterval(this.otpTimer);

            setTimeout(() => {
                this.completeRegistration();
            }, 1800);
        }
    },

    prevRegStep() {
        if (this.regStep > 1 && this.regStep < 6) {
            this.regStep--;
            this.updateRegWizardUI();
        }
    },

    updateRegWizardUI() {
        for (let i = 1; i <= 6; i++) {
            const stepEl = document.getElementById(`regStepView${i}`);
            if (stepEl) stepEl.style.display = i === this.regStep ? 'block' : 'none';
        }
    },

    startOtpTimer() {
        this.otpTimeLeft = 29;
        const timerEl = document.getElementById('otpTimerText');

        if (this.otpTimer) clearInterval(this.otpTimer);
        this.otpTimer = setInterval(() => {
            if (this.otpTimeLeft > 0) {
                this.otpTimeLeft--;
                if (timerEl) timerEl.textContent = `Resend in 00:${this.otpTimeLeft.toString().padStart(2, '0')}`;
            } else {
                clearInterval(this.otpTimer);
                if (timerEl) timerEl.textContent = 'Resend OTP Now';
            }
        }, 1000);
    },

    resendOtp() {
        window.MKApp.notify('OTP RESENT', 'A new 6-digit code was sent to your contact.', 'gold');
        this.startOtpTimer();
    },

    completeRegistration() {
        const name = this.regRole === 'farmer' 
            ? (document.getElementById('regFarmerName')?.value || 'Registered Farmer')
            : (document.getElementById('regBuyerCompany')?.value || 'Registered Buyer');
        const email = document.getElementById('regEmail')?.value || 'user@middlemankiller.com';
        const mobile = document.getElementById('regMobile')?.value || '9876543210';
        const pwd = document.getElementById('regPassword')?.value || 'Farmer@123';

        const userObj = {
            name: name,
            email: email,
            mobile: mobile,
            password: pwd,
            role: this.regRole,
            verified: true,
            avatar: this.regRole === 'farmer' ? '🌱' : '🏢'
        };

        const registered = JSON.parse(localStorage.getItem('mk_registered_accounts') || '[]');
        registered.push(userObj);
        localStorage.setItem('mk_registered_accounts', JSON.stringify(registered));

        window.MKApp.loginUserSession(userObj);
        window.MKApp.closeModal('authModal');
        window.MKApp.notify('ACCOUNT CREATED!', `Welcome, ${name}!`, 'green');
    },

    // Crop Registration Wizard
    initWizard() {
        this.currentWizardStep = 1;
        this.updateWizardUI();
    },

    nextWizardStep() {
        if (this.currentWizardStep === 5) {
            window.MKAI.startCropScan(() => {
                this.currentWizardStep++;
                this.updateWizardUI();
            });
            return;
        }

        if (this.currentWizardStep < 7) {
            this.currentWizardStep++;
            this.updateWizardUI();
        } else {
            this.publishCropListing();
        }
    },

    prevWizardStep() {
        if (this.currentWizardStep > 1) {
            this.currentWizardStep--;
            this.updateWizardUI();
        }
    },

    updateWizardUI() {
        for (let i = 1; i <= 7; i++) {
            const stepEl = document.getElementById(`wizardStep${i}`);
            const indEl = document.getElementById(`stepInd${i}`);

            if (stepEl) stepEl.style.display = i === this.currentWizardStep ? 'block' : 'none';
            if (indEl) {
                if (i === this.currentWizardStep) indEl.className = 'wizard-step-indicator active';
                else if (i < this.currentWizardStep) indEl.className = 'wizard-step-indicator completed';
                else indEl.className = 'wizard-step-indicator';
            }
        }
    },

    publishCropListing() {
        const title = document.getElementById('regCropTitle')?.value || "Fresh Wheat Batch";
        const selectedCrop = document.getElementById('regCropSelect')?.value || "Wheat";
        const quantity = document.getElementById('regCropQty')?.value || "200 Quintals";

        const newCrop = {
            id: `crop-${Date.now()}`,
            title: title,
            cropName: selectedCrop,
            farmer: "Rajesh Patel",
            location: "Anand, Gujarat",
            quantity: quantity,
            grade: "Premium Grade A+",
            qualityScore: 94,
            fairPrice: "₹2,835/Q",
            currentBid: "₹2,835/Q",
            harvestDate: "Today",
            verified: true,
            isAuction: false,
            image: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=800&q=80",
            category: "Grains"
        };

        window.MKData.crops.unshift(newCrop);

        if (window.MKApp) {
            window.MKApp.notify('CROP PUBLISHED!', `${title} is now live on the marketplace.`, 'green');
            window.MKApp.closeModal('cropRegModal');
            window.MKApp.renderMarketplace();
        }
    },

    releaseEscrowFunds() {
        const stage4 = document.getElementById('escrowStage4');
        if (stage4) {
            stage4.className = 'escrow-stage-card completed';
            stage4.querySelector('.escrow-stage-num').textContent = '✓';
        }

        const balanceEl = document.getElementById('farmerEarningsVal');
        if (balanceEl) balanceEl.textContent = '₹8.24L';

        if (window.MKApp) {
            window.MKApp.notify('ESCROW RELEASED!', '₹3,42,000 transferred directly to Bank A/C', 'gold');
        }
    }
};
