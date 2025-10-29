# 🚀 GitHub & Vercel Deployment Guide

## Current Status

✅ **All 7 AI Models Trained** - 86.76% average accuracy  
✅ **Git Repository Initialized** - Local commit complete  
✅ **Vercel Configuration Ready** - `frontend/vercel.json` created  
⏳ **GitHub Remote** - Not configured yet  
⏳ **Vercel Deployment** - Pending

---

## 📋 Step-by-Step Deployment Guide

### PART 1: GitHub Setup (5 minutes)

#### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `medai-pro`
3. Description: `AI-powered medical diagnosis system with 7 organ-specific models`
4. Visibility: **Private** (recommended for medical data)
5. **DO NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

#### Step 2: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Run these in your terminal:

```bash
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/medai-pro.git

# Verify remote
git remote -v

# Push to GitHub
git push -u origin master
```

**Example:**
```bash
git remote add origin https://github.com/johndoe/medai-pro.git
git push -u origin master
```

#### Step 3: Verify Upload

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/medai-pro`
2. You should see all files uploaded
3. Check that `backend/models/weights/` contains your trained models

---

### PART 2: Vercel Deployment (10 minutes)

#### Step 1: Install Vercel CLI (Optional)

```bash
npm install -g vercel
```

#### Step 2: Deploy Frontend to Vercel

**Option A: Using Vercel Dashboard (Recommended)**

1. Go to https://vercel.com/
2. Sign in with GitHub
3. Click "Add New Project"
4. Import your `medai-pro` repository
5. Configure project:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Install Command:** `npm install --legacy-peer-deps`

6. Add Environment Variables:
   ```
   VITE_CLERK_PUBLISHABLE_KEY=your_clerk_key_here
   VITE_API_URL=your_backend_url_here
   ```

7. Click "Deploy"

**Option B: Using Vercel CLI**

```bash
cd frontend
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? medai-pro
# - Directory? ./
# - Override settings? Yes
#   - Build Command: npm run build
#   - Output Directory: dist
#   - Development Command: npm run dev
```

#### Step 3: Configure Environment Variables

In Vercel Dashboard:

1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add these variables:

```
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
VITE_API_URL=https://your-backend-url.com
```

4. Redeploy the project

---

### PART 3: Backend Deployment (15 minutes)

#### Option A: Deploy to Railway (Recommended)

1. Go to https://railway.app/
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose `medai-pro` repository
6. Configure:
   - **Root Directory:** `backend`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

7. Add Environment Variables:
   ```
   DATABASE_URL=postgresql://...
   CLERK_SECRET_KEY=sk_test_...
   CLERK_PUBLISHABLE_KEY=pk_test_...
   JWT_SECRET=your_secret_here
   ENVIRONMENT=production
   ```

8. Deploy

#### Option B: Deploy to Render

1. Go to https://render.com/
2. Sign in with GitHub
3. Click "New +" → "Web Service"
4. Connect `medai-pro` repository
5. Configure:
   - **Name:** medai-pro-backend
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

6. Add Environment Variables (same as Railway)
7. Deploy

---

### PART 4: Database Setup (10 minutes)

#### Option A: Supabase (Recommended)

1. Go to https://supabase.com/
2. Create new project
3. Get connection string from Settings → Database
4. Update `DATABASE_URL` in backend environment variables

#### Option B: Railway PostgreSQL

1. In Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Copy connection string
4. Update `DATABASE_URL` in backend environment variables

---

### PART 5: Final Configuration (5 minutes)

#### Update Frontend Environment Variables

After backend is deployed, update Vercel environment variables:

```
VITE_API_URL=https://your-backend-url.railway.app
```

Or for Render:
```
VITE_API_URL=https://medai-pro-backend.onrender.com
```

#### Redeploy Frontend

In Vercel Dashboard:
1. Go to Deployments
2. Click "..." on latest deployment
3. Click "Redeploy"

---

## 🔍 Verification Checklist

### ✅ GitHub

- [ ] Repository created on GitHub
- [ ] Local repository connected to GitHub remote
- [ ] All files pushed to GitHub
- [ ] Models visible in `backend/models/weights/`

### ✅ Vercel (Frontend)

- [ ] Project deployed to Vercel
- [ ] Environment variables configured
- [ ] Frontend accessible at Vercel URL
- [ ] No build errors

### ✅ Backend (Railway/Render)

- [ ] Backend deployed successfully
- [ ] Environment variables configured
- [ ] Database connected
- [ ] API endpoints accessible

### ✅ Integration

- [ ] Frontend can connect to backend
- [ ] Authentication working (Clerk)
- [ ] AI models loading correctly
- [ ] File uploads working

---

## 🐛 Troubleshooting

### Issue: Git Push Fails

**Error:** `failed to push some refs`

**Solution:**
```bash
git pull origin master --allow-unrelated-histories
git push -u origin master
```

### Issue: Vercel Build Fails

**Error:** `npm install failed`

**Solution:**
Update build command to:
```bash
npm install --legacy-peer-deps && npm run build
```

### Issue: Backend Models Not Loading

**Error:** `FileNotFoundError: models/weights/...`

**Solution:**
1. Check that models are in Git repository
2. Verify `.gitignore` doesn't exclude model files
3. Re-push to GitHub if needed

### Issue: Large File Upload Fails

**Error:** `file exceeds GitHub's file size limit of 100 MB`

**Solution:**
Use Git LFS for large model files:
```bash
git lfs install
git lfs track "*.pth"
git lfs track "*.pkl"
git add .gitattributes
git commit -m "Add Git LFS tracking"
git push
```

---

## 📊 Expected Deployment Times

| Step | Time | Status |
|------|------|--------|
| GitHub Setup | 5 min | ⏳ Pending |
| Vercel Frontend | 10 min | ⏳ Pending |
| Backend Deployment | 15 min | ⏳ Pending |
| Database Setup | 10 min | ⏳ Pending |
| Final Configuration | 5 min | ⏳ Pending |
| **Total** | **45 min** | ⏳ Pending |

---

## 🎯 Quick Commands Reference

### GitHub

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/medai-pro.git

# Push to GitHub
git push -u origin master

# Check status
git status

# Add all changes
git add .

# Commit
git commit -m "Your message"

# Push updates
git push
```

### Vercel

```bash
# Deploy
vercel

# Deploy to production
vercel --prod

# Check deployment status
vercel ls
```

---

## 📞 Next Steps

1. **Create GitHub Repository** (5 min)
   - Go to https://github.com/new
   - Create `medai-pro` repository

2. **Push to GitHub** (2 min)
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/medai-pro.git
   git push -u origin master
   ```

3. **Deploy to Vercel** (10 min)
   - Go to https://vercel.com/
   - Import GitHub repository
   - Configure and deploy

4. **Deploy Backend** (15 min)
   - Choose Railway or Render
   - Connect GitHub repository
   - Configure and deploy

5. **Test Everything** (10 min)
   - Test frontend at Vercel URL
   - Test backend API endpoints
   - Test AI model predictions

---

## ✅ Success Criteria

- ✅ GitHub repository created and pushed
- ✅ Frontend deployed to Vercel
- ✅ Backend deployed to Railway/Render
- ✅ Database connected
- ✅ All 7 AI models working
- ✅ Authentication working
- ✅ Full application accessible online

---

**Total Deployment Time:** ~45 minutes  
**Difficulty:** Medium  
**Status:** Ready to deploy

**Let me know when you're ready to start, and I'll guide you through each step!**

