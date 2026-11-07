# Propuesta Técnica - BOSCONIAN (Sharp X68000)
**Grupo:** G6 - Spawn Point
**Curso:** Introducción al desarrollo de videojuegos

---

## Nombre y descripción del grupo

### Integrantes
| Nombre | Correo | Usuario GitHub |
|--------|--------|---------------|
|Santiago Bernal Gonzalez| s.bernalg2@uniandes.edu.co|sbernalg2|
|Maria Alejandra Sanabria Salazar|ma.sanabrias@uniandes.edu.co|               |
|Amelia Serrano Arango|a.serranoa2@uniandes.edu.co|               |

### Enlaces
- **Repositorio GitHub (privado):** https://github.com/sbernalg2/BOSCONIAN-Sharp-X68000-G6-Spawn-Point

---

## Propuesta técnica

### Tecnologías
| Herramienta | Uso |
|-------------|-----|
| Python 3.x | Lenguaje |
| Pygame-CE | Render, input, sonido |
| Esper 2.5 | Arquitectura ECS |
| pygbag | Build web |
| PyInstaller | Build Windows |
| itch.io | Publicación |

### Patrones de diseño a aplicar
| Patrón | Cómo lo aplicaremos |
|--------|---------------------|
| Game Loop | |
| ECS | |
| Command | <!-- input de teclado/gamepad --> |
| State | <!-- IA de enemigos, estados del jugador, alertas --> |
| Service Locator | <!-- imágenes, sonidos, fuentes, configs --> |
| Escena | <!-- intro, título, juego, victoria, derrota... --> |

### Bonos que evaluaremos implementar
- [ ] Intro animado
- [ ] Modo atractor
- [ ] Cutscene
- [ ] Gamepad
- [ ] Nivel jefe
- [ ] Segunda habilidad especial
- [ ] Formaciones
- [ ] Enemigo espía
- [ ] Escena de puntaje máximo
- [ ] Modo editor