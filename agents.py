import os
from crewai import Agent

from tools import search_jobs, send_email, track_application, read_resume

def get_llm():
    from langchain_groq import ChatGroq
    return ChatGroq(
        model="llama3-70b-8192",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7
    )
    

def create_agents():
    llm = get_llm()

    job_monitor = Agent(
        role="Job Monitor",
        goal="Search and find relevant job postings based on user's role and location",
        backstory="""You are an expert job researcher who knows how to find 
        the best job opportunities across the web. You search thoroughly 
        and return structured job listings.""",
        tools=[search_jobs],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    resume_tailor = Agent(
        role="Resume Tailor",
        goal="Tailor the user's resume to match each specific job description",
        backstory="""You are an expert resume writer and ATS optimization specialist. 
        You know how to rewrite resumes to match job descriptions perfectly, 
        using the right keywords to pass ATS systems.""",
        tools=[read_resume],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    cover_letter_writer = Agent(
        role="Cover Letter Writer",
        goal="Write compelling personalized cover letters for each job application",
        backstory="""You are a professional cover letter writer who creates 
        personalized, engaging cover letters that highlight the candidate's 
        strengths and match the job requirements perfectly.""",
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    application_sender = Agent(
        role="Application Sender",
        goal="Send job applications via email with tailored resume and cover letter",
        backstory="""You are responsible for sending professional job applications 
        via email. You ensure all applications are sent correctly with proper 
        formatting and attachments.""",
        tools=[send_email],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    tracker = Agent(
        role="Application Tracker",
        goal="Track all job applications in Google Sheets and provide status updates",
        backstory="""You are an organized tracker who maintains detailed records 
        of all job applications, their status, and important details in 
        Google Sheets for easy monitoring.""",
        tools=[track_application],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    return job_monitor, resume_tailor, cover_letter_writer, application_sender, tracker
