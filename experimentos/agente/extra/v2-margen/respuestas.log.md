# Log de corrida del agente

- Fecha: 2026-10-04T20:36:21
- Modelo: `deepseek/deepseek-v4-flash-0731`
- Preguntas: `eval_extra\preguntas_agente_extra.jsonl` (12)

## Resumen

| Pregunta | Herramientas | Llamadas al modelo | Tokens entrada | Tokens salida (razonamiento) | Costo USD | Segundos |
|---|---|---|---|---|---|---|
| Y01 | buscar_documentos | 2 | 3679 | 115 (29) | 0.000203 | 58.0 |
| Y02 | buscar_documentos | 2 | 3707 | 164 (48) | 0.000266 | 7.4 |
| Y03 | buscar_documentos | 2 | 3761 | 290 (158) | 0.000428 | 10.8 |
| Y04 | consultar_camas | 2 | 3649 | 106 (32) | 0.000191 | 3.6 |
| Y05 | consultar_guardia | 2 | 3745 | 235 (141) | 0.000358 | 5.6 |
| Y06 | consultar_turnos | 2 | 3649 | 118 (27) | 0.000207 | 4.1 |
| Y07 | consultar_farmacia | 2 | 3658 | 116 (30) | 0.000204 | 7.9 |
| Y08 | consultar_espera | 2 | 3720 | 150 (96) | 0.000249 | 4.7 |
| Y09 | consultar_turnos, buscar_documentos | 2 | 3886 | 382 (200) | 0.000548 | 8.4 |
| Y10 | consultar_camas, buscar_documentos | 2 | 3825 | 196 (65) | 0.000309 | 7.5 |
| Y11 | consultar_farmacia, buscar_documentos | 2 | 3970 | 376 (160) | 0.000542 | 13.6 |
| Y12 | consultar_espera, buscar_documentos | 2 | 3921 | 228 (121) | 0.000351 | 8.2 |
| **Total** | | 24 | 45170 | 2476 (1107) | **0.003856** | 139.8 |

## Y01

**Pregunta:** ¿Cuántas horas de ayuno necesito para un análisis de colesterol?

### Llamada al modelo 1

Usage: 1762 tokens de entrada (0 en caché), 83 de salida (29 de razonamiento), USD 0.000133.

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "ayuno para análisis de colesterol laboratorio"}`

Resultado:

```text
Laboratorio de análisis clínicos — Ayuno
Para glucemia y análisis de rutina se piden 8 horas de ayuno. Para el perfil de lípidos (colesterol y triglicéridos) el ayuno es de 12 horas. Se puede tomar agua.
```

### Llamada al modelo 2

Usage: 1917 tokens de entrada (1792 en caché), 32 de salida (0 de razonamiento), USD 0.000070.

**Respuesta:**

> Para el análisis de colesterol (perfil de lípidos) necesitás 12 horas de ayuno. Se puede tomar agua.

Herramientas: buscar_documentos · costo USD 0.000203

## Y02

**Pregunta:** Si falto a varios turnos sin avisar, ¿me pueden sancionar?

### Llamada al modelo 1

Usage: 1763 tokens de entrada (1536 en caché), 97 de salida (48 de razonamiento), USD 0.000151.

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "sanciones por faltar a turnos sin avisar"}`

Resultado:

```text
Turnos en consultorios externos — Cancelación y ausencias
Un turno se puede cancelar hasta 24 horas antes sin penalidad. Quien falta sin avisar a tres turnos en el mismo año queda suspendido para sacar turnos por la web durante 60 días; en ese período puede pedirlos solo en forma presencial.
```

### Llamada al modelo 2

Usage: 1944 tokens de entrada (0 en caché), 67 de salida (0 de razonamiento), USD 0.000115.

**Respuesta:**

> Sí. Si faltás sin avisar a tres turnos en el mismo año, te suspenden para sacar turnos por la web durante 60 días; en ese período solo podés pedirlos en forma presencial. Ojo: si cancelás hasta 24 horas antes, no hay penalidad.

