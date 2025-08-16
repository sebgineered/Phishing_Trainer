from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
import uuid

@dataclass
class Target:
    """Represents a target user for a phishing campaign."""
    email: str
    name: Optional[str] = None
    department: Optional[str] = None
    clicked: bool = False
    submitted_data: bool = False
    training_sent: bool = False
    click_time: Optional[datetime] = None
    submission_time: Optional[datetime] = None
    training_time: Optional[datetime] = None

@dataclass
class PhishingTemplate:
    """Represents a phishing email template."""
    name: str
    subject: str
    content: str
    difficulty: int = 3  # Scale of 1-5
    tags: List[str] = field(default_factory=list)
    custom: bool = False

@dataclass
class TrainingContent:
    """Represents training content to be sent after phishing simulation."""
    name: str
    subject: str
    content: str
    difficulty: int = 3  # Scale of 1-5
    tags: List[str] = field(default_factory=list)

@dataclass
class Campaign:
    """Represents a phishing simulation campaign."""
    name: str
    template: PhishingTemplate
    training: TrainingContent
    targets: List[Target] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    active: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    
    @property
    def total_targets(self) -> int:
        """Get the total number of targets in the campaign."""
        return len(self.targets)
    
    @property
    def click_count(self) -> int:
        """Get the number of targets who clicked the phishing link."""
        return sum(1 for target in self.targets if target.clicked)
    
    @property
    def submission_count(self) -> int:
        """Get the number of targets who submitted data."""
        return sum(1 for target in self.targets if target.submitted_data)
    
    @property
    def training_count(self) -> int:
        """Get the number of targets who received training."""
        return sum(1 for target in self.targets if target.training_sent)
    
    @property
    def click_rate(self) -> float:
        """Get the click-through rate as a percentage."""
        if not self.targets:
            return 0.0
        return (self.click_count / self.total_targets) * 100
    
    @property
    def submission_rate(self) -> float:
        """Get the data submission rate as a percentage."""
        if not self.targets:
            return 0.0
        return (self.submission_count / self.total_targets) * 100
    
    @property
    def status(self) -> str:
        """Get the current status of the campaign."""
        if not self.start_time:
            return "Draft"
        if not self.active:
            return "Completed"
        return "Active"