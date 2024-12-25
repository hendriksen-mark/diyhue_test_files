from typing import Any, Dict

from configHandler import bridgeConfig_Light
import wled
import native_multi
import homeassistant_ws
import govee
protocols = [wled, native_multi, homeassistant_ws, govee]
import logManager

logging = logManager.logger.get_logger(__name__)

def syncWithLights(off_if_unreachable: bool) -> None:
    """
    Synchronize the state of the lights with their actual state.

    Args:
        off_if_unreachable (bool): If True, set state to off if the light is unreachable.
    """
    logging.info("start lights sync")
    for key, light in bridgeConfig_Light.items():
        for protocol in protocols:
            if light.protocol == protocol.__name__:
                try:
                    logging.debug("fetch " + light.name)
                    new_state: Dict[str, Any] = protocol.get_light_state(light)
                    logging.debug(new_state)
                    light.state.update(new_state)
                    light.state["reachable"] = True
                except Exception as e:
                    light.state["reachable"] = False
                    if off_if_unreachable:
                        light.state["on"] = False
                    logging.warning(f"{light.name} is unreachable: {e}")
                break
