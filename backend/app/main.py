"""
The Middleman Killer - Backend FastAPI Application Server
Provides RESTful API endpoints for authentication, crop management,
market intelligence, AI predictions, live auctions, and KrishiAI.
"""
from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import datetime
import uuid
import sys
from pathlib import Path

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add app directory and project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(PROJECT_ROOT))

app = FastAPI(
    title="The Middleman Killer API",
    description="Direct Farm-to-Buyer Agricultural Marketplace Backend",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Frontend Static Files
if (PROJECT_ROOT / "css").exists():
    app.mount("/css", StaticFiles(directory=str(PROJECT_ROOT / "css")), name="css")
if (PROJECT_ROOT / "js").exists():
    app.mount("/js", StaticFiles(directory=str(PROJECT_ROOT / "js")), name="js")
if (PROJECT_ROOT / "data").exists():
    app.mount("/data", StaticFiles(directory=str(PROJECT_ROOT / "data")), name="data")
if (PROJECT_ROOT / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(PROJECT_ROOT / "assets")), name="assets")

@app.get("/", response_class=FileResponse)
def serve_index():
    return FileResponse(str(PROJECT_ROOT / "index.html"))

# In-memory / Database state
DEMO_ACCOUNTS = [
    {
        "email": "farmer@middlemankiller.com",
        "mobile": "9876543210",
        "password": "Farmer@123",
        "role": "farmer",
        "name": "Rajesh Patel",
        "location": "Anand, Gujarat",
        "verified": True,
        "avatar": "🌱"
    },
    {
        "email": "buyer@middlemankiller.com",
        "mobile": "9812345678",
        "password": "Buyer@123",
        "role": "buyer",
        "company": "Shree Foods Pvt. Ltd.",
        "name": "Anand Sharma",
        "location": "Ahmedabad, Gujarat",
        "verified": True,
        "avatar": "🏢"
    },
    {
        "email": "admin@middlemankiller.com",
        "mobile": "9999999999",
        "password": "Admin@123",
        "role": "admin",
        "name": "System Administrator",
        "location": "Gujarat HQ",
        "verified": True,
        "avatar": "🛡️"
    }
]

CROPS_DATABASE = [
    {
        "id": "CROP-001",
        "crop": "Cotton",
        "farmer": "Rajesh Patel",
        "location": "Anand, Gujarat",
        "quantity": "50 Quintals",
        "price": "₹6,850/Q",
        "quality": "Grade A+ (94/100)",
        "badge": "AI Scanned",
        "verified": True,
        "status": "Active"
    },
    {
        "id": "CROP-002",
        "crop": "Groundnut (Peanut)",
        "farmer": "Ramesh Patel",
        "location": "Junagadh, Gujarat",
        "quantity": "120 Quintals",
        "price": "₹5,400/Q",
        "quality": "Grade A (89/100)",
        "badge": "Direct Farm",
        "verified": True,
        "status": "Active"
    },
    {
        "id": "CROP-003",
        "crop": "Cumin",
        "farmer": "Suresh Parmar",
        "location": "Unjha, Gujarat",
        "quantity": "30 Quintals",
        "price": "₹28,500/Q",
        "quality": "Premium Export (96/100)",
        "badge": "Live Auction",
        "verified": True,
        "status": "Active"
    },
    {
        "id": "CROP-004",
        "crop": "Wheat",
        "farmer": "Bhavik Shah",
        "location": "Rajkot, Gujarat",
        "quantity": "200 Quintals",
        "price": "₹2,450/Q",
        "quality": "Grade B+ (86/100)",
        "badge": "Direct Farm",
        "verified": True,
        "status": "Active"
    }
]

MARKET_TICKER = [
    {"crop": "Cotton (Shankar-6)", "price": "₹6,850/Q", "change": "+4.2%", "positive": True},
    {"crop": "Groundnut (Bold)", "price": "₹5,400/Q", "change": "+2.1%", "positive": True},
    {"crop": "Cumin (Unjha Export)", "price": "₹28,500/Q", "change": "-1.5%", "positive": False},
    {"crop": "Wheat (Lok-1)", "price": "₹2,450/Q", "change": "+1.8%", "positive": True},
    {"crop": "Paddy (Basmati)", "price": "₹3,900/Q", "change": "+3.4%", "positive": True},
    {"crop": "Sesame (White)", "price": "₹14,200/Q", "change": "+0.9%", "positive": True}
]

