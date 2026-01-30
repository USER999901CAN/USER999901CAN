#!/bin/bash

# Deployment script for retirement planner

echo "🚀 Retirement Planner - GitHub Deployment Script"
echo "================================================"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git repository already exists"
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
if [ -z "$CURRENT_BRANCH" ]; then
    echo "📝 Creating main branch..."
    git checkout -b main
    echo "✅ Main branch created"
else
    echo "✅ Current branch: $CURRENT_BRANCH"
fi

# Add all files
echo ""
echo "📁 Adding files to git..."
git add .

# Show status
echo ""
echo "📊 Git status:"
git status --short

# Commit
echo ""
read -p "Enter commit message (or press Enter for default): " COMMIT_MSG
if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Update retirement planner with scenario management"
fi

git commit -m "$COMMIT_MSG"
echo "✅ Changes committed"

# Check if remote exists
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
if [ -z "$REMOTE_URL" ]; then
    echo ""
    echo "🔗 No remote repository configured"
    echo "Please create a repository on GitHub first:"
    echo "  1. Go to https://github.com/USER999901CAN"
    echo "  2. Click 'New repository'"
    echo "  3. Name it 'retirement-planner'"
    echo "  4. Don't initialize with README (we already have one)"
    echo ""
    read -p "Enter the repository URL (e.g., https://github.com/USER999901CAN/retirement-planner.git): " REPO_URL
    
    if [ ! -z "$REPO_URL" ]; then
        git remote add origin "$REPO_URL"
        echo "✅ Remote added: $REPO_URL"
    else
        echo "❌ No URL provided. Exiting."
        exit 1
    fi
else
    echo "✅ Remote already configured: $REMOTE_URL"
fi

# Push to GitHub
echo ""
echo "🚀 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Go to https://share.streamlit.io/"
    echo "  2. Click 'New app'"
    echo "  3. Select your repository: USER999901CAN/retirement-planner"
    echo "  4. Set main file: app.py"
    echo "  5. Click 'Deploy'"
    echo ""
    echo "Your app will be live at: https://[your-app-name].streamlit.app"
else
    echo ""
    echo "❌ Push failed. Please check the error message above."
    echo ""
    echo "Common issues:"
    echo "  - Authentication: You may need to set up SSH keys or personal access token"
    echo "  - Repository doesn't exist: Create it on GitHub first"
    echo "  - Branch protection: Check repository settings"
fi
