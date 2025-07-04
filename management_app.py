#!/usr/bin/env python3
"""
Management interface for the professional Telegram AI Bot.
Provides status monitoring, logs viewing, and basic controls.
"""

import os
import subprocess
import signal
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
BOT_DIR = Path(__file__).parent
BOT_SCRIPT = BOT_DIR / "main.py"
BOT_LOG = BOT_DIR / "bot.log"
MANAGEMENT_LOG = BOT_DIR / "management.log"

def get_bot_pid():
    """Get the PID of the running bot process."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "main.py"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(result.stdout.strip().split('\n')[0])
        return None
    except Exception as e:
        logger.error(f"Error getting bot PID: {e}")
        return None

def is_bot_running():
    """Check if the bot is currently running."""
    return get_bot_pid() is not None

@app.route('/')
def index():
    """Main status page."""
    bot_running = is_bot_running()
    bot_pid = get_bot_pid() if bot_running else None
    
    return jsonify({
        "service": "Telegram AI Bot Management",
        "status": "running" if bot_running else "stopped",
        "bot_pid": bot_pid,
        "version": "2.0.0-professional",
        "architecture": "enterprise-grade",
        "features": [
            "OpenAI Assistant API Integration",
            "11 Character Personalities",
            "Professional Architecture",
            "Comprehensive Testing",
            "Type Safety",
            "Production Ready"
        ]
    })

@app.route('/status')
def status():
    """Get detailed bot status."""
    bot_running = is_bot_running()
    bot_pid = get_bot_pid() if bot_running else None
    
    # Get log file size
    log_size = 0
    if BOT_LOG.exists():
        log_size = BOT_LOG.stat().st_size
    
    return jsonify({
        "bot_running": bot_running,
        "bot_pid": bot_pid,
        "log_file_size": log_size,
        "log_file_exists": BOT_LOG.exists(),
        "project_directory": str(BOT_DIR),
        "python_version": subprocess.run(
            ["python3", "--version"], 
            capture_output=True, 
            text=True
        ).stdout.strip()
    })

@app.route('/logs')
def logs():
    """Get bot logs."""
    lines = request.args.get('lines', 50, type=int)
    lines = min(lines, 1000)  # Limit to 1000 lines max
    
    if not BOT_LOG.exists():
        return jsonify({"error": "Log file not found", "logs": []})
    
    try:
        result = subprocess.run(
            ["tail", f"-{lines}", str(BOT_LOG)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            log_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            return jsonify({
                "logs": log_lines,
                "lines_requested": lines,
                "lines_returned": len(log_lines)
            })
        else:
            return jsonify({"error": "Failed to read logs", "logs": []})
            
    except Exception as e:
        return jsonify({"error": f"Error reading logs: {str(e)}", "logs": []})

@app.route('/start', methods=['POST'])
def start_bot():
    """Start the bot."""
    if is_bot_running():
        return jsonify({
            "success": False,
            "message": "Bot is already running",
            "pid": get_bot_pid()
        })
    
    try:
        # Start bot in background
        process = subprocess.Popen(
            ["nohup", "python3", str(BOT_SCRIPT)],
            stdout=open(BOT_LOG, 'a'),
            stderr=subprocess.STDOUT,
            cwd=BOT_DIR,
            preexec_fn=os.setsid
        )
        
        # Give it a moment to start
        import time
        time.sleep(2)
        
        if is_bot_running():
            return jsonify({
                "success": True,
                "message": "Bot started successfully",
                "pid": get_bot_pid()
            })
        else:
            return jsonify({
                "success": False,
                "message": "Bot failed to start - check logs"
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error starting bot: {str(e)}"
        })

@app.route('/stop', methods=['POST'])
def stop_bot():
    """Stop the bot."""
    bot_pid = get_bot_pid()
    
    if not bot_pid:
        return jsonify({
            "success": False,
            "message": "Bot is not running"
        })
    
    try:
        # Send SIGTERM first
        os.kill(bot_pid, signal.SIGTERM)
        
        # Give it time to shutdown gracefully
        import time
        time.sleep(3)
        
        # Check if still running
        if is_bot_running():
            # Force kill if still running
            os.kill(bot_pid, signal.SIGKILL)
            time.sleep(1)
        
        if not is_bot_running():
            return jsonify({
                "success": True,
                "message": f"Bot stopped successfully (PID: {bot_pid})"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Failed to stop bot"
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error stopping bot: {str(e)}"
        })

@app.route('/restart', methods=['POST'])
def restart_bot():
    """Restart the bot."""
    # Stop first
    stop_result = stop_bot()
    
    if not stop_result.get_json().get('success', False):
        # If stop failed but bot isn't running, that's ok
        if is_bot_running():
            return jsonify({
                "success": False,
                "message": "Failed to stop bot for restart"
            })
    
    # Wait a moment
    import time
    time.sleep(2)
    
    # Start again
    start_result = start_bot()
    
    if start_result.get_json().get('success', False):
        return jsonify({
            "success": True,
            "message": "Bot restarted successfully",
            "pid": get_bot_pid()
        })
    else:
        return jsonify({
            "success": False,
            "message": "Failed to start bot after stop"
        })

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "telegram-ai-bot-management",
        "timestamp": subprocess.run(
            ["date", "-Iseconds"], 
            capture_output=True, 
            text=True
        ).stdout.strip()
    })

if __name__ == '__main__':
    logger.info("Starting Telegram AI Bot Management Interface...")
    logger.info(f"Bot directory: {BOT_DIR}")
    logger.info(f"Bot script: {BOT_SCRIPT}")
    logger.info(f"Bot log: {BOT_LOG}")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=8080, debug=False)

