# Log de corrida del agente

- Fecha: 2026-10-04T20:25:53
- Modelo: `deepseek/deepseek-v4-flash-0731`
- Preguntas: `eval_extra\preguntas_agente_extra.jsonl` (12)

## Resumen

| Pregunta | Herramientas | Llamadas al modelo | Tokens entrada | Tokens salida (razonamiento) | Costo USD | Segundos |
|---|---|---|---|---|---|---|
| Y01 | buscar_documentos | 2 | 1787 | 206 (59) | 0.000291 | 61.8 |
| Y02 | buscar_documentos | 2 | 1941 | 393 (138) | 0.000533 | 6.7 |
| Y03 | buscar_documentos | 2 | 1828 | 287 (103) | 0.000395 | 4.5 |
| Y04 | consultar_camas | 3 | 2894 | 269 (97) | 0.000388 | 9.4 |
| Y05 | consultar_guardia | 3 | 3139 | 374 (156) | 0.000526 | 11.3 |
| Y06 | consultar_turnos | 2 | 1761 | 145 (27) | 0.000212 | 4.3 |
| Y07 | consultar_farmacia | 3 | 2903 | 235 (87) | 0.000345 | 4.0 |
| Y08 | consultar_espera | 2 | 1797 | 209 (77) | 0.000295 | 11.4 |
| Y09 | buscar_documentos, consultar_turnos | 2 | 1976 | 445 (146) | 0.000600 | 15.3 |
| Y10 | consultar_camas, buscar_documentos | 2 | 1958 | 408 (165) | 0.000552 | 10.1 |
| Y11 | consultar_farmacia, buscar_documentos | 3 | 3511 | 534 (159) | 0.000737 | 29.6 |
| Y12 | consultar_espera, buscar_documentos | 2 | 2016 | 288 (129) | 0.000399 | 17.5 |
| **Total** | | 28 | 27511 | 3793 (1343) | **0.005273** | 185.9 |

## Y01

**Pregunta:** ¿Cuántas horas de ayuno necesito para un análisis de colesterol?

### Llamada al modelo 1

Usage: 818 tokens de entrada (0 en caché), 79 de salida (32 de razonamiento), USD 0.000114.

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "ayuno análisis de colesterol horas"}`

Resultado:

```text
Laboratorio de análisis clínicos — Ayuno
Para glucemia y análisis de rutina se piden 8 horas de ayuno. Para el perfil de lípidos (colesterol y triglicéridos) el ayuno es de 12 horas. Se puede tomar agua.
```

### Llamada al modelo 2

Usage: 969 tokens de entrada (768 en caché), 127 de salida (27 de razonamiento), USD 0.000177.

**Respuesta:**

> Para un análisis de colesterol (perfil de lípidos), necesitás **12 horas de ayuno**. 
>
> Algunas aclaraciones:
> - Durante el ayuno **sí podés tomar agua**.
> - Para otros análisis de rutina o glucemia, el ayuno es de 8 horas, pero en el caso del colesterol y triglicéridos son 12 horas.
>
> ¿Necesitás saber algo más sobre el laboratorio o los turnos?

Herramientas: buscar_documentos · costo USD 0.000291

## Y02

**Pregunta:** Si falto a varios turnos sin avisar, ¿me pueden sancionar?

### Llamada al modelo 1

Usage: 819 tokens de entrada (768 en caché), 138 de salida (54 de razonamiento), USD 0.000189.

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "sanciones por faltar a turnos sin avisar"}`

Resultado:

```text
Turnos en consultorios externos — Cancelación y ausencias
Un turno se puede cancelar hasta 24 horas antes sin penalidad. Quien falta sin avisar a tres turnos en el mismo año queda suspendido para sacar turnos por la web durante 60 días; en ese período puede pedirlos solo en forma presencial.
```

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "inasistencia a turnos sin aviso"}`

Resultado:

```text
Turnos en consultorios externos — Cancelación y ausencias
Un turno se puede cancelar hasta 24 horas antes sin penalidad. Quien falta sin avisar a tres turnos en el mismo año queda suspendido para sacar turnos por la web durante 60 días; en ese período puede pedirlos solo en forma presencial.
```

### Llamada al modelo 2

Usage: 1122 tokens de entrada (768 en caché), 255 de salida (84 de razonamiento), USD 0.000343.

**Respuesta:**

> Sí, según la normativa del hospital, hay una sanción por faltar a turnos sin avisar. Te detallo lo que encontré en los documentos:
>
> **Regla de cancelación:**
> - Un turno se puede cancelar hasta **24 horas antes** sin penalidad.
>
> **Sanción por ausencias:**
> - Quien falta **sin avisar a 3 turnos en el mismo año** queda **suspendido para sacar turnos por la web durante 60 días**.
> - Durante ese período, los turnos solo se pueden pedir **en forma presencial**.
>
> En resumen: si cancelás con más de 24 horas de anticipación no tenés problema, pero si acumulás tres ausencias sin aviso en el año, te restringen el acceso a la reserva online por dos meses. ¿Necesitás más detalles sobre el procedimiento?

Herramientas: buscar_documentos · costo USD 0.000533

## Y03

**Pregunta:** Estoy embarazada de 30 semanas, ¿puedo anotarme al curso de preparación para el parto y cuándo es?

### Llamada al modelo 1

Usage: 832 tokens de entrada (768 en caché), 93 de salida (46 de razonamiento), USD 0.000132.

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "curso de preparación para el parto"}`

Resultado:

```text
Maternidad y parto — Curso de preparación para el parto
Es gratuito, se dicta los martes a las 17:00 en el aula del segundo piso y consta de seis encuentros. Se puede empezar desde la semana 28 de embarazo.
```

### Llamada al modelo 2

Usage: 996 tokens de entrada (768 en caché), 194 de salida (57 de razonamiento), USD 0.000263.

**Respuesta:**

> ¡Sí, podés anotarte! 😊
>
> Según la información del hospital, el **curso de preparación para el parto**:
>
> - **Es gratuito**.
> - Se dicta los **martes a las 17:00** en el **aula del segundo piso**.
> - Consta de **seis encuentros**.
> - Se puede empezar desde la **semana 28 de embarazo**, y vos estás de 30 semanas, así que estás dentro del período para anotarte.
>
> ¿Querés que te ayude con algo más, como consultar turnos o alguna otra información?

Herramientas: buscar_documentos · costo USD 0.000395

## Y04

**Pregunta:** ¿Queda algún lugar en la UTI?

### Llamada al modelo 1

Usage: 811 tokens de entrada (768 en caché), 101 de salida (52 de razonamiento), USD 0.000142.

**Herramienta** `consultar_camas` con argumentos `{"sector": "UTI"}`

Resultado:

```text
{"error": "'UTI' no existe", "opciones": ["cirugia_general", "clinica_medica", "maternidad", "neonatologia", "pediatria", "terapia_intensiva"]}
```

### Llamada al modelo 2

Usage: 974 tokens de entrada (768 en caché), 78 de salida (23 de razonamiento), USD 0.000115.

**Herramienta** `consultar_camas` con argumentos `{"sector": "terapia_intensiva"}`

Resultado:

```text
{"sector": "terapia_intensiva", "fecha": "2026-10-05", "datos": {"total": 12, "ocupadas": 12, "libres": 0}}
```

### Llamada al modelo 3

Usage: 1109 tokens de entrada (768 en caché), 90 de salida (22 de razonamiento), USD 0.000132.

**Respuesta:**

> No, lamentablemente no queda lugar en la UTI (terapia intensiva). En este momento las 12 camas están ocupadas y no hay ninguna libre.
>
> ¿Querés que consulte disponibilidad en otro sector, como clínica médica o cirugía general?

Herramientas: consultar_camas · costo USD 0.000388

## Y05

**Pregunta:** ¿Qué psiquiatra o psicólogo está de guardia hoy a la tarde?

### Llamada al modelo 1

Usage: 818 tokens de entrada (768 en caché), 142 de salida (60 de razonamiento), USD 0.000194.

**Herramienta** `consultar_guardia` con argumentos `{"especialidad": "psiquiatría"}`

Resultado:

```text
{"error": "'psiquiatría' no existe", "opciones": ["cardiologia", "clinica_medica", "obstetricia", "pediatria", "salud_mental", "traumatologia"]}
```

**Herramienta** `consultar_guardia` con argumentos `{"especialidad": "psicología"}`

Resultado:

