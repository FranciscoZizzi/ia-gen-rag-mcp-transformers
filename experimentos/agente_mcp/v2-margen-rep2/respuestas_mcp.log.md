# Log de corrida del agente

- Fecha: 2026-10-07T13:56:52
- Modelo: `deepseek/deepseek-v4-flash-0731`
- Preguntas: `datos\preguntas_agente_dev.jsonl` (12)
- Transporte: MCP stdio (`servidor_mcp.py`), herramientas descubiertas con tools/list

## Resumen

| Pregunta | Herramientas | Llamadas al modelo | Tokens entrada | Tokens salida (razonamiento) | Costo USD | Segundos |
|---|---|---|---|---|---|---|
| A01 | buscar_documentos | 2 | 3713 | 134 (35) | 0.000238 | 5.8 |
| A02 | buscar_documentos | 2 | 3733 | 204 (43) | 0.000328 | 15.6 |
| A03 | buscar_documentos | 2 | 3680 | 147 (40) | 0.000254 | 17.1 |
| A04 | buscar_documentos | 2 | 3762 | 207 (45) | 0.000333 | 5.8 |
| A05 | consultar_camas | 2 | 3659 | 113 (41) | 0.000211 | 2.7 |
| A06 | consultar_guardia | 2 | 3682 | 108 (29) | 0.000205 | 6.4 |
| A07 | consultar_turnos | 2 | 3675 | 112 (42) | 0.000210 | 5.7 |
| A08 | consultar_farmacia | 2 | 3663 | 113 (24) | 0.000091 | 11.3 |
| A09 | consultar_espera | 2 | 3659 | 95 (32) | 0.000187 | 2.3 |
| A10 | consultar_camas, buscar_documentos | 2 | 3956 | 348 (175) | 0.000517 | 13.6 |
| A11 | consultar_turnos, buscar_documentos | 2 | 3854 | 312 (145) | 0.000469 | 4.8 |
| A12 | consultar_farmacia, buscar_documentos | 2 | 3958 | 341 (143) | 0.000508 | 6.3 |
| **Total** | | 24 | 44994 | 2234 (794) | **0.003550** | 97.4 |

## A01

**Pregunta:** ¿Cuál es el horario de visita en neonatología para los abuelos?

### Llamada al modelo 1

Usage: 1763 tokens de entrada (1536 en caché), 88 de salida (35 de razonamiento), USD 0.000144.

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "horario de visita neonatología abuelos"}`

Resultado:

```text
Régimen de visitas — Neonatología
Madre y padre tienen ingreso libre las 24 horas. Los abuelos pueden visitar martes y jueves de 16:00 a 17:00, uno por vez y con la presencia de uno de los padres. Los hermanos del recién nacido no ingresan al sector durante la temporada de virus respiratorios, de mayo a septiembre.
```

### Llamada al modelo 2

Usage: 1950 tokens de entrada (1792 en caché), 46 de salida (0 de razonamiento), USD 0.000094.

**Respuesta:**

> En neonatología, los abuelos pueden visitar los **martes y jueves de 16:00 a 17:00**, uno por vez y siempre con la presencia de uno de los padres.

Herramientas: buscar_documentos · costo USD 0.000238

## A02

**Pregunta:** ¿Qué preparación necesita una colonoscopía?

### Llamada al modelo 1

Usage: 1755 tokens de entrada (1536 en caché), 91 de salida (43 de razonamiento), USD 0.000148.

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "preparación para colonoscopía"}`

Resultado:

```text
Preparación para estudios de diagnóstico por imágenes y endoscopía — Colonoscopía
Los tres días previos se sigue una dieta sin residuos: sin frutas, verduras, legumbres ni cereales integrales. La tarde anterior se toma la solución evacuante de polietilenglicol, cuatro litros repartidos en cuatro horas. Desde la medianoche solo se permiten líquidos claros, y el ayuno total es de 6 horas antes del turno. El paciente tiene que venir acompañado, porque el estudio se hace con sedación.
```

### Llamada al modelo 2

Usage: 1978 tokens de entrada (1536 en caché), 113 de salida (0 de razonamiento), USD 0.000180.

