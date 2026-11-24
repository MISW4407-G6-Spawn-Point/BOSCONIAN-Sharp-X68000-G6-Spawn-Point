# BOSCONIAN (Sharp X68000) - Proyecto Final
Curso: Introducción al desarrollo de videojuegos con ECS
Stack: Python + Pygame-CE + Esper 2.5 · Resolución: 320x256 a 60 FPS

## Integrantes
| Nombre | Correo | Codigo |
|--------|--------|---------------|
|Santiago Bernal Gonzalez| s.bernalg2@uniandes.edu.co|202115057|
|Maria Alejandra Sanabria Salazar|ma.sanabrias@uniandes.edu.co|202326786|
|Amelia Serrano Arango|a.serranoa2@uniandes.edu.co|202221556|
|Kevin Andres Castillo Peña|ka.castillo@uniandes.edu.co|202316252|

## Mapa del repositorio
| Ruta | Qué contiene |
|------|--------------|
| `main.py` | Punto de entrada |
| `esper/` | Librería Esper embebida (para web) |
| `assets/cfg/` | Configuración JSON (niveles, entidades, jefe, alertas, UI, gamepad) |
| `assets/img/` `assets/snd/` `assets/fnt/` | Recursos gráficos, sonido y fuente |
| `src/engine/` | GameEngine, Service Locator, servicios y entrada de gamepad |
| `src/engine/scenes/` | Clase base de escenas |
| `src/game/` | Escenas concretas del juego y editor de niveles |
| `src/ecs/components/` | Componentes `c_*.py` y tags `c_tag_*.py` |
| `src/ecs/systems/` | Sistemas `s_*.py` |
| `src/create/` | Creación de entidades (prefabs) |
| `docs/` | Propuesta (`semana5/`), diagramas y referencias |
| `save/` | Récord y niveles del editor (se crea al jugar, no se versiona) |
| `LICENCIAS.md` | Créditos y licencias de gráficos, música, fuente y sonidos |

## Ejecutar
```
pip install -r requirements.txt
python main.py           (escritorio)
python -m pygbag .       (navegador, http://localhost:8000)
```

## Controles
| Teclado | Gamepad | Acción |
|---------|---------|--------|
| Flechas | Cruceta / stick izquierdo | Girar / mover la nave (8 direcciones) |
| Z | A | Disparar |
| X | B | BOOST: súper velocidad (no letal) |
| P / Enter | START | Pausa / reanudar |
| ESC | BACK | Volver al título (en juego y desde instrucciones/créditos) |
| Enter / Z (menús) | START / A | Empezar partida |
| I (título y pausa) | Y | Instrucciones (HOW TO PLAY) |
| C (título y pausa) | X | Créditos |
| ← / → (instrucciones) | Cruceta / stick ← → | Cambiar de página |
| F1 / F2 / F3 | — | Trampas: siguiente nivel / invencible / alerta roja |
| F4 | — | Editor de niveles: clic pone base, clic derecho la quita, R rota, M núcleo, J inicio del jugador, 1-4 opciones, S guarda, L carga, D vuelve al original, F4 juega |

> **Gamepad:** funciona con controles tipo Xbox en Windows sin configurar nada. Si otro control numera los botones distinto, se cambian los números en `assets/cfg/gamepad.json` (`buttons` para escritorio, `web_buttons` para la versión web).

## Mecánicas
- **Habilidad especial por nivel:** en el nivel 1 la nave dispara 2 balas (adelante y atrás); desde el nivel 2 (`"special_shot": true` en `assets/cfg/level.json`) dispara 4: 3 al frente en abanico (separación `special_spread` de `bullet.json`) y 1 atrás. Al iniciar esos niveles aparece el aviso "SPECIAL WEAPON!".
- **BOOST:** súper velocidad por cargas. Las cargas se recuperan recogiendo cápsulas en el mapa, que también se ven en el radar.
- **Ronda jefe MOTHER BASE:** después de la ronda 10 aparece una base gigante con dos fases (primero los cañones, luego el núcleo), barra de vida y música propia. Al destruirla se pasa a la pantalla de victoria.
- **Alerta (CONDITION):** con el tiempo pasa de verde a amarilla y a roja, y en amarilla y roja aparecen más enemigos. Si el espía escapa, la alerta se pone en roja. Cada cambio tiene su sonido y la alerta roja tiene música propia.
- **Récord persistente:** el puntaje máximo se guarda en `save/` y, al superarlo, aparece la escena NEW HI-SCORE.
- **Presentación:** intro animada, cutscene BLAST OFF! al inicio de cada nivel y modo demo automático después del título.
- **Editor de niveles (F4):** permite cambiar las bases, el inicio del jugador y las opciones de cada ronda. Guarda en `save/levels.json` (escritorio) o en `localStorage` (web).
