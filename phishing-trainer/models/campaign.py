from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

@dataclass
class Target:
    """Represents a target recipient for a phishing campaign."""
    email: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "queued"  # queued, sent, bounced, clicked, completed-quiz, failed
    send_ts: Optional[float] = None
    click_ts: Optional[float] = None
    track_url: Optional[str] = None
    message_id: Optional[str] = None
    quiz_score: Optional[int] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "email": self.email,
            "id": self.id,
            "status": self.status,
            "send_ts": self.send_ts,
            "click_ts": self.click_ts,
            "track_url": self.track_url,
            "message_id": self.message_id,
            "quiz_score": self.quiz_score,
            "error": self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Target':
        """Create a Target instance from a dictionary."""
        return cls(
            email=data["email"],
            id=data.get("id", str(uuid.uuid4())),
            status=data.get("status", "queued"),
            send_ts=data.get("send_ts"),
            click_ts=data.get("click_ts"),
            track_url=data.get("track_url"),
            message_id=data.get("message_id"),
            quiz_score=data.get("quiz_score"),
            error=data.get("error")
        )

@dataclass
class EmailContent:
    """Represents the content of a phishing email."""
    subject: str
    body_html: str
    body_text: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "subject": self.subject,
            "body_html": self.body_html,
            "body_text": self.body_text
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailContent':
        """Create an EmailContent instance from a dictionary."""
        return cls(
            subject=data["subject"],
            body_html=data["body_html"],
            body_text=data.get("body_text")
        )

@dataclass
class CompanyInfo:
    """Represents information about the company being simulated in the phishing campaign."""
    name: str
    website: Optional[str] = None
    news: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "website": self.website,
            "news": self.news
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompanyInfo':
        """Create a CompanyInfo instance from a dictionary."""
        return cls(
            name=data["name"],
            website=data.get("website"),
            news=data.get("news")
        )

@dataclass
class ScenarioInfo:
    """Represents information about the phishing scenario."""
    type: str  # credential-theft, invoice, oauth-consent, shipping, etc.
    difficulty: int = 3  # 1-5 scale
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type,
            "difficulty": self.difficulty
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScenarioInfo':
        """Create a ScenarioInfo instance from a dictionary."""
        return cls(
            type=data["type"],
            difficulty=data.get("difficulty", 3)
        )

@dataclass
class AdvancedOptions:
    """Represents advanced options for a phishing campaign."""
    display_name: Optional[str] = None
    reply_to: Optional[str] = None
    sending_window: str = "Business Hours"  # Immediate, Business Hours, Spread over 24h, Spread over 48h
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "display_name": self.display_name,
            "reply_to": self.reply_to,
            "sending_window": self.sending_window
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdvancedOptions':
        """Create an AdvancedOptions instance from a dictionary."""
        return cls(
            display_name=data.get("display_name"),
            reply_to=data.get("reply_to"),
            sending_window=data.get("sending_window", "Business Hours")
        )

@dataclass
class CampaignMetrics:
    """Represents metrics for a phishing campaign."""
    click_rate: float = 0.0
    quiz_completion_rate: float = 0.0
    avg_quiz_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "click_rate": self.click_rate,
            "quiz_completion_rate": self.quiz_completion_rate,
            "avg_quiz_score": self.avg_quiz_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CampaignMetrics':
        """Create a CampaignMetrics instance from a dictionary."""
        return cls(
            click_rate=data.get("click_rate", 0.0),
            quiz_completion_rate=data.get("quiz_completion_rate", 0.0),
            avg_quiz_score=data.get("avg_quiz_score", 0.0)
        )

@dataclass
class Campaign:
    """Represents a phishing campaign."""
    name: str
    company: CompanyInfo
    scenario: ScenarioInfo
    recipients: List[Target] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    status: str = "draft"  # draft, active, completed, cancelled
    email_content: Optional[EmailContent] = None
    advanced: AdvancedOptions = field(default_factory=AdvancedOptions)
    metrics: CampaignMetrics = field(default_factory=CampaignMetrics)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "status": self.status,
            "company": self.company.to_dict(),
            "scenario": self.scenario.to_dict(),
            "recipients": [r.to_dict() for r in self.recipients],
            "email_content": self.email_content.to_dict() if self.email_content else None,
            "advanced": self.advanced.to_dict(),
            "metrics": self.metrics.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Campaign':
        """Create a Campaign instance from a dictionary."""
        campaign = cls(
            name=data["name"],
            company=CompanyInfo.from_dict(data["company"]),
            scenario=ScenarioInfo.from_dict(data["scenario"]),
            id=data.get("id", str(uuid.uuid4())),
            created_at=data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M")),
            status=data.get("status", "draft"),
            advanced=AdvancedOptions.from_dict(data.get("advanced", {})),
            metrics=CampaignMetrics.from_dict(data.get("metrics", {}))
        )
        
        # Add recipients
        campaign.recipients = [Target.from_dict(r) for r in data.get("recipients", [])]
        
        # Add email content if available
        if "email_content" in data and data["email_content"]:
            campaign.email_content = EmailContent.from_dict(data["email_content"])
        
        return campaign
    
    def update_metrics(self) -> None:
        """Update campaign metrics based on recipient data."""
        total_recipients = len(self.recipients)
        if total_recipients == 0:
            return
        
        sent_count = sum(1 for r in self.recipients if r.status in ['sent', 'clicked', 'completed-quiz'])
        clicked_count = sum(1 for r in self.recipients if r.status in ['clicked', 'completed-quiz'])
        quiz_count = sum(1 for r in self.recipients if r.status == 'completed-quiz')
        
        self.metrics.click_rate = clicked_count / sent_count if sent_count > 0 else 0
        self.metrics.quiz_completion_rate = quiz_count / clicked_count if clicked_count > 0 else 0
        
        quiz_scores = [r.quiz_score for r in self.recipients if r.quiz_score is not None]
        self.metrics.avg_quiz_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0