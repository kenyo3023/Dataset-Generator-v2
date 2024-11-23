from openai import OpenAI

from .generic import GenericOpenAIWrapper


class OpenAIWrapper(GenericOpenAIWrapper):
    """
    A wrapper class for the OpenAI API to extend the functionality of the base OpenAI class
    by customizing chat completion behavior with default parameters.

    This class extends the GenericOpenAIWrapper to interact with OpenAI's API and merges
    default parameters with any additional ones provided during the chat completion call.

    Attributes:
        base_client (OpenAI): An instance of the OpenAI API client.
        default_chat_params (dict): Default parameters for chat completions.
        __original_create (function): A reference to the original create method for chat completions in OpenAI.

    Methods:
        __create(**kwargs):
            Merges the default parameters with the provided ones and calls the original create method.

        __getattr__(name):
            Delegates attribute access to the underlying OpenAI client instance.
    
    Args:
        **chat_params (dict): Default parameters to be used for chat completions.
    """

    def __init__(self, **chat_params):
        """
        Initializes the WrapperForOpenAI with default chat parameters.

        Args:
            **chat_params (dict): Default parameters to be used for chat completions.
        """
        super().__init__(OpenAI, **chat_params)


# class OpenAIWrapper(OpenAI):
    
#     def __init__(self, **chat_params):
#         super().__init__()
#         self.default_chat_params = chat_params
#         self.__original_create = self.chat.completions.create
#         self.chat.completions.create = self.__create
    
#     def __create(self, **kwargs):
#         merged_params = {**self.default_chat_params, **kwargs}
#         return self.__original_create(**merged_params)