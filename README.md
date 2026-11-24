# BOSCONIAN (Sharp X68000) - Proyecto Final
Curso: Introducción al desarrollo de videojuegos con ECS
Stack: Python + Pygame-CE + Esper 2.5 · Resolución: 256x208

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
| `assets/cfg/` | Configuración JSON (niveles, entidades, alertas, UI) |
| `assets/img/` `assets/snd/` `assets/fnt/` | Recursos gráficos, sonido y fuente |
| `src/engine/` | GameEngine, Service Locator y servicios |
| `src/engine/scenes/` | Clase base de escenas |
| `src/game/` | Escenas concretas del juego |
| `src/ecs/components/` | Componentes `c_*.py` y tags `c_tag_*.py` |
| `src/ecs/systems/` | Sistemas `s_*.py` |
| `src/create/` | Creación de entidades (prefabs) |
| `docs/` | Propuesta, avance, post-mortems y diagramas |

## Ejecutar
pip install -r requirements.txt
python main.py           (escritorio)
python -m pygbag .       (navegador, http://localhost:8000)

## Controles y mecánicas
| Tecla | Acción |
|-------|--------|
| Flechas | Girar / mover la nave (8 direcciones) |
| Z | Disparar |
| X | BOOST: súper velocidad (no letal) |
| P | Pausa |
| ESC | Volver al título (en juego y desde instrucciones/créditos) |
| Enter / Z (menús) | Empezar partida |
| I (título) | Instrucciones (HOW TO PLAY) |
| C (título) | Créditos |
| F1 / F2 / F3 | Trampas: siguiente nivel / invencible / alerta roja |
| F4 | Editor de niveles: clic pone base, clic derecho la quita, R rota, M núcleo, J inicio del jugador, 1-4 opciones, S guarda, L carga, D vuelve al original, F4 juega |

- **Habilidad especial por nivel:** en el nivel 1 la nave dispara 2 balas (adelante y atrás); desde el nivel 2 (`"special_shot": true` en `assets/cfg/level.json`) dispara 4: 3 al frente en abanico (separación `special_spread` de `bullet.json`) y 1 atrás. Al iniciar esos niveles aparece el aviso "SPECIAL WEAPON!".
