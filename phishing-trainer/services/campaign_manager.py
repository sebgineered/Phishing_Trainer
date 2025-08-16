import os
import json
import uuid
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

class CampaignManager:
    """Service for managing phishing simulation campaigns."""
    
    def __init__(self):
        """Initialize the campaign manager."""
        # Ensure data directory exists
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Path to campaigns data file
        self.campaigns_file = self.data_dir / "campaigns.json"
        
        # Load existing campaigns
        self.campaigns = self._load_campaigns()
    
    def _load_campaigns(self) -> Dict[str, Any]:
        """Load existing campaigns from file."""
        if not self.campaigns_file.exists():
            return {}
        
        try:
            with open(self.campaigns_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading campaigns: {e}")
            return {}
    
    def _save_campaigns(self):
        """Save campaigns to file."""
        try:
            with open(self.campaigns_file, 'w') as f:
                json.dump(self.campaigns, f, indent=2)
        except Exception as e:
            print(f"Error saving campaigns: {e}")
    
    def create_campaign(self, name: str, company_info: Dict[str, Any], 
                       scenario_info: Dict[str, Any], targets: List[Dict[str, Any]], 
                       email_content: Optional[Dict[str, Any]] = None,
                       advanced_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new phishing simulation campaign.
        
        Args:
            name: The name of the campaign
            company_info: Information about the company to impersonate
            scenario_info: Information about the phishing scenario
            targets: List of target recipients
            email_content: Optional pre-generated email content
            advanced_options: Optional advanced campaign options
            
        Returns:
            The created campaign object
        """
        # Generate a unique ID for the campaign
        campaign_id = str(uuid.uuid4())
        
        # Create campaign object
        campaign = {
            "id": campaign_id,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "draft",  # draft, scheduled, in_progress, completed
            "company_info": company_info,
            "scenario_info": scenario_info,
            "targets": targets,
            "email_content": email_content or {},
            "advanced_options": advanced_options or {},
            "metrics": {
                "total_targets": len(targets),
                "emails_sent": 0,
                "emails_opened": 0,
                "links_clicked": 0,
                "quizzes_completed": 0,
                "avg_quiz_score": 0
            }
        }
        
        # Add to campaigns and save
        self.campaigns[campaign_id] = campaign
        self._save_campaigns()
        
        return campaign
    
    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get a campaign by ID.
        
        Args:
            campaign_id: The ID of the campaign
            
        Returns:
            The campaign object, or None if not found
        """
        return self.campaigns.get(campaign_id)
    
    def get_all_campaigns(self) -> List[Dict[str, Any]]:
        """Get all campaigns.
        
        Returns:
            A list of all campaign objects
        """
        return list(self.campaigns.values())
    
    def update_campaign(self, campaign_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a campaign.
        
        Args:
            campaign_id: The ID of the campaign to update
            updates: Dictionary of fields to update
            
        Returns:
            The updated campaign object, or None if not found
        """
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return None
        
        # Update the campaign
        for key, value in updates.items():
            if key in campaign and isinstance(campaign[key], dict) and isinstance(value, dict):
                # Merge dictionaries for nested fields
                campaign[key].update(value)
            else:
                # Replace the field
                campaign[key] = value
        
        # Update the updated_at timestamp
        campaign["updated_at"] = datetime.now().isoformat()
        
        # Save the changes
        self._save_campaigns()
        
        return campaign
    
    def delete_campaign(self, campaign_id: str) -> bool:
        """Delete a campaign.
        
        Args:
            campaign_id: The ID of the campaign to delete
            
        Returns:
            True if the campaign was deleted, False if not found
        """
        if campaign_id not in self.campaigns:
            return False
        
        # Remove the campaign
        del self.campaigns[campaign_id]
        
        # Save the changes
        self._save_campaigns()
        
        return True
    
    def clone_campaign(self, campaign_id: str, new_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Clone an existing campaign.
        
        Args:
            campaign_id: The ID of the campaign to clone
            new_name: Optional new name for the cloned campaign
            
        Returns:
            The cloned campaign object, or None if the original was not found
        """
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return None
        
        # Create a new campaign ID
        new_campaign_id = str(uuid.uuid4())
        
        # Clone the campaign
        new_campaign = campaign.copy()
        new_campaign["id"] = new_campaign_id
        new_campaign["name"] = new_name or f"{campaign['name']} (Clone)"
        new_campaign["created_at"] = datetime.now().isoformat()
        new_campaign["updated_at"] = datetime.now().isoformat()
        new_campaign["status"] = "draft"
        
        # Reset metrics
        new_campaign["metrics"] = {
            "total_targets": len(new_campaign["targets"]),
            "emails_sent": 0,
            "emails_opened": 0,
            "links_clicked": 0,
            "quizzes_completed": 0,
            "avg_quiz_score": 0
        }
        
        # Add to campaigns and save
        self.campaigns[new_campaign_id] = new_campaign
        self._save_campaigns()
        
        return new_campaign
    
    def update_campaign_metrics(self, campaign_id: str, metrics_updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update the metrics for a campaign.
        
        Args:
            campaign_id: The ID of the campaign
            metrics_updates: Dictionary of metrics to update
            
        Returns:
            The updated campaign metrics, or None if campaign not found
        """
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return None
        
        # Update the metrics
        campaign["metrics"].update(metrics_updates)
        
        # Update the updated_at timestamp
        campaign["updated_at"] = datetime.now().isoformat()
        
        # Save the changes
        self._save_campaigns()
        
        return campaign["metrics"]
    
    def update_target_status(self, campaign_id: str, recipient_id: str, 
                           status: str, additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update the status of a target recipient in a campaign.
        
        Args:
            campaign_id: The ID of the campaign
            recipient_id: The ID of the recipient
            status: The new status (queued, sent, bounced, clicked, completed-quiz)
            additional_data: Optional additional data to update
            
        Returns:
            True if the target was updated, False if not found
        """
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return False
        
        # Find the target
        target_found = False
        for target in campaign["targets"]:
            if target.get("id") == recipient_id:
                # Update the status
                target["status"] = status
                target["status_updated_at"] = datetime.now().isoformat()
                
                # Add additional data if provided
                if additional_data:
                    target.update(additional_data)
                
                target_found = True
                break
        
        if not target_found:
            return False
        
        # Update campaign metrics based on status change
        metrics = campaign["metrics"]
        if status == "sent":
            metrics["emails_sent"] = metrics.get("emails_sent", 0) + 1
        elif status == "clicked":
            metrics["links_clicked"] = metrics.get("links_clicked", 0) + 1
        elif status == "completed-quiz":
            metrics["quizzes_completed"] = metrics.get("quizzes_completed", 0) + 1
            
            # Update average quiz score if provided
            if additional_data and "quiz_score" in additional_data:
                total_score = metrics.get("avg_quiz_score", 0) * (metrics["quizzes_completed"] - 1)
                total_score += additional_data["quiz_score"]
                metrics["avg_quiz_score"] = total_score / metrics["quizzes_completed"]
        
        # Update the updated_at timestamp
        campaign["updated_at"] = datetime.now().isoformat()
        
        # Save the changes
        self._save_campaigns()
        
        return True
    
    def get_campaign_statistics(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed statistics for a campaign.
        
        Args:
            campaign_id: The ID of the campaign
            
        Returns:
            A dictionary of campaign statistics, or None if campaign not found
        """
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return None
        
        metrics = campaign["metrics"]
        total_targets = metrics["total_targets"]
        
        # Calculate percentages
        stats = {
            "total_targets": total_targets,
            "emails_sent": metrics.get("emails_sent", 0),
            "emails_sent_percent": (metrics.get("emails_sent", 0) / total_targets * 100) if total_targets > 0 else 0,
            "links_clicked": metrics.get("links_clicked", 0),
            "click_rate": (metrics.get("links_clicked", 0) / metrics.get("emails_sent", 1) * 100) if metrics.get("emails_sent", 0) > 0 else 0,
            "quizzes_completed": metrics.get("quizzes_completed", 0),
            "quiz_completion_rate": (metrics.get("quizzes_completed", 0) / metrics.get("links_clicked", 1) * 100) if metrics.get("links_clicked", 0) > 0 else 0,
            "avg_quiz_score": metrics.get("avg_quiz_score", 0),
            "status_counts": self._count_target_statuses(campaign)
        }
        
        return stats
    
    def _count_target_statuses(self, campaign: Dict[str, Any]) -> Dict[str, int]:
        """Count the number of targets in each status.
        
        Args:
            campaign: The campaign object
            
        Returns:
            A dictionary of status counts
        """
        status_counts = {
            "queued": 0,
            "sent": 0,
            "bounced": 0,
            "clicked": 0,
            "completed-quiz": 0
        }
        
        for target in campaign["targets"]:
            status = target.get("status", "queued")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return status_counts