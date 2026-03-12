# ToneForgeAI - Test Examples

This document contains test examples for all available API endpoints in ToneForgeAI.

---

## 1. Formalize Email (`POST /formalize_email`)

Rewrites a raw email in a professional tone with optional translation.

### Example 1.1: Business Email Formalization

**Request:**
```json
{
  "raw_email": "hey, i need the report by friday. also can u send me the sales data? thx",
  "category": "business",
  "language": "english"
}
```

**Expected Response:**
```json
{
  "category": "business",
  "email": {
    "subject": "Request for Report and Sales Data",
    "sender": "(Original Sender)",
    "to": "(Original Receiver)",
    "cc": null,
    "body": "Dear [Receiver Name],\n\nI hope this email finds you well. I am writing to request the weekly report, which I need by Friday. Additionally, could you please send me the latest sales data?\n\nPlease let me know if you have any questions or need further clarification.\n\nSincerely,\n[Sender Name]"
  }
}
```

### Example 1.2: Academic Email Formalization

**Request:**
```json
{
  "raw_email": "prof i missed class yesterday can u tell me what i missed and when is the assignment due",
  "category": "academic",
  "language": "english"
}
```

**Expected Response:**
```json
{
  "category": "academic",
  "email": {
    "subject": "Missed Class Inquiry - [Course Name]",
    "sender": "(Original Sender)",
    "to": "(Original Receiver)",
    "cc": null,
    "body": "Dear Professor [Last Name],\n\nI hope you are doing well. I am writing to inquire about the material covered in yesterday's class, which I was unable to attend. Could you please let me know what topics were discussed and any important announcements made?\n\nAdditionally, I would appreciate clarification on the assignment due date.\n\nBest regards,\n[Full Name]\n[Institution]"
  }
}
```

### Example 1.3: Corporate Email with Translation

**Request:**
```json
{
  "raw_email": "team meeting moved to 3pm tomorrow. be there.",
  "category": "corporate",
  "language": "spanish"
}
```

**Expected Response:**
```json
{
  "category": "corporate",
  "email": {
    "subject": "Team Meeting Rescheduled",
    "sender": "(Original Sender)",
    "to": "(Original Receiver)",
    "cc": null,
    "body": "Hello Team,\n\nThis is to inform you that the team meeting has been rescheduled to 3:00 PM tomorrow. Your attendance is required.\n\nKind regards,\n[Name]\n[Designation]\n[Company]"
  },
  "translated_email": {
    "subject": "Reunión de equipo reprogramada",
    "sender": "(Original Sender)",
    "to": "(Original Receiver)",
    "cc": null,
    "body": "Hola Equipo,\n\nLe informamos que la reunión de equipo ha sido reprogramada para las 3:00 PM de mañana. Su asistencia es requerida.\n\nSaludos cordiales,\n[Nombre]\n[Cargo]\n[Empresa]",
    "language": "Spanish"
  }
}
```

---

## 2. Generate Reply (`POST /generate_reply`)

Generates a polished, tone-matched reply to an incoming email.

### Example 2.1: Business Reply

**Request:**
```json
{
  "original_email": "Subject: Q4 Budget Review\n\nDear Team,\n\nWe need to discuss the Q4 budget allocations. Please prepare your department's spending report by end of week.\n\nRegards,\nFinance Department",
  "category": "business"
}
```

**Expected Response:**
```json
{
  "category": "business",
  "smart_reply": {
    "subject": "Re: Q4 Budget Review",
    "sender": "(Original Sender)",
    "to": "Finance Department",
    "body": "Dear Finance Team,\n\nThank you for the notification regarding the Q4 budget review. I acknowledge the request and will ensure that our department's spending report is prepared and submitted by the end of this week.\n\nShould you require any additional information or clarification, please do not hesitate to reach out.\n\nSincerely,\n[Your Name]"
  }
}
```

### Example 2.2: Academic Reply

**Request:**
```json
{
  "original_email": "Subject: Research Paper Submission\n\nDear Student,\n\nYour research paper draft needs significant revisions. Please schedule a meeting to discuss the feedback.\n\nDr. Smith",
  "category": "academic"
}
```

