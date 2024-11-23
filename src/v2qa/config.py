import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Union

from utils.dict import CaseInsensitiveDict


@dataclass
class ActionConfig:
    type: bool | str | int
    task: str
    task_params: dict = field(default_factory=dict)

@dataclass
class ConditionConfig:
    type: bool | str | int
    task: str
    task_params: dict = field(default_factory=dict)

@dataclass
class FlowConfig:
    action: Union[ActionConfig, List[ActionConfig]]
    condition: Union[ConditionConfig, List[ConditionConfig]]

    def __init__(
        self,
        action: Union[ActionConfig, List[ActionConfig]],
        condition: Union[ConditionConfig, List[ConditionConfig]],
        *,
        action_dict: Dict[str, ActionConfig] = None,
        condition_dict: Dict[str, ConditionConfig] = None,
    ):
        # if isinstance(action, str):
        #     self.action = action_dict[action] if action_dict else action
        if isinstance(action, str):
            self.action = CaseInsensitiveDict({True: action_dict[action]})
        else:
            # Handle the mapping case where action is a dictionary
            self.action = CaseInsensitiveDict({
                key: action_dict[action_name] if action_dict else action_name
                for key, action_name in action.items()
            })

        self.condition = condition_dict[condition] if condition_dict else condition

@dataclass
class RailInputConfig:
    flows: List[FlowConfig] = field(default_factory=list)

@dataclass
class RailOutputConfig:
    flows: List[FlowConfig] = field(default_factory=list)

@dataclass
class RailsConfig:
    input  : RailInputConfig = field(default_factory=RailInputConfig)
    output : RailOutputConfig = field(default_factory=RailOutputConfig)
    name   : str = 'rails'

    @classmethod
    def from_yaml(cls, yaml_path: Union[str, Path]) -> 'RailsConfig':
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if cls.name not in config:
            raise KeyError(f"Missing required '{cls.name}' field in configuration.")
        return cls.from_dict(config[cls.name])

    @classmethod
    def from_dict(
        cls,
        rail_configs: dict,
        *,
        action_dict: Dict[str, ActionConfig] = None,
        condition_dict: Dict[str, ConditionConfig] = None,
        flow_dict: List[FlowConfig] = None,
    ) -> 'RailsConfig':

        process_flows = lambda flows, flow_dict, action_dict, condition_dict: {
            (key := flow) if isinstance(flow, str) else next(iter(flow.keys())): 
            flow_dict[key] if isinstance(flow, str) else FlowConfig(
                **next(iter(flow.values())),
                action_dict=action_dict,
                condition_dict=condition_dict
            )
            for flow in flows
        }

        return cls(
            input=RailInputConfig(
                flows= process_flows(
                    rail_configs.get('input', {}).get('flows', []),
                    flow_dict,
                    action_dict,
                    condition_dict
                )
            ),
            output=RailOutputConfig(
                flows= process_flows(
                    rail_configs.get('output', {}).get('flows', []),
                    flow_dict,
                    action_dict,
                    condition_dict
                )
            ),
        )

@dataclass
class Configs:
    actions: List[ActionConfig]
    conditions: List[ConditionConfig]
    flows: List[FlowConfig]
    rails: RailsConfig

    @classmethod
    def from_yaml(cls, yaml_path: Union[str, Path]) -> 'Configs':
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)

    @classmethod
    def from_dict(cls, config: dict) -> 'Configs':

        _name = 'actions'
        actions = {_name: ActionConfig(**_config) for _name, _config in config[_name].items()}

        _name = 'conditions'
        conditions = {_name: ConditionConfig(**_config) for _name, _config in config[_name].items()}

        _name = 'flows'
        flows = {_name: FlowConfig(
            **_config,
            action_dict=actions,
            condition_dict=conditions,
        )
        for _name, _config in config[_name].items()}

        _name = 'rails'
        rails = RailsConfig.from_dict(
            config[_name],
            action_dict=actions,
            condition_dict=conditions,
            flow_dict=flows,
        )

        return cls(
            actions=actions,
            conditions=conditions,
            flows=flows,
            rails=rails,
        )