REGIONAL_PRICES = [
    {"region": "Anand APMC", "crop": "Cotton", "min": "₹6,400", "max": "₹6,900", "avg": "₹6,720", "trend": "▲ High Demand"},
    {"region": "Junagadh Mandi", "crop": "Groundnut", "min": "₹5,100", "max": "₹5,550", "avg": "₹5,380", "trend": "▲ Steady"},
    {"region": "Unjha Market Yard", "crop": "Cumin", "min": "₹27,000", "max": "₹29,200", "avg": "₹28,400", "trend": "▼ Slight Dip"},
    {"region": "Rajkot Mandi", "crop": "Wheat", "min": "₹2,350", "max": "₹2,520", "avg": "₹2,460", "trend": "▲ Bullish"},
    {"region": "Gondal Yard", "crop": "Castor", "min": "₹5,800", "max": "₹6,150", "avg": "₹6,010", "trend": "▲ High Demand"}
]

AUCTIONS_STATE = {
    "crop": "Cotton (Shankar-6 Super Fine)",
    "quantity": "100 Quintals",
    "basePrice": 4500,
    "currentBid": 4820,
    "timeLeftSeconds": 161,
    "bids": [
        {"id": 1, "buyer": "Adani Wilmar Logistics", "amount": 4820, "time": "2 mins ago", "status": "Leading"},
        {"id": 2, "buyer": "Gujarat State Coop Fed", "amount": 4780, "time": "5 mins ago", "status": "Outbid"},
        {"id": 3, "buyer": "Reliance Retail Agri", "amount": 4650, "time": "12 mins ago", "status": "Outbid"}
    ]
}

# Request Models
class LoginRequest(BaseModel):
    identifier: str
    password: str

class CropCreateRequest(BaseModel):
    crop: str
    farmer: Optional[str] = "Rajesh Patel"
    location: Optional[str] = "Anand, Gujarat"
    quantity: str
    price: str

class BidRequest(BaseModel):
    amount: float
    buyerName: Optional[str] = "Verified Buyer"

class ChatRequest(BaseModel):
    message: str
    lang: Optional[str] = "en"

class CropScanRequest(BaseModel):
    cropName: Optional[str] = "Cotton"

# Routes
@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "The Middleman Killer Backend API",
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.post("/api/v1/auth/login")
def login(req: LoginRequest):
    ident = req.identifier.strip().lower()
    for acc in DEMO_ACCOUNTS:
        if (acc["email"].lower() == ident or acc["mobile"] == ident) and acc["password"] == req.password:
            return {
                "status": "success",
                "user": acc,
                "token": f"mk_token_{uuid.uuid4().hex[:12]}"
            }
    # Fallback authentication for quick demo testing
    return {
        "status": "success",
        "user": {
            "email": req.identifier,
            "mobile": req.identifier,
            "role": "farmer",
            "name": "Authenticated User",
            "location": "Gujarat",
            "verified": True,
            "avatar": "🌱"
        },
        "token": f"mk_token_{uuid.uuid4().hex[:12]}"
    }

@app.get("/api/v1/crops")
def get_crops():
    return {"status": "success", "count": len(CROPS_DATABASE), "crops": CROPS_DATABASE}

@app.post("/api/v1/crops")
def create_crop(req: CropCreateRequest):
    new_crop = {
        "id": f"CROP-{len(CROPS_DATABASE)+1:03d}",
        "crop": req.crop,
        "farmer": req.farmer,
        "location": req.location,
        "quantity": req.quantity,
        "price": req.price,
        "quality": "Grade A+ (AI Verified)",
        "badge": "AI Scanned",
        "verified": True,
        "status": "Active"
    }
    CROPS_DATABASE.insert(0, new_crop)
    return {"status": "success", "message": "Crop registered successfully", "crop": new_crop}

