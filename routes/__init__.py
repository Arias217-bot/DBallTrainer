# routes/__init__.py
from .usuario_routes import usuario_bp
from .equipo_routes import equipo_bp
from .categoria_edad_routes import categoria_edad_bp
from .categoria_sexo_routes import categoria_sexo_bp
from .jugadas_routes import jugadas_bp
from .rol_routes import rol_bp
from .posicion_routes import posicion_bp
from .detalle_jugada_routes import detalle_jugada_bp
from .torneo_routes import torneo_bp
from .equipo_rival_routes import equipo_rival_bp
from .jugadores_rivales_routes import jugadores_rivales_bp
from .mensajes_routes import mensajes_bp
from .partido_routes import partido_bp
from .usuario_equipo_routes import usuario_equipo_bp
from .administrador_routes import administrador_bp
from .videos_routes import videos_bp
from .deteccion_routes import deteccion_bp
from .modalidad_routes import modalidad_bp

# Definir los blueprints aquí para importarlos fácilmente
blueprints = [usuario_bp, 
              equipo_bp, 
              categoria_edad_bp, 
              categoria_sexo_bp, 
              jugadas_bp, 
              rol_bp, 
              posicion_bp, 
              detalle_jugada_bp,
              torneo_bp,
              equipo_rival_bp,
              jugadores_rivales_bp,
              mensajes_bp,
              partido_bp,
              usuario_equipo_bp,
              administrador_bp,
              videos_bp,
              deteccion_bp,
              modalidad_bp]
