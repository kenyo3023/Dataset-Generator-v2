import re
import copy
import json
import importlib
from jinja2 import Template
from typing import Dict, List

from .config import *
from utils.image_process import encode_image


class NoMatchingFlowError(Exception):
    def __init__(self, image_path, flows):
        self.image_path = image_path
        self.flows = list(flows.keys())
        super().__init__(
            f"No matching flow found for image: {image_path}. "
            f"Attempted flows: {', '.join(self.flows)}"
        )

def update_params(_dict:dict, key:str=None, params_to_update:dict={}):
    # Determine keys to update
    key_to_update = [key] if _dict and key else list(_dict.keys())
    for key in key_to_update:
        _dict[key].params.update(params_to_update)

def update_flow_task_params(_flows:dict, task:str, params:dict={}):
    if not params:
        return

    for key, value in params.items():

        # Case 1: Key exists in _flows
        if key in _flows:

            # If value is a nested dictionary
            if isinstance(value, dict):
                for _key, _value in value.items():

                    if getattr(_flows[key], task) and _key in getattr(_flows[key], task):
                        # Update params to specified task.params
                        update_params(getattr(_flows[key], task), key=_key, params_to_update=_value)
                    else:
                        # Update params to all task.params
                        update_params(getattr(_flows[key], task), params_to_update=value)

        # Case 2: Key doesn't exist in _flows - update all flows
        else:
            for _key, _value in _flows.items():
                if getattr(_flows[_key], task):
                    update_params(getattr(_flows[_key], task), params_to_update={key:value})

def update_flow_params(
    _flows:dict,
    action_params:dict={},
    condition_params:dict={},
):
    update_flow_task_params(_flows, 'action', action_params)
    update_flow_task_params(_flows, 'condition', condition_params)


class RailFlow:

    def __init__(self, engine=None):
        self.engine = engine

    def _prepare_messages(
        self,
        prompt_template:str,
        prompt_params:dict={},
        image_path:str=None,
    ):
        # image_url = encode_image(image_path)

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": Template(prompt_template).render(**prompt_params),
                    },
                    *(
                        [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": encode_image(image_path),
                                },
                            }
                        ] if image_path else []
                    ),
                ],
            }
        ]
        return messages

    # def parse_and_get_generated_messages(self, content:str):
    #     """Parses the input content to extract generated messages.

    #     Args:
    #         content (str): The content containing the JSON messages.

    #     Returns:
    #         list: A list of messages extracted from the content if successful; otherwise, None.
    #     """
    #     pattern = r'.*?"messages":\s*(\[[^]]*\]).*?'
    #     match = re.search(pattern, content, re.DOTALL)

    #     if match:
    #         try:
    #             json_str = match.group(1)
    #             messages = json.loads(json_str)
    #             return messages
    #         except Exception as e:
    #             return None # TODO
    #     else:
    #         print("No match found.")
    #         return None # TODO

    def execute_prompt_task(
        self,
        task:str,
        source:str=None,
        params:dict={},
        generation_params:dict={},
        image_path:str=None,
    ):
        messages = self._prepare_messages(
            prompt_template=task,
            prompt_params=params,
            image_path=image_path,
        )

        response = self.engine.chat.completions.create(
            messages=messages,
            **generation_params,
        )
        return response.choices[0].message.content

    def execute_function_task(
        self,
        task:str,
        source:str=None,
        params:dict={},
        generation_params:dict={},
        image_path:str=None,
    ):
        if source:
            source = source.replace('/', '.')
            module = importlib.import_module(source)
            function = getattr(module, task)
            if not function:
                raise ValueError(
                    f"Function '{task}' not found in module '{source}'.",
                    "Please ensure the function exists."
                )
        else:
            function = globals().get(task, None)
            if not function:
                raise ValueError(
                    f"Function '{task}' not found in global scope or module '{source}'.",
                    "Please ensure the function exists."
                )
        return function(**params)

    def execute_condition(self, type:TaskType, **kwargs):
        if type == TaskType.prompt:
            return self.execute_prompt_task(**kwargs)
        elif type == TaskType.function:
            return self.execute_function_task(**kwargs)
        return ValueError(f"Invalid TaskType: {type}. Expected in {TaskType.__annotations__}.")

    def execute_action(self, type:TaskType, **kwargs):
        if type == TaskType.prompt:
            return self.execute_prompt_task(**kwargs)
        elif type == TaskType.function:
            return self.execute_function_task(**kwargs)
        return ValueError(f"Invalid TaskType: {type}. Expected in {TaskType.__annotations__}.")

    def generate(
        self,
        flows:Dict[str, List[FlowConfig]],
        generation_params:dict={},
        action_params:dict={},
        condition_params:dict={},
        image_path:str=None,
    ):
        _flows = copy.deepcopy(flows)
        update_flow_params(
            _flows,
            action_params=action_params,
            condition_params=condition_params
        )

        for _, flow in _flows.items():

            if _condition:=flow.condition:
                _condition_response = self.execute_condition(
                    **_condition.__dict__,
                    generation_params=generation_params,
                    image_path=image_path,
                )
                _action = flow.action
                _selected_action = _action[_condition_response]
            else:
                _action = flow.action
                _selected_action = _action[DEFAULT_CONDITION]
            return self.execute_action(
                **_selected_action.__dict__,
                generation_params=generation_params,
                image_path=image_path,
            )
        raise NoMatchingFlowError(image_path, _flows)