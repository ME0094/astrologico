#!/bin/bash
# ASTROLOGICO - GitHub Upload Instructions
# Following this script will push your local repository to GitHub

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ASTROLOGICO v2.0 - GitHub Upload Guide                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Error: Git repository not initialized"
    echo "Run: git init"
    exit 1
fi

echo "✓ Git repository ready"
echo ""

# Option 1: Using HTTPS (Personal Access Token)
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  OPTION 1: Push with HTTPS (Using Personal Access Token)      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Step 1: Create a new repository on GitHub"
echo "  a) Go to https://github.com/new"
echo "  b) Create repository named: astrologico"
echo "  c) Description: Professional astrological calculator with AI"
echo "  d) Choose: Public (recommended for open source)"
echo "  e) DO NOT initialize with README (we have one)"
echo "  f) Click 'Create repository'"
echo ""

echo "Step 2: Create a Personal Access Token"
echo "  a) Go to https://github.com/settings/tokens/new"
echo "  b) Name: astrologico-push"
echo "  c) Expiration: 90 days"
echo "  d) Select scopes: repo (full control)"
echo "  e) Click 'Generate token'"
echo "  f) Copy the token (you won't see it again!)"
echo ""

echo "Step 3: Push to GitHub"
echo "  Replace GITHUB_USERNAME and TOKEN below:"
echo ""
echo "  git remote add origin https://GITHUB_TOKEN@github.com/GITHUB_USERNAME/astrologico.git"
echo "  git branch -M main"
echo "  git push -u origin main"
echo ""
echo "EXAMPLE:"
echo "  git remote add origin https://ghp_xxxxxxxxxxxx@github.com/myusername/astrologico.git"
echo "  git branch -M main"
echo "  git push -u origin main"
echo ""

# Option 2: Using SSH Key
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  OPTION 2: Push with SSH (Recommended for repeated use)       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Step 1: Check if you have SSH key"
echo "  ls -la ~/.ssh/id_rsa"
echo ""

echo "Step 2: If no SSH key, generate one"
echo "  ssh-keygen -t ed25519 -C 'your_email@example.com'"
echo ""

echo "Step 3: Add SSH key to GitHub"
echo "  a) Go to https://github.com/settings/keys"
echo "  b) Click 'New SSH key'"
echo "  c) Title: astrologico-linux"
echo "  d) Paste your public key:"
echo "     cat ~/.ssh/id_rsa.pub"
echo "  e) Click 'Add SSH key'"
echo ""

echo "Step 4: Create repository on GitHub"
echo "  (Same as Option 1, Step 1)"
echo ""

echo "Step 5: Push with SSH"
echo "  Replace GITHUB_USERNAME:"
echo ""
echo "  git remote add origin git@github.com:GITHUB_USERNAME/astrologico.git"
echo "  git branch -M main"
echo "  git push -u origin main"
echo ""

# Option 3: Using GitHub CLI
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  OPTION 3: Using GitHub CLI (Easiest if you have 'gh')        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Step 1: Install GitHub CLI (if not already installed)"
echo "  Linux: sudo apt-get install gh"
echo "  macOS: brew install gh"
echo ""

echo "Step 2: Authenticate"
echo "  gh auth login"
echo "  (Choose: GitHub.com, HTTPS, Paste an authentication token)"
echo ""

echo "Step 3: Create and push in one command"
echo "  gh repo create astrologico --public --source=. --remote=origin --push"
echo ""

# Quick check of repo status
echo "════════════════════════════════════════════════════════════════"
echo "📊  CURRENT GIT STATUS"
echo "════════════════════════════════════════════════════════════════"
echo ""
git log --oneline -1
echo ""
git status
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "📝  QUICK REFERENCE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Files ready to push:"
git ls-files | wc -l
echo "files"
echo ""
echo "Total size:"
du -sh .
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ VERIFICATION CHECKLIST"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Before pushing, verify:"
echo "  ☐ You've created a GitHub account (https://github.com/join)"
echo "  ☐ You've created a new repository on GitHub"
echo "  ☐ You have authentication ready (Token, SSH key, or gh CLI)"
echo "  ☐ All files are committed (git status shows 'nothing to commit')"
echo "  ☐ You choose the right remote URL (HTTPS or SSH)"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "🚀 NEXT STEPS"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Choose your preferred method above (1, 2, or 3)"
echo "Follow the step-by-step instructions"
echo "Then run the push command"
echo ""
echo "Questions? Check:"
echo "  - GitHub Help: https://docs.github.com/en/get-started"
echo "  - Git Guide: https://git-scm.com/doc"
echo ""
