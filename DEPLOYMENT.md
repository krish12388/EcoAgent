# 🚀 Render Deployment Guide

## Prerequisites
- Render account (https://render.com)
- GitHub repository connected to Render
- Groq API key

## Quick Deploy

### Option 1: Using render.yaml (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Render deployment config"
   git push origin master
   ```

2. **Create New Project on Render**
   - Go to https://dashboard.render.com
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`

3. **Set Environment Variables**
   - Go to your service settings
   - Add environment variables:
     - `GROQ_API_KEY`: Your Groq API key (mark as secret)
     - Other vars are auto-configured from render.yaml

### Option 2: Manual Setup

#### Backend Deployment

1. **Create Web Service**
   - Dashboard → New → Web Service
   - Connect repository: `https://github.com/yourusername/EcoAgent`
   - Name: `ecoagent-backend`
   - Runtime: Python 3
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Environment Variables**
   ```env
   PYTHON_VERSION=3.12.7
   GROQ_API_KEY=your_groq_api_key_here
   AGENT_MODEL=llama-3.3-70b-versatile
   AGENT_TEMPERATURE=0.7
   API_HOST=0.0.0.0
   ```

3. **Health Check**
   - Path: `/health`

#### Frontend Deployment

1. **Create Static Site**
   - Dashboard → New → Static Site
   - Connect repository
   - Name: `ecoagent-frontend`
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/dist`

2. **Update API URL**
   - Edit `frontend/src/services/api.js`
   - Change `API_BASE_URL` to your backend URL:
     ```javascript
     const API_BASE_URL = 'https://ecoagent-backend.onrender.com/api';
     ```

## Troubleshooting

### Build Fails with pandas Error
- Ensure Python version is 3.12.7 (not 3.14)
- Check `runtime.txt` exists with `python-3.12.7`
- Update pandas: `pandas>=2.2.3`

### Service Won't Start
- Check logs: Dashboard → Service → Logs
- Verify GROQ_API_KEY is set correctly
- Test locally first: `python backend/main.py`

### Frontend Can't Connect to Backend
- Check CORS settings in `backend/main.py`
- Add your frontend URL to `allow_origins`:
  ```python
  allow_origins=[
      "https://ecoagent-frontend.onrender.com",
      "http://localhost:5173"
  ]
  ```

### Free Tier Limitations
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- 750 hours/month free (upgrade for always-on)

## Production Checklist

- [ ] API key rotated and stored as secret
- [ ] CORS configured for production domain
- [ ] Health check endpoint working
- [ ] Frontend API URL updated
- [ ] Error tracking enabled (Sentry)
- [ ] Monitoring set up
- [ ] Backup strategy in place

## Monitoring

### Check Service Health
```bash
curl https://ecoagent-backend.onrender.com/health
```

### View Logs
- Dashboard → Service → Logs
- Filter by level: Info, Warning, Error

### Metrics
- Dashboard → Service → Metrics
- Monitor: CPU, Memory, Request rate

## Scaling

### Upgrade Plans
- **Starter**: $7/month - Always on, custom domain
- **Standard**: $25/month - More resources
- **Pro**: $85/month - High performance

### Horizontal Scaling
- Render auto-scales based on traffic
- Configure in service settings

## Cost Optimization

1. **Use Free Tier Wisely**
   - Combine multiple services in one repository
   - Optimize cold start time

2. **Reduce API Calls**
   - Set `budget_level=low` in analysis
   - Cache results when possible
   - Limit `num_rooms` and `num_buildings`

3. **Monitor Groq Usage**
   - Check usage at https://console.groq.com
   - Set up alerts for quota limits

## Support

- Render Docs: https://render.com/docs
- Community Forum: https://community.render.com
- Status Page: https://status.render.com

---

**Deployment Time:** ~5-10 minutes
**First Deploy:** May take longer due to dependency installation
