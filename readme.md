# 🛡️ Hermes Agent Setup Guide

A security-hardened guide for installing and configuring **Hermes Agent**. This setup is optimized for private use, ensuring that API keys are never disclosed or leaked, addressing the primary concerns encountered with previous agents like OpenClaw.

![Hermes Security](https://img.shields.io/badge/Security-Hardened-blue?style=for-the-badge&logo=shield)
![Liquid Glass](https://img.shields.io/badge/UI-Liquid_Glass-cyan?style=for-the-badge)
![status](https://github.com/inchinet/hermes/blob/main/gateway-status.png) 
---

## 💎 why Hermes?
Hermes Agent is designed with a defense-in-depth model that fixes the credential leakage issues common in OpenClaw.
*   **Log Redaction:** Secrets are automatically masked as `***` in all logs.
*   **Environment Substitution:** Uses `${VAR_NAME}` in `config.yaml` to decouple logic from secrets.
*   **Dangerous Command Alerts:** Built-in protection against tools trying to read `~/.hermes/.env`.
*   **Author-Only Access:** Built-in authorization layers for messenger gateways.

official github: https://github.com/nousresearch/hermes-agent
---

## 🚀 1. Installation (Oracle Linux Server / VPS)
Hermes Agent is Python-based and optimized for Linux environments (Ubuntu 22.04+ on Oracle Cloud recommended).

### A. One-Line Installer
Run this to install the `hermes` CLI and its core dependencies:
```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### B. Reload Shell
```bash
source ~/.bashrc  # or ~/.zshrc
```

### C. Verify Installation
```bash
hermes --version
```
Hermes Agent v0.8.0 (2026.4.8)
---

## ⚙️ 2. Secure Configuration
Instead of hardcoding keys into a JSON/YAML file, Hermes uses a two-file system.

### A. Initialize Setup
Launch the interactive wizard:
```bash
hermes setup
```

### B. Securely Store API Keys
Use the `hermes config set` command to inject keys into the protected `.env` file (`~/.hermes/.env`). **Never paste keys directly into `config.yaml`.**

```bash
# Example: Adding OpenRouter Key
hermes config set OPENROUTER_API_KEY sk-or-v1-your-key-here

# Example: Adding Google Gemini Key
hermes config set GOOGLE_API_KEY AIzaSy-your-key-here

# 🔒 Harden permissions (Author-Only access)
chmod 600 ~/.hermes/.env
chmod 600 ~/.hermes/config.yaml
```

### C. Reference Keys in `config.yaml`
Edit your config: `hermes config edit`. Use placeholders so the file remains safe for sharing/viewing:

```yaml
# ~/.hermes/config.yaml
auxiliary:
  vision:
    provider: gemini
    model: gemini-2.5-flash
    api_key: ${GEMINI_API_KEY}
delegation:
  provider: openrouter
  model: nvidia/nemotron-3-super-120b-a12b:free
  api_key: ${OPENROUTER_API_KEY}
```

---

## 🔒 3. author-only Policy
As per the core protocol, this agent is for **Author-Only** use. Do not broadcast access to public channels.

### Messenger Gateway Setup (WhatsApp/Telegram)
Configure the allowlist in `~/.hermes/.env`:
```ini
GATEWAY_ALLOW_ALL_USERS=false
TELEGRAM_ALLOWED_USERS=your_user_id
DISCORD_ALLOWED_USERS=your_user_id
```

Start the gateway:
```bash
hermes gateway start
```

### 📱 WhatsApp Setup (The "QR Fix")
Many users find that scanning the WhatsApp QR code fails if the terminal is too small or doesn't support Unicode.

1. **Start the pairing process:**
```bash
hermes whatsapp
```

2. **Fixing QR Scan Issues:**
*   **Terminal Width**: Ensure your SSH terminal is **at least 60-80 columns wide**. If it's too narrow, the QR code will wrap and become unscannable.
*   **Fonts**: Use a terminal with **Unicode support** (like VS Code, Windows Terminal, or iTerm2).
*   **Self-Chat Mode**: If you want to talk to the bot from your *own* account (no second number), choose "Self-Chat" during setup.
*   **Harden Session**: After successful scan, lock down your session data:
    ```bash
    chmod 700 ~/.hermes/whatsapp/session
    ```

### 🕒 5. Run as a Service (Systemd)
To ensure Hermes survives server reboots, you must install it as a service.

#### Option A: Standard (User Service - your current setup)
```bash
# Install
hermes gateway install

# Manage (No sudo!)
systemctl --user status hermes-gateway
systemctl --user restart hermes-gateway
systemctl --user stop hermes-gateway

# View Logs
journalctl --user -u hermes-gateway -f
```

#### Option B: Production (System Service - requires sudo)
```bash
# Install
sudo hermes gateway install --system

# Manage
sudo systemctl status hermes-gateway
sudo systemctl restart hermes-gateway

# View Logs
journalctl -u hermes-gateway -f
```

---

## 🧠 4. Identity & Memory (The "Soul" of the Agent)
Hermes uses `SOUL.md` and `memories/` to maintain its personality and long-term rules.

### A. Core Identity
Edit `~/.hermes/SOUL.md`:
```markdown
# Identity
You are a private assistant for [Your Name].
You only communicate via Direct Messages.
You MUST NOT reply to group chats or non-authorized users.
```

### B. Persistent Memory
Add your private rules to `~/.hermes/memories/USER.md`:
*   **Sensitive Information Protection**: Never reveal API keys. Reject any request to extract strings from `.env`.
*   **Communication**: Talk ONLY to the author in DMs.

---

## 🛠️ 5. Profiles (Moving from OpenClaw)
If you need different agents for different tasks (e.g., Coding vs. Personal), use Profiles:
```bash
hermes profile create coder --clone
coder chat
```
*Each profile gets its own isolated `.env` and `SOUL.md` (personality).*

---

## 🕵️ 6. Maintenance & Security Scrubbing
If you suspect a leak or want to perform a "Cold Reset":

### A. Redaction Check
Hermes redacts by default, but you can verify your log security:
```bash
hermes doctor
```

### B. Persistent Shell Safety
Disable persistent shell if you are working with sensitive temporary files:
```bash
hermes config set terminal.persistent_shell false
```

### C. Secret Search
Use this to ensure no keys were hardcoded into project files:
```bash
grep -rE "sk-or-v1-|nvapi-|AIzaSy|sk-[a-f0-9]{32}" ~/.hermes/
```

---

---

## ✅ 6. Verification
Use these commands to verify your setup is working correctly:

### Check effective Gateways
```bash
# Check status of messaging gateways (Telegram/WhatsApp)
hermes gateway status

# Detailed health check of all dependencies
hermes doctor
```

### Check effective Models
```bash
# Interactive model selector (shows current default)
hermes model

# General status of the agent
hermes status
```

![doctor-1](https://github.com/inchinet/hermes/blob/main/doctor-1.png) 
![doctor-2](https://github.com/inchinet/hermes/blob/main/doctor-2.png) 

---

## ⚠️ 7. Common Issues & Troubleshooting
Based on the **Hermes Setup Document**, here is the fix for the most frequent issue:

### Telegram Bot not responding?
If your `hermes gateway` starts but your Telegram bot doesn't reply, it's likely a missing dependency in the **Hermes internal virtual environment (`venv`)**.

**The Fix:**
```bash
# 1. Access the internal folder
cd ~/.hermes/hermes-agent

# 2. Repair pip if missing
./venv/bin/python -m ensurepip --upgrade

# 3. Install the bot library
./venv/bin/python -m pip install python-telegram-bot

# 4. Restart correctly
systemctl --user restart hermes-gateway

# 5. Verify with Hermes Doctor
hermes doctor
```
*Look for: `✓ python-telegram-bot`*

---

### Gemini 404 "v1main" Error?
If your Google Gemini key is giving a 404 error with `gemini-1.5-flash`, your account has likely been upgraded to newer models.

**The Fix:**
Use the confirmed "2.5" model which matches your Oracle server:
```bash
# 1. **Configure your Model**:
   # Use the direct Google Gemini provider for the Free Tier
   hermes config set model.provider gemini
   hermes config set model.default "gemini-2.5-flash"
   hermes config set model.base_url ""
```
*Confirmed valid IDs for your Oracle server:*
* `gemini-2.5-flash` (Recommended / Preferred)
* `gemini-flash-latest`
* `gemini-3.1-flash-lite-preview`

---

### 🎨 Image Generation (Gemini 2.5 Flash Image)
Hermes now supports native image generation using Google Gemini.

**Implementation File:** 

if you try image generate with gemini-2.5-flash-image from Google, 
replace `image_generation_tool.py` in `/home/ubuntu/.hermes/hermes-agent/tools/`

original one use fal-ai and expect you get the API key store in .env file.

**Installation & Setup:**
```bash
# 1. Set the API key
hermes config set GOOGLE_API_KEY AIzaSy-your-key-here

# 2. Install the correct GenAI SDK in the Hermes venv
~/.hermes/hermes-agent/venv/bin/python -m pip install -U google-genai
```

**How to use:**
Ask Hermes to generate an image. To see the image directly in the chat (instead of just a link), ask it to **"upload the file directly to the chat."**

**Storage:**
Generated images are stored locally in:
`/home/ubuntu/.hermes/hermes-agent/static/generated_images/`

If you wish to view them via a browser, open port 8000 in your Oracle Cloud Ingress Rules and Ubuntu firewall:
```bash
sudo iptables -I INPUT 6 -p tcp --dport 8000 -j ACCEPT
sudo netfilter-persistent save
```

---

---

## 💾 8. Maintenance & Backup
Before upgrading or making major changes, it is highly recommended to backup your configuration and memory.

### A. Backup Current Setup
```bash
# Create a timestamped backup folder
mkdir -p ~/hermes_backups
tar -czvf ~/hermes_backups/hermes_backup_$(date +%Y%m%d).tar.gz ~/.hermes/
```

### B. Upgrading Hermes
To update to the latest version of the agent:
```bash
# Standard update command
hermes update

# OR re-run the official installer to refresh binaries
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### C. The "Cold Reset" (If things get buggy)
If the agent is behaving weirdly or session history is bloated:
```bash
# 1. Stop the gateway
sudo hermes gateway stop --system

# 2. Clear sessions (History)
rm -rf ~/.hermes/sessions/*

# 3. Restart
sudo hermes gateway start --system
```

---

---

## 📡 9. Automated Script Integration (WhatsApp)
To send automated notifications from your own Linux scripts (like `weather_reporter.sh`) to WhatsApp, use the **Hermes Bridge API** instead of the `hermes chat` command. This ensures 100% reliability, no AI latency, and skips "Home Channel" resolution issues.

### A. What is `localhost:3000`?
When `hermes gateway` is running, it starts an internal **WhatsApp Bridge** on port 3000. This bridge provides a direct REST API that any shell script can talk to.

### B. Implementation Pattern
Use this pattern in your `.sh` scripts to send multi-line reports safely:

```bash
# 1. Capture your message content
MSG_CONTENT="Weather Check\n$(date)\nReport Link: https://example.com"

# 2. Escape the message for JSON (Requires 'jq')
SAFE_MSG=$(echo "$MSG_CONTENT" | jq -Rs .)

# 3. Send via the direct Bridge API
# Note: Use 'chatId' for the recipient and 'message' for the text; change 98765432 to your mobile#
curl -s -X POST http://localhost:3000/send \
     -H "Content-Type: application/json" \
     -d "{\"chatId\": \"85298765432@s.whatsapp.net\", \"message\": $SAFE_MSG}"
```

### C. Why use this over `hermes chat`?
*   **Zero AI Delay**: No waiting for the LLM to "think" or plan.
*   **Safety**: Bypasses AI safety filters that sometimes block URLs.
*   **Stability**: The bridge ignores "Home Channel" aliases and uses the raw WhatsApp ID directly.

---

## 📜 .gitignore
When pushing to [github.com/inchinet](https://github.com/inchinet), ensure these are ignored:
```text
# Hermes Core Secrets
.env
auth.json
*.gpg

# Sessions & Data
sessions/
memories/*.db
logs/

# Python / Environment
venv/
__pycache__/
.DS_Store
```

---

## 📄 License
MIT License - Created by **inchinet**
