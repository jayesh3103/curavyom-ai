from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time
import asyncio
import os
from backend.agents.orchestrator import MasterAgent
from backend.utils.pdf_processor import extract_text_from_pdf

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="CuraVyom API", version="1.0.0")

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    os.getenv("FRONTEND_URL", ""), # Production frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount reports directory
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    id: int
    sender: str
    agent: Optional[str] = None
    text: str
    timestamp: str

@app.get("/")
async def root():
    return {"status": "online", "system": "CuraVyom Agentic Protocol v2.0"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Simulate processing delay
        await asyncio.sleep(1)
        
        # Instantiate Master Agent
        master = MasterAgent()
        response_data = await master.process_query(request.message)
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Analyzes uploaded files. Uses pypdf for PDF text extraction.
    """
    # Simulate processing delay
    await asyncio.sleep(1.0)
    
    filename = file.filename.lower()
    
    if ".pdf" in filename:
        content = await file.read()
        extracted_text = extract_text_from_pdf(content)
        
        # Truncate if too long for a summary, but return enough for context
        preview = extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
        
        return {
            "status": "success",
            "analysis": f"**PDF Analysis Complete**\n\n**Extracted Content:**\n{preview}\n\n(Full text processed for context)",
            "full_text": extracted_text, # Frontend can use this to feed back into chat context
            "type": "document"
        }
    elif "structure" in filename or ".mol" in filename or ".png" in filename:
        return {
            "status": "success",
            "analysis": "Chemical Structure Analysis: Identified indole scaffold. High similarity to serotonin receptor modulators.",
            "type": "structure"
        }
    else:
        return {
            "status": "success",
            "analysis": f"Processed {filename}. No specific molecular data found, but metadata extracted.",
            "type": "generic"
        }

class SubscriptionRequest(BaseModel):
    email: str

@app.post("/subscribe")
async def subscribe(request: SubscriptionRequest):
    """
    Handles newsletter subscriptions.
    In a production environment, this would integrate with an SMTP server (e.g., SendGrid, AWS SES)
    to send a confirmation email.
    """
    # Simulate SMTP delay
    await asyncio.sleep(1)
    
    # Log the subscription (mocking database storage)
    print(f"New subscription: {request.email}")
    
    # Mock sending email
    # send_email(to=request.email, subject="Welcome to CuraVyom", body="Thank you for subscribing...")
    
    return {"status": "success", "message": "Subscription confirmed. Check your email for updates."}

class ContactRequest(BaseModel):
    firstName: str
    lastName: str
    email: str
    message: str

@app.post("/api/contact")
async def contact_form(request: ContactRequest):
    """
    Handles contact form submissions.
    Simulates sending an email to the admin and a confirmation to the user.
    """
    # Simulate SMTP delay
    await asyncio.sleep(1.5)
    
    # Log the message (mocking email sending)
    print(f"New Contact Message from {request.firstName} {request.lastName} ({request.email}): {request.message}")
    print(f"Sending notification to: mr.jayeshvmuley@gmail.com")
    print(f"Sending auto-reply to: {request.email}")
    
    # Mock sending emails
    # send_email(to="mr.jayeshvmuley@gmail.com", subject="New Contact Message", body=request.message)
    # send_email(to=request.email, subject="We received your message", body="Thank you for contacting us...")
    
    return {"status": "success", "message": "Message sent successfully."}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Simulate "typing" or "processing" logs
            await websocket.send_json({"type": "log", "content": "Received query. Initiating Master Agent..."})
            await asyncio.sleep(0.5)
            
            # Instantiate Master Agent
            master = MasterAgent()
            
            # In a real streaming scenario, the agent would yield chunks.
            # Here we simulate streaming logs before the final result.
            await websocket.send_json({"type": "log", "content": "Decomposing task..."})
            await asyncio.sleep(0.5)
            
            await websocket.send_json({"type": "log", "content": "Deploying worker agents..."})
            await asyncio.sleep(0.5)
            
            # Get final response
            response_data = await master.process_query(data)
            
            # Send final response
            await websocket.send_json({"type": "response", "data": response_data})
            
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