```text
{"error": "'psicología' no existe", "opciones": ["cardiologia", "clinica_medica", "obstetricia", "pediatria", "salud_mental", "traumatologia"]}
```

### Llamada al modelo 2

Usage: 1076 tokens de entrada (768 en caché), 75 de salida (22 de razonamiento), USD 0.000112.

**Herramienta** `consultar_guardia` con argumentos `{"especialidad": "salud_mental"}`

Resultado:

```text
{"especialidad": "salud_mental", "fecha": "2026-10-05", "datos": [{"profesional": "Lic. Andrés Villalba", "horario": "08:00-20:00"}, {"profesional": "Dra. Sofía Ledesma", "horario": "20:00-08:00"}]}
```

### Llamada al modelo 3

Usage: 1245 tokens de entrada (768 en caché), 157 de salida (74 de razonamiento), USD 0.000220.

**Respuesta:**

> Esta tarde está de guardia en **Salud Mental** el **Lic. Andrés Villalba**, con horario de **08:00 a 20:00 hs**. 
>
> La Dra. Sofía Ledesma cubre el turno noche (20:00 a 08:00).

Herramientas: consultar_guardia · costo USD 0.000526

## Y06

**Pregunta:** ¿Para cuándo hay turno con el dermatólogo?

### Llamada al modelo 1

Usage: 813 tokens de entrada (0 en caché), 74 de salida (27 de razonamiento), USD 0.000107.

**Herramienta** `consultar_turnos` con argumentos `{"especialidad": "dermatología"}`

Resultado:

```text
{"especialidad": "dermatologia", "fecha": "2026-10-05", "datos": ["2026-11-03 11:00", "2026-11-05 11:30"]}
```

### Llamada al modelo 2

Usage: 948 tokens de entrada (768 en caché), 71 de salida (0 de razonamiento), USD 0.000105.

**Respuesta:**

> El próximo turno con el dermatólogo es:
>
> - **Martes 3 de noviembre de 2026 a las 11:00 hs**
> - **Jueves 5 de noviembre de 2026 a las 11:30 hs**
>
> ¿Querés que te ayude a reservar alguno de estos turnos?

Herramientas: consultar_turnos · costo USD 0.000212

## Y07

**Pregunta:** ¿Hay paracetamol de 500 en la farmacia?

### Llamada al modelo 1

Usage: 813 tokens de entrada (768 en caché), 77 de salida (26 de razonamiento), USD 0.000111.

**Herramienta** `consultar_farmacia` con argumentos `{"medicamento": "paracetamol"}`

Resultado:

```text
{"error": "'paracetamol' no existe", "opciones": ["amoxicilina 500 mg", "enalapril 10 mg", "insulina NPH", "levotiroxina 50 mcg", "metformina 850 mg", "paracetamol 500 mg", "salbutamol aerosol"]}
```

### Llamada al modelo 2

Usage: 971 tokens de entrada (768 en caché), 92 de salida (38 de razonamiento), USD 0.000133.

**Herramienta** `consultar_farmacia` con argumentos `{"medicamento": "paracetamol 500 mg"}`

Resultado:

```text
{"medicamento": "paracetamol 500 mg", "fecha": "2026-10-05", "datos": {"stock": 2500, "unidad": "comprimidos"}}
```

### Llamada al modelo 3

Usage: 1119 tokens de entrada (1024 en caché), 66 de salida (23 de razonamiento), USD 0.000101.

**Respuesta:**

> Sí, hay paracetamol de 500 mg en la farmacia. El stock actual es de **2500 comprimidos** (actualizado al 05/10/2026).

Herramientas: consultar_farmacia · costo USD 0.000345

## Y08

**Pregunta:** Me duele mucho el pecho, ¿cuánto voy a tener que esperar si me ponen naranja?

### Llamada al modelo 1

Usage: 826 tokens de entrada (768 en caché), 79 de salida (46 de razonamiento), USD 0.000114.

**Herramienta** `consultar_espera` con argumentos `{}`

Resultado:

```text
{"fecha": "2026-10-05", "minutos_por_nivel": {"rojo": 0, "naranja": 7, "amarillo": 48, "verde": 135, "azul": 210}}
```

### Llamada al modelo 2

Usage: 971 tokens de entrada (768 en caché), 130 de salida (31 de razonamiento), USD 0.000181.

