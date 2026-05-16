# Job-agent-ai
An autonomous multi-agent AI system that finds jobs, tailors your resume, writes cover letters, sends applications via Gmail, and tracks everything in Google Sheets — fully automated.
Solution
An AI-powered autonomous agent system that does everything automatically:
Agent 1 — Job Monitor: Searches the web in real-time using Tavily API to find relevant job postings based on your role and location.
Agent 2 — Resume Tailor: Reads your uploaded PDF resume and rewrites it using AI to match each job's requirements and keywords for ATS optimization.
Agent 3 — Cover Letter Writer: Generates a personalized, professional cover letter for each job using Groq LLM (LLaMA 3.3).
Agent 4 — Application Sender: Automatically sends the tailored resume and cover letter to recruiters via Gmail API.
Agent 5 — Application Tracker: Logs every application — company, role, status, date — into Google Sheets automatically.

Tech Stack

CrewAI — Multi-agent orchestration
Groq + LLaMA 3.3 — AI brain (free, fast)
Tavily API — Real-time job search
Gmail API — Automated email sending
Google Sheets API — Application tracking
Flask — Web UI
PyPDF2 — Resume parsing


Impact

Saves 3-4 hours per day per job seeker
Increases application volume by 10x
Improves ATS match rate through keyword optimization
Zero manual effort after setup
Sonnet 4.6
