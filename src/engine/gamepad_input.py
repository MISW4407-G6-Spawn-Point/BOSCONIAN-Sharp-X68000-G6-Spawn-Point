"""Soporte de gamepad: traduce los eventos del control a teclas virtuales.

Cada boton, cruceta o stick del control se convierte en un KEYDOWN/KEYUP de la tecla
configurada en gamepad.json, asi todas las escenas funcionan sin saber que hay un control.

Solo usa pygame.joystick. Los botones llegan como numeros y cada marca los numera
distinto: si un control no responde bien, se ajusta "buttons" (o "web_buttons") en el JSON.
"""

import sys
import pygame


_AXIS_KEYS = {0: ("left", "right"), 1: ("up", "down")}


class GamepadInput:
    def __init__(self, cfg:dict) -> None:
        self._deadzone = cfg["deadzone"]
        self._release_zone = cfg["release_zone"]
        buttons = cfg["web_buttons"] if sys.platform == "emscripten" else cfg["buttons"]
        self._buttons = {int(button): self._key(name) for button, name in buttons.items()}

        self._joysticks = {}
        self._axis_state = {}
        self._held_keys:dict[int, set] = {}
        self._handlers = {
            pygame.JOYDEVICEADDED: self._on_added,
            pygame.JOYDEVICEREMOVED: self._on_removed,
            pygame.JOYBUTTONDOWN: self._on_button,
            pygame.JOYBUTTONUP: self._on_button,
            pygame.JOYHATMOTION: self._on_hat,
            pygame.JOYAXISMOTION: self._on_axis,
        }

    def translate(self, event:pygame.event.Event) -> list:
        """Devuelve los eventos que debe recibir la escena por cada evento de pygame."""
        handler = self._handlers.get(event.type)
        if handler is None:
            return [event]
        out = []
        handler(event, out)
        return out

    def _on_added(self, event, out:list):
        joystick = pygame.joystick.Joystick(event.device_index)
        self._joysticks.setdefault(joystick.get_instance_id(), joystick)

    def _on_removed(self, event, out:list):
        instance = event.instance_id
        self._joysticks.pop(instance, None)
        for key, sources in self._held_keys.items():
            if any(source[0] == instance for source in sources):
                sources.difference_update({s for s in sources if s[0] == instance})
                if not sources:
                    out.append(self._key_event(pygame.KEYUP, key))
        for axis_id in [a for a in self._axis_state if a[0] == instance]:
            del self._axis_state[axis_id]

    def _on_button(self, event, out:list):
        key = self._buttons.get(event.button)
        if key is not None:
            pressed = event.type == pygame.JOYBUTTONDOWN
            self._set_key((event.instance_id, "btn", event.button), key, pressed, out)

    def _on_hat(self, event, out:list):
        x, y = event.value
        hat = (event.instance_id, "hat", event.hat)
        self._set_key(hat + ("left",), pygame.K_LEFT, x < 0, out)
        self._set_key(hat + ("right",), pygame.K_RIGHT, x > 0, out)
        self._set_key(hat + ("up",), pygame.K_UP, y > 0, out)
        self._set_key(hat + ("down",), pygame.K_DOWN, y < 0, out)

    def _on_axis(self, event, out:list):
        """Stick izquierdo como cruceta, con histeresis para que no parpadee cerca del umbral."""
        if event.axis not in _AXIS_KEYS:
            return
        axis_id = (event.instance_id, event.axis)
        state = self._axis_state.get(axis_id, 0)
        if abs(event.value) >= self._deadzone:
            state = 1 if event.value > 0 else -1
        elif abs(event.value) <= self._release_zone:
            state = 0
        self._axis_state[axis_id] = state
        negative, positive = _AXIS_KEYS[event.axis]
        source = (event.instance_id, "axis", event.axis)
        self._set_key(source + (negative,), self._key(negative), state < 0, out)
        self._set_key(source + (positive,), self._key(positive), state > 0, out)

    def _set_key(self, source:tuple, key:int, pressed:bool, out:list):
        """Una tecla sigue apretada mientras alguna fuente (boton, stick, cruceta) la tenga."""
        sources = self._held_keys.setdefault(key, set())
        if pressed and source not in sources:
            sources.add(source)
            if len(sources) == 1:
                out.append(self._key_event(pygame.KEYDOWN, key))
        elif not pressed and source in sources:
            sources.discard(source)
            if not sources:
                out.append(self._key_event(pygame.KEYUP, key))

    @staticmethod
    def _key_event(event_type:int, key:int) -> pygame.event.Event:
        return pygame.event.Event(event_type, key=key, mod=0, unicode="", scancode=0,
                                  from_gamepad=True)

    @staticmethod
    def _key(name:str) -> int:
        return pygame.key.key_code(name)