**Respuesta:**

> Según la información actual de la guardia, si te asignan el nivel **naranja**, la espera estimada es de aproximadamente **7 minutos**.
>
> Igualmente, te recomiendo que te acerques a la guardia para que te evalúen cuanto antes, ya que el dolor de pecho puede ser algo serio. ¿Necesitás que consulte algo más, como la guardia de alguna especialidad en particular?

Herramientas: consultar_espera · costo USD 0.000295

## Y09

**Pregunta:** Me dieron orden de kinesiología, ¿cuándo hay turno y qué tengo que llevar a la sesión?

### Llamada al modelo 1

Usage: 828 tokens de entrada (768 en caché), 157 de salida (70 de razonamiento), USD 0.000214.

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "kinesiología turno sesión qué llevar"}`

Resultado:

```text
Kinesiología y rehabilitación
Las sesiones de kinesiología ambulatoria se hacen con orden médica, que indica el diagnóstico y la cantidad de sesiones. Cada orden cubre un máximo de 10 sesiones; para continuar se necesita una orden nueva.

Las sesiones duran 45 minutos. Hay que traer ropa cómoda y una toalla. Dos ausencias sin aviso dan de baja el tratamiento.
```

**Herramienta** `consultar_turnos` con argumentos `{"especialidad": "kinesiología"}`

Resultado:

```text
{"especialidad": "kinesiologia", "fecha": "2026-10-05", "datos": ["2026-10-06 18:00", "2026-10-08 18:00"]}
```

### Llamada al modelo 2

Usage: 1148 tokens de entrada (0 en caché), 288 de salida (76 de razonamiento), USD 0.000386.

**Respuesta:**

> ¡Hola! Te cuento lo que encontré sobre kinesiología:
>
> **Próximos turnos disponibles:**
> - **Martes 06/10/2026 a las 18:00**
> - **Jueves 08/10/2026 a las 18:00**
>
> **Qué tenés que llevar a la sesión:**
> - **Ropa cómoda**
> - **Una toalla**
>
> **Algunas cosas a tener en cuenta:**
> - Las sesiones duran **45 minutos**.
> - Tu orden médica indica el diagnóstico y la cantidad de sesiones. Cada orden cubre un **máximo de 10 sesiones**; para continuar después necesitás una orden nueva.
> - **Dos ausencias sin aviso dan de baja el tratamiento**, así que si no podés asistir, avisá con tiempo.
>
> ¿Querés que te confirme alguno de los turnos o necesitás algo más?

Herramientas: buscar_documentos, consultar_turnos · costo USD 0.000600

## Y10

**Pregunta:** Voy a tener a mi bebé acá, ¿hay camas en maternidad y quién me puede acompañar en el parto?

### Llamada al modelo 1

Usage: 830 tokens de entrada (768 en caché), 173 de salida (99 de razonamiento), USD 0.000234.

**Herramienta** `consultar_camas` con argumentos `{"sector": "maternidad"}`

Resultado:

```text
{"sector": "maternidad", "fecha": "2026-10-05", "datos": {"total": 20, "ocupadas": 11, "libres": 9}}
```

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "acompañamiento en el parto"}`

Resultado:

```text
Maternidad y parto — Parto
La mujer puede estar acompañada durante el trabajo de parto y el parto por la persona que elija. Después de un parto normal, el alta es a las 48 horas; después de una cesárea, a las 72 horas.
```

### Llamada al modelo 2

Usage: 1128 tokens de entrada (0 en caché), 235 de salida (66 de razonamiento), USD 0.000318.

**Respuesta:**

> ¡Hola! Te cuento lo que encontré:
>
> **Camas en Maternidad:**
> Hay disponibilidad. De las 20 camas del sector, 11 están ocupadas y quedan **9 libres**.
>
> **Acompañamiento en el parto:**
> Sí, podés estar acompañada. Según la normativa del hospital, **la mujer puede estar acompañada durante el trabajo de parto y el parto por la persona que elija** (pareja, familiar, amiga, etc.).
>
> Además, como dato útil: después de un parto normal, el alta es a las 48 horas; después de una cesárea, a las 72 horas.
>
> ¿Necesitás saber algo más, por ejemplo sobre turnos, guardia o algún medicamento?

Herramientas: consultar_camas, buscar_documentos · costo USD 0.000552