@app.get("/api/v1/market/ticker")
def get_market_ticker():
    return {"status": "success", "ticker": MARKET_TICKER}

@app.get("/api/v1/market/regional")
def get_regional_prices():
    return {"status": "success", "regional": REGIONAL_PRICES}

@app.post("/api/v1/ai/scan")
def ai_crop_scan(req: CropScanRequest):
    return {
        "status": "success",
        "crop": req.cropName,
        "qualityScore": 94,
        "grade": "Grade A+ (Premium Export)",
        "moisture": "8.2%",
        "grainPurity": "98.7%",
        "fairPriceEstimate": "₹6,850/Q",
        "recommendation": "SELL NOW (High demand in Anand APMC)"
    }

@app.post("/api/v1/ai/fair-price")
def ai_fair_price(body: Dict[str, Any] = Body(default={})):
    crop_name = body.get("crop", "Cotton")
    return {
        "status": "success",
        "crop": crop_name,
        "fairPrice": 6850,
        "minPrice": 6400,
        "maxPrice": 7200,
        "decision": "SELL NOW",
        "confidence": "94%",
        "netProfitGain": "+18.4% vs Middlemen",
        "factors": [
            {"label": "Demand (+7.8%)", "val": 0.9, "color": "#D96C3B"},
            {"label": "Supply (Tight)", "val": 0.85, "color": "#D6A84F"},
            {"label": "Weather (Alert)", "val": 0.75, "color": "#82957D"},
            {"label": "Quality (94/100)", "val": 0.95, "color": "#2ECC71"},
            {"label": "History (+14%)", "val": 0.88, "color": "#D6A84F"}
        ]
    }

@app.post("/api/v1/ai/chat")
def krishi_ai_chat(req: ChatRequest):
    msg = req.message.lower()
    lang = req.lang or "en"
    
    if "price" in msg or "ભાવ" in msg or "દામ" in msg or "મંડી" in msg:
        if lang == "gu":
            reply = "નમસ્તે! આજે ગુજરાતની મંડીઓમાં ઘઉં, ડાંગર અને મગફળીના ભાવમાં +૬.૮% નો વધારો જોવા મળ્યો છે. લાઈવ હરાજીમાં પાક મૂકવાથી વધુ નફો મળશે."
        elif lang == "hi":
            reply = "नमस्ते! आज गुजरात मंडियों में गेहूं, धान और मूंगफली की कीमतों में +6.8% की वृद्धि हुई है। लाइव नीलामी में फसल बेचने से अधिक लाभ होगा।"
        else:
            reply = "Namaste! Today's benchmark prices for Wheat, Paddy (Rice), and Groundnut (Peanut) in Gujarat mandis are up by +6.8%. Placing your crop in Live Auction now will maximize returns."
    elif "sell" in msg or "વેચવું" in msg or "બેચના" in msg:
        reply = "AI Recommendation: SELL NOW! Mandi demand index is peaking at 92/100. Direct buyer matching eliminates 12% middleman commission."
    else:
        reply = f"KrishiAI Assist: I analyzed market trends for your query. Current regional sentiment is highly favorable for direct farmer-to-buyer sales with guaranteed Escrow protection."

    return {
        "status": "success",
        "query": req.message,
        "reply": reply,
        "language": lang
    }

@app.get("/api/v1/auctions")
def get_auctions():
    return {"status": "success", "auction": AUCTIONS_STATE}

@app.post("/api/v1/auctions/bid")
def place_bid(req: BidRequest):
    if req.amount <= AUCTIONS_STATE["currentBid"]:
        raise HTTPException(status_code=400, detail=f"Bid must be higher than current bid of ₹{AUCTIONS_STATE['currentBid']}")
    
    AUCTIONS_STATE["currentBid"] = req.amount
    new_bid = {
        "id": len(AUCTIONS_STATE["bids"]) + 1,
        "buyer": req.buyerName or "Verified Buyer",
        "amount": req.amount,
        "time": "Just now",
        "status": "Leading"
    }
    AUCTIONS_STATE["bids"].insert(0, new_bid)
    return {"status": "success", "message": "Bid placed successfully", "currentBid": req.amount, "bids": AUCTIONS_STATE["bids"]}