**Expected Response:**
```json
{
  "category": "academic",
  "smart_reply": {
    "subject": "Re: Research Paper Submission",
    "sender": "(Original Sender)",
    "to": "Dr. Smith",
    "body": "Dear Dr. Smith,\n\nThank you for reviewing my research paper draft. I appreciate your feedback and would be grateful for the opportunity to discuss the revisions in detail.\n\nI am available for a meeting during your office hours this week. Please let me know what time would be most convenient for you.\n\nBest regards,\n[Your Full Name]\n[Institution]"
  }
}
```

### Example 2.3: Corporate Reply

**Request:**
```json
{
  "original_email": "Subject: Project Alpha Delay\n\nHello,\n\nWe're experiencing delays with the vendor delivery. This may impact our timeline. What are our options?\n\nBest,\nProject Team",
  "category": "corporate"
}
```

**Expected Response:**
```json
{
  "category": "corporate",
  "smart_reply": {
    "subject": "Re: Project Alpha Delay",
    "sender": "(Original Sender)",
    "to": "Project Team",
    "body": "Hello Project Team,\n\nThank you for the update regarding the vendor delivery delay. Let's explore the following options:\n\n1. Contact alternative vendors for expedited delivery\n2. Adjust the project timeline with stakeholder approval\n3. Implement a phased delivery approach\n\nI suggest we schedule a call tomorrow to discuss the best course of action.\n\nKind regards,\n[Your Name]\n[Your Designation]\n[Company]"
  }
}
```

---

## 3. Negotiate Email (`POST /negotiate_email`)

Runs a multi-agent email negotiation simulation between two parties.

### Example 3.1: Business Negotiation - Salary Discussion

**Request:**
```json
{
  "topic": "Annual salary increase negotiation",
  "our_position": "Requesting 15% increase based on performance and market rates",
  "their_position": "Budget constraints allow maximum 8% increase this year",
  "category": "business",
  "max_rounds": 3
}
```

**Expected Response:**
```json
{
  "topic": "Annual salary increase negotiation",
  "rounds_completed": 3,
  "agreement_reached": true,
  "summary": "Both parties agreed to a 12% salary increase with a performance review in 6 months for potential additional adjustment.",
  "email_thread": [
    {
      "role": "proposer",
      "subject": "Proposal: Annual Salary Adjustment",
      "body": "Dear [Recipient],\n\nI am writing to discuss my annual salary adjustment. Based on my performance over the past year and current market rates, I am requesting a 15% increase..."
    },
    {
      "role": "responder",
      "subject": "Re: Proposal: Annual Salary Adjustment",
      "body": "Dear [Sender],\n\nThank you for your proposal. We value your contributions; however, due to budget constraints, the maximum increase we can offer this year is 8%..."
    },
    {
      "role": "proposer",
      "subject": "Re: Proposal: Annual Salary Adjustment",
      "body": "Dear [Recipient],\n\nI appreciate your response and understand the budget constraints. Would you consider a 12% increase with a performance review in 6 months?..."
    },
    {
      "role": "responder",
      "subject": "Re: Proposal: Annual Salary Adjustment",
      "body": "Dear [Sender],\n\nThank you for your flexibility. We agree to a 12% salary increase with a performance review scheduled in 6 months for potential additional adjustment..."
    }
  ]
}
```

### Example 3.2: Corporate Negotiation - Contract Terms

**Request:**
```json
{
  "topic": "Software licensing contract renewal",
  "our_position": "Seeking 20% discount for 2-year commitment, payment terms net-60",
  "their_position": "Standard pricing only, payment terms net-30",
  "category": "corporate",
  "max_rounds": 2
}
```

**Expected Response:**
```json
{
  "topic": "Software licensing contract renewal",
  "rounds_completed": 2,
  "agreement_reached": false,
  "summary": "Partial agreement on pricing (15% discount for 2-year commitment). Payment terms remain under discussion - proposer requested net-45 as middle ground.",
  "email_thread": [
    {
      "role": "proposer",
      "subject": "Contract Renewal Discussion - Software License",
      "body": "Hello,\n\nWe are interested in renewing our software license for a 2-year commitment. In exchange, we are seeking a 20% discount and net-60 payment terms..."
    },
    {
      "role": "responder",
      "subject": "Re: Contract Renewal Discussion - Software License",
      "body": "Hello,\n\nThank you for your interest in renewing. We can offer standard pricing with our standard net-30 payment terms..."
    }
  ]
}
```

