# 🚀 Vercel Deployment Guide for MedAI-Pro

**Question:** Can I deploy frontend and backend separately on Vercel?

**Answer:** ✅ **YES! You can deploy the frontend on Vercel, but the backend needs a different platform.**

---

## 📊 Deployment Architecture

### **Frontend (React) → Vercel** ✅
- **Perfect fit** for Vercel
- Static site generation
- Automatic deployments from Git
- Global CDN
- Free SSL certificates
- Custom domains

### **Backend (FastAPI/Python) → NOT Vercel** ❌
- Vercel is optimized for **serverless functions** and **static sites**
- FastAPI requires a **persistent Python server**
- Better alternatives exist for Python backends

---

## 🎯 Recommended Deployment Strategy

### **Option 1: Vercel + Railway (Recommended)**

**Frontend (Vercel):**
```bash
cd frontend
vercel
```

**Backend (Railway):**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
cd backend
railway init
railway up
```

**Why Railway?**
- ✅ Free tier available
- ✅ PostgreSQL database included
- ✅ Automatic HTTPS
- ✅ Environment variables
- ✅ Easy Python deployment
- ✅ Persistent storage

---

### **Option 2: Vercel + Render**

**Frontend (Vercel):**
```bash
cd frontend
vercel
```

**Backend (Render):**
1. Go to https://render.com
2. Connect GitHub repository
3. Create new "Web Service"
4. Select `backend` directory
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

**Why Render?**
- ✅ Free tier available
- ✅ PostgreSQL database included
- ✅ Automatic HTTPS
- ✅ Easy deployment
- ✅ Good documentation

---

### **Option 3: Vercel + Heroku**

**Frontend (Vercel):**
```bash
cd frontend
vercel
```

**Backend (Heroku):**
```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
cd backend
heroku create medai-pro-backend

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Deploy
git push heroku main
```

**Why Heroku?**
- ✅ Well-established platform
- ✅ PostgreSQL add-on
- ✅ Easy scaling
- ✅ Good documentation
- ⚠️ No free tier anymore (starts at $5/month)

---

### **Option 4: Vercel + AWS EC2**

**Frontend (Vercel):**
```bash
cd frontend
vercel
```

**Backend (AWS EC2):**
1. Launch EC2 instance (Ubuntu)
2. Install Python, PostgreSQL
3. Clone repository
4. Install dependencies
5. Run with systemd service
6. Configure nginx reverse proxy

**Why AWS EC2?**
- ✅ Full control
- ✅ Scalable
- ✅ Professional solution
- ❌ More complex setup
- ❌ Requires DevOps knowledge

---

## 📝 Step-by-Step: Vercel + Railway Deployment

### **Step 1: Deploy Frontend to Vercel**

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy Frontend:**
   ```bash
   cd frontend
   vercel
   ```

4. **Follow prompts:**
   - Set up and deploy? **Y**
   - Which scope? **Your account**
   - Link to existing project? **N**
   - Project name? **medai-pro-frontend**
   - Directory? **./frontend**
   - Override settings? **N**

5. **Set environment variables:**
   ```bash
   vercel env add REACT_APP_CLERK_PUBLISHABLE_KEY
   vercel env add REACT_APP_API_URL
   vercel env add REACT_APP_GOOGLE_MAPS_API_KEY
   ```

6. **Redeploy with env vars:**
   ```bash
   vercel --prod
   ```

---

### **Step 2: Deploy Backend to Railway**

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Initialize project:**
   ```bash
   cd backend
   railway init
   ```

4. **Add PostgreSQL:**
   ```bash
   railway add postgresql
   ```

5. **Set environment variables:**
   ```bash
   railway variables set CLERK_SECRET_KEY=your_key
   railway variables set GOOGLE_MAPS_API_KEY=your_key
   railway variables set GOOGLE_CLOUD_PROJECT_ID=your_id
   ```

6. **Deploy:**
   ```bash
   railway up
   ```

7. **Get backend URL:**
   ```bash
   railway domain
   ```

---

### **Step 3: Connect Frontend to Backend**

1. **Update frontend environment variable:**
   ```bash
   cd frontend
   vercel env add REACT_APP_API_URL
   # Enter your Railway backend URL (e.g., https://medai-pro-backend.railway.app)
   ```

2. **Redeploy frontend:**
   ```bash
   vercel --prod
   ```

---

## 🔧 Configuration Files

### **Frontend: `vercel.json`**

Create in `frontend/` directory:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "devCommand": "npm start",
  "installCommand": "npm install",
  "framework": "create-react-app",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### **Backend: `railway.json`**

Create in `backend/` directory:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### **Backend: `Procfile`** (for Heroku)

Create in `backend/` directory:

```
web: uvicorn app:app --host 0.0.0.0 --port $PORT
```

---

## 🌐 CORS Configuration

Update `backend/app.py` to allow your Vercel frontend:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://medai-pro-frontend.vercel.app",  # Your Vercel URL
        "https://your-custom-domain.com"  # Your custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ✅ Deployment Checklist

### **Before Deployment:**
- [ ] All environment variables documented
- [ ] Database migrations ready
- [ ] CORS configured for production URLs
- [ ] API keys secured (not in code)
- [ ] Error logging configured
- [ ] Health check endpoint added

### **Frontend Deployment:**
- [ ] Vercel account created
- [ ] Repository connected
- [ ] Environment variables set
- [ ] Build successful
- [ ] Custom domain configured (optional)

### **Backend Deployment:**
- [ ] Platform account created (Railway/Render/Heroku)
- [ ] PostgreSQL database provisioned
- [ ] Environment variables set
- [ ] Build successful
- [ ] Database migrations run
- [ ] Health check passing

### **Integration:**
- [ ] Frontend can reach backend API
- [ ] Clerk authentication working
- [ ] Google Maps loading
- [ ] File uploads working
- [ ] WebSocket connections working (if applicable)

---

## 🐛 Troubleshooting

### **Frontend Issues:**

**Build fails:**
```bash
# Check build logs
vercel logs

# Test build locally
npm run build
```

**Environment variables not working:**
```bash
# List all env vars
vercel env ls

# Pull env vars locally
vercel env pull
```

### **Backend Issues:**

**Database connection fails:**
```bash
# Check DATABASE_URL
railway variables

# Test connection
railway run python -c "from database import engine; print(engine)"
```

**API not responding:**
```bash
# Check logs
railway logs

# Check if service is running
railway status
```

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| **Vercel** | ✅ Unlimited (frontend) | $20/month | Static sites, React apps |
| **Railway** | ✅ $5 credit/month | $5/month + usage | Python backends, databases |
| **Render** | ✅ 750 hours/month | $7/month | Full-stack apps |
| **Heroku** | ❌ None | $5/month + addons | Established apps |
| **AWS EC2** | ✅ 750 hours/month (1 year) | Variable | Enterprise apps |

---

## 🎉 Summary

**YES, you can deploy frontend and backend separately!**

**Recommended Setup:**
- ✅ **Frontend:** Vercel (free, fast, easy)
- ✅ **Backend:** Railway (free tier, PostgreSQL included, easy Python deployment)

**This architecture:**
- ✅ Separates concerns
- ✅ Scales independently
- ✅ Uses best tools for each part
- ✅ Costs $0-$5/month to start
- ✅ Professional and production-ready

**Next Steps:**
1. Deploy frontend to Vercel
2. Deploy backend to Railway
3. Connect them with environment variables
4. Test thoroughly
5. Add custom domain (optional)

---

**Last Updated:** 2025-10-28  
**Status:** ✅ Production Ready