**Respuesta:**

> Para la colonoscopía:
>
> - **3 días previos:** dieta sin residuos (sin frutas, verduras, legumbres ni cereales integrales).
> - **Tarde anterior:** tomar 4 litros de solución evacuante de polietilenglicol, repartidos en 4 horas.
> - **Desde la medianoche:** solo líquidos claros.
> - **Ayuno total:** 6 horas antes del turno.
> - **Acompañado:** sí, porque el estudio se hace con sedación.

Herramientas: buscar_documentos · costo USD 0.000328

## A03

**Pregunta:** ¿Qué documentos tengo que llevar a la primera consulta con un especialista?

### Llamada al modelo 1

Usage: 1761 tokens de entrada (1536 en caché), 94 de salida (40 de razonamiento), USD 0.000152.

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "qué documentación llevar a la primera consulta con especialista"}`

Resultado:

```text
Turnos en consultorios externos — Qué llevar a la primera consulta
DNI, credencial de la cobertura de salud, la derivación y los estudios previos relacionados con el motivo de consulta, en papel o en el teléfono.
```

### Llamada al modelo 2

Usage: 1919 tokens de entrada (1536 en caché), 53 de salida (0 de razonamiento), USD 0.000102.

**Respuesta:**

> Para la primera consulta con un especialista tenés que llevar: DNI, credencial de tu cobertura de salud, la derivación y los estudios previos relacionados con el motivo de consulta (en papel o en el teléfono).

Herramientas: buscar_documentos · costo USD 0.000254

## A04

**Pregunta:** ¿Quiénes pueden donar sangre?

### Llamada al modelo 1

Usage: 1753 tokens de entrada (1536 en caché), 101 de salida (45 de razonamiento), USD 0.000161.

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "quiénes pueden donar sangre requisitos"}`

Resultado:

```text
Donación de sangre
El servicio de hemoterapia recibe donantes de lunes a sábado de 7:30 a 12:00, en el primer piso.

Pueden donar personas de 18 a 65 años que pesen más de 50 kilos y se sientan bien. No hay que venir en ayunas: se recomienda un desayuno liviano, sin lácteos ni grasas. Entre una donación y la siguiente tienen que pasar al menos 2 meses en los hombres y 3 meses en las mujeres.

No pueden donar por 12 meses quienes se hicieron un tatuaje o un piercing en ese período.
```

### Llamada al modelo 2

Usage: 2009 tokens de entrada (1792 en caché), 106 de salida (0 de razonamiento), USD 0.000172.

**Respuesta:**

> Pueden donar sangre las personas de 18 a 65 años que pesen más de 50 kilos y se sientan bien. No hace falta ir en ayunas: se recomienda un desayuno liviano, sin lácteos ni grasas. Entre donación y donación tienen que pasar al menos 2 meses en hombres y 3 meses en mujeres. No pueden donar por 12 meses quienes se hicieron un tatuaje o un piercing en ese período.

Herramientas: buscar_documentos · costo USD 0.000333

## A05

**Pregunta:** ¿Hay camas libres en terapia intensiva ahora?

### Llamada al modelo 1

Usage: 1756 tokens de entrada (1536 en caché), 90 de salida (41 de razonamiento), USD 0.000147.

**Herramienta** `consultar_camas` con argumentos `{"sector": "terapia_intensiva"}`

Resultado:

```text
{"sector": "terapia_intensiva", "fecha": "2026-10-05", "datos": {"total": 12, "ocupadas": 12, "libres": 0}}
```

### Llamada al modelo 2

Usage: 1903 tokens de entrada (1792 en caché), 23 de salida (0 de razonamiento), USD 0.000064.

**Respuesta:**

> No, ahora no hay camas libres en terapia intensiva: las 12 están ocupadas.

Herramientas: consultar_camas · costo USD 0.000211

## A06

**Pregunta:** ¿Quién está de guardia en cardiología esta noche?

### Llamada al modelo 1

Usage: 1757 tokens de entrada (1536 en caché), 77 de salida (29 de razonamiento), USD 0.000130.

**Herramienta** `consultar_guardia` con argumentos `{"especialidad": "cardiologia"}`

