# MoodFlow Deployment Guide 🚀

## Quick Deployment Options

### Option 1: Heroku (Recommended for Demo)
```bash
# Install Heroku CLI
# Create Heroku app
heroku create moodflow-demo

# Set environment variables
heroku config:set HF_API_KEY=your_key
heroku config:set OPENAI_API_KEY=your_key
heroku config:set INTASEND_PUBLISHABLE_KEY=your_key
heroku config:set INTASEND_SECRET_KEY=your_key
heroku config:set FLASK_SECRET_KEY=your_secret

# Deploy
git push heroku main
```

### Option 2: Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Option 3: Render
1. Connect GitHub repository
2. Set environment variables in dashboard
3. Auto-deploy from main branch

## Environment Variables Checklist ✅

Before deployment, ensure these are set:
- [ ] `HF_API_KEY` - Hugging Face API token
- [ ] `OPENAI_API_KEY` - OpenAI API key
- [ ] `INTASEND_PUBLISHABLE_KEY` - IntaSend public key
- [ ] `INTASEND_SECRET_KEY` - IntaSend secret key
- [ ] `FLASK_SECRET_KEY` - Random secret for sessions

## API Key Setup Instructions

### Hugging Face (Free)
1. Visit https://huggingface.co/
2. Create account → Settings → Access Tokens
3. Create new token with "Read" permissions

### OpenAI (Free Tier Available)
1. Visit https://platform.openai.com/
2. Create account → API Keys
3. Create new secret key

### IntaSend (Free Sandbox)
1. Visit https://sandbox.intasend.com/
2. Create account → API Keys
3. Get both publishable and secret keys

## Production Checklist 📋

### Security
- [ ] Change `test=True` to `test=False` in IntaSend config
- [ ] Set `FLASK_ENV=production`
- [ ] Enable HTTPS/SSL
- [ ] Add rate limiting
- [ ] Set up monitoring

### Database
- [ ] Migrate from SQLite to PostgreSQL
- [ ] Set up database backups
- [ ] Add database indexes for performance

### Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Add application monitoring
- [ ] Configure log aggregation

## Demo Day Tips 🎯

### Live Demo Script
1. **Open app** - Show modern, responsive design
2. **Write journal entry** - Demonstrate AI sentiment analysis
3. **Show payment flow** - Click "Unlock Insight" button
4. **Payment success** - Return to app, show AI insight
5. **Show chart** - Visualize mood trends over time

### Backup Plan
- Have 3-4 pre-written journal entries ready
- Screenshot the payment flow in case of connectivity issues
- Prepare video demo as fallback

### Key Selling Points
- "Built in 5 days for the hackathon"
- "Real money transactions with IntaSend"
- "Production-ready codebase with security best practices"
- "Targets underserved African market"