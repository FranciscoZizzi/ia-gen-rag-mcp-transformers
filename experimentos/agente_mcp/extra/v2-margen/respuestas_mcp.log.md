# Log de corrida del agente

- Fecha: 2026-10-07T14:02:38
- Modelo: `deepseek/deepseek-v4-flash-0731`
- Preguntas: `eval_extra\preguntas_agente_extra.jsonl` (12)
- Transporte: MCP stdio (`servidor_mcp.py`), herramientas descubiertas con tools/list

## Resumen

| Pregunta | Herramientas | Llamadas al modelo | Tokens entrada | Tokens salida (razonamiento) | Costo USD | Segundos |
|---|---|---|---|---|---|---|
| Y01 | buscar_documentos | 2 | 3680 | 116 (31) | 0.000215 | 11.0 |
| Y02 | buscar_documentos | 2 | 3707 | 166 (48) | 0.000279 | 24.0 |
| Y03 | buscar_documentos | 2 | 3778 | 273 (147) | 0.000417 | 18.1 |
| Y04 | consultar_camas | 2 | 3653 | 109 (33) | 0.000205 | 4.4 |
| Y05 | consultar_guardia | 2 | 3770 | 263 (172) | 0.000405 | 19.6 |
| Y06 | consultar_turnos | 2 | 3648 | 114 (28) | 0.000212 | 6.8 |
| Y07 | consultar_farmacia | 2 | 3654 | 111 (28) | 0.000208 | 3.6 |
| Y08 | consultar_espera | 2 | 3742 | 173 (119) | 0.000289 | 26.8 |
| Y09 | consultar_turnos, buscar_documentos | 2 | 3881 | 318 (150) | 0.000477 | 13.9 |
| Y10 | consultar_camas, buscar_documentos | 2 | 3832 | 229 (92) | 0.000362 | 11.3 |
| Y11 | consultar_farmacia, buscar_documentos | 2 | 3953 | 368 (169) | 0.000542 | 15.4 |
| Y12 | consultar_espera, buscar_documentos | 2 | 3980 | 223 (114) | 0.000357 | 15.0 |
| **Total** | | 24 | 45278 | 2463 (1131) | **0.003968** | 169.9 |

## Y01

**Pregunta:** ¿Cuántas horas de ayuno necesito para un análisis de colesterol?

### Llamada al modelo 1

Usage: 1762 tokens de entrada (0 en caché), 84 de salida (31 de razonamiento), USD 0.000139.

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "ayuno para análisis de colesterol laboratorio"}`

Resultado:

```text
Laboratorio de análisis clínicos — Ayuno
Para glucemia y análisis de rutina se piden 8 horas de ayuno. Para el perfil de lípidos (colesterol y triglicéridos) el ayuno es de 12 horas. Se puede tomar agua.
```

### Llamada al modelo 2

Usage: 1918 tokens de entrada (1792 en caché), 32 de salida (0 de razonamiento), USD 0.000075.

**Respuesta:**

> Para el análisis de colesterol (perfil de lípidos) necesitás 12 horas de ayuno. Se puede tomar agua.

Herramientas: buscar_documentos · costo USD 0.000215

## Y02

**Pregunta:** Si falto a varios turnos sin avisar, ¿me pueden sancionar?

### Llamada al modelo 1

Usage: 1763 tokens de entrada (1536 en caché), 97 de salida (48 de razonamiento), USD 0.000156.

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "sanciones por faltar a turnos sin avisar"}`

Resultado:

```text
Turnos en consultorios externos — Cancelación y ausencias
Un turno se puede cancelar hasta 24 horas antes sin penalidad. Quien falta sin avisar a tres turnos en el mismo año queda suspendido para sacar turnos por la web durante 60 días; en ese período puede pedirlos solo en forma presencial.
```

### Llamada al modelo 2

Usage: 1944 tokens de entrada (1792 en caché), 69 de salida (0 de razonamiento), USD 0.000123.

**Respuesta:**

> Sí. Si faltás sin avisar a tres turnos en el mismo año, te suspenden para sacar turnos por la web durante 60 días; en ese período solo podés pedirlos en forma presencial. Igual, un turno se puede cancelar hasta 24 horas antes sin penalidad.

Herramientas: buscar_documentos · costo USD 0.000279

## Y03

**Pregunta:** Estoy embarazada de 30 semanas, ¿puedo anotarme al curso de preparación para el parto y cuándo es?

### Llamada al modelo 1