Resultado:

```text
{"especialidad": "cardiologia", "fecha": "2026-10-05", "datos": [{"profesional": "Dr. Julián Ferreyra", "horario": "08:00-20:00"}, {"profesional": "Dra. Paula Benítez", "horario": "20:00-08:00"}]}
```

### Llamada al modelo 2

Usage: 1925 tokens de entrada (0 en caché), 31 de salida (0 de razonamiento), USD 0.000074.

**Respuesta:**

> Esta noche (turno 20:00-08:00) está de guardia en cardiología la Dra. Paula Benítez.

Herramientas: consultar_guardia · costo USD 0.000205

## A07

**Pregunta:** ¿Cuándo es el próximo turno disponible con traumatología?

### Llamada al modelo 1

Usage: 1758 tokens de entrada (0 en caché), 86 de salida (42 de razonamiento), USD 0.000142.

**Herramienta** `consultar_turnos` con argumentos `{"especialidad": "traumatologia"}`

Resultado:

```text
{"especialidad": "traumatologia", "fecha": "2026-10-05", "datos": ["2026-10-07 08:40", "2026-10-07 09:00", "2026-10-08 14:20"]}
```

### Llamada al modelo 2

Usage: 1917 tokens de entrada (0 en caché), 26 de salida (0 de razonamiento), USD 0.000068.

**Respuesta:**

> El próximo turno con traumatología es el **miércoles 7 de octubre a las 08:40**.

Herramientas: consultar_turnos · costo USD 0.000210

## A08

**Pregunta:** ¿Tienen enalapril de 10 mg en la farmacia?

### Llamada al modelo 1

Usage: 1759 tokens de entrada (1758 en caché), 77 de salida (23 de razonamiento), USD 0.000053.

**Herramienta** `consultar_farmacia` con argumentos `{"medicamento": "enalapril 10 mg"}`

Resultado:

```text
{"medicamento": "enalapril 10 mg", "fecha": "2026-10-05", "datos": {"stock": 0, "unidad": "comprimidos", "reposicion": "2026-10-09"}}
```

### Llamada al modelo 2

Usage: 1904 tokens de entrada (1903 en caché), 36 de salida (1 de razonamiento), USD 0.000038.

**Respuesta:**

> No, hoy no hay enalapril de 10 mg en la farmacia. La reposición está prevista para el 09/10/2026.

Herramientas: consultar_farmacia · costo USD 0.000091

## A09

**Pregunta:** ¿Cuánto se está esperando hoy en la guardia si me clasifican como verde?

### Llamada al modelo 1

Usage: 1765 tokens de entrada (1536 en caché), 63 de salida (32 de razonamiento), USD 0.000112.

**Herramienta** `consultar_espera` con argumentos `{}`

Resultado:

```text
{"fecha": "2026-10-05", "minutos_por_nivel": {"rojo": 0, "naranja": 7, "amarillo": 48, "verde": 135, "azul": 210}}
```

### Llamada al modelo 2

Usage: 1894 tokens de entrada (1792 en caché), 32 de salida (0 de razonamiento), USD 0.000075.

**Respuesta:**

> Hoy en la guardia, si te clasifican como verde, la espera es de 135 minutos (2 horas y cuarto).

Herramientas: consultar_espera · costo USD 0.000187

## A10

**Pregunta:** Quiero internar a mi nene en pediatría, ¿hay lugar y me puedo quedar con él?

### Llamada al modelo 1

Usage: 1769 tokens de entrada (0 en caché), 200 de salida (95 de razonamiento), USD 0.000288.

**Herramienta** `consultar_camas` con argumentos `{"sector": "pediatria"}`

Resultado:

```text
{"sector": "pediatria", "fecha": "2026-10-05", "datos": {"total": 24, "ocupadas": 17, "libres": 7}}
```

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "acompañante en internación de pediatría puede quedarse"}`

Resultado:

```text
Ingreso a internación programada — Acompañante
Se permite un acompañante por paciente internado durante la noche, salvo en terapia intensiva. El acompañante recibe una tarjeta que presenta en el control de acceso.

---

