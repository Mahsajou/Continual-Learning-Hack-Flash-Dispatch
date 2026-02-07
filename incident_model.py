from typing import List, Optional
from pydantic import BaseModel, Field

class DispatchInfo(BaseModel):
    incident_number: Optional[str] = Field(None, description="Unique identifier for the event")
    date_time: Optional[str] = Field(None, description="Timestamp of call/dispatch/arrival")
    address: Optional[str] = Field(None, description="Verified address or location of occurrence")
    incident_type: Optional[str] = Field(None, description="Nature of the emergency (e.g., Medical, Police)")
    priority_level: Optional[str] = Field(None, description="Urgency level assigned (e.g., Priority 1)")

class PersonInfo(BaseModel):
    name: Optional[str] = Field(None, description="Name of the person")
    role: Optional[str] = Field(None, description="Role: Victim, Witness, Caller, Suspect, etc.")
    contact_info: Optional[str] = Field(None, description="Phone number or other contact details")

class GeneralDetails(BaseModel):
    involved_parties: List[PersonInfo] = Field(default_factory=list, description="List of people involved")
    description_of_events: Optional[str] = Field(None, description="Chronological, factual account of what happened")
    scene_description: Optional[str] = Field(None, description="Environmental factors, weather, hazards")
    evidence_property: Optional[str] = Field(None, description="Notes on evidence collected or property damage")

class IncidentReport(BaseModel):
    dispatch_info: DispatchInfo
    general_details: GeneralDetails
