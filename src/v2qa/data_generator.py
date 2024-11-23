import re
import json
from jinja2 import Template
from typing import Dict, List

from v2qa.config import *
from utils.image_process import encode_image


class NoMatchingFlowError(Exception):
    def __init__(self, image_path, flows):
        self.image_path = image_path
        self.flows = list(flows.keys())
        super().__init__(
            f"No matching flow found for image: {image_path}. "
            f"Attempted flows: {', '.join(self.flows)}"
        )

class BudgeRigar:

    def __init__(self, engine=None):
        self.engine = engine

    def _prepare_messages(
        self,
        image_path:str,
        prompt_template:str,
        prompt_params:dict={},
    ):
        image_url = encode_image(image_path)

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": Template(prompt_template).render(**prompt_params),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                        "url": image_url,
                        },
                    },
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
        image_path:str,
        type:bool,
        task:str,
        params:dict={},
        generation_params:dict={},
    ):
        messages = self._prepare_messages(image_path, task, params)

        response = self.engine.chat.completions.create(
            messages=messages,
            **generation_params,
        )

        response_content = response.choices[0].message.content
        if (type:=eval(type)) == bool:
            return eval(response_content)
        # elif type == str:
        #     return type(response_content.lower())
        else:
            return type(response_content.strip())

    def execute_action(
        self,
        image_path:str,
        type:bool,
        task:str,
        params:dict={},
        generation_params:dict={},
    ):
        messages = self._prepare_messages(image_path, task, params)
        return messages

        response = self.engine.chat.completions.create(
            messages=messages,
            **generation_params,
        )
        print(f'response.choices[0].message.content: {response.choices[0].message.content}')
        return self.parse_and_get_generated_messages(response.choices[0].message.content)

    def generate(
        self,
        image_path:str,
        flows:Dict[str, List[FlowConfig]],
        generation_params:dict={},
    ):
        for _, flow in flows.items():

            _config = flow.condition
            if _cond_response:= self.execute_condition(
                image_path,
                **_config.__dict__,
                generation_params=generation_params,
            ):
                _config = flow.action
                _action = _config[_cond_response]
                return self.execute_action(
                    image_path,
                    **_action.__dict__,
                    generation_params=generation_params,
                )
        raise NoMatchingFlowError(image_path, flows)