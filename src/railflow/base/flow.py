import re
import json
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

    def parse_and_get_generated_messages(self, content:str):
        """Parses the input content to extract generated messages.

        Args:
            content (str): The content containing the JSON messages.

        Returns:
            list: A list of messages extracted from the content if successful; otherwise, None.
        """
        pattern = r'.*?"messages":\s*(\[[^]]*\]).*?'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            try:
                json_str = match.group(1)
                messages = json.loads(json_str)
                return messages
            except Exception as e:
                return None # TODO
        else:
            print("No match found.")
            return None # TODO

    def execute_condition(
        self,
        type:bool,
        task:str,
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

        response_content = response.choices[0].message.content

        # if (type:=eval(type)) == bool:
        #     return eval(response_content)
        # # elif type == str:
        # #     return type(response_content.lower())
        # else:
        #     return type(response_content.strip())
        return response_content.strip()

    def execute_action(
        self,
        type:bool,
        task:str,
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
        # return self.parse_and_get_generated_messages(response.choices[0].message.content)
        return response.choices[0].message.content

    def generate(
        self,
        flows:Dict[str, List[FlowConfig]],
        generation_params:dict={},
        prompt_params:dict={},
        image_path:str=None,
    ):
        for _, flow in flows.items():

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
        raise NoMatchingFlowError(image_path, flows)