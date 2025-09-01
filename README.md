# MoodFlow 🌊💭
### AI-Powered Mood Journal with Monetized Insights

**Transform your emotional journey into actionable insights with cutting-edge AI technology.**

## 🔗 **Links**

- **📊 Pitch Deck**: [View Presentation](https://gamma.app/docs/MoodFlow-AI-Powered-Emotional-Intelligence-yts4y6lfkx2b06q)
- **🚀 Live Demo**: [https://moodflow-65ff8364178a.herokuapp.com/]

---

## 🎯 **The Problem We Solve**

Mental health awareness is growing, but **74% of people** struggle to understand their emotional patterns. Traditional journaling lacks the analytical depth needed for meaningful self-reflection, while professional therapy remains expensive and inaccessible for many.

## ✨ **Our Solution**

**MoodFlow** combines the therapeutic benefits of journaling with advanced AI analysis, offering:

- **🆓 Free Sentiment Analysis** - Instant mood tracking using state-of-the-art AI
- **💎 Premium AI Insights** - Personalized, actionable guidance for emotional growth
- **📊 Visual Analytics** - Track your emotional journey over time
- **💰 Accessible Monetization** - Pay only for the insights you want

---

## 🚀 **Key Features**

### Core Functionality
- ✍️ **Intuitive Journaling** - Clean, distraction-free writing experience
- 🤖 **AI Sentiment Analysis** - Powered by Hugging Face's RoBERTa model
- 📈 **Mood Visualization** - Interactive charts showing emotional trends
- 🌙 **Dark/Light Theme** - Modern UI with user preference persistence

### Premium Features
- 💡 **AI-Generated Insights** - Compassionate, personalized guidance from OpenAI
- 🔒 **Secure Payment Processing** - IntaSend integration for African markets
- 📱 **Responsive Design** - Works seamlessly on all devices

---

## 🛠 **Tech Stack**

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | Python + Flask | RESTful API & Business Logic |
| **Database** | SQLite | Lightweight, embedded storage |
| **Frontend** | HTML5 + CSS3 + JavaScript | Modern, responsive UI |
| **UI Framework** | Bootstrap 5 | Component library & grid system |
| **Charts** | Chart.js | Interactive data visualization |
| **AI (Free)** | Hugging Face API | Sentiment analysis |
| **AI (Premium)** | OpenAI GPT-3.5 | Personalized insights |
| **Payments** | IntaSend | Secure payment processing |
| **Security** | python-dotenv | Environment variable management |

---

## 💰 **Monetization Strategy**

### Revenue Model: **Freemium + Pay-Per-Insight**
- **Free Tier**: Unlimited journaling + sentiment analysis
- **Premium**: KES 50 per AI insight (pay-as-you-go)
- **Target Market**: Young professionals, students, mental health enthusiasts
- **Scalability**: Low infrastructure costs, high-margin digital product

### Why This Works
1. **Low Barrier to Entry** - Users experience value before paying
2. **Micro-transactions** - Affordable pricing for African markets
3. **High Perceived Value** - Personalized AI coaching at fraction of therapy cost
4. **Recurring Engagement** - Daily journaling creates habit formation

---

## 🚀 **Installation & Setup**

### Prerequisites
- Python 3.8+
- Git
- API Keys (see below)

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd moodflow
```

### 2. Create Virtual Environment
```bash
python -m venv moodflow_env
source moodflow_env/bin/activate  # Windows: moodflow_env\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create `.env` file with your API keys:
```bash
# AI Services
HF_API_KEY=hf_your_hugging_face_key
OPENAI_API_KEY=sk-your_openai_key

# Payment Processing
INTASEND_PUBLISHABLE_KEY=ISPubKey_test_your_key
INTASEND_SECRET_KEY=ISSecretKey_test_your_key

# Security
FLASK_SECRET_KEY=your_random_secret_key
```

### 5. Run Application
```bash
python app.py
```

Visit `http://localhost:5000` to access MoodFlow! 🎉

---

## 📖 **How to Use**

### For Users:
1. **Write** - Express your thoughts and feelings freely
2. **Analyze** - Get instant AI-powered sentiment analysis (FREE)
3. **Unlock** - Pay KES 50 for personalized AI insights
4. **Track** - Visualize your emotional journey over time

### For Developers:
1. **Journal API** - POST `/api/entry` with text content
2. **Payment Flow** - POST `/api/create-payment-link` → redirect → webhook processing
3. **Insight Generation** - POST `/api/generate-insight` for premium users
4. **Data Retrieval** - GET `/api/entries` for journal history

---

## 🔒 **Security Features**

- ✅ **Webhook Signature Verification** - Prevents payment fraud
- ✅ **Environment Variable Protection** - API keys never exposed
- ✅ **SQL Injection Prevention** - Parameterized queries
- ✅ **CORS Configuration** - Controlled cross-origin requests
- ✅ **Input Sanitization** - XSS protection

---

## 📊 **API Integrations**

### Hugging Face (Sentiment Analysis)
- **Model**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Purpose**: Free sentiment classification
- **Output**: Emotion label + confidence score

### OpenAI (Premium Insights)
- **Model**: GPT-3.5 Turbo
- **Purpose**: Personalized coaching responses
- **Output**: Supportive, actionable guidance

### IntaSend (Payment Processing)
- **Purpose**: Secure payment links for African markets
- **Features**: Webhook automation, metadata tracking
- **Currency**: KES (Kenyan Shilling)

---

## 🎨 **Design Philosophy**

- **Modern Aesthetics** - Gradient backgrounds, glassmorphism effects
- **Accessibility First** - High contrast, semantic HTML, keyboard navigation
- **Mobile Responsive** - Progressive enhancement for all screen sizes
- **Performance Optimized** - Lightweight assets, efficient API calls

---

## 🔮 **Future Roadmap**

### Phase 1 (Current)
- ✅ Core journaling functionality
- ✅ AI sentiment analysis
- ✅ Payment integration
- ✅ Premium insights

### Phase 2 (3 months)
- 📧 **Email Reminders** - Automated journaling prompts
- 🎯 **Goal Tracking** - Mood improvement targets
- 📱 **PWA Support** - Offline-first mobile experience
- 📊 **Advanced Analytics** - Weekly/monthly mood reports

### Phase 3 (6 months)
- 👥 **Therapist Integration** - Connect with licensed professionals
- 🎵 **Mood-Based Music** - Spotify integration for emotional playlists
- 🔔 **Smart Notifications** - AI-driven check-in recommendations
- 💼 **Enterprise Packages** - Workplace mental health solutions

---

## 💡 **Market Opportunity**

### Target Market Size
- **Global Mental Health Apps**: $5.6B market by 2026
- **African Digital Health**: 40% annual growth rate
- **Journaling Apps**: 15M+ active users globally

### Competitive Advantage
1. **African Payment Integration** - First mood journal with IntaSend
2. **Hybrid AI Approach** - Free analysis + premium insights
3. **Cultural Sensitivity** - Designed for African user preferences
4. **Affordable Pricing** - Micro-transactions vs. expensive subscriptions

---

## 🏆 **Technical Achievements**

- **Clean Architecture** - Separation of concerns, maintainable codebase
- **API-First Design** - RESTful endpoints for future mobile apps
- **Real-time Analytics** - Dynamic chart updates without page refresh
- **Secure Payment Flow** - Production-ready webhook handling
- **Modern Frontend** - CSS Grid, Flexbox, smooth animations
- **Error Handling** - Graceful degradation and user feedback

---

## 🤝 **Credits & Acknowledgments**

- **Hugging Face** - Sentiment analysis AI models
- **OpenAI** - GPT-3.5 for personalized insights
- **IntaSend** - Payment processing for African markets
- **Chart.js** - Beautiful data visualizations
- **Bootstrap** - Responsive UI framework

---

## 📄 **License**

MIT License - See LICENSE file for details

---

**Built with ❤️ for the Vibe Coding 4-3-2 Hackathon**

*Empowering emotional intelligence through technology* 🚀