Régimen de visitas — Pediatría
Madre, padre o tutor pueden permanecer las 24 horas junto al paciente. Para el resto de los familiares, la visita es de 17:00 a 19:00, con un máximo de dos personas.

---

Régimen de visitas — Maternidad
La visita en la sala de puérperas es de 15:00 a 20:00. La persona acompañante de la madre puede quedarse también durante la noche.
```

### Llamada al modelo 2

Usage: 2187 tokens de entrada (0 en caché), 148 de salida (80 de razonamiento), USD 0.000229.

**Respuesta:**

> Sí, hay lugar: en pediatría hay 24 camas, 17 ocupadas y 7 libres. Y sí, te podés quedar: como madre, padre o tutor podés permanecer las 24 horas junto a tu nene.

Herramientas: consultar_camas, buscar_documentos · costo USD 0.000517

## A11

**Pregunta:** Necesito turno con cardiología, ¿cuál es el primero y qué tengo que llevar?

### Llamada al modelo 1

Usage: 1766 tokens de entrada (1536 en caché), 189 de salida (100 de razonamiento), USD 0.000274.

**Herramienta** `consultar_turnos` con argumentos `{"especialidad": "cardiologia"}`

Resultado:

```text
{"especialidad": "cardiologia", "fecha": "2026-10-05", "datos": ["2026-10-14 09:30", "2026-10-14 10:00", "2026-10-16 15:00"]}
```

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "qué documentación llevar a la primera consulta en consultorios externos"}`

Resultado:

```text
Turnos en consultorios externos — Qué llevar a la primera consulta
DNI, credencial de la cobertura de salud, la derivación y los estudios previos relacionados con el motivo de consulta, en papel o en el teléfono.
```

### Llamada al modelo 2

Usage: 2088 tokens de entrada (1792 en caché), 123 de salida (45 de razonamiento), USD 0.000195.

**Respuesta:**

> El primer turno con cardiología es el **miércoles 14 de octubre de 2026 a las 09:30**.
>
> Para la primera consulta tenés que llevar: **DNI, credencial de tu cobertura de salud, la derivación y los estudios previos relacionados con el motivo de consulta** (en papel o en el teléfono).

Herramientas: consultar_turnos, buscar_documentos · costo USD 0.000469

## A12

**Pregunta:** Me recetaron insulina NPH, ¿la tienen y qué necesito para retirarla?

### Llamada al modelo 1

Usage: 1765 tokens de entrada (1536 en caché), 178 de salida (69 de razonamiento), USD 0.000260.

**Herramienta** `consultar_farmacia` con argumentos `{"medicamento": "insulina NPH"}`

Resultado:

```text
{"medicamento": "insulina NPH", "fecha": "2026-10-05", "datos": {"stock": 0, "unidad": "frascos", "reposicion": "2026-10-12"}}
```

**Herramienta** `buscar_documentos` con argumentos `{"consulta": "cómo retirar un medicamento en la farmacia del hospital"}`

Resultado:

```text
Farmacia del hospital
La farmacia de pacientes ambulatorios está en planta baja, junto a admisión, y atiende de lunes a viernes de 8:00 a 20:00. Entrega medicación a pacientes del hospital con receta de un profesional de la institución.

Para retirar medicación se presenta el DNI del paciente. Si retira otra persona, lleva su propio DNI y el del paciente.

Los medicamentos de alto costo, como los oncológicos y los biológicos, requieren un formulario de solicitud firmado por el especialista y aprobado por el comité de farmacia, que se reúne los miércoles.

La farmacia no hace entregas los fines de semana. Las recetas tienen una validez de 30 días desde la fecha de emisión.
```

### Llamada al modelo 2

Usage: 2193 tokens de entrada (1792 en caché), 163 de salida (74 de razonamiento), USD 0.000248.

**Respuesta:**

> La insulina NPH hoy no hay stock en la farmacia (0 frascos). La reposición está prevista para el 12/10/2026.
>
> Para retirarla cuando esté: presentás el DNI del paciente. Si la retira otra persona, lleva su propio DNI y el del paciente. La receta tiene validez de 30 días desde su emisión.

Herramientas: consultar_farmacia, buscar_documentos · costo USD 0.000508

