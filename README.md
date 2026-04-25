# 🌿 AwareBot — Market Decision Agent

> Intent-aware AI agent for Kenyan smallholder farmers and market sellers.

## The Problem

A broker offers a farmer 45 KES/kg for tomatoes.  
The farmer doesn't know Kongowea price today is 95 KES/kg.  
He accepts. He just lost half his income.

**The exploit is simple: information asymmetry.**

## The Solution

AwareBot asks one question before giving advice: **Why are you selling?**

| Intent | Decision |
|--------|----------|
| 🚨 Emergency | SELL NOW — accept 45+, move today |
| 💰 Profit | WAIT — counter at 95, prices recover |
| 📦 Clearing | WHOLESALE — move volume, reduce spoilage risk |

Same tomatoes. Same market. Three different decisions.  
Because context matters.

## How It Works

3-turn onboarding flow:
1. **Who are you?** — Farmer / Seller / Mixed
2. **Why selling?** — Profit / Emergency / Clearing
3. **What + where?** — Goods and location

Then Gemini Flash synthesizes market signals and produces a structured decision.

## Stack

| Layer | Tool |
|-------|------|
| LLM | Gemini 2.0 Flash |
| Backend | FastAPI |
| Deployment | Google Cloud Run |
| Data | Mock Kongowea market prices |

## Run Locally

```bash
git clone https://github.com/kwisdomk/AwareBot.git
cd AwareBot
pip install -r requirements.txt
# Add GOOGLE_API_KEY to .env
uvicorn app.main:app --reload
```

## Live Demo

[Live on Cloud Run →](YOUR_CLOUD_RUN_URL)

## Track

**AI for Agriculture** — Build with AI Pwani 2026 Buildathon
