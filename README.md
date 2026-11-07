# BOSCONIAN (Sharp X68000) - Proyecto Final
Curso: Introducción al desarrollo de videojuegos con ECS
Stack: Python + Pygame-CE + Esper 2.5 · Resolución: 256x208

## Integrantes
| Nombre | Correo | Codigo |
|--------|--------|---------------|
|Santiago Bernal Gonzalez| s.bernalg2@uniandes.edu.co|202115057|
|Maria Alejandra Sanabria Salazar|ma.sanabrias@uniandes.edu.co|               |
|Amelia Serrano Arango|a.serranoa2@uniandes.edu.co|               |

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