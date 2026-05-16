import os
import threading
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from crewai import Crew, Process

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
os.makedirs('uploads', exist_ok=True)

job_status = {"running": False, "log": [], "done": False, "result": ""}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Job Application Agent</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
        .header { background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 30px 20px; text-align: center; }
        .header h1 { font-size: 2rem; color: white; }
        .header p { color: #e0d9ff; margin-top: 8px; }
        .container { max-width: 700px; margin: 40px auto; padding: 0 20px; }
        .card { background: #1e293b; border-radius: 16px; padding: 32px; margin-bottom: 24px; border: 1px solid #334155; }
        .card h2 { color: #a78bfa; margin-bottom: 24px; font-size: 1.2rem; }
        .form-group { margin-bottom: 20px; }
        label { display: block; color: #94a3b8; font-size: 0.85rem; margin-bottom: 6px; font-weight: 500; }
        input, select { width: 100%; padding: 12px 16px; background: #0f172a; border: 1px solid #334155; border-radius: 10px; color: #e2e8f0; font-size: 1rem; outline: none; transition: border 0.2s; }
        input:focus, select:focus { border-color: #6366f1; }
        .upload-area { border: 2px dashed #334155; border-radius: 10px; padding: 30px; text-align: center; cursor: pointer; transition: border 0.2s; }
        .upload-area:hover { border-color: #6366f1; }
        .upload-area input { display: none; }
        .upload-area p { color: #64748b; font-size: 0.9rem; margin-top: 8px; }
        .upload-area .icon { font-size: 2rem; }
        #file-name { color: #a78bfa; margin-top: 8px; font-size: 0.9rem; }
        .btn { width: 100%; padding: 14px; background: linear-gradient(135deg, #6366f1, #8b5cf6); border: none; border-radius: 10px; color: white; font-size: 1rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
        .btn:hover { opacity: 0.9; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .status-card { display: none; }
        .log-box { background: #0f172a; border-radius: 10px; padding: 16px; height: 250px; overflow-y: auto; font-family: monospace; font-size: 0.85rem; border: 1px solid #334155; }
        .log-line { padding: 3px 0; color: #94a3b8; }
        .log-line.success { color: #34d399; }
        .log-line.info { color: #60a5fa; }
        .spinner { display: inline-block; width: 18px; height: 18px; border: 3px solid #6366f1; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; margin-right: 8px; vertical-align: middle; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .step-row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #1e293b; }
        .step-num { background: #6366f1; color: white; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 700; flex-shrink: 0; }
        .step-text { color: #cbd5e1; font-size: 0.9rem; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        @media(max-width: 500px) { .grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI Job Application Agent</h1>
        <p>Let AI find jobs, tailor your resume, and apply — automatically</p>
    </div>

    <div class="container">
        <!-- How it works -->
        <div class="card">
            <h2>⚡ How It Works</h2>
            <div class="step-row"><div class="step-num">1</div><div class="step-text">Fill in your details and upload your resume PDF</div></div>
            <div class="step-row"><div class="step-num">2</div><div class="step-text">AI searches for matching jobs using Tavily</div></div>
            <div class="step-row"><div class="step-num">3</div><div class="step-text">Gemini AI tailors your resume and writes cover letters</div></div>
            <div class="step-row"><div class="step-num">4</div><div class="step-text">Applications sent automatically via Gmail</div></div>
            <div class="step-row" style="border:none"><div class="step-num">5</div><div class="step-text">Everything tracked in Google Sheets</div></div>
        </div>

        <!-- Form -->
        <div class="card" id="form-card">
            <h2>📋 Your Details</h2>
            <form id="apply-form" enctype="multipart/form-data">
                <div class="grid">
                    <div class="form-group">
                        <label>Full Name *</label>
                        <input type="text" name="name" placeholder="e.g. Sri Reddy" required>
                    </div>
                    <div class="form-group">
                        <label>Phone Number *</label>
                        <input type="tel" name="phone" placeholder="e.g. +91 9876543210" required>
                    </div>
                </div>
                <div class="form-group">
                    <label>Your Email Address *</label>
                    <input type="email" name="email" placeholder="your@gmail.com" required>
                </div>
                <div class="grid">
                    <div class="form-group">
                        <label>Target Job Role *</label>
                        <input type="text" name="role" placeholder="e.g. Software Engineer" required>
                    </div>
                    <div class="form-group">
                        <label>Preferred Location *</label>
                        <input type="text" name="location" placeholder="e.g. Bangalore, Remote" required>
                    </div>
                </div>
                <div class="form-group">
                    <label>Years of Experience *</label>
                    <select name="experience" required>
                        <option value="">Select experience</option>
                        <option value="0">Fresher (0 years)</option>
                        <option value="1">1 year</option>
                        <option value="2">2 years</option>
                        <option value="3">3 years</option>
                        <option value="4">4 years</option>
                        <option value="5+">5+ years</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Upload Resume (PDF) *</label>
                    <div class="upload-area" onclick="document.getElementById('resume').click()">
                        <div class="icon">📄</div>
                        <p>Click to upload your resume PDF</p>
                        <div id="file-name">No file chosen</div>
                        <input type="file" id="resume" name="resume" accept=".pdf" onchange="updateFileName(this)" required>
                    </div>
                </div>
                <button type="submit" class="btn" id="submit-btn">🚀 Start AI Job Search & Apply</button>
            </form>
        </div>

        <!-- Status -->
        <div class="card status-card" id="status-card">
            <h2><span class="spinner"></span> AI Agents Working...</h2>
            <div class="log-box" id="log-box"></div>
        </div>

        <!-- Done -->
        <div class="card" id="done-card" style="display:none; text-align:center;">
            <div style="font-size:3rem">✅</div>
            <h2 style="color:#34d399; margin-top:12px;">Applications Sent!</h2>
            <p style="color:#94a3b8; margin-top:8px;">Check your Google Sheets for the full tracking report.</p>
            <button class="btn" style="margin-top:20px; max-width:200px; margin-left:auto; margin-right:auto" onclick="location.reload()">Apply More Jobs</button>
        </div>
    </div>

    <script>
        function updateFileName(input) {
            document.getElementById('file-name').textContent = input.files[0]?.name || 'No file chosen';
        }

        document.getElementById('apply-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            document.getElementById('submit-btn').disabled = true;
            document.getElementById('submit-btn').textContent = 'Starting...';
            document.getElementById('status-card').style.display = 'block';

            await fetch('/start', { method: 'POST', body: formData });
            pollStatus();
        });

        function pollStatus() {
            const logBox = document.getElementById('log-box');
            const interval = setInterval(async () => {
                const res = await fetch('/status');
                const data = await res.json();
                logBox.innerHTML = data.log.map(l => 
                    `<div class="log-line ${l.includes('✅') ? 'success' : l.includes('🔍') || l.includes('📝') ? 'info' : ''}">${l}</div>`
                ).join('');
                logBox.scrollTop = logBox.scrollHeight;

                if (data.done) {
                    clearInterval(interval);
                    document.getElementById('status-card').style.display = 'none';
                    document.getElementById('done-card').style.display = 'block';
                }
            }, 2000);
        }
    </script>
</body>
</html>
"""

def run_crew(user_data):
    from tasks import create_tasks
    global job_status
    try:
        job_status["log"].append("🔍 Agent 1: Searching for jobs...")
        tasks = create_tasks(user_data)

        from agents import create_agents
        job_monitor, resume_tailor, cover_letter_writer, application_sender, tracker = create_agents()

        crew = Crew(
            agents=[job_monitor, resume_tailor, cover_letter_writer, application_sender, tracker],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )

        job_status["log"].append("📝 Agent 2: Tailoring resume...")
        job_status["log"].append("✍️ Agent 3: Writing cover letters...")
        job_status["log"].append("📧 Agent 4: Sending applications...")
        job_status["log"].append("📊 Agent 5: Tracking in Google Sheets...")

        result = crew.kickoff()

        job_status["log"].append("✅ All done! Applications sent successfully.")
        job_status["result"] = str(result)
        job_status["done"] = True
    except Exception as e:
        job_status["log"].append(f"❌ Error: {str(e)}")
        job_status["done"] = True


@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/start', methods=['POST'])
def start():
    global job_status
    job_status = {"running": True, "log": ["🚀 Starting AI Job Agent..."], "done": False, "result": ""}

    file = request.files.get('resume')
    resume_path = ''
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(resume_path)

    user_data = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'role': request.form.get('role'),
        'location': request.form.get('location'),
        'experience': request.form.get('experience'),
        'resume_path': resume_path
    }

    thread = threading.Thread(target=run_crew, args=(user_data,))
    thread.daemon = True
    thread.start()

    return jsonify({"status": "started"})


@app.route('/status')
def status():
    return jsonify(job_status)


@app.route('/dashboard')
def dashboard():
    return render_template_string(HTML)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
