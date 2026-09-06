# Voltereta ALMA · Radar de experiencia

Prototipo local que convierte reseñas públicas recientes en alertas investigables por local, motivo y periodo.

## Abrir

Abre `index.html` en Chrome o Edge. No requiere instalación ni servidor.
El panel se adapta al tema claro u oscuro del sistema; el botón de la barra superior fija uno de los dos.

## Qué muestra

- **Vista general**: el estado del grupo y, al lado, el único local con una señal abierta. Cabe en una pantalla, sin desplazamiento.
- **Local a local**: por cada local, las tres notas (últimas 100, ficha, últimas 25), la distribución de estrellas, los temas de las reseñas negativas, la evidencia pública con enlace a cada reseña original y una acción propuesta.
- **Día a día**: el ritmo de reseñas negativas por semanas y por días, con el texto de cada una.
- **Método y datos**: cómo se calculan delta y el valor p, y qué abre una alerta.

## Cómo se decide una alerta

No se calcula con la nota, sino con el porcentaje de reseñas de 1 y 2 estrellas. Se compara ese porcentaje
en las últimas 100 reseñas contra el resto de la muestra del mismo local, y se abre alerta solo si se cumplen
las dos condiciones: el porcentaje ha subido, y el valor p está por debajo de 0,05.

Con la muestra actual solo Toscana la cumple: su nota reciente cae a 4,10 frente a 4,80 en la ficha, con p = 0,001.

## Lo que estos datos NO permiten decir

Google solo da fechas relativas y acumula todo lo anterior a un mes en un único cubo, «hace un mes».
Ese cubo queda **fuera** de la serie semanal: en dos locales contiene el 88 % y el 100 % de sus bloques
antiguos, así que compararlo con una semana real produciría una tendencia inventada. Por la misma razón,
las estrellas de Google no se mezclan con las de Tripadvisor: sus muestras y sus sesgos son distintos.

Los temas se detectan por palabras clave sobre el texto de las reseñas negativas, sin interpretar el sentido
de cada frase. Sirven para orientar dónde mirar, no para contar quejas.

## Alcance

- 1.760 reseñas recientes de Google: 300 por cada local prioritario y 200 por los demás, salvo Kioto (60).
- Ocho fichas Google con 133.393 valoraciones visibles en conjunto; siete tienen dos bloques comparables.
- Fecha de cierre de la captura: 5 de septiembre de 2026.

Consulta `NOTA_DE_EVIDENCIA.md` para las decisiones metodológicas y `metricas.csv` para las cifras que alimentan el panel.
