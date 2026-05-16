from crewai import Task
from agents import create_agents

def create_tasks(user_data: dict):
    job_monitor, resume_tailor, cover_letter_writer, application_sender, tracker = create_agents()

    resume_path = user_data.get('resume_path', '')
    role = user_data.get('role', '')
    location = user_data.get('location', '')
    name = user_data.get('name', '')
    email = user_data.get('email', '')
    phone = user_data.get('phone', '')
    experience = user_data.get('experience', '')

    search_task = Task(
        description=f"""Search for {role} job openings in {location}. 
        Find at least 3-5 relevant job postings with company names, 
        job titles, requirements, and contact emails if available.
        Search query: '{role} jobs {location} 2025'""",
        expected_output="A list of 3-5 job postings with company name, job title, requirements, and contact email",
        agent=job_monitor
    )

    tailor_task = Task(
        description=f"""Read the resume from {resume_path} and tailor it for a {role} position.
        The candidate has {experience} years of experience.
        Rewrite the resume bullet points to match common {role} job requirements.
        Use ATS-friendly keywords. Keep it professional and concise.""",
        expected_output="A tailored resume text optimized for the target role",
        agent=resume_tailor,
        context=[search_task]
    )

    cover_letter_task = Task(
        description=f"""Write a professional cover letter for {name} applying for {role} positions.
        Candidate details:
        - Name: {name}
        - Email: {email}
        - Phone: {phone}
        - Years of Experience: {experience}
        - Target Role: {role}
        - Target Location: {location}
        
        Make it compelling, personalized, and under 300 words.""",
        expected_output="A professional cover letter ready to send",
        agent=cover_letter_writer,
        context=[search_task, tailor_task]
    )

    send_task = Task(
        description=f"""Send job applications for the found job postings.
        For each job that has a contact email:
        - Send an email with the cover letter as the body
        - Attach the resume from {resume_path}
        - Use professional subject line: "Application for [Role] - {name}"
        
        If no contact email found, note it as "Apply via website".""",
        expected_output="Confirmation of emails sent with list of companies applied to",
        agent=application_sender,
        context=[search_task, cover_letter_task]
    )

    track_task = Task(
        description=f"""Track all job applications in Google Sheets.
        For each application sent, record:
        - Name: {name}
        - Role: {role}
        - Company name
        - Status: Applied
        - Email sent to
        - Today's date
        - Any notes
        
        Format as JSON and use the Track Application tool.""",
        expected_output="Confirmation that all applications are tracked in Google Sheets",
        agent=tracker,
        context=[send_task]
    )

    return [search_task, tailor_task, cover_letter_task, send_task, track_task]