Herramientas: buscar_documentos · costo USD 0.000266

## Y03

**Pregunta:** Estoy embarazada de 30 semanas, ¿puedo anotarme al curso de preparación para el parto y cuándo es?

### Llamada al modelo 1

Usage: 1776 tokens de entrada (1536 en caché), 138 de salida (82 de razonamiento), USD 0.000204.

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "curso de preparación para el parto inscripción semanas de embarazo"}`

Resultado:

```text
Maternidad y parto — Curso de preparación para el parto
Es gratuito, se dicta los martes a las 17:00 en el aula del segundo piso y consta de seis encuentros. Se puede empezar desde la semana 28 de embarazo.
```

### Llamada al modelo 2

Usage: 1985 tokens de entrada (1536 en caché), 152 de salida (76 de razonamiento), USD 0.000225.

**Respuesta:**

> Sí, podés anotarte: el curso de preparación para el parto se puede empezar desde la semana 28 de embarazo y vos estás de 30. Es gratuito, se dicta los martes a las 17:00 en el aula del segundo piso y consta de seis encuentros.

Herramientas: buscar_documentos · costo USD 0.000428

## Y04

**Pregunta:** ¿Queda algún lugar en la UTI?

### Llamada al modelo 1

Usage: 1755 tokens de entrada (1536 en caché), 82 de salida (32 de razonamiento), USD 0.000132.

**Herramienta** `consultar_camas` con argumentos `{"sector": "terapia_intensiva"}`

Resultado:

```text
{"sector": "terapia_intensiva", "fecha": "2026-10-05", "datos": {"total": 12, "ocupadas": 12, "libres": 0}}
```

### Llamada al modelo 2

Usage: 1894 tokens de entrada (1792 en caché), 24 de salida (0 de razonamiento), USD 0.000060.

**Respuesta:**

> No, hoy en terapia intensiva no quedan camas libres: las 12 están ocupadas.

Herramientas: consultar_camas · costo USD 0.000191

## Y05

**Pregunta:** ¿Qué psiquiatra o psicólogo está de guardia hoy a la tarde?

### Llamada al modelo 1

Usage: 1762 tokens de entrada (1536 en caché), 127 de salida (82 de razonamiento), USD 0.000189.

**Herramienta** `consultar_guardia` con argumentos `{"especialidad": "salud_mental"}`

Resultado:

```text
{"especialidad": "salud_mental", "fecha": "2026-10-05", "datos": [{"profesional": "Lic. Andrés Villalba", "horario": "08:00-20:00"}, {"profesional": "Dra. Sofía Ledesma", "horario": "20:00-08:00"}]}
```

### Llamada al modelo 2

Usage: 1983 tokens de entrada (1792 en caché), 108 de salida (59 de razonamiento), USD 0.000168.

**Respuesta:**

> Hoy a la tarde está de guardia en salud mental el Lic. Andrés Villalba (turno de 08:00 a 20:00).

Herramientas: consultar_guardia · costo USD 0.000358

## Y06

**Pregunta:** ¿Para cuándo hay turno con el dermatólogo?

### Llamada al modelo 1

Usage: 1757 tokens de entrada (1536 en caché), 74 de salida (27 de razonamiento), USD 0.000121.

**Herramienta** `consultar_turnos` con argumentos `{"especialidad": "dermatologia"}`

Resultado:

```text
{"especialidad": "dermatologia", "fecha": "2026-10-05", "datos": ["2026-11-03 11:00", "2026-11-05 11:30"]}
```

### Llamada al modelo 2

Usage: 1892 tokens de entrada (1792 en caché), 44 de salida (0 de razonamiento), USD 0.000085.

**Respuesta:**

> Los próximos turnos con dermatología son el **3 de noviembre de 2026 a las 11:00** y el **5 de noviembre de 2026 a las 11:30**.

Herramientas: consultar_turnos · costo USD 0.000207

## Y07

**Pregunta:** ¿Hay paracetamol de 500 en la farmacia?

### Llamada al modelo 1

Usage: 1757 tokens de entrada (0 en caché), 88 de salida (30 de razonamiento), USD 0.000139.

**Herramienta** `consultar_farmacia` con argumentos `{"medicamento": "paracetamol 500 mg"}`

Resultado:

```text
{"medicamento": "paracetamol 500 mg", "fecha": "2026-10-05", "datos": {"stock": 2500, "unidad": "comprimidos"}}
```

### Llamada al modelo 2

Usage: 1901 tokens de entrada (1792 en caché), 28 de salida (0 de razonamiento), USD 0.000065.

**Respuesta:**

> Sí, hay paracetamol de 500 mg en la farmacia: 2.500 comprimidos en stock.

Herramientas: consultar_farmacia · costo USD 0.000204

## Y08

**Pregunta:** Me duele mucho el pecho, ¿cuánto voy a tener que esperar si me ponen naranja?

### Llamada al modelo 1

Usage: 1770 tokens de entrada (1536 en caché), 114 de salida (83 de razonamiento), USD 0.000173.

**Herramienta** `consultar_espera` con argumentos `{}`

Resultado:

```text
{"fecha": "2026-10-05", "minutos_por_nivel": {"rojo": 0, "naranja": 7, "amarillo": 48, "verde": 135, "azul": 210}}
```

### Llamada al modelo 2

Usage: 1950 tokens de entrada (1792 en caché), 36 de salida (13 de razonamiento), USD 0.000076.

**Respuesta:**

> Si te clasifican como naranja, la espera hoy es de 7 minutos.

Herramientas: consultar_espera · costo USD 0.000249

## Y09

**Pregunta:** Me dieron orden de kinesiología, ¿cuándo hay turno y qué tengo que llevar a la sesión?

### Llamada al modelo 1

Usage: 1772 tokens de entrada (1536 en caché), 179 de salida (83 de razonamiento), USD 0.000256.

**Herramienta** `consultar_turnos` con argumentos `{"especialidad": "kinesiologia"}`

Resultado:

```text
{"especialidad": "kinesiologia", "fecha": "2026-10-05", "datos": ["2026-10-06 18:00", "2026-10-08 18:00"]}
```

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "qué llevar a la sesión de kinesiología"}`

