# backend/app/services/sequence_service.py
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from typing import Dict, Any, Optional, List
from app.models.automation import AutomationSequence, SequenceExecution

class SequenceService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_sequence(self, workspace_id: int, sequence_data: dict) -> AutomationSequence:
        """Create a new automation sequence"""
        new_sequence = AutomationSequence(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            name=sequence_data['name'],
            description=sequence_data.get('description'),
            steps=sequence_data.get('steps', []),
            status="paused"
        )
        self.db.add(new_sequence)
        self.db.commit()
        self.db.refresh(new_sequence)
        return new_sequence
    
    def update_sequence(self, sequence_id: str, sequence_data: dict) -> Optional[AutomationSequence]:
        """Update an existing sequence"""
        sequence = self.db.query(AutomationSequence).filter(
            AutomationSequence.id == sequence_id
        ).first()
        if not sequence:
            return None
        
        if 'name' in sequence_data:
            sequence.name = sequence_data['name']
        if 'description' in sequence_data:
            sequence.description = sequence_data['description']
        if 'steps' in sequence_data:
            sequence.steps = sequence_data['steps']
        if 'status' in sequence_data:
            sequence.status = sequence_data['status']
        
        sequence.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(sequence)
        return sequence
    
    def delete_sequence(self, sequence_id: str) -> bool:
        """Delete a sequence"""
        sequence = self.db.query(AutomationSequence).filter(
            AutomationSequence.id == sequence_id
        ).first()
        if not sequence:
            return False
        self.db.delete(sequence)
        self.db.commit()
        return True
    
    def get_sequences(self, workspace_id: int) -> List[AutomationSequence]:
        """Get all sequences for a workspace"""
        return self.db.query(AutomationSequence).filter(
            AutomationSequence.workspace_id == workspace_id
        ).order_by(AutomationSequence.created_at.desc()).all()
    
    def get_sequence(self, sequence_id: str) -> Optional[AutomationSequence]:
        """Get a single sequence by ID"""
        return self.db.query(AutomationSequence).filter(
            AutomationSequence.id == sequence_id
        ).first()
    
    def toggle_status(self, sequence_id: str, is_active: bool) -> Optional[AutomationSequence]:
        """Activate or pause a sequence"""
        sequence = self.get_sequence(sequence_id)
        if not sequence:
            return None
        sequence.status = "active" if is_active else "paused"
        self.db.commit()
        self.db.refresh(sequence)
        return sequence
    
    def test_sequence(self, sequence_id: str) -> Dict:
        """Test execute a sequence (dummy)"""
        sequence = self.get_sequence(sequence_id)
        if not sequence:
            return {"success": False, "message": "Sequence not found"}
        
        print(f"\n{'='*60}")
        print(f"🧪 TESTING SEQUENCE: {sequence.name}")
        print(f"Steps: {len(sequence.steps)}")
        for i, step in enumerate(sequence.steps):
            delay = step.get('delay', 0)
            step_type = step.get('type', 'unknown')
            content = step.get('content', '')[:50]
            print(f"  Step {i+1}: After {delay}h → Send {step_type}: {content}...")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "message": f"Test executed for sequence: {sequence.name}",
            "sequence_id": sequence_id,
            "steps_count": len(sequence.steps)
        }
    
    def get_analytics(self, sequence_id: str) -> Dict:
        """Get analytics for a sequence"""
        sequence = self.get_sequence(sequence_id)
        if not sequence:
            return {}
        
        return {
            "total_triggered": sequence.total_triggered,
            "completed_count": sequence.completed_count,
            "completion_rate": round((sequence.completed_count / sequence.total_triggered * 100) if sequence.total_triggered > 0 else 0, 1),
            "last_triggered_at": sequence.last_triggered_at,
            "steps": sequence.steps
        }