"""
Interview Prep Notes Generator (Hackathon Stretch Feature).
Automatically generates or retrieves structured interview preparation guides
for any role that enters the 'interview' stage.
"""
from typing import Dict, Any


CURATED_PREP_NOTES: Dict[str, Dict[str, Any]] = {
    "zentech::backend engineer": {
        "company": "Zentech Solutions",
        "role": "Backend Engineer",
        "interview_date": "2026-10-25",
        "round_type": "Technical Round with Tech Lead",
        "tech_focus": ["High-throughput Microservices", "PostgreSQL Indexing & Optimization", "Redis Caching Strategies", "Distributed Locks & Concurrency"],
        "company_brief": "Fast-scaling enterprise logistics & workflow automation platform handling 15M+ daily API transactions.",
        "key_questions": [
            {
                "question": "How would you handle race conditions when two concurrent requests update the same inventory item?",
                "answer_tip": "Discuss optimistic concurrency control using version numbers vs pessimistic locking (SELECT FOR UPDATE). For distributed systems, explain Redis Redlock or database row-level locking."
            },
            {
                "question": "Explain composite database indexing and the leftmost prefix rule.",
                "answer_tip": "Index on (A, B, C) accelerates queries matching A, or (A, B), or (A, B, C). It will not help queries on B alone or C alone."
            },
            {
                "question": "How do you design an idempotent payment processing webhook?",
                "answer_tip": "Store unique webhook transaction ID in an idempotency table with unique constraints, wrap status updates in an atomic DB transaction."
            }
        ],
        "smart_questions_to_ask": [
            "How does your team handle schema migrations with zero downtime under continuous write load?",
            "What has been the biggest bottleneck your team solved over the past quarter?"
        ]
    },
    "zerodha::systems & infrastructure engineer": {
        "company": "Zerodha",
        "role": "Systems & Infrastructure Engineer",
        "interview_date": "2026-10-28",
        "round_type": "Technical & Systems Architecture Round 1",
        "tech_focus": ["Linux Kernel & Low-Latency Networking", "Go / Rust Systems", "Kafka / ZeroMQ Message Queues", "High-frequency Trading Ingestion"],
        "company_brief": "India's largest retail brokerage built on open-source software, processing billions in trade volume with minimal server footprint.",
        "key_questions": [
            {
                "question": "How would you diagnose intermittent network packet drops on a Linux production node?",
                "answer_tip": "Check `netstat -s`, `ethtool -S`, NIC ring buffer drops (`rx_dropped`), kernel socket buffer memory `net.core.rmem_max`, and TCP backlog queues."
            },
            {
                "question": "Explain memory-mapped files (mmap) vs standard read/write syscalls.",
                "answer_tip": "mmap avoids copying data between kernel and user space buffers (zero-copy), mapping file directly into process virtual memory."
            }
        ],
        "smart_questions_to_ask": [
            "How does Zerodha approach zero-vendor-lockin infrastructure while maintaining 99.999% trading uptime during market opening spikes?",
            "What monitoring metrics does the on-call engineer watch closest at 9:15 AM?"
        ]
    },
    "finly::frontend engineer": {
        "company": "Finly",
        "role": "Frontend Engineer",
        "interview_date": "2026-10-27",
        "round_type": "Technical & Architecture Discussion",
        "tech_focus": ["React 19 / Modern JavaScript", "State Management & Optimistic UI", "Web Performance & Core Web Vitals", "Financial Ledger UI Security"],
        "company_brief": "B2B financial automation and expense management software provider focused on instant reconciliation.",
        "key_questions": [
            {
                "question": "How do you achieve 60fps rendering for tabular data with 50,000 live updating rows?",
                "answer_tip": "Window virtualization (e.g., TanStack Virtual / react-window) so only viewport rows exist in DOM, Web Workers for parsing incoming websocket batches."
            },
            {
                "question": "Explain how you protect a client-side SPA against XSS and CSRF when storing authentication tokens.",
                "answer_tip": "Use HttpOnly, Secure, SameSite=Strict cookies rather than localStorage. Ensure strict Content-Security-Policy (CSP) headers."
            }
        ],
        "smart_questions_to_ask": [
            "What is your approach to balancing snappy client-side optimistic UI updates with financial ledger data consistency?",
            "How is the frontend team structuring design system components across web and mobile?"
        ]
    }
}


def get_interview_prep(company: str, role: str) -> Dict[str, Any]:
    """Retrieve curated prep notes or dynamic fallback for any role."""
    key = f"{company.lower().strip()}::{role.lower().strip()}"
    
    # Try exact or partial match
    for k, prep in CURATED_PREP_NOTES.items():
        if company.lower() in k or k in key:
            return prep
            
    # Dynamic structured fallback
    return {
        "company": company,
        "role": role,
        "interview_date": "Upcoming",
        "round_type": "Technical Screening Round",
        "tech_focus": ["Core Problem Solving & Data Structures", "System Design & Architecture", "Clean Code & Production Debugging", "Cultural & Communication Fit"],
        "company_brief": f"{company} is actively scaling their engineering department for the {role} position.",
        "key_questions": [
            {
                "question": f"Walk us through the most technically challenging project you led as a {role}.",
                "answer_tip": "Use the STAR method (Situation, Task, Action, Result). Highlight architecture tradeoffs, metrics, and failures you overcame."
            },
            {
                "question": "How do you ensure reliability and testability in your software design?",
                "answer_tip": "Discuss unit testing, integration tests, CI/CD automated gates, observability (metrics, logs, traces), and canary rollouts."
            }
        ],
        "smart_questions_to_ask": [
            f"What does success look like for this {role} within the first 90 days?",
            "What is the team's greatest engineering challenge currently being solved?"
        ]
    }