Resultado:

```text
Kinesiología y rehabilitación
Las sesiones de kinesiología ambulatoria se hacen con orden médica, que indica el diagnóstico y la cantidad de sesiones. Cada orden cubre un máximo de 10 sesiones; para continuar se necesita una orden nueva.

Las sesiones duran 45 minutos. Hay que traer ropa cómoda y una toalla. Dos ausencias sin aviso dan de baja el tratamiento.
```

### Llamada al modelo 2

Usage: 2114 tokens de entrada (1792 en caché), 203 de salida (117 de razonamiento), USD 0.000292.

**Respuesta:**

> El próximo turno de kinesiología es el **martes 6/10 a las 18:00** (y hay otro el jueves 8/10 a las 18:00).
>
> Para la sesión tenés que llevar **ropa cómoda y una toalla**. La orden médica ya la tenés, y cubre hasta 10 sesiones.

Herramientas: consultar_turnos, buscar_documentos · costo USD 0.000548

## Y10

**Pregunta:** Voy a tener a mi bebé acá, ¿hay camas en maternidad y quién me puede acompañar en el parto?

### Llamada al modelo 1

Usage: 1774 tokens de entrada (1536 en caché), 152 de salida (65 de razonamiento), USD 0.000222.

**Herramienta** `consultar_camas` con argumentos `{"sector": "maternidad"}`

Resultado:

