/**
 * THE MIDDLEMAN KILLER - Internationalization (i18n) Dictionary & Engine
 * Supports: English (en), Gujarati (gu), Hindi (hi)
 */

window.MKI18n = {
    currentLang: localStorage.getItem('mk_language') || 'en',

    translations: {
        en: {
            // Brand & Navigation
            brandTitle: "THE MIDDLEMAN",
            brandSub: "KILLER",
            tagline: "Direct from Farm. Fair for Everyone.",
            navHome: "Home",
            navFarmerPortal: "Farmer Portal",
            navFairPrice: "Fair Price AI",
            navMarketplace: "Marketplace",
            navAuctions: "Live Auctions",
            navLogistics: "Logistics",
            navAdmin: "Admin Command",
            navLoginRegister: "Login / Register",
            navSellDirect: "Start Selling Directly",
            navExploreMarket: "Explore Marketplace",

            // Ticker & Headers
            tickerTitle: "LIVE MANDI PULSE",
            heroBadge: "AI-POWERED DIRECT AGRICULTURAL MARKETPLACE",
            heroTitle1: "KILL THE MIDDLEMAN.",
            heroTitle2: "EMPOWER THE FARMER.",
            heroSubtitle: "An AI-powered direct agricultural marketplace connecting farmers with verified buyers through fair pricing, transparent auctions, secure payments and intelligent logistics.",
            
            // Problem Section
            problemTag: "TRADITIONAL SUPPLY CHAIN VS MIDDLEMAN KILLER",
            problemTitle: "WHERE DOES THE FARMER'S MONEY GO?",
            problemSubtitle: "In the traditional agricultural chain, 5+ intermediaries drain up to 35% of the total crop value before reaching the end buyer.",
            tradChainTitle: "TRADITIONAL SUPPLY CHAIN (LEAKAGE)",
            farmer: "FARMER",
            trader: "LOCAL TRADER",
            wholesaler: "WHOLESALER",
            distributor: "DISTRIBUTOR",
            retailer: "RETAILER",
            buyer: "BUYER",
            leakageNotice: "⚠️ VALUE LEAKAGE TO MIDDLEMEN: ₹800 / QUINTAL (25% PROFIT DRAINED FROM FARMER)",

            // Pipeline Nodes
            nodeFarm: "🌱 FARM",
            nodeAiQuality: "🤖 AI QUALITY",
            nodeFairPrice: "💰 FAIR PRICE",
            nodeAuction: "🔴 AUCTION",
            nodeBuyer: "🤝 BUYER",
            nodeEscrow: "🔐 ESCROW",
            nodeLogistics: "🚚 LOGISTICS",
            nodeDelivery: "🏠 DELIVERY",

            // Farmer Dashboard
            farmerGreeting: "Good Morning 👋",
            farmerSubhead: "Your farm in Anand, Gujarat is currently performing +14% above regional benchmark.",
            btnRegisterCrop: "REGISTER NEW CROP",
            statTotalCrops: "Total Crops Registered",
            statActiveListings: "Active Listings",
            statCurrentEarnings: "Current Earnings",
            statPendingEscrow: "Pending Escrow",
            chartMarketTitle: "Market Intelligence & Price Trend (Anand Mandi)",
            trustScoreTitle: "FARMER TRUST SCORE",
            weatherAlertTitle: "AI WEATHER HARVEST ALERT — Anand & Kheda District",
            weatherAlertText: "Heavy rainfall (45mm+) predicted within 36 hours. Recommendation: Delay fresh harvesting by 12–18 hours to prevent grain moisture damage.",
            askKrishiAdvice: "Ask KrishiAI Advice",

            // AI Fair Price Radar
            radarTag: "ALGORITHMIC PRICING INTELLIGENCE",
            radarTitle: "AI FAIR PRICE RADAR ENGINE",
            radarSubtitle: "Algorithmic price determination evaluating real-time Mandi rates, regional crop supply, local weather impact, soil grade, and corporate demand.",
            currentMandiRate: "Current Traditional Mandi Rate:",
            aiFairBenchmark: "AI Calculated Fair Benchmark:",
            expectedAuctionRange: "Expected Auction Range:",
            btnApplyFairPrice: "Apply Fair Price to Marketplace",

            // Marketplace
            marketTag: "DIRECT AGRICULTURAL MARKETPLACE",
            marketTitle: "VERIFIED CROP LISTINGS",
            marketSubtitle: "Buy directly from certified farmers with AI quality reports, fair prices, and escrow safety.",
            filterAll: "ALL",
            btnPlaceBid: "Place Bid",
            btnBuyDirect: "Buy Direct",
            searchPlaceholder: "Search wheat, paddy, groundnut, location, farmer...",

            // Live Auction
            auctionTag: "REAL-TIME TRANSPARENT AUCTION",
            auctionTitle: "LIVE CROP AUCTION",
            auctionSubtitle: "Corporate buyers bidding transparently for premium quality verified crops.",
            spotlightItem: "SPOTLIGHT ITEM #AU-2849",
            startingPrice: "Starting Price",
            currentHighestBid: "Current Highest Bid",
            closingIn: "AUCTION CLOSING IN:",
            btnPlaceBidNow: "PLACE YOUR BID NOW",
            liveBidActivity: "LIVE BID ACTIVITY",

            // Logistics
            logisticsTag: "INTELLIGENT COLD-CHAIN LOGISTICS",
            logisticsTitle: "GUJARAT SHIPMENT TRACKING MAP",
            logisticsSubtitle: "Geo-fenced GPS route tracking across Gujarat hubs with temperature telemetry for guaranteed grain freshness.",
            vehicle: "Vehicle:",
            driver: "Driver:",
            estimatedEta: "Estimated ETA:",
            storageTemp: "Storage Temp:",
            humidity: "Humidity:",

            // Escrow
            escrowTag: "FINTECH ESCROW PROTECTION",
            escrowTitle: "SECURE SMART ESCROW VAULT",
            escrowSubtitle: "Funds are locked securely upon order placement and released automatically to the farmer upon verified geo-delivery.",
            step1PaymentLocked: "Step 01: Buyer Payment Locked",
            step2QualityVerified: "Step 02: AI Crop Quality Verified",
            step3GpsTelemetry: "Step 03: In-Transit GPS Telemetry",
            step4FarmerPayout: "Step 04: Instant Farmer Payout Release",
            btnSimulateRelease: "Simulate Delivery Release",

            // Admin
            adminTag: "SYSTEM COMMAND CENTER",
            adminTitle: "ADMIN PLATFORM INTELLIGENCE",
            adminSubtitle: "Real-time monitoring across Gujarat agricultural trade, platform volume & AI trust metrics.",
            statVerifiedFarmers: "Total Verified Farmers",
            statVerifiedBuyers: "Verified Buyers",
            statTotalVolume: "Total Direct Volume",
            statFraudScore: "AI Fraud Risk Score",
            regionalTableTitle: "Regional Trade & Fraud Monitor (Gujarat Hubs)",

            // Auth Modals & Wizard
            authSignIn: "Sign In",
            authCreateAccount: "Create Account",
            lblEmailOrMobile: "Email Address or Mobile Number",
            lblPassword: "Password",
            phEmailOrMobile: "Enter email or mobile number",
            phPassword: "Enter your password",
            btnSignInSubmit: "Sign In",
            lblRememberMe: "Remember Me",
            btnForgotPwd: "Forgot Password?",
            lblSelectRole: "Select Your Platform Role",
            roleFarmerTitle: "FARMER",
            roleFarmerDesc: "Sell crops directly, get fair prices & escrow payouts.",
            roleBuyerTitle: "BUYER",
            roleBuyerDesc: "Source quality crops directly from verified farms.",
            stepPersonalDetails: "PERSONAL / BUSINESS DETAILS",
            stepContactInfo: "CONTACT INFORMATION",
            stepPasswordSecurity: "PASSWORD & SECURITY",
            stepOtpVerify: "VERIFY YOUR ACCOUNT",
            otpNotice: "We've sent a 6-digit verification code to your registered contact.",
            btnVerifyAccount: "VERIFY & CREATE ACCOUNT",
            accountCreatedTitle: "ACCOUNT CREATED SUCCESSFULLY",
            accountCreatedSub: "Welcome to The Middleman Killer direct agricultural ecosystem!",
            
            // Logout
            logoutTitle: "LOG OUT?",
            logoutSub: "Are you sure you want to end your session?",
            btnCancel: "Cancel",
            btnLogout: "Logout",

            // KrishiAI Chatbot
            krishiTitle: "KrishiAI Assistant",
            krishiSub: "Active Voice & Text AI",
            krishiWelcome: "Namaste! I'm KrishiAI, your agricultural intelligence assistant. How can I help your farm today?",
            krishiPlaceholder: "Ask today's price, weather, auction advice..."
        },

        gu: {
            // Brand & Navigation
            brandTitle: "ધ મિડલમેન",
            brandSub: "કિલર",
            tagline: "સીધું ખેતરથી. સૌ માટે ન્યાયી.",
            navHome: "હોમ",
            navFarmerPortal: "ખેડૂત પોર્ટલ",
            navFairPrice: "એઆઈ વાજબી ભાવ",
            navMarketplace: "માર્કેટપ્લેસ",
            navAuctions: "લાઇવ હરાજી",
            navLogistics: "લોજિસ્ટિક્સ",
            navAdmin: "એડમિન કમાન્ડ",
            navLoginRegister: "લોગિન / રજીસ્ટર",
            navSellDirect: "સીધું વેચાણ શરૂ કરો",
            navExploreMarket: "માર્કેટપ્લેસ જુઓ",

            // Ticker & Headers
            tickerTitle: "લાઇવ મંડી પલ્સ",
            heroBadge: "AI-સંચાલિત ડાયરેક્ટ કૃષિ માર્કેટપ્લેસ",
            heroTitle1: "મધ્યસ્થીઓને હટાવો.",
            heroTitle2: "ખેડૂતને સશક્ત બનાવો.",
            heroSubtitle: "એક એઆઈ-સંચાલિત કૃષિ માર્કેટપ્લેસ જે ખેડૂતોને વાજબી ભાવો, પારદર્શક હરાજી અને સુરક્ષિત ચૂકવણી દ્વારા સીધા વેપારીઓ સાથે જોડે છે.",
            
            // Problem Section
            problemTag: "પરંપરાગત સપ્લાય ચેન વિ મિડલમેન કિલર",
            problemTitle: "ખેડૂતના નાણાં ક્યાં જાય છે?",
            problemSubtitle: "પરંપરાગત કૃષિ સાંકળમાં, ૫+ મધ્યસ્થીઓ પાકના કુલ મૂલ્યના ૩૫% સુધીનો નફો મેળવી લે છે.",
            tradChainTitle: "પરંપરાગત સપ્લાય ચેન (નાણાકીય લીકેજ)",
            farmer: "ખેડૂત",
            trader: "સ્થાનિક વેપારી",
            wholesaler: "જથ્થાબંધ વેપારી",
            distributor: "ડિસ્ટ્રીબ્યુટર",
            retailer: "રિટેલર",
            buyer: "ખરીદદાર",
            leakageNotice: "⚠️ મધ્યસ્થીઓ દ્વારા લીકેજ: ₹૮૦૦ / ક્વિન્ટલ (ખેડૂતનો ૨૫% નફો ઓછો થાય છે)",

            // Pipeline Nodes
            nodeFarm: "🌱 ખેતર",
            nodeAiQuality: "🤖 એઆઈ ક્વોલિટી",
            nodeFairPrice: "💰 વાજબી ભાવ",
            nodeAuction: "🔴 હરાજી",
            nodeBuyer: "🤝 ખરીદદાર",
            nodeEscrow: "🔐 એસ્ક્રો",
            nodeLogistics: "🚚 લોજિસ્ટિક્સ",
            nodeDelivery: "🏠 ડિલિવરી",

            // Farmer Dashboard
            farmerGreeting: "સુપ્રભાત 👋",
            farmerSubhead: "આણંદ, ગુજરાતનું તમારું ખેતર પ્રાદેશિક સરેરાશ કરતાં +૧૪% સારું પ્રદર્શન કરી રહ્યું છે.",
            btnRegisterCrop: "નવો પાક ઉમેરો",
            statTotalCrops: "કુલ નોંધાયેલ પાક",
            statActiveListings: "સક્રિય યાદી",
            statCurrentEarnings: "વર્તમાન કમાણી",
            statPendingEscrow: "પેન્ડિંગ એસ્ક્રો",
            chartMarketTitle: "માર્કેટ ઇન્ટેલિજન્સ અને ભાવ પ્રવાહ (આણંદ મંડી)",
            trustScoreTitle: "ખેડૂત વિશ્વાસ સ્કોર",
            weatherAlertTitle: "AI હવામાન ચેતવણી — આણંદ અને ખેડા જિલ્લો",
            weatherAlertText: "૩૬ કલાકમાં ભારે વરસાદ (૪૫મીમી+) ની આગાહી. ભલામણ: અનાજને નુકસાનથી બચાવવા માટે લણણી ૧૨-૧૮ કલાક મુલતવી રાખો.",
            askKrishiAdvice: "કૃષિAI ની સલાહ લો",

            // AI Fair Price Radar
            radarTag: "એલ્ગોરિધમિક પ્રાઇસિંગ ઇન્ટેલિજન્સ",
            radarTitle: "AI વાજબી ભાવ રાડાર એન્જિન",
            radarSubtitle: "રીઅલ-ટાઇમ મંડીના ભાવો, પાકની ઉપલબ્ધતા, હવામાન અને માંગનું મૂલ્યાંકન કરીને એઆઈ દ્વારા નક્કી કરેલ ભાવ.",
            currentMandiRate: "વર્તમાન મંડી ભાવ:",
            aiFairBenchmark: "એઆઈ ગણતરી કરેલ વાજબી ભાવ:",
            expectedAuctionRange: "અપેક્ષિત હરાજી રેન્જ:",
            btnApplyFairPrice: "માર્કેટપ્લેસ પર વાજબી ભાવ લાગુ કરો",

            // Marketplace
            marketTag: "ડાયરેક્ટ કૃષિ માર્કેટપ્લેસ",
            marketTitle: "ચકાસાયેલ પાકની યાદી",
            marketSubtitle: "એઆઈ ક્વોલિટી રિપોર્ટ અને એસ્ક્રો સુરક્ષા સાથે પ્રમાણિત ખેડૂતો પાસેથી સીધી ખરીદી કરો.",
            filterAll: "બધા",
            btnPlaceBid: "બોલી લગાવો",
            btnBuyDirect: "સીધી ખરીદી કરો",
            searchPlaceholder: "ઘઉં, ડાંગર, મગફળી, સ્થળ, ખેડૂત શોધો...",

            // Live Auction
            auctionTag: "રીઅલ-ટાઇમ પારદર્શક હરાજી",
            auctionTitle: "લાઇવ પાક હરાજી",
            auctionSubtitle: "કોર્પોરેટ ખરીદદારો દ્વારા ઉચ્ચ ગુણવત્તાવાળા ચકાસાયેલ પાકની પારદર્શક હરાજી.",
            spotlightItem: "વિશેષ આઇટમ #AU-2849",
            startingPrice: "શરૂઆતી ભાવ",
            currentHighestBid: "વર્તમાન સર્વોચ્ચ બોલી",
            closingIn: "હરાજી સમાપ્ત થવામાં સમય:",
            btnPlaceBidNow: "તમારી બોલી લગાવો",
            liveBidActivity: "લાઇવ બોલી પ્રવૃત્તિ",

            // Logistics
            logisticsTag: "ઇન્ટેલિજન્ટ કોલ્ડ-ચેઇન લોજિસ્ટિક્સ",
            logisticsTitle: "ગુજરાત શિપમેન્ટ ટ્રેકિંગ મેપ",
            logisticsSubtitle: "અનાજની તાજગી માટે ટેમ્પરેચર ટેલિમેટ્રી સાથે ગુજરાતમાં રીઅલ-ટાઇમ ટ્રેકિંગ.",
            vehicle: "વાહન:",
            driver: "ડ્રાઇવર:",
            estimatedEta: "અંદાજિત સમય:",
            storageTemp: "સ્ટોરેજ તાપમાન:",
            humidity: "ભેજ:",

            // Escrow
            escrowTag: "ફિનટેક એસ્ક્રો સુરક્ષા",
            escrowTitle: "સુરક્ષિત સ્માર્ટ એસ્ક્રો વોલ્ટ",
            escrowSubtitle: "ઓર્ડર સમયે નાણાં સુરક્ષિત રીતે લોક થાય છે અને ડિલિવરી ચકાસણી પછી ખેડૂતને મળે છે.",
            step1PaymentLocked: "પગલું ૦૧: ખરીદદાર ચૂકવણી લોક થઈ",
            step2QualityVerified: "પગલું ૦૨: પાક ગુણવત્તા ચકાસાઈ",
            step3GpsTelemetry: "પગલું ૦૩: ટ્રાન્ઝિટ જીપીએસ ટ્રેકિંગ",
            step4FarmerPayout: "પગલું ૦૪: ખેડૂતને ત્વરિત ચૂકવણી",
            btnSimulateRelease: "ચૂકવણી રિલીઝનું સિમ્યુલેશન કરો",

            // Admin
            adminTag: "સિસ્ટમ કમાન્ડ સેન્ટર",
            adminTitle: "એડમિન પ્લેટફોર્મ ઇન્ટેલિજન્સ",
            adminSubtitle: "ગુજરાત કૃષિ વેપાર અને એઆઈ સિક્યોરિટીનું રીઅલ-ટાઇમ મોનિટરિંગ.",
            statVerifiedFarmers: "કુલ પ્રમાણિત ખેડૂતો",
            statVerifiedBuyers: "પ્રમાણિત ખરીદદારો",
            statTotalVolume: "કુલ સીધો વેપાર",
            statFraudScore: "એઆઈ ફ્રોડ રિસ્ક સ્કોર",
            regionalTableTitle: "પ્રાદેશિક વેપાર અને ફ્રોડ મોનિટર (ગુજરાત)",

            // Auth Modals & Wizard
            authSignIn: "સાાઇન ઇન",
            authCreateAccount: "ખાતું બનાવો",
            lblEmailOrMobile: "ઇમેઇલ અથવા મોબાઇલ નંબર",
            lblPassword: "પાસવર્ડ",
            phEmailOrMobile: "ઇમેઇલ અથવા મોબાઇલ નંબર દાખલ કરો",
            phPassword: "તમારો પાસવર્ડ દાખલ કરો",
            btnSignInSubmit: "સાાઇન ઇન કરો",
            lblRememberMe: "મને યાદ રાખો",
            btnForgotPwd: "પાસવર્ડ ભૂલી ગયા?",
            lblSelectRole: "તમારો રોલ પસંદ કરો",
            roleFarmerTitle: "ખેડૂત",
            roleFarmerDesc: "સીધો પાક વેચો, વાજબી ભાવ અને એસ્ક્રો ચૂકવણી મેળવો.",
            roleBuyerTitle: "ખરીદદાર",
            roleBuyerDesc: "ચકાસાયેલ ખેતરોમાંથી સીધા ઉચ્ચ ગુણવત્તાવાળા પાકની ખરીદી કરો.",
            stepPersonalDetails: "વ્યક્તિગત / વ્યવસાયિક વિગતો",
            stepContactInfo: "સંપર્ક માહિતી",
            stepPasswordSecurity: "પાસવર્ડ અને સુરક્ષા",
            stepOtpVerify: "ખાતાની ચકાસણી કરો",
            otpNotice: "અમે તમારા સંપર્ક નંબર પર ૬-અંકનો વેરિફિકેશન કોડ મોકલ્યો છે.",
            btnVerifyAccount: "ચકાસો અને ખાતું બનાવો",
            accountCreatedTitle: "ખાતું સફળતાપૂર્વક બની ગયું છે",
            accountCreatedSub: "ધ મિડલમેન કિલર કૃષિ પ્લેટફોર્મ પર આપનું સ્વાગત છે!",
            
            // Logout
            logoutTitle: "લોગ આઉટ કરવું છે?",
            logoutSub: "શું તમે તમારું સેશન સમાપ્ત કરવા માંગો છો?",
            btnCancel: "રદ કરો",
            btnLogout: "લોગ આઉટ",

            // KrishiAI Chatbot
            krishiTitle: "કૃષિAI આસિસ્ટન્ટ",
            krishiSub: "સક્રિય વોઇસ અને ટેક્સ્ટ એઆઈ",
            krishiWelcome: "નમસ્તે રાજેશ! હું કૃષિAI છું. આજે હું તમારા ખેતર માટે કેવી રીતે મદદ કરી શકું?",
            krishiPlaceholder: "આજના ભાવ, હવામાન, હરાજીની સલાહ પૂછો..."
        },

        hi: {
            // Brand & Navigation
            brandTitle: "द मिडलमैन",
            brandSub: "किलर",
            tagline: "सीधे खेत से। सबके लिए न्यायसंगत।",
            navHome: "होम",
            navFarmerPortal: "किसान पोर्टल",
            navFairPrice: "एआई सही मूल्य",
            navMarketplace: "मार्केटप्लेस",
            navAuctions: "लाइव नीलामी",
            navLogistics: "लॉजिस्टिक्स",
            navAdmin: "एडमिन कमांड",
            navLoginRegister: "लॉगिन / रजिस्टर",
            navSellDirect: "सीधे बेचना शुरू करें",
            navExploreMarket: "मार्केटप्लेस देखें",

            // Ticker & Headers
            tickerTitle: "लाइव मंडी पल्स",
            heroBadge: "AI-संचालित प्रत्यक्ष कृषि मार्केटप्लेस",
            heroTitle1: "बिचौलियों को हटाओ।",
            heroTitle2: "किसान को सशक्त बनाओ।",
            heroSubtitle: "एक एआई-संचालित कृषि मार्केटप्लेस जो किसानों को उचित मूल्यों, पारदर्शी नीलामी और सुरक्षित भुगतान के माध्यम से सीधे खरीदारों से जोड़ता है।",
            
            // Problem Section
            problemTag: "पारंपरिक आपूर्ति श्रृंखला बनाम मिडलमैन किलर",
            problemTitle: "किसान का पैसा कहां जाता है?",
            problemSubtitle: "पारंपरिक कृषि श्रृंखला में, 5+ बिचौलिए अंतिम खरीदार तक पहुंचने से पहले फसल के कुल मूल्य का 35% तक ले लेते हैं।",
            tradChainTitle: "पारंपरिक आपूर्ति श्रृंखला (वित्तीय नुकसान)",
            farmer: "किसान",
            trader: "स्थानीय व्यापारी",
            wholesaler: "थोक व्यापारी",
            distributor: "वितरक",
            retailer: "खुदरा विक्रेता",
            buyer: "खरीदार",
            leakageNotice: "⚠️ बिचौलियों को नुकसान: ₹800 / क्विंटल (किसान का 25% मुनाफा घट जाता है)",

            // Pipeline Nodes
            nodeFarm: "🌱 खेत",
            nodeAiQuality: "🤖 एआई गुणवत्ता",
            nodeFairPrice: "💰 सही मूल्य",
            nodeAuction: "🔴 नीलामी",
            nodeBuyer: "🤝 खरीदार",
            nodeEscrow: "🔐 एस्क्रो",
            nodeLogistics: "🚚 लॉजिस्टिक्स",
            nodeDelivery: "🏠 डिलीवरी",

            // Farmer Dashboard
            farmerGreeting: "शुभ प्रभात 👋",
            farmerSubhead: "आनंद, गुजरात में आपका खेत क्षेत्रीय औसत से +14% बेहतर प्रदर्शन कर रहा है।",
            btnRegisterCrop: "नई फसल पंजीकृत करें",
            statTotalCrops: "कुल पंजीकृत फसलें",
            statActiveListings: "सक्रिय सूचियां",
            statCurrentEarnings: "वर्तमान कमाई",
            statPendingEscrow: "लंबित एस्क्रो",
            chartMarketTitle: "मार्केट इंटेलिजेंस और मूल्य रुझान (आनंद मंडी)",
            trustScoreTitle: "किसान ट्रस्ट स्कोर",
            weatherAlertTitle: "AI मौसम चेतावनी — आनंद एवं खेड़ा जिला",
            weatherAlertText: "36 घंटों में भारी बारिश (45 मिमी+) का अनुमान। सलाह: फसल क्षति से बचने के लिए कटाई 12-18 घंटे टालें।",
            askKrishiAdvice: "कृषिAI की सलाह लें",

            // AI Fair Price Radar
            radarTag: "एल्गोरिदम मूल्य निर्धारण इंटेलिजेंस",
            radarTitle: "AI उचित मूल्य रडार इंजन",
            radarSubtitle: "रियल-टाइम मंडी दरों, फसल आपूर्ति, मौसम और मांग का मूल्यांकन करके एआई द्वारा निर्धारित मूल्य।",
            currentMandiRate: "वर्तमान मंडी दर:",
            aiFairBenchmark: "एआई उचित मूल्य:",
            expectedAuctionRange: "अपेक्षित नीलामी सीमा:",
            btnApplyFairPrice: "मार्केटप्लेस पर सही मूल्य लागू करें",

            // Marketplace
            marketTag: "प्रत्यक्ष कृषि मार्केटप्लेस",
            marketTitle: "सत्यापित फसल सूची",
            marketSubtitle: "एआई गुणवत्ता रिपोर्ट और एस्क्रो सुरक्षा के साथ प्रमाणित किसानों से सीधे खरीदें।",
            filterAll: "सभी",
            btnPlaceBid: "बोली लगाएं",
            btnBuyDirect: "सीधे खरीदें",
            searchPlaceholder: "गेहूं, धान, मूंगफली, स्थान, किसान खोजें...",

            // Live Auction
            auctionTag: "रियल-टाइम पारदर्शी नीलामी",
            auctionTitle: "लाइव फसल नीलामी",
            auctionSubtitle: "कॉर्पोरेट खरीदारों द्वारा प्रीमियम गुणवत्ता वाली फसलों की पारदर्शी नीलामी।",
            spotlightItem: "विशेष आइटम #AU-2849",
            startingPrice: "शुरुआती मूल्य",
            currentHighestBid: "वर्तमान उच्चतम बोली",
            closingIn: "नीलामी समाप्त होने में समय:",
            btnPlaceBidNow: "अपनी बोली लगाएं",
            liveBidActivity: "लाइव बोली गतिविधि",

            // Logistics
            logisticsTag: "इंटेलिजेंट कोल्ड-चेन लॉजिस्टिक्स",
            logisticsTitle: "गुजरात शिपमेंट ट्रैकिंग मैप",
            logisticsSubtitle: "अनाज की ताजगी के लिए तापमान टेलीमेट्री के साथ गुजरात में रियल-टाइम ट्रैकिंग।",
            vehicle: "वाहन:",
            driver: "चालक:",
            estimatedEta: "अनुमानित समय:",
            storageTemp: "भंडारण तापमान:",
            humidity: "नमी:",

            // Escrow
            escrowTag: "फिनटेक एस्क्रो सुरक्षा",
            escrowTitle: "सुरक्षित स्मार्ट एस्क्रो वॉल्ट",
            escrowSubtitle: "ऑर्डर के समय राशि सुरक्षित रूप से लॉक होती है और डिलीवरी सत्यापन के बाद किसान को जारी की जाती है।",
            step1PaymentLocked: "चरण 01: खरीदार भुगतान लॉक हुआ",
            step2QualityVerified: "चरण 02: फसल गुणवत्ता सत्यापित",
            step3GpsTelemetry: "चरण 03: ट्रांजिट जीपीएस ट्रैकिंग",
            step4FarmerPayout: "चरण 04: किसान को तुरंत भुगतान",
            btnSimulateRelease: "भुगतान जारी करने का अनुकरण करें",

            // Admin
            adminTag: "सिस्टम कमांड सेंटर",
            adminTitle: "एडमिन प्लेटफॉर्म इंटेलिजेंस",
            adminSubtitle: "गुजरात कृषि व्यापार और एआई सुरक्षा की रियल-टाइम निगरानी।",
            statVerifiedFarmers: "कुल सत्यापित किसान",
            statVerifiedBuyers: "सत्यापित खरीदार",
            statTotalVolume: "कुल प्रत्यक्ष व्यापार",
            statFraudScore: "एआई फ्रॉड रिस्क स्कोर",
            regionalTableTitle: "क्षेत्रीय व्यापार और धोखाधड़ी मॉनिटर (गुजरात)",

            // Auth Modals & Wizard
            authSignIn: "साइन इन",
            authCreateAccount: "खाता बनाएं",
            lblEmailOrMobile: "ईमेल या मोबाइल नंबर",
            lblPassword: "पासवर्ड",
            phEmailOrMobile: "ईमेल या मोबाइल नंबर दर्ज करें",
            phPassword: "अपना पासवर्ड दर्ज करें",
            btnSignInSubmit: "साइन इन करें",
            lblRememberMe: "मुझे याद रखें",
            btnForgotPwd: "पासवर्ड भूल गए?",
            lblSelectRole: "अपनी भूमिका चुनें",
            roleFarmerTitle: "किसान",
            roleFarmerDesc: "फसल सीधे बेचें, सही मूल्य और एस्क्रो भुगतान पाएं।",
            roleBuyerTitle: "खरीदार",
            roleBuyerDesc: "सत्यापित खेतों से सीधे उच्च गुणवत्ता वाली फसलें खरीदें।",
            stepPersonalDetails: "व्यक्तिगत / व्यावसायिक विवरण",
            stepContactInfo: "संपर्क जानकारी",
            stepPasswordSecurity: "पासवर्ड और सुरक्षा",
            stepOtpVerify: "खाता सत्यापित करें",
            otpNotice: "हमने आपके संपर्क नंबर पर 6-अंकों का सत्यापन कोड भेजा है।",
            btnVerifyAccount: "सत्यापित करें और खाता बनाएं",
            accountCreatedTitle: "खाता सफलतापूर्वक बन गया",
            accountCreatedSub: "द मिडलमैन किलर प्लेटफॉर्म पर आपका स्वागत है!",
            
            // Logout
            logoutTitle: "लॉग आउट करें?",
            logoutSub: "क्या आप अपना सत्र समाप्त करना चाहते हैं?",
            btnCancel: "रद्द करें",
            btnLogout: "लॉग आउट",

            // KrishiAI Chatbot
            krishiTitle: "कृषिAI सहायक",
            krishiSub: "सक्रिय वॉयस और टेक्स्ट एआई",
            krishiWelcome: "नमस्ते राजेश! मैं कृषिAI हूं। आज मैं आपके खेत के लिए क्या मदद कर सकता हूं?",
            krishiPlaceholder: "आज के भाव, मौसम, नीलामी सलाह पूछें..."
        }
    },

    setLanguage(lang) {
        if (!this.translations[lang]) return;
        this.currentLang = lang;
        localStorage.setItem('mk_language', lang);

        const dict = this.translations[lang];

        // Replace text content for data-i18n elements
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (dict[key]) el.textContent = dict[key];
        });

        // Replace placeholder for data-i18n-placeholder elements
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (dict[key]) el.setAttribute('placeholder', dict[key]);
        });

        // Trigger dynamic updates for role navigation and charts
        if (window.MKApp) {
            window.MKApp.renderDynamicNavigation();
            window.MKApp.renderMarketplace();
        }
    },

    getText(key) {
        return (this.translations[this.currentLang] && this.translations[this.currentLang][key]) 
            || this.translations.en[key] 
            || key;
    }
};
