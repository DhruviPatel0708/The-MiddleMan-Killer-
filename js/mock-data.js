/**
 * THE MIDDLEMAN KILLER - Mock Data Store & Authentication Registry
 * STRICT 10 SUPPORTED CROPS ONLY
 */

window.MKData = {
    // Approved Strict 10 Crops List
    approvedCrops: [
        "Cotton",
        "Groundnut (Peanut)",
        "Cumin",
        "Bajara (Bajra / Pearl Millet)",
        "Wheat",
        "Paddy (Rice)",
        "Maize",
        "Tobacco",
        "Sesame",
        "Castor"
    ],

    // Pre-configured Hackathon Demo Accounts
    demoAccounts: [
        {
            email: "farmer@middlemankiller.com",
            mobile: "9876543210",
            password: "Farmer@123",
            role: "farmer",
            name: "Rajesh Patel",
            location: "Anand, Gujarat",
            verified: true,
            avatar: "🌱"
        },
        {
            email: "buyer@middlemankiller.com",
            mobile: "9812345678",
            password: "Buyer@123",
            role: "buyer",
            company: "Shree Foods Pvt. Ltd.",
            name: "Anand Sharma",
            location: "Ahmedabad, Gujarat",
            verified: true,
            avatar: "🏢"
        },
        {
            email: "admin@middlemankiller.com",
            mobile: "9999999999",
            password: "Admin@123",
            role: "admin",
            name: "System Administrator",
            location: "Gujarat HQ",
            verified: true,
            avatar: "🛡️"
        }
    ],

    // Navigation Menu Config by Role
    roleNavMenus: {
        farmer: [
            { id: "farmerDashboardView", labelKey: "navFarmerPortal", icon: "layout-dashboard" },
            { id: "marketplaceView", labelKey: "navMarketplace", icon: "sprout" },
            { id: "cropRegAction", labelKey: "btnRegisterCrop", icon: "plus-circle", action: "openCropModal" },
            { id: "fairPriceRadarView", labelKey: "navFairPrice", icon: "radar" },
            { id: "liveAuctionView", labelKey: "navAuctions", icon: "zap" },
            { id: "logisticsView", labelKey: "navLogistics", icon: "truck" },
            { id: "escrowPaymentView", labelKey: "escrowTag", icon: "lock" },
            { id: "krishiAiAction", labelKey: "krishiTitle", icon: "bot", action: "toggleKrishi" },
            { id: "trustScoreSection", labelKey: "trustScoreTitle", icon: "shield-check" }
        ],
        buyer: [
            { id: "marketplaceView", labelKey: "navMarketplace", icon: "shopping-bag" },
            { id: "liveAuctionView", labelKey: "navAuctions", icon: "zap" },
            { id: "escrowPaymentView", labelKey: "escrowTag", icon: "lock" },
            { id: "logisticsView", labelKey: "navLogistics", icon: "truck" },
            { id: "fairPriceRadarView", labelKey: "navFairPrice", icon: "radar" },
            { id: "krishiAiAction", labelKey: "krishiTitle", icon: "bot", action: "toggleKrishi" }
        ],
        admin: [
            { id: "adminDashboardView", labelKey: "navAdmin", icon: "shield-check" },
            { id: "adminRegionalSection", labelKey: "regionalTableTitle", icon: "users" },
            { id: "adminFraudSection", labelKey: "statFraudScore", icon: "alert-triangle" },
            { id: "marketplaceView", labelKey: "navMarketplace", icon: "sprout" },
            { id: "liveAuctionView", labelKey: "navAuctions", icon: "zap" },
            { id: "escrowPaymentView", labelKey: "escrowTag", icon: "lock" },
            { id: "logisticsView", labelKey: "navLogistics", icon: "truck" }
        ]
    },

    farmer: {
        name: "Rajesh Patel",
        location: "Anand, Gujarat",
        farmSize: "12.5 Acres",
        trustScore: 94,
        metrics: {
            totalCrops: 24,
            activeListings: 8,
            currentEarnings: "₹4.82L",
            buyerInterest: 127,
            pendingPayments: "₹82,400",
            performanceVsRegional: "+14%"
        }
    },

    // Live Ticker Data (Strictly 10 Approved Crops)
    marketTicker: [
        { crop: "Wheat", price: "₹2,835/Q", change: "+6.8%", positive: true },
        { crop: "Groundnut (Peanut)", price: "₹6,450/Q", change: "+4.2%", positive: true },
        { crop: "Cotton", price: "₹7,120/Q", change: "+8.1%", positive: true },
        { crop: "Bajara (Bajra / Pearl Millet)", price: "₹2,250/Q", change: "+3.4%", positive: true },
        { crop: "Paddy (Rice)", price: "₹4,820/Q", change: "+5.2%", positive: true },
        { crop: "Cumin", price: "₹24,500/Q", change: "+9.4%", positive: true },
        { crop: "Sesame", price: "₹12,400/Q", change: "+6.1%", positive: true },
        { crop: "Castor", price: "₹5,950/Q", change: "+2.8%", positive: true },
        { crop: "Maize", price: "₹2,100/Q", change: "-0.5%", positive: false },
        { crop: "Tobacco", price: "₹8,300/Q", change: "+4.9%", positive: true }
    ],

    // Crop Marketplace Listings (Strictly 10 Approved Crops)
    crops: [
        {
            id: "crop-001",
            title: "Premium Grade Paddy (Rice)",
            cropName: "Paddy (Rice)",
            farmer: "Verified Farmer",
            location: "Anand, Gujarat",
            quantity: "150 Quintals",
            grade: "Premium Grade A+",
            qualityScore: 94,
            fairPrice: "₹4,650/Q",
            currentBid: "₹4,820/Q",
            harvestDate: "12 Aug 2026",
            verified: true,
            isAuction: true,
            auctionEndTime: 161,
            image: "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=800&q=80",
            category: "Grains"
        },
        {
            id: "crop-002",
            title: "High-Oil Content Groundnut (Peanut)",
            cropName: "Groundnut (Peanut)",
            farmer: "Verified Farmer",
            location: "Rajkot, Gujarat",
            quantity: "280 Quintals",
            grade: "Grade A",
            qualityScore: 91,
            fairPrice: "₹6,300/Q",
            currentBid: "₹6,450/Q",
            harvestDate: "18 Aug 2026",
            verified: true,
            isAuction: false,
            image: "https://images.unsplash.com/photo-1567427017947-545c5f8d16ad?auto=format&fit=crop&w=800&q=80",
            category: "Oilseeds"
        },
        {
            id: "crop-003",
            title: "Long Staple Fiber Cotton",
            cropName: "Cotton",
            farmer: "Verified Farmer",
            location: "Mehsana, Gujarat",
            quantity: "400 Quintals",
            grade: "Premium Grade A+",
            qualityScore: 96,
            fairPrice: "₹7,000/Q",
            currentBid: "₹7,120/Q",
            harvestDate: "15 Aug 2026",
            verified: true,
            isAuction: true,
            auctionEndTime: 420,
            image: "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?auto=format&fit=crop&w=800&q=80",
            category: "Fiber"
        },
        {
            id: "crop-004",
            title: "Export Quality Cumin Seeds",
            cropName: "Cumin",
            farmer: "Verified Farmer",
            location: "Unjha, Gujarat",
            quantity: "85 Quintals",
            grade: "Export Quality",
            qualityScore: 98,
            fairPrice: "₹24,000/Q",
            currentBid: "₹24,500/Q",
            harvestDate: "10 Aug 2026",
            verified: true,
            isAuction: true,
            auctionEndTime: 890,
            image: "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=800&q=80",
            category: "Spices"
        },
        {
            id: "crop-005",
            title: "Organic Bajara (Bajra / Pearl Millet)",
            cropName: "Bajara (Bajra / Pearl Millet)",
            farmer: "Verified Farmer",
            location: "Jamnagar, Gujarat",
            quantity: "300 Quintals",
            grade: "Standard Grade A",
            qualityScore: 90,
            fairPrice: "₹2,200/Q",
            currentBid: "₹2,250/Q",
            harvestDate: "20 Aug 2026",
            verified: true,
            isAuction: false,
            image: "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?auto=format&fit=crop&w=800&q=80",
            category: "Millets"
        },
        {
            id: "crop-006",
            title: "Golden Sharbati Durum Wheat",
            cropName: "Wheat",
            farmer: "Verified Farmer",
            location: "Anand, Gujarat",
            quantity: "320 Quintals",
            grade: "Premium Grade A+",
            qualityScore: 95,
            fairPrice: "₹2,780/Q",
            currentBid: "₹2,835/Q",
            harvestDate: "05 Aug 2026",
            verified: true,
            isAuction: false,
            image: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=800&q=80",
            category: "Grains"
        },
        {
            id: "crop-007",
            title: "High-Yield White Maize Grain",
            cropName: "Maize",
            farmer: "Verified Farmer",
            location: "Vadodara, Gujarat",
            quantity: "220 Quintals",
            grade: "Grade A",
            qualityScore: 92,
            fairPrice: "₹2,050/Q",
            currentBid: "₹2,100/Q",
            harvestDate: "14 Aug 2026",
            verified: true,
            isAuction: false,
            image: "https://images.unsplash.com/photo-1551754655-cd27e38d2076?auto=format&fit=crop&w=800&q=80",
            category: "Grains"
        },
        {
            id: "crop-008",
            title: "Commercial Leaf Tobacco Batch",
            cropName: "Tobacco",
            farmer: "Verified Farmer",
            location: "Anand, Gujarat",
            quantity: "110 Quintals",
            grade: "Grade A",
            qualityScore: 89,
            fairPrice: "₹8,100/Q",
            currentBid: "₹8,300/Q",
            harvestDate: "08 Aug 2026",
            verified: true,
            isAuction: false,
            image: "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=800&q=80",
            category: "Cash Crop"
        },
        {
            id: "crop-009",
            title: "Natural White Sesame Seeds",
            cropName: "Sesame",
            farmer: "Verified Farmer",
            location: "Junagadh, Gujarat",
            quantity: "95 Quintals",
            grade: "Export Grade A+",
            qualityScore: 97,
            fairPrice: "₹12,100/Q",
            currentBid: "₹12,400/Q",
            harvestDate: "11 Aug 2026",
            verified: true,
            isAuction: true,
            auctionEndTime: 600,
            image: "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=800&q=80",
            category: "Oilseeds"
        },
        {
            id: "crop-010",
            title: "High Oil Content Castor Seeds",
            cropName: "Castor",
            farmer: "Verified Farmer",
            location: "Patan, Gujarat",
            quantity: "350 Quintals",
            grade: "Grade A",
            qualityScore: 93,
            fairPrice: "₹5,800/Q",
            currentBid: "₹5,950/Q",
            harvestDate: "17 Aug 2026",
            verified: true,
            isAuction: false,
            image: "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=800&q=80",
            category: "Oilseeds"
        }
    ],

    // Live Auction Bids (Using 10 Approved Crops)
    bidsHistory: [
        { id: 1, buyer: "Adani Wilmar Agri (Buyer #4821)", amount: 4820, time: "Just now", status: "Leading" },
        { id: 2, buyer: "ITC Food Division (Buyer #1732)", amount: 4800, time: "42s ago", status: "Outbid" },
        { id: 3, buyer: "Reliance Retail Grain (Buyer #8211)", amount: 4760, time: "1m 15s ago", status: "Outbid" },
        { id: 4, buyer: "Gujarat Agri Corp (Buyer #3391)", amount: 4710, time: "2m 04s ago", status: "Outbid" },
        { id: 5, buyer: "Patanjali Foods (Buyer #9024)", amount: 4650, time: "3m 30s ago", status: "Outbid" }
    ],

    // Intra-Gujarat Logistics Data
    shipment: {
        id: "TRK-8849-GJ",
        cropName: "150 Qtl Paddy (Rice)",
        driver: "Sukhdev Singh (GJ-06-AZ-9921)",
        vehicle: "18-Ton Multi-Axle Refrigerated Truck",
        origin: "Verified Farm, Rajkot, Gujarat",
        destination: "Adani Wilmar Processing Plant, Surat, Gujarat",
        status: "IN_TRANSIT",
        eta: "3 Hours 45 Mins",
        temperature: "22°C (Optimal Storage)",
        humidity: "48%",
        waypoints: [
            { name: "Farm Loading (Rajkot, Gujarat)", completed: true, time: "07:30 AM" },
            { name: "Transit Hub (Ahmedabad, Gujarat)", completed: true, time: "10:15 AM" },
            { name: "Transit Hub (Vadodara, Gujarat)", completed: false, current: true, time: "12:00 PM" },
            { name: "Final Destination (Surat, Gujarat)", completed: false, time: "03:15 PM" }
        ]
    },

    // Regional Activity (Gujarat Only)
    regionalMapData: [
        { city: "Ahmedabad", activeFarmers: 1420, tradeVolume: "₹18.4 Cr", topCrop: "Cotton & Wheat", riskLevel: "Low (2%)" },
        { city: "Rajkot", activeFarmers: 2150, tradeVolume: "₹32.1 Cr", topCrop: "Groundnut (Peanut)", riskLevel: "Low (1.5%)" },
        { city: "Surat", activeFarmers: 980, tradeVolume: "₹14.2 Cr", topCrop: "Paddy (Rice)", riskLevel: "Low (3%)" },
        { city: "Gandhinagar", activeFarmers: 740, tradeVolume: "₹11.8 Cr", topCrop: "Bajara & Wheat", riskLevel: "Low (1%)" },
        { city: "Mehsana", activeFarmers: 1680, tradeVolume: "₹21.5 Cr", topCrop: "Castor & Cumin", riskLevel: "Low (2.4%)" },
        { city: "Anand", activeFarmers: 1310, tradeVolume: "₹16.9 Cr", topCrop: "Tobacco & Maize", riskLevel: "Low (1.8%)" },
        { city: "Junagadh", activeFarmers: 1890, tradeVolume: "₹26.4 Cr", topCrop: "Sesame & Groundnut", riskLevel: "Low (2.1%)" },
        { city: "Vadodara", activeFarmers: 1120, tradeVolume: "₹15.7 Cr", topCrop: "Maize & Cotton", riskLevel: "Low (2%)" },
        { city: "Jamnagar", activeFarmers: 1450, tradeVolume: "₹19.8 Cr", topCrop: "Groundnut & Cumin", riskLevel: "Low (1.9%)" }
    ],

    krishiAiKnowledge: [
        {
            keywords: ["price", "today", "rate", "wheat", "market"],
            response: "Today's benchmark price for Sharbati Wheat in Anand mandi is ₹2,835/Q, up 6.8%. The AI Fair Price Radar predicts high demand (+7.8%)."
        },
        {
            keywords: ["sell", "now", "timing", "harvest"],
            response: "Based on current regional weather alerts (heavy rain expected in 36 hrs), putting your Paddy (Rice) into Live Auction NOW will likely net 8-12% above MSP."
        },
        {
            keywords: ["quality", "grade", "scan", "check"],
            response: "Your Groundnut (Peanut) batch achieved an AI Quality Score of 94/100 (Premium Grade A+). Moisture is 7.2% and aflatoxin risk is zero."
        }
    ]
};