---

## 4. Parse Legal Email (`POST /parse_legal_email`)

Analyzes legal or contract emails and returns structured risk analysis.

### Example 4.1: Contract Review Email

**Request:**
```json
{
  "raw_email": "Subject: Service Agreement Terms\n\nDear Partner,\n\nPer our discussion, here are the key terms:\n\n1. Payment is due within 30 days of invoice date.\n2. All deliverables must be completed by December 31, 2024.\n3. You agree to indemnify and hold us harmless from any claims arising from your work.\n4. This agreement is confidential and may not be disclosed without written consent.\n5. Either party may terminate with 60 days written notice.\n6. Our liability is limited to the total contract value.\n\nPlease confirm acceptance by signing and returning by November 15, 2024.\n\nRegards,\nLegal Department"
}
```

**Expected Response:**
```json
{
  "obligations": [
    "Payment due within 30 days of invoice date",
    "All deliverables must be completed by December 31, 2024",
    "Indemnify and hold harmless from claims arising from work",
    "Maintain confidentiality of agreement terms",
    "Provide 60 days written notice for termination"
  ],
  "deadlines": [
    "December 31, 2024 - Deliverables completion",
    "November 15, 2024 - Acceptance confirmation deadline",
    "30 days - Payment terms",
    "60 days - Termination notice period"
  ],
  "clauses": [
    {
      "clause_type": "Payment Terms",
      "text": "Payment is due within 30 days of invoice date",
      "risk_level": "low"
    },
    {
      "clause_type": "Indemnification",
      "text": "You agree to indemnify and hold us harmless from any claims arising from your work",
      "risk_level": "high"
    },
    {
      "clause_type": "Confidentiality",
      "text": "This agreement is confidential and may not be disclosed without written consent",
      "risk_level": "medium"
    },
    {
      "clause_type": "Termination",
      "text": "Either party may terminate with 60 days written notice",
      "risk_level": "low"
    },
    {
      "clause_type": "Liability",
      "text": "Our liability is limited to the total contract value",
      "risk_level": "medium"
    }
  ],
  "risk_flags": [
    "indemnify",
    "hold us harmless",
    "limited liability",
    "confidential",
    "without written consent"
  ],
  "overall_risk": "high",
  "plain_summary": "This email outlines a service agreement with significant obligations. The indemnification clause carries high risk as it requires you to protect the other party from all claims. Payment is due in 30 days, work must be completed by year-end, and the agreement is confidential. Either party can terminate with 60 days notice, and the other party's liability is capped at the contract value. Response is required by November 15, 2024."
}
```

### Example 4.2: NDA Review Email

**Request:**
```json
{
  "raw_email": "Subject: Mutual NDA for Discussion\n\nHello,\n\nBefore we proceed with discussions, please review and sign the attached NDA.\n\nKey points:\n- Confidential information includes all technical, business, and financial data\n- Obligation lasts 5 years from disclosure date\n- No public announcements without mutual written consent\n- Breach may result in irreparable harm and injunctive relief\n- Governing law: State of Delaware\n\nPlease return signed copy by end of week.\n\nThanks,\nBusiness Development"
}
```

