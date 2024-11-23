class GenericOpenAIWrapper:
    """
    A wrapper class to extend the functionality of a given base class by customizing
    the chat completion behavior. It merges default parameters with any provided arguments
    for chat completion calls.

    Attributes:
        base_client (object): An instance of the base class provided to the wrapper.
        default_chat_params (dict): Default parameters for chat completions.
        __original_create (function): A reference to the original `create` method of the base class.

    Methods:
        __create(**kwargs):
            Merges the default parameters with the provided ones and calls the original `create` method.

        __getattr__(name):
            Delegates attribute access to the wrapped client instance.

    Args:
        base (type): The base class to wrap (e.g., OpenAI or AzureOpenAI).
        **chat_params (dict): Default parameters to be used for chat completions.
    """
    
    def __init__(self, base, **chat_params):
        """
        Initializes the OpenAIWrapper with a base class and default chat parameters.

        Args:
            base (type): The class to wrap (e.g., OpenAI or AzureOpenAI).
            **chat_params (dict): Default parameters to be used for chat completions.
        """
        self.base_client = base()
        self.default_chat_params = chat_params
        
        # Backup the original method
        self.__original_create = self.base_client.chat.completions.create
        
        # Replace the original method with the wrapped one
        self.base_client.chat.completions.create = self.__create

    def __create(self, **kwargs):
        """
        Merges the default parameters with the provided ones and calls the original `create` method.

        This method is used as a replacement for the original `create` method in `chat.completions`.
        It ensures that default parameters are always included, while additional parameters can still be passed.

        Args:
            **kwargs (dict): Additional parameters to override or extend the default chat parameters.

        Returns:
            Response: The response from the original `create` method after completing the chat request.
        """
        merged_params = {**self.default_chat_params, **kwargs}
        return self.__original_create(**merged_params)

    def __getattr__(self, name):
        """
        Delegates attribute access to the wrapped client instance.

        This method allows the wrapper to forward any attribute lookup (such as methods or properties)
        to the underlying base client instance, enabling seamless interaction with the original class.

        Args:
            name (str): The name of the attribute being accessed.

        Returns:
            The value of the requested attribute from the base client instance.
        """
        return getattr(self.base_client, name)
