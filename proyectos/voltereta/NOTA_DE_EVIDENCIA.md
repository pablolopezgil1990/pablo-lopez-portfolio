# Nota de evidencia · Voltereta ALMA v3

## Decisión de fuente

Google y Tripadvisor no se convierten en una sola media. Sus volúmenes, ordenación, perfiles de usuario y distribución de estrellas son distintos. Un promedio daría una cifra fácil de leer, pero difícil de defender.

El modelo propuesto usa:

- **Google como sensor operativo.** Genera la alerta mediante cambios dentro del mismo local y en bloques consecutivos del mismo tamaño.
- **Tripadvisor como contraste.** Aumenta la confianza si aparece el mismo problema, por ejemplo reservas o acceso.
- **Datos internos como verificación.** Reservas, comandas, turnos, tiempos de cocina y ubicación de mesa confirman la causa.

## Muestra reciente de Google

Se recopilaron reseñas visibles ordenadas por novedad. La muestra final cubre los ocho locales:

| Local | Muestra | Negativas | Últimas 100 | 100 anteriores | Cobertura aproximada |
|---|---:|---:|---:|---:|---:|
| Casa · Valencia | 200 | 5 | 2 | 3 | 1 día → 1 mes |
| Bali · Valencia | 200 | 17 | 4 | 13 | 5 h → 4 semanas |
| Manhattan · Valencia | 200 | 16 | 7 | 9 | 40 min → 1 mes |
| Kioto · Valencia | 60 | 1 | 1 | — | 15 h → 2 semanas |
| Nueva Zelanda · Zaragoza | 300 | 17 | 7 | 5 | 11 h → 1 mes |
| París · Sevilla | 200 | 9 | 2 | 7 | 47 min → 1 mes |
| Tanzania · Alicante | 300 | 16 | 4 | 5 | 1 h → 1 semana |
| Toscana · Córdoba | 300 | 23 | 15 | 7 | 21 h → 1 mes |

“Últimas 100” son las 100 reseñas más recientes. “100 anteriores” es el bloque inmediatamente anterior, situado a la derecha en orden temporal. No es un periodo fijo de calendario: depende de la velocidad de reseñas de cada local. Las fechas de Google son relativas y, en algunos casos, redondeadas; ALMA conserva el primer y último marcador de cada bloque.

## Señales principales

### Toscana

La puntuación visible es 4,8★ sobre 7.289 opiniones. En la muestra reciente, las negativas pasan de 1 a 7 y después a 15 por cada bloque de 100. Entre las últimas 100 aparecen cuatro menciones clasificadas como comida o ejecución, cuatro como espera o servicio y tres como reserva o acceso.

La señal requiere revisar las tres semanas afectadas: asignación de patio durante agosto, tiempo entre entrantes y principales, ejecución de pizzas y recuperación de incidencias.

### Nueva Zelanda

Cinco negativas comparten la etiqueta temporal “hace 6 días”. Dos describen una espera y problemas de platos muy parecidos. Pueden proceder de una sola visita o mesa. La aplicación avisa del incidente y exige deduplicarlo antes de calcular su impacto operativo.

### Tanzania

Las 300 reseñas cubren aproximadamente una semana. Hay 16 negativas, aunque el bloque más reciente mejora: 4 frente a 5 y 7 en los bloques anteriores. Google y la muestra de Tripadvisor coinciden en fricción de reservas o contacto. La alerta se mantiene como incidencia abierta, no como deterioro confirmado.

## Fichas públicas

Las ocho fichas Google sumaban 133.393 valoraciones visibles al cerrar la muestra. Siete locales tienen al menos dos bloques comparables. Kioto queda marcado como “Muestra corta” porque la interfaz pública solo permitió recuperar 60 reseñas en esta captura.

## Limitaciones técnicas

Se utilizó `gosom/google-maps-scraper` v1.17.4 para localizar y validar fichas. La vía extendida de reseñas devolvió un bloqueo de Google, descrito también en incidencias públicas del repositorio. La muestra reciente se completó sobre la interfaz pública, ordenada por “Más recientes”, conservando identificadores únicos y enlaces directos individuales para evitar duplicados durante el desplazamiento.

Para producción conviene conectar una fuente autorizada o un proveedor con condiciones estables, programar capturas diarias y guardar la fecha exacta de extracción. La alerta debe enlazarse después con información interna del restaurante.

## Regla propuesta para producción

1. Calcular negativas de 1–2★ por bloques comparables dentro de Google.
2. Abrir alerta cuando el bloque reciente supere la base histórica y alcance un mínimo de casos.
3. Elevar la confianza si el mismo motivo aparece en otra plataforma o en datos internos.
4. Agrupar reseñas potencialmente correlacionadas por fecha, texto y visita antes de estimar alcance.
5. Cerrar la alerta cuando la causa se haya confirmado y el siguiente bloque vuelva al nivel normal.
