import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Union

from utils.dict import CaseInsensitiveDict


DEFAULT_CONDITION = 'True'

@dataclass
class PromptConfig:
    task   :str
    source :str  = None
    params :dict = field(default_factory=dict)

@dataclass
class FunctionConfig:
    task   :str
    source :str = None
    params :dict = field(default_factory=dict)

@dataclass
class TaskType:
    prompt   :str = 'prompt'
    function :str = 'function'

@dataclass
class TaskConfig:
    type: Union[str, TaskType]
    task: str
    params: dict = field(default_factory=dict)

    def __init__(
        self,
        type: Union[str, TaskType],
        task: Union[str, dict, PromptConfig, FunctionConfig],
        params: dict = field(default_factory={}),
        *,
        prompt_dict: Dict[str, PromptConfig] = None,
        function_dict: Dict[str, FunctionConfig] = None,
    ):

        base_task_config = {}

        if prompt_dict and type == TaskType.prompt and task in prompt_dict:
            base_task_config:PromptConfig = prompt_dict[task]

        elif function_dict and type == TaskType.function and task in function_dict:
            base_task_config:FunctionConfig = function_dict[task]

        # # Dynamically initialize all fields
        # init_args = locals()  # Get all local variables
        # for field_name in ActionConfig.__dataclass_fields__:
        #     if field_name in init_args:
        #         setattr(self, field_name, init_args[field_name])

        if base_task_config and isinstance(base_task_config, PromptConfig | FunctionConfig):
            self.type = type
            self.task = base_task_config.task
            self.params = {**base_task_config.params, **params}

        else:
            self.type = type
            self.task = task
            self.params = params

@dataclass
class ActionConfig(TaskConfig):
    def __init__(
        self,
        type: Union[str, TaskType],
        task: str,
        params: dict = {},
        *,
        prompt_dict: Dict[str, PromptConfig] = None,
        function_dict: Dict[str, FunctionConfig] = None,
    ):
        super().__init__(
            type=type,
            task=task,
            params=params,
            prompt_dict=prompt_dict,
            function_dict=function_dict
        )

@dataclass
class ConditionConfig(TaskConfig):
    def __init__(
        self,
        type: Union[str, TaskType],
        task: str,
        params: dict = {},
        *,
        prompt_dict: Dict[str, PromptConfig] = None,
        function_dict: Dict[str, FunctionConfig] = None,
    ):
        super().__init__(
            type=type,
            task=task,
            params=params,
            prompt_dict=prompt_dict,
            function_dict=function_dict
        )

@dataclass
class FlowConfig:
    action: Union[ActionConfig, List[ActionConfig]] = None
    condition: Union[ConditionConfig, List[ConditionConfig]] = None

    def __init__(
        self,
        action: Union[ActionConfig, List[ActionConfig]] = None,
        condition: Union[ConditionConfig, List[ConditionConfig]] = None,
        *,
        action_dict: Dict[str, ActionConfig] = None,
        condition_dict: Dict[str, ConditionConfig] = None,
    ):
        # if isinstance(action, str):
        #     self.action = action_dict[action] if action_dict else action
        if isinstance(action, str):
            self.action = CaseInsensitiveDict({DEFAULT_CONDITION: action_dict[action]})
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
class RailConfig:
    input  : RailInputConfig = field(default_factory=RailInputConfig)
    output : RailOutputConfig = field(default_factory=RailOutputConfig)
    name   : str = 'rails'

    @classmethod
    def from_yaml(cls, yaml_path: Union[str, Path]) -> 'RailConfig':
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
    ) -> 'RailConfig':

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
class RailFlowConfig:
    prompts: List[PromptConfig]
    functions: List[FunctionConfig]
    actions: List[ActionConfig]
    conditions: List[ConditionConfig]
    flows: List[FlowConfig]
    rails: RailConfig

    @classmethod
    def from_yaml(cls, yaml_path: Union[str, Path]) -> 'RailFlowConfig':
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)

    @classmethod
    def from_dict(cls, config: dict) -> 'RailFlowConfig':

        _name = 'prompts'
        prompts = {_name: PromptConfig(**_config) for _name, _config in config[_name].items()} \
            if config.get(_name) else {}

        _name = 'functions'
        functions = {_name: FunctionConfig(**_config) for _name, _config in config[_name].items()} \
            if config.get(_name) else {}

        _name = 'actions'
        actions = {
            _name: ActionConfig(**_config, prompt_dict=prompts)#, function_dict=functions)
            for _name, _config in config[_name].items()
        } if config.get(_name) else {}

        _name = 'conditions'
        conditions = {
            _name: ConditionConfig(**_config, prompt_dict=prompts)#, function_dict=functions)
            for _name, _config in config[_name].items()
        } if config.get(_name) else {}

        _name = 'flows'
        flows = {
            _name: FlowConfig(
                **_config,
                action_dict=actions,
                condition_dict=conditions,
            ) for _name, _config in config[_name].items()
        } if config.get(_name) else {}

        _name = 'rails'
        rails = RailConfig.from_dict(
            config[_name],
            action_dict=actions,
            condition_dict=conditions,
            flow_dict=flows,
        ) if config.get(_name) else {}

        return cls(
            prompts=prompts,
            functions=functions,
            actions=actions,
            conditions=conditions,
            flows=flows,
            rails=rails,
        )