Usage: 1776 tokens de entrada (1536 en caché), 155 de salida (103 de razonamiento), USD 0.000230.

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "curso de preparación para el parto inscripción semanas de gestación"}`

Resultado:

```text
Maternidad y parto — Curso de preparación para el parto
Es gratuito, se dicta los martes a las 17:00 en el aula del segundo piso y consta de seis encuentros. Se puede empezar desde la semana 28 de embarazo.
```

### Llamada al modelo 2

Usage: 2002 tokens de entrada (1536 en caché), 118 de salida (44 de razonamiento), USD 0.000187.

**Respuesta:**

> Sí, podés anotarte: el curso de preparación para el parto se puede empezar desde la semana 28 de embarazo y vos estás de 30. Es gratuito, se dicta los martes a las 17:00 en el aula del segundo piso y consta de seis encuentros.

Herramientas: buscar_documentos · costo USD 0.000417

## Y04

**Pregunta:** ¿Queda algún lugar en la UTI?

### Llamada al modelo 1

Usage: 1755 tokens de entrada (1536 en caché), 86 de salida (33 de razonamiento), USD 0.000142.

**Herramienta** `consultar_camas` con argumentos `{"sector": "terapia_intensiva"}`

Resultado:

```text
{"sector": "terapia_intensiva", "fecha": "2026-10-05", "datos": {"total": 12, "ocupadas": 12, "libres": 0}}
```

### Llamada al modelo 2

Usage: 1898 tokens de entrada (1792 en caché), 23 de salida (0 de razonamiento), USD 0.000064.

**Respuesta:**

> No, hoy en la UTI no quedan lugares: las 12 camas están ocupadas.

Herramientas: consultar_camas · costo USD 0.000205

## Y05

**Pregunta:** ¿Qué psiquiatra o psicólogo está de guardia hoy a la tarde?

### Llamada al modelo 1

Usage: 1762 tokens de entrada (1536 en caché), 152 de salida (110 de razonamiento), USD 0.000226.

**Herramienta** `consultar_guardia` con argumentos `{"especialidad": "salud_mental"}`

Resultado:

```text
{"especialidad": "salud_mental", "fecha": "2026-10-05", "datos": [{"profesional": "Lic. Andrés Villalba", "horario": "08:00-20:00"}, {"profesional": "Dra. Sofía Ledesma", "horario": "20:00-08:00"}]}
```

### Llamada al modelo 2

Usage: 2008 tokens de entrada (1792 en caché), 111 de salida (62 de razonamiento), USD 0.000178.

**Respuesta:**

> Hoy a la tarde está de guardia en salud mental el Lic. Andrés Villalba (turno de 08:00 a 20:00).

Herramientas: consultar_guardia · costo USD 0.000405

## Y06

**Pregunta:** ¿Para cuándo hay turno con el dermatólogo?

### Llamada al modelo 1

Usage: 1757 tokens de entrada (1536 en caché), 73 de salida (28 de razonamiento), USD 0.000125.

**Herramienta** `consultar_turnos` con argumentos `{"especialidad": "dermatologia"}`

Resultado:

```text
{"especialidad": "dermatologia", "fecha": "2026-10-05", "datos": ["2026-11-03 11:00", "2026-11-05 11:30"]}
```

### Llamada al modelo 2

Usage: 1891 tokens de entrada (1536 en caché), 41 de salida (0 de razonamiento), USD 0.000087.

**Respuesta:**

> El próximo turno con dermatología es el **3 de noviembre de 2026 a las 11:00**. También hay otro el **5 de noviembre a las 11:30**.

Herramientas: consultar_turnos · costo USD 0.000212

## Y07

**Pregunta:** ¿Hay paracetamol de 500 en la farmacia?

### Llamada al modelo 1

Usage: 1757 tokens de entrada (0 en caché), 84 de salida (28 de razonamiento), USD 0.000139.

**Herramienta** `consultar_farmacia` con argumentos `{"medicamento": "paracetamol 500 mg"}`

Resultado:

```text
{"medicamento": "paracetamol 500 mg", "fecha": "2026-10-05", "datos": {"stock": 2500, "unidad": "comprimidos"}}
```

### Llamada al modelo 2

Usage: 1897 tokens de entrada (1792 en caché), 27 de salida (0 de razonamiento), USD 0.000069.

**Respuesta:**

> Sí, hay paracetamol de 500 mg en la farmacia: 2500 comprimidos en stock.

Herramientas: consultar_farmacia · costo USD 0.000208

## Y08

**Pregunta:** Me duele mucho el pecho, ¿cuánto voy a tener que esperar si me ponen naranja?

### Llamada al modelo 1

Usage: 1770 tokens de entrada (1536 en caché), 136 de salida (106 de razonamiento), USD 0.000206.

**Herramienta** `consultar_espera` con argumentos `{}`

Resultado:

```text
{"fecha": "2026-10-05", "minutos_por_nivel": {"rojo": 0, "naranja": 7, "amarillo": 48, "verde": 135, "azul": 210}}
```

### Llamada al modelo 2

Usage: 1972 tokens de entrada (1536 en caché), 37 de salida (13 de razonamiento), USD 0.000083.

**Respuesta:**

> Si te clasifican como naranja, la espera hoy es de unos 7 minutos.

Herramientas: consultar_espera · costo USD 0.000289

## Y09

**Pregunta:** Me dieron orden de kinesiología, ¿cuándo hay turno y qué tengo que llevar a la sesión?

### Llamada al modelo 1

Usage: 1772 tokens de entrada (0 en caché), 174 de salida (80 de razonamiento), USD 0.000255.

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

Usage: 2109 tokens de entrada (1792 en caché), 144 de salida (70 de razonamiento), USD 0.000222.

**Respuesta:**

> Tenés turnos de kinesiología el **martes 06/10 a las 18:00** y el **jueves 08/10 a las 18:00**.
>
> Para la sesión tenés que llevar **ropa cómoda y una toalla**. Las sesiones duran 45 minutos.

Herramientas: consultar_turnos, buscar_documentos · costo USD 0.000477

## Y10

**Pregunta:** Voy a tener a mi bebé acá, ¿hay camas en maternidad y quién me puede acompañar en el parto?

### Llamada al modelo 1

Usage: 1774 tokens de entrada (0 en caché), 159 de salida (75 de razonamiento), USD 0.000235.

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

Usage: 2058 tokens de entrada (0 en caché), 70 de salida (17 de razonamiento), USD 0.000127.

**Respuesta:**

> Sí, en maternidad hay 9 camas libres de 20 (11 ocupadas) hoy.
>
> En cuanto al acompañamiento: podés estar acompañada durante el trabajo de parto y el parto por la persona que elijas.

Herramientas: consultar_camas, buscar_documentos · costo USD 0.000362

## Y11

**Pregunta:** Mi mamá toma levotiroxina de 50, ¿hay stock y puedo ir a retirarla yo por ella?

### Llamada al modelo 1

Usage: 1772 tokens de entrada (0 en caché), 168 de salida (66 de razonamiento), USD 0.000247.

**Herramienta** `consultar_farmacia` con argumentos `{"medicamento": "levotiroxina 50 mcg"}`

Resultado:

```text
{"medicamento": "levotiroxina 50 mcg", "fecha": "2026-10-05", "datos": {"stock": 90, "unidad": "comprimidos"}}
```

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "retirar medicamento por otra persona farmacia requisitos"}`

