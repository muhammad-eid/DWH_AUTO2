import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)



class StateManager:
    """
    A utility class to manage session state in Streamlit.

    This class provides methods to create, get, set, delete, and toggle session state variables.
    Each session state variable is scoped to the owner provided during initialization.

    Attributes:
        owner (str): The owner or namespace for the session state variables.
    """

    def __init__(self, owner: str, states: dict):
        """
        Initialize the StateManager with an owner.

        Args:
            owner (str): The namespace for the session state variables.
        """
        self.owner = owner
        key = self._key("state_manager")
        if key not in st.session_state:
            st.session_state[key] = self
            for name, default in states.items():
                self._create(name, default)
            self._create('status_loaded', True)
        else:
            # Reuse the existing instance
            existing_instance = st.session_state[key]
            self.__dict__ = existing_instance.__dict__

    def _key(self, name: str) -> str:
        """
        Generate a unique key for the session state variable.

        Args:
            name (str): The name of the session state variable.

        Returns:
            str: A unique key combining the owner and the variable name.
        """
        return f"{self.owner}.{name}"

    def _create(self, name: str, default=None):
        """
        Create a new session state variable.

        Args:
            name (str): The name of the session state variable.
            default: The default value for the variable.

        Returns:
            The created session state variable.

        Raises:
            ValueError: If the session state variable already exists.
        """
        key = self._key(name)
        if key not in st.session_state:
            st.session_state[key] = default
            logger.info(f"Created session state variable '{key}' with default value: {default}")
            return st.session_state[key]
        else:
            logger.error(f"Failed to create session state variable '{key}': already exists.")
            raise ValueError(f"State '{key}' already exists. Use 'set' to update it.")

    def _delete(self, name: str):
        """
        Delete a session state variable.

        Args:
            name (str): The name of the session state variable.

        Raises:
            ValueError: If the session state variable does not exist.
        """
        key = self._key(name)
        if key in st.session_state:
            del st.session_state[key]
            logger.info(f"Deleted session state variable '{key}'.")
        else:
            logger.error(f"Failed to delete session state variable '{key}': does not exist.")
            raise ValueError(f"State '{key}' does not exist. Use 'create' to initialize it.")

    def set(self, name: str, value):
        """
        Set the value of a session state variable.

        Args:
            name (str): The name of the session state variable.
            value: The value to set.

        Returns:
            The updated session state variable.

        Raises:
            ValueError: If the session state variable does not exist.
        """
        key = self._key(name)
        if key in st.session_state:
            st.session_state[key] = value
            logger.info(f"Set session state variable '{key}' to value: {value}")
            return st.session_state[key]
        else:
            logger.error(f"Failed to set session state variable '{key}': does not exist.")
            raise ValueError(f"State '{key}' does not exist. Use 'create' to initialize it.")

    def get(self, name: str):
        """
        Get the value of a session state variable.

        Args:
            name (str): The name of the session state variable.

        Returns:
            The value of the session state variable.

        Raises:
            ValueError: If the session state variable does not exist.
        """
        key = self._key(name)
        if key in st.session_state:
            value = st.session_state[key]
            logger.info(f"Retrieved session state variable '{key}' with value: {value}")
            return value
        else:
            logger.error(f"Failed to get session state variable '{key}': does not exist.")
            raise ValueError(f"State '{key}' does not exist. Use 'create' to initialize it.")

    def toggle(self, name: str):
        """
        Toggle the value of a boolean session state variable.

        Args:
            name (str): The name of the session state variable.

        Returns:
            The toggled value of the session state variable.

        Raises:
            ValueError: If the session state variable does not exist or is not a boolean.
        """
        key = self._key(name)
        if key in st.session_state:
            if isinstance(st.session_state[key], bool):
                st.session_state[key] = not st.session_state[key]
                logger.info(f"Toggled session state variable '{key}' to value: {st.session_state[key]}")
                return st.session_state[key]
            else:
                logger.error(f"Failed to toggle session state variable '{key}': not a boolean.")
                raise ValueError(f"State '{key}' is not a boolean and cannot be toggled.")
        else:
            logger.error(f"Failed to toggle session state variable '{key}': does not exist.")
            raise ValueError(f"State '{key}' does not exist. Use 'create' to initialize it.")
        
    # def status_loaded(owner: str):
    #     """
    #     Check if the status is loaded in the session state.

    #     Returns:
    #         bool: True if the status is loaded, False otherwise.
    #     """
    #     key = f"{owner}.status_loaded"
    #     return st.session_state.get(key, False)
    
    # def load(owner: str):
    #     """
    #     Check if the status is loaded in the session state.

    #     Returns:
    #         bool: True if the status is loaded, False otherwise.
    #     """
    #     key = f"{owner}.state_manager"
    #     return st.session_state.get(key)