**Expected Response:**
```json
{
  "obligations": [
    "Protect all technical, business, and financial data as confidential",
    "Maintain confidentiality obligation for 5 years from disclosure",
    "No public announcements without mutual written consent",
    "Return signed NDA by end of week"
  ],
  "deadlines": [
    "5 years - Confidentiality obligation period",
    "End of week - Signed NDA return deadline"
  ],
  "clauses": [
    {
      "clause_type": "Confidentiality",
      "text": "Confidential information includes all technical, business, and financial data",
      "risk_level": "medium"
    },
    {
      "clause_type": "Term",
      "text": "Obligation lasts 5 years from disclosure date",
      "risk_level": "low"
    },
    {
      "clause_type": "Public Announcements",
      "text": "No public announcements without mutual written consent",
      "risk_level": "low"
    },
    {
      "clause_type": "Remedies",
      "text": "Breach may result in irreparable harm and injunctive relief",
      "risk_level": "medium"
    },
    {
      "clause_type": "Governing Law",
      "text": "Governing law: State of Delaware",
      "risk_level": "low"
    }
  ],
  "risk_flags": [
    "irreparable harm",
    "injunctive relief",
    "without mutual written consent"
  ],
  "overall_risk": "medium",
  "plain_summary": "This is a mutual NDA requiring both parties to keep all shared information confidential for 5 years. The agreement covers technical, business, and financial data. Public announcements require written consent from both parties. Breach could lead to legal injunctions. The agreement is governed by Delaware law. A signed copy is requested by end of week."
}
```

---

## API Usage Notes

### Base URL
```
http://localhost:8000
```

### cURL Examples

**Formalize Email:**
```bash
curl -X POST http://localhost:8000/formalize_email \
  -H "Content-Type: application/json" \
  -d '{"raw_email": "hey send me the file", "category": "business", "language": "english"}'
```

**Generate Reply:**
```bash
curl -X POST http://localhost:8000/generate_reply \
  -H "Content-Type: application/json" \
  -d '{"original_email": "Subject: Meeting\nWhen are you free?", "category": "corporate"}'
```

**Negotiate Email:**
```bash
curl -X POST http://localhost:8000/negotiate_email \
  -H "Content-Type: application/json" \
  -d '{"topic": "Price negotiation", "our_position": "$1000", "their_position": "$500", "category": "business", "max_rounds": 2}'
```

**Parse Legal Email:**
```bash
curl -X POST http://localhost:8000/parse_legal_email \
  -H "Content-Type: application/json" \
  -d '{"raw_email": "Subject: Contract\nPayment due in 30 days. Liability limited to contract value."}'
```

---

## Frontend Request Bodies (Copy-Paste Ready)

Use these JSON objects directly in your frontend code (fetch, axios, etc.) or API testing tools like Postman, Insomnia, or Thunder Client.

### 1. Formalize Email

**Business - Quick Request:**
```json
{
  "raw_email": "hey send me the file",
  "category": "business",
  "language": "english"
}
```

**Business - Full Example:**
```json
{
  "raw_email": "Subject: Project Update\n\nhey team,\n\njust checking in on the project status. where are we at? need updates by EOD.\n\nthx",
  "category": "business",
  "language": "english"
}
```

**Academic - Request to Professor:**
```json
{
  "raw_email": "prof i cant make it to class tomorrow can i submit the assignment late",
  "category": "academic",
  "language": "english"
}
```

**Corporate - Team Announcement:**
```json
{
  "raw_email": "everyone - new policy starts monday. read the doc i sent. questions? ask HR.",
  "category": "corporate",
  "language": "english"
}
```

**With Translation - English to French:**
```json
{
  "raw_email": "Subject: Meeting Tomorrow\n\nHi, can we meet at 2pm tomorrow to discuss the project?",
  "category": "business",
  "language": "french"
}
```

**With Translation - English to German:**
```json
{
  "raw_email": "Subject: Invoice Attached\n\nPlease find the invoice attached. Payment due in 14 days.",
  "category": "corporate",
  "language": "german"
}
```

**With Translation - English to Spanish:**
```json
{
  "raw_email": "Subject: Welcome Aboard!\n\nHi, welcome to the team! Your first day is Monday at 9am.",
  "category": "business",
  "language": "spanish"
}
```

**With Translation - English to Hindi:**
```json
{
  "raw_email": "Subject: Diwali Greetings\n\nWishing you and your family a happy and prosperous Diwali!",
  "category": "corporate",
  "language": "hindi"
}
```

---

### 2. Generate Reply

**Business Reply - Meeting Request:**
```json
{
  "original_email": "Subject: Meeting Request\n\nHi,\n\nCan we schedule a call this week to discuss the proposal?\n\nBest,\nJohn",
  "category": "business"
}
```

