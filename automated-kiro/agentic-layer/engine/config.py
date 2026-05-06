"""Workflow configuration loader.

Loads workflow.yaml (agentic development workflow config) and returns validated PipelineConfig.
"""

import os
from pathlib import Path
from typing import Optional, List

import yaml

from .types import (
    PipelineConfig,
    PhaseConfig,
    GateConfig,
    LoopConfig,
    EscalationConfig,
    PipelinePhase,
)


def _get_default_config_path() -> Path:
    """Return path to the default workflow.yaml for the Kiro example."""
    return Path(__file__).parent.parent / "examples" / "kiro" / "workflow.yaml"


def load_config(config_path: Optional[str] = None) -> PipelineConfig:
    """Load and validate pipeline.yaml.

    Args:
        config_path: Path to pipeline.yaml. If None, uses default location.

    Returns:
        Validated PipelineConfig instance.

    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If YAML is invalid or fails validation.
    """
    path = Path(config_path) if config_path else _get_default_config_path()

    if not path.exists():
        raise FileNotFoundError(f"Pipeline config not found: {path}")

    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError(f"Pipeline config must be a YAML mapping, got {type(raw)}")

    # Parse phases -- supports three formats:
    # 1. List of strings: ["plan", "build", "test"]
    # 2. List of dicts: [{"name": "plan", "tools": [...]}]
    # 3. Dict of dicts: {"plan": {"prompt": "...", "permissions": "plan"}}
    phases = []
    raw_phases = raw.get("phases", [])
    if isinstance(raw_phases, dict):
        # Dict format (new pipeline.yaml): keys are phase names, values are config
        for phase_name, phase_data in raw_phases.items():
            if not isinstance(phase_data, dict):
                phase_data = {}
            phase_data = dict(phase_data)  # copy to avoid mutating raw
            # Extract gate reference (can be a file path string or inline dict)
            gate_ref = phase_data.pop("gate", None)
            gate = None
            if isinstance(gate_ref, dict):
                gate = GateConfig(**gate_ref)
            elif isinstance(gate_ref, str):
                # File reference -- store as string, resolved later
                pass
            # Remove fields not in PhaseConfig
            phase_data.pop("healing", None)
            phase_data.pop("description", None)
            phase_data.pop("permissions", None)
            template = phase_data.pop("prompt", "")
            # Map 'required' if present
            required = phase_data.pop("required", True)
            # Build tools list from permissions reference if not explicit
            tools = phase_data.pop("tools", [])
            phases.append(PhaseConfig(name=phase_name, required=required, tools=tools, gate=gate, template=template, **phase_data))
    elif isinstance(raw_phases, list):
        for phase_entry in raw_phases:
            if isinstance(phase_entry, str):
                phases.append(PhaseConfig(name=phase_entry))
            elif isinstance(phase_entry, dict):
                phase_data = dict(phase_entry)
                gate_data = phase_data.pop("gate", None)
                gate = GateConfig(**gate_data) if isinstance(gate_data, dict) else None
                phases.append(PhaseConfig(**phase_data, gate=gate))

    # Parse loops
    loops = {}
    for loop_name, loop_data in raw.get("loops", {}).items():
        loops[loop_name] = LoopConfig(**loop_data)

    # Parse escalation
    esc_data = raw.get("escalation", {})
    escalation = EscalationConfig(**esc_data) if esc_data else EscalationConfig()

    # Handle tools -- can be a string (file path reference) or a dict
    tools_raw = raw.get("tools", {})
    tools = tools_raw if isinstance(tools_raw, dict) else {}

    return PipelineConfig(
        version=raw.get("version", 1),
        runner=raw.get("runner", "kiro"),
        phases=phases,
        gates=raw.get("gates", {}),
        loops=loops,
        tools=tools,
        escalation=escalation,
        routing=raw.get("routing", {}),
    )


def get_phase_config(config: PipelineConfig, phase: PipelinePhase) -> Optional[PhaseConfig]:
    """Get PhaseConfig for a specific phase name."""
    for p in config.phases:
        if p.name == phase:
            return p
    return None


def get_gate_config(config: PipelineConfig, phase: PipelinePhase) -> Optional[GateConfig]:
    """Get the GateConfig bound to a phase.

    Checks the phase's embedded gate first, then the top-level gates mapping.
    """
    phase_config = get_phase_config(config, phase)
    if phase_config and phase_config.gate:
        return phase_config.gate
    # Check top-level gates mapping (e.g., gates.after_test)
    gate_key = f"after_{phase}"
    gate_ref = config.gates.get(gate_key)
    if isinstance(gate_ref, dict):
        return GateConfig(**gate_ref)
    return None


def get_tools_for_phase(config: PipelineConfig, phase: PipelinePhase) -> List[str]:
    """Return the tool permission list for a phase."""
    phase_config = get_phase_config(config, phase)
    if phase_config:
        return phase_config.tools
    return []
