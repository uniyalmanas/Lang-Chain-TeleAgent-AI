from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # Appends incoming messages to history
    messages: Annotated[List[BaseMessage], add_messages]
    # Tracks routing destination: 'billing_agent', 'network_agent', 'plan_agent', 'FINISH'
    next: str
    # Active agent identifier for UI telemetry
    active_agent: str
    # Real-time execution step logs for UI visualization
    execution_logs: List[dict]
    # Customer ID context
    customer_id: str
    # A/B Testing Variant context ('Variant A (Discount Focus)' or 'Variant B (Speed Focus)')
    ab_variant: Optional[str]
    # Human-In-The-Loop approval state
    requires_human_approval: Optional[bool]
    pending_tool_call: Optional[dict]