**Business Reply - Follow-up:**
```json
{
  "original_email": "Subject: Follow-up on Previous Discussion\n\nHi,\n\nJust following up on our conversation last week. Any updates?\n\nThanks,\nSarah",
  "category": "business"
}
```

**Academic Reply - Assignment Query:**
```json
{
  "original_email": "Subject: Assignment Clarification\n\nDear Professor,\n\nCould you please clarify the requirements for the final project?\n\nRegards,\nStudent",
  "category": "academic"
}
```

**Academic Reply - Recommendation Request:**
```json
{
  "original_email": "Subject: Recommendation Letter Request\n\nDear Dr. Johnson,\n\nI am applying for graduate programs and would be honored if you could write a recommendation letter for me.\n\nBest regards,\nEmily Chen",
  "category": "academic"
}
```

**Corporate Reply - Project Update:**
```json
{
  "original_email": "Subject: Q4 Project Status\n\nTeam,\n\nPlease provide your weekly status updates by Friday EOD.\n\nRegards,\nPMO",
  "category": "corporate"
}
```

**Corporate Reply - Policy Change:**
```json
{
  "original_email": "Subject: New Remote Work Policy\n\nAll,\n\nEffective next month, remote work requires manager approval. See attached policy.\n\nHR",
  "category": "corporate"
}
```

---

### 3. Negotiate Email

**Salary Negotiation:**
```json
{
  "topic": "Annual salary increase negotiation",
  "our_position": "Requesting 15% increase based on performance and market rates",
  "their_position": "Budget constraints allow maximum 8% increase this year",
  "category": "business",
  "max_rounds": 3
}
```

**Vendor Contract Negotiation:**
```json
{
  "topic": "Software licensing contract renewal",
  "our_position": "Seeking 20% discount for 2-year commitment, payment terms net-60",
  "their_position": "Standard pricing only, payment terms net-30",
  "category": "corporate",
  "max_rounds": 3
}
```

**Service Level Agreement:**
```json
{
  "topic": "SLA uptime guarantee negotiation",
  "our_position": "Require 99.9% uptime with financial penalties for downtime",
  "their_position": "Can offer 99.5% uptime, no penalties, only service credits",
  "category": "business",
  "max_rounds": 2
}
```

**Partnership Terms:**
```json
{
  "topic": "Revenue share for joint venture",
  "our_position": "Proposing 60/40 split in our favor due to larger investment",
  "their_position": "Prefer 50/50 split as both parties bring equal value",
  "category": "corporate",
  "max_rounds": 4
}
```

**Freelance Project Rate:**
```json
{
  "topic": "Website development project pricing",
  "our_position": "Quoted $5000 for full-stack development with 3 revisions",
  "their_position": "Budget capped at $3500, need unlimited revisions",
  "category": "business",
  "max_rounds": 3
}
```

---

### 4. Parse Legal Email

**Service Agreement Analysis:**
```json
{
  "raw_email": "Subject: Service Agreement Terms\n\nDear Partner,\n\nPer our discussion, here are the key terms:\n\n1. Payment is due within 30 days of invoice date.\n2. All deliverables must be completed by December 31, 2024.\n3. You agree to indemnify and hold us harmless from any claims arising from your work.\n4. This agreement is confidential and may not be disclosed without written consent.\n5. Either party may terminate with 60 days written notice.\n6. Our liability is limited to the total contract value.\n\nPlease confirm acceptance by signing and returning by November 15, 2024.\n\nRegards,\nLegal Department"
}
```

**NDA Analysis:**
```json
{
  "raw_email": "Subject: Mutual NDA for Discussion\n\nHello,\n\nBefore we proceed with discussions, please review and sign the attached NDA.\n\nKey points:\n- Confidential information includes all technical, business, and financial data\n- Obligation lasts 5 years from disclosure date\n- No public announcements without mutual written consent\n- Breach may result in irreparable harm and injunctive relief\n- Governing law: State of Delaware\n\nPlease return signed copy by end of week.\n\nThanks,\nBusiness Development"
}
```

