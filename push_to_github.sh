#!/bin/bash
# Upload to GitHub - Run after adding SSH key to GitHub

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║       ASTROLOGICO - PUSHING TO GitHub                        ║"
echo "║       ME0094/astrologico                                     ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

cd /home/user/astrologico

# Verify SSH connection
echo "🔐 Verifying SSH connection to GitHub..."
ssh -T git@github.com 2>&1 | head -3
echo ""

# Check git status
echo "📋 Git status:"
git status --short | head -5
if [ $(git status --short | wc -l) -eq 0 ]; then
    echo "   ✓ All files committed"
else
    echo "   ⚠️  Some files not committed"
fi
echo ""

# Show what will be pushed
echo "📦 Ready to push:"
echo "   Repository: ME0094/astrologico"
echo "   Branch: main"
echo "   Commits: $(git log --oneline | wc -l)"
echo "   Files: $(git ls-files | wc -l)"
echo ""

# Ask for confirmation
echo "🚀 Ready to push to GitHub? (yes/no)"
read confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "⏳ Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║           ✅ PUSH SUCCESSFUL!                                ║"
    echo "║                                                               ║"
    echo "║  Your code is now live at:                                   ║"
    echo "║  https://github.com/ME0094/astrologico                       ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📊 Repository details:"
    git remote -v
    echo ""
    echo "🎉 Congratulations! Your Astrologico project is on GitHub!"
else
    echo ""
    echo "❌ Push failed. Possible causes:"
    echo "   1. SSH key not added to GitHub account"
    echo "   2. SSH connection issue"
    echo "   3. Repository doesn't exist yet"
    echo ""
    echo "💡 Try this to debug:"
    echo "   ssh -T git@github.com"
    echo "   git remote -v"
fi