## Y11

**Pregunta:** Mi mamá toma levotiroxina de 50, ¿hay stock y puedo ir a retirarla yo por ella?

### Llamada al modelo 1

Usage: 828 tokens de entrada (768 en caché), 171 de salida (81 de razonamiento), USD 0.000231.

**Herramienta** `consultar_farmacia` con argumentos `{"medicamento": "levotiroxina 50"}`

Resultado:

```text
{"error": "'levotiroxina 50' no existe", "opciones": ["amoxicilina 500 mg", "enalapril 10 mg", "insulina NPH", "levotiroxina 50 mcg", "metformina 850 mg", "paracetamol 500 mg", "salbutamol aerosol"]}
```

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "retirar medicación por otra persona requisitos"}`

Resultado:

```text
Farmacia del hospital
La farmacia de pacientes ambulatorios está en planta baja, junto a admisión, y atiende de lunes a viernes de 8:00 a 20:00. Entrega medicación a pacientes del hospital con receta de un profesional de la institución.

Para retirar medicación se presenta el DNI del paciente. Si retira otra persona, lleva su propio DNI y el del paciente.

Los medicamentos de alto costo, como los oncológicos y los biológicos, requieren un formulario de solicitud firmado por el especialista y aprobado por el comité de farmacia, que se reúne los miércoles.

La farmacia no hace entregas los fines de semana. Las recetas tienen una validez de 30 días desde la fecha de emisión.
```

### Llamada al modelo 2

Usage: 1268 tokens de entrada (768 en caché), 90 de salida (27 de razonamiento), USD 0.000134.

**Herramienta** `consultar_farmacia` con argumentos `{"medicamento": "levotiroxina 50 mcg"}`

Resultado:

```text
{"medicamento": "levotiroxina 50 mcg", "fecha": "2026-10-05", "datos": {"stock": 90, "unidad": "comprimidos"}}
```

### Llamada al modelo 3

Usage: 1415 tokens de entrada (1280 en caché), 273 de salida (51 de razonamiento), USD 0.000371.

**Respuesta:**

> ¡Hola! Te confirmo la información:
>
> **Stock de levotiroxina 50 mcg:** ✅ Sí, hay stock disponible (90 comprimidos en farmacia).
>
> **¿Podés retirarla vos por tu mamá?** ✅ Sí, se puede. Según las normas del hospital, para retirar medicación por otra persona necesitás presentar:
> - **Tu propio DNI**
> - **El DNI de tu mamá** (la paciente)
>
> Además, tené en cuenta que:
> - La receta debe ser de un profesional de la institución y tener **validez de 30 días** desde su emisión.
> - La farmacia de pacientes ambulatorios está en **planta baja, junto a admisión**, y atiende de **lunes a viernes de 8:00 a 20:00** (no entrega los fines de semana).
>
> Así que podés acercarte en ese horario con ambos DNI y la receta vigente. ¿Necesitás algo más?

Herramientas: consultar_farmacia, buscar_documentos · costo USD 0.000737

## Y12

**Pregunta:** Llegué a la guardia, me clasificaron amarillo: ¿cuánto se está esperando y cuál es el tiempo máximo que corresponde?

### Llamada al modelo 1

Usage: 833 tokens de entrada (0 en caché), 149 de salida (87 de razonamiento), USD 0.000203.

**Herramienta** `consultar_espera` con argumentos `{}`

Resultado:

```text
{"fecha": "2026-10-05", "minutos_por_nivel": {"rojo": 0, "naranja": 7, "amarillo": 48, "verde": 135, "azul": 210}}
```

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "tiempo máximo de espera clasificación amarillo triage"}`

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

Usage: 1183 tokens de entrada (768 en caché), 139 de salida (42 de razonamiento), USD 0.000196.

**Respuesta:**

> Según la información actual de la guardia:
>
> - **Espera actual para clasificación amarilla:** 48 minutos.
> - **Tiempo máximo que corresponde (nivel amarillo / urgencia):** 60 minutos.
>
> Estás dentro del rango esperado: la espera actual (48 min) es menor al máximo permitido (60 min). Te recomiendo permanecer atento/a al llamado. ¿Necesitás algo más?

Herramientas: consultar_espera, buscar_documentos · costo USD 0.000399