**Employment Contract Analysis:**
```json
{
  "raw_email": "Subject: Employment Offer - Terms\n\nDear Candidate,\n\nWe are pleased to offer you the position. Key terms:\n\n- Start date: January 15, 2025\n- Probation period: 90 days\n- Non-compete: 12 months post-employment within 50 mile radius\n- IP Assignment: All work product belongs to company\n- Termination: At-will with 2 weeks notice\n- Benefits: Health insurance after 60 days\n\nPlease sign and return by Friday.\n\nHR Team"
}
```

**Vendor Agreement Analysis:**
```json
{
  "raw_email": "Subject: Vendor Agreement Update\n\nDear Vendor,\n\nUpdated terms for our partnership:\n\n- Minimum order quantity: 500 units per month\n- Lead time: 4 weeks from order date\n- Quality guarantee: 98% defect-free rate required\n- Penalty: 5% discount for each 1% below target\n- Force majeure: Standard clauses apply\n- Dispute resolution: Binding arbitration in New York\n\nConfirm acceptance by return email.\n\nProcurement Team"
}
```

**Consulting Agreement Analysis:**
```json
{
  "raw_email": "Subject: Consulting Engagement Letter\n\nDear Consultant,\n\nEngagement terms:\n\n- Rate: $150/hour, billed weekly\n- Expenses: Pre-approved only, with receipts\n- Deliverables: Weekly progress reports\n- Ownership: All work product is work-for-hire\n- Confidentiality:永久的 (perpetual)\n- Liability cap: Limited to fees paid in prior 3 months\n\nPlease countersign by EOD.\n\nManagement"
}
```

---

## JavaScript Fetch Examples

For frontend developers, here are ready-to-use fetch examples:

### Formalize Email
```javascript
const response = await fetch('http://localhost:8000/formalize_email', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    raw_email: 'hey send me the file',
    category: 'business',
    language: 'english'
  })
});

const data = await response.json();
console.log(data);
```

### Generate Reply
```javascript
const response = await fetch('http://localhost:8000/generate_reply', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    original_email: 'Subject: Meeting\nWhen are you free?',
    category: 'corporate'
  })
});

const data = await response.json();
console.log(data);
```

### Negotiate Email
```javascript
const response = await fetch('http://localhost:8000/negotiate_email', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    topic: 'Price negotiation',
    our_position: '$1000',
    their_position: '$500',
    category: 'business',
    max_rounds: 2
  })
});

const data = await response.json();
console.log(data);
```

### Parse Legal Email
```javascript
const response = await fetch('http://localhost:8000/parse_legal_email', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    raw_email: 'Subject: Contract\nPayment due in 30 days.'
  })
});

const data = await response.json();
console.log(data);
```

---

## Axios Examples

### Formalize Email
```javascript
import axios from 'axios';

const response = await axios.post('http://localhost:8000/formalize_email', {
  raw_email: 'hey send me the file',
  category: 'business',
  language: 'english'
});

console.log(response.data);
```

### Generate Reply
```javascript
const response = await axios.post('http://localhost:8000/generate_reply', {
  original_email: 'Subject: Meeting\nWhen are you free?',
  category: 'corporate'
});

console.log(response.data);
```

### Negotiate Email
```javascript
const response = await axios.post('http://localhost:8000/negotiate_email', {
  topic: 'Price negotiation',
  our_position: '$1000',
  their_position: '$500',
  category: 'business',
  max_rounds: 2
});

console.log(response.data);
```

### Parse Legal Email
```javascript
const response = await axios.post('http://localhost:8000/parse_legal_email', {
  raw_email: 'Subject: Contract\nPayment due in 30 days.'
});

console.log(response.data);
```

---

## Environment Setup

Ensure you have the following in your `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## Available Categories

| Category   | Description                          | Use Case                    |
|------------|--------------------------------------|-----------------------------|
| `business` | Professional, concise, polite        | General business communication |
| `academic` | Respectful, formal, academic         | University/research communication |
| `corporate`| Professional, structured, direct     | Internal corporate communication |

---

## Available Languages for Translation

Any language supported by the LLM can be specified, including:
- `english` (default, no translation)
- `spanish`
- `french`
- `german`
- `hindi`
- `chinese`
- `japanese`
- And many more...