Resultado:

```text
Farmacia del hospital
La farmacia de pacientes ambulatorios está en planta baja, junto a admisión, y atiende de lunes a viernes de 8:00 a 20:00. Entrega medicación a pacientes del hospital con receta de un profesional de la institución.

Para retirar medicación se presenta el DNI del paciente. Si retira otra persona, lleva su propio DNI y el del paciente.

Los medicamentos de alto costo, como los oncológicos y los biológicos, requieren un formulario de solicitud firmado por el especialista y aprobado por el comité de farmacia, que se reúne los miércoles.

La farmacia no hace entregas los fines de semana. Las recetas tienen una validez de 30 días desde la fecha de emisión.
```

### Llamada al modelo 2

Usage: 2181 tokens de entrada (1792 en caché), 200 de salida (103 de razonamiento), USD 0.000295.

**Respuesta:**

> Sí, hay stock: 90 comprimidos de levotiroxina 50 mcg.
>
> Y sí, podés retirarla vos por ella: la farmacia entrega con receta de un profesional de la institución, y si retira otra persona, tenés que llevar tu DNI y el de tu mamá. Atiende de lunes a viernes de 8:00 a 20:00 en planta baja, junto a admisión.

Herramientas: consultar_farmacia, buscar_documentos · costo USD 0.000542

## Y12

**Pregunta:** Llegué a la guardia, me clasificaron amarillo: ¿cuánto se está esperando y cuál es el tiempo máximo que corresponde?

### Llamada al modelo 1

Usage: 1777 tokens de entrada (1536 en caché), 159 de salida (89 de razonamiento), USD 0.000236.

**Herramienta** `consultar_espera` con argumentos `{}`

Resultado:

```text
{"fecha": "2026-10-05", "minutos_por_nivel": {"rojo": 0, "naranja": 7, "amarillo": 48, "verde": 135, "azul": 210}}
```

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "tiempo máximo de espera en guardia según clasificación triage amarillo"}`

Resultado:

```text
Guardia y clasificación por prioridad (triage) — Los cinco niveles
- Nivel 1, rojo (resucitación): atención inmediata.
- Nivel 2, naranja (emergencia): atención en 10 minutos como máximo.
- Nivel 3, amarillo (urgencia): atención dentro de los 60 minutos.
- Nivel 4, verde (urgencia menor): atención dentro de las 2 horas.
- Nivel 5, azul (no urgente): atención dentro de las 4 horas, o derivación a consultorio externo.

---

Guardia y clasificación por prioridad (triage)
En la guardia de adultos del Hospital Provincial Arroyo Claro la atención no sigue el orden de llegada. Una enfermera clasifica a cada paciente en uno de cinco niveles según la urgencia, y ese nivel define el tiempo máximo de espera.
```

### Llamada al modelo 2

Usage: 2203 tokens de entrada (0 en caché), 64 de salida (25 de razonamiento), USD 0.000122.

**Respuesta:**

> En la guardia, nivel amarillo (urgencia): la espera actual es de **48 minutos** y el tiempo máximo que corresponde es de **60 minutos**.

Herramientas: consultar_espera, buscar_documentos · costo USD 0.000357

