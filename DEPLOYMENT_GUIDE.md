# Deployment Guide - Streamlit Community Cloud

## Prerequisites
- GitHub account
- Streamlit Community Cloud account (free at https://streamlit.io/cloud)

## Step 1: Push to GitHub

```bash
cd retirement_planner

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Canadian Retirement Planning Calculator"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/USER999901CAN/retirement-planner.git

# Push to GitHub
git push -u origin main
```

## Step 2: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select your GitHub repository: `USER999901CAN/retirement-planner`
4. Set main file path: `app.py`
5. Click "Deploy"

Your app will be live at: `https://[your-app-name].streamlit.app`

## Step 3: Configure (Optional)

### Custom Domain
- Go to app settings → General
- Add custom domain if you have one

### Secrets (if needed)
- Go to app settings → Secrets
- Add any API keys or sensitive data

## Features That Work on Streamlit Cloud

✅ **Scenario Management**
- Upload/download scenarios (browser-based)
- Save multiple scenarios in session
- Calculate all scenarios at once
- Scenario comparison

✅ **All Calculations**
- Retirement projections
- Monte Carlo simulations
- Export to CSV/Excel/PDF

✅ **Session Persistence**
- Scenarios persist during your session
- Lost on browser refresh (by design)

## Important Notes

1. **No File System Storage**: Scenarios are stored in session state, not files
2. **Session-Based**: Each user has their own isolated session
3. **Free Tier Limits**: 
   - 1 GB RAM
   - 1 CPU core
   - Should be sufficient for this app

## Troubleshooting

### App Won't Start
- Check requirements.txt has all dependencies
- Check Python version compatibility (3.8+)

### Slow Performance
- Monte Carlo with 10,000 simulations may take 10-20 seconds
- This is normal and expected

### Scenarios Not Persisting
- This is by design - scenarios are session-based
- Users download/upload JSON files for persistence

## Updating Your App

```bash
# Make changes to your code
git add .
git commit -m "Description of changes"
git push

# Streamlit Cloud auto-deploys on push
```

## Support

- Streamlit Docs: https://docs.streamlit.io/
- Community Forum: https://discuss.streamlit.io/