```text
{"sector": "maternidad", "fecha": "2026-10-05", "datos": {"total": 20, "ocupadas": 11, "libres": 9}}
```

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "quién puede acompañar en el parto"}`

Resultado:

```text
Maternidad y parto — Parto
La mujer puede estar acompañada durante el trabajo de parto y el parto por la persona que elija. Después de un parto normal, el alta es a las 48 horas; después de una cesárea, a las 72 horas.
```

### Llamada al modelo 2

Usage: 2051 tokens de entrada (1792 en caché), 44 de salida (0 de razonamiento), USD 0.000087.

**Respuesta:**

> Sí, hoy en maternidad hay 9 camas libres de 20. Y durante el trabajo de parto y el parto podés estar acompañada por la persona que elijas.

Herramientas: consultar_camas, buscar_documentos · costo USD 0.000309

## Y11

**Pregunta:** Mi mamá toma levotiroxina de 50, ¿hay stock y puedo ir a retirarla yo por ella?

### Llamada al modelo 1

Usage: 1772 tokens de entrada (1536 en caché), 185 de salida (80 de razonamiento), USD 0.000264.

**Herramienta** `consultar_farmacia` con argumentos `{"medicamento": "levotiroxina 50 mcg"}`

Resultado:

```text
{"medicamento": "levotiroxina 50 mcg", "fecha": "2026-10-05", "datos": {"stock": 90, "unidad": "comprimidos"}}
```

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "cómo retirar medicamentos de la farmacia por otra persona requisitos"}`

Resultado:

```text
Farmacia del hospital
La farmacia de pacientes ambulatorios está en planta baja, junto a admisión, y atiende de lunes a viernes de 8:00 a 20:00. Entrega medicación a pacientes del hospital con receta de un profesional de la institución.

Para retirar medicación se presenta el DNI del paciente. Si retira otra persona, lleva su propio DNI y el del paciente.

Los medicamentos de alto costo, como los oncológicos y los biológicos, requieren un formulario de solicitud firmado por el especialista y aprobado por el comité de farmacia, que se reúne los miércoles.

La farmacia no hace entregas los fines de semana. Las recetas tienen una validez de 30 días desde la fecha de emisión.
```

### Llamada al modelo 2

Usage: 2198 tokens de entrada (0 en caché), 191 de salida (80 de razonamiento), USD 0.000278.

**Respuesta:**

> Sí, hay stock: 90 comprimidos de levotiroxina 50 mcg.
>
> Y sí, podés retirarla vos por ella: la farmacia entrega a otra persona si llevás tu DNI y el DNI de tu mamá. Eso sí, la receta tiene que ser de un profesional del hospital y tener menos de 30 días de emitida. La farmacia está en planta baja, junto a admisión, de lunes a viernes de 8 a 20.

Herramientas: consultar_farmacia, buscar_documentos · costo USD 0.000542

## Y12

**Pregunta:** Llegué a la guardia, me clasificaron amarillo: ¿cuánto se está esperando y cuál es el tiempo máximo que corresponde?

### Llamada al modelo 1

Usage: 1777 tokens de entrada (1536 en caché), 166 de salida (97 de razonamiento), USD 0.000239.

**Herramienta** `consultar_espera` con argumentos `{}`

Resultado:

```text
{"fecha": "2026-10-05", "minutos_por_nivel": {"rojo": 0, "naranja": 7, "amarillo": 48, "verde": 135, "azul": 210}}
```

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "tiempo máximo de espera según clasificación triage amarillo"}`

Resultado:

```text
Guardia y clasificación por prioridad (triage) — Los cinco niveles
- Nivel 1, rojo (resucitación): atención inmediata.
- Nivel 2, naranja (emergencia): atención en 10 minutos como máximo.
- Nivel 3, amarillo (urgencia): atención dentro de los 60 minutos.
- Nivel 4, verde (urgencia menor): atención dentro de las 2 horas.
- Nivel 5, azul (no urgente): atención dentro de las 4 horas, o derivación a consultorio externo.
```

### Llamada al modelo 2

Usage: 2144 tokens de entrada (0 en caché), 62 de salida (24 de razonamiento), USD 0.000112.

**Respuesta:**

> En la guardia hoy la espera para nivel amarillo es de **48 minutos**. El tiempo máximo que corresponde para ese nivel (urgencia) es **60 minutos**.

Herramientas: consultar_espera, buscar_documentos · costo USD 0.000351

