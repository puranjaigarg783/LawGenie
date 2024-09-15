from typing import Dict

from pydantic import BaseModel, Field


class AgentOutput(BaseModel):
    """Output of each clause agent"""

    analysis: str = Field(description="An analysis of the section in laymen terms")
    recommendation: str = Field(
        description="How the current clause deviates from the benchmark documents"
    )


class FinalOutput(BaseModel):
    data: Dict[str, AgentOutput]
