import os
import sys
from contextlib import redirect_stdout
from crewai import Agent, Task, Crew

# --- KEY SETUP ---
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")

# --- AGENT DEFINITION ---
researcher = Agent(
  role='Expert Research Analyst',
  goal='Discover and report fascinating information on any given topic.',
  backstory="""You are a world-class research analyst, known for your ability 
  to dig deep and find compelling, verifiable facts. You are a master of synthesis 
  and can explain complex topics simply.""",
  verbose=True,
  allow_delegation=False
)

# --- TASK DEFINITION ---
# The task is correctly named 'research_task' here.
research_task = Task(
  description='Tell me a fun and interesting fact about the Roman Empire.',
  expected_output='A single, concise paragraph containing one interesting fact.',
  agent=researcher
)

# --- CREW DEFINITION ---
# We now pass the correct variable name, 'research_task'.
research_crew = Crew(
  agents=[researcher],
  tasks=[research_task], 
  verbose=True
)

# --- LOGGING AND EXECUTION ---
logfile = "crew_execution_log.txt"
print(f"Kicking off the research crew... All actions will be logged to '{logfile}'")

# We redirect the console output to our log file for this block
with open(logfile, 'w') as f:
    with redirect_stdout(f):
        result = research_crew.kickoff()

# This will print to the console after the logging is complete
print("\n\n--------------------")
print("Crew execution finished. Final Result:")
print(result)

print(f"\n[SUCCESS] The full execution log has been saved to '{logfile}'")