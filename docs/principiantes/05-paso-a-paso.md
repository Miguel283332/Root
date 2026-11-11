# 05 · Paso a paso de la construcción

Cada fase: **qué haces → qué necesitas → pasos → cómo sé que está bien → errores típicos**. Las cifras
exactas y tablas están en la [guía técnica](../construccion/README.md); aquí está el *cómo* para quien empieza.
Si una comprobación falla, **no sigas**: corrígelo antes.

---

## Fase 1 · Diseño en el ordenador (8–10 h)

**Qué haces:** compruebas en el ordenador que el ala vuela y sacas las plantillas que usarás para cortar.
**Necesitas:** XFLR5, OpenVSP, `clarky.dat`, impresora o copistería ([03](03-programas.md)).

1. Instala XFLR5 y OpenVSP; instala el repositorio (`ctest` en verde).
2. En XFLR5, carga el perfil **Clark Y**, haz la polar a Re ≈ 260 000 y define el ala de 3000 × 300 mm con **diedro 2°**.
3. Analiza de −2° a 12° y apunta **CLmax** y el ángulo con CL ≈ 0,8 (será tu **incidencia, ~4°**).
4. En OpenVSP monta ala, fuselaje y cola con las cotas del informe; mira que quede **simétrico**.
5. Genera la plantilla: `python3 tools/plantilla_perfil.py clarky.dat --cuerda 300`.
6. Imprímela **al 100 %**, mide el cuadrado de 50 mm y la cuerda de 300 mm.
7. Calcula pesos y CG: `python3 tools/perf_calc.py masas` y `python3 tools/perf_calc.py diseno`.

**Está bien cuando:** CLmax ≥ 1,2; CG entre 25 y 30 % MAC; la plantilla mide lo que dice. **Errores
típicos:** imprimir "ajustado a página" (plantilla a otra escala: ¡mídela!); confundir cm y mm en XFLR5.

---

## Fase 2 · El ala (14–18 h)

**Qué haces:** cortas cuatro bloques de foam con la forma del perfil, les haces el canal del larguero, los
unes, pegas los tubos de carbono y forras el ala.
**Necesitas:** foam XPS de 40 mm, hilo de nicromo y fuente de 12 V, 2 plantillas de perfil, regla de acero,
CA, epoxi, tubos de carbono 12/10 mm, película termorretráctil, secador o pistola de calor.

1. **Plantillas rígidas.** Pega la plantilla impresa sobre contrachapado fino o cartón pluma y recorta
   **dos iguales** con el perfil exacto. Marca en ambas el 25 % de cuerda y el centro del larguero.
2. **Bloques.** Marca y corta con cutter y regla **cuatro piezas de 750 × 300 × 40 mm** (cada plancha da
   dos). Si alguna sale torcida, repite: sobra material.
3. **Montar el corte.** Fija una plantilla en cada **cara** del bloque con alfileres o cinta; el hilo debe
   rozar ambas plantillas a la vez. **Dos personas**: una a cada lado del arco, moviéndose **a la misma
   velocidad** (≈ 1 cm/s). Si una va más rápida, el perfil sale distinto en un lado.
4. **Cortar.** Hilo caliente, avance **continuo, sin pararse** (si te paras, el hilo funde un surco). Haz
   primero una prueba en un resto. Corta de **borde de salida a borde de ataque y vuelve** apoyando el hilo
   en las plantillas.
5. **Canal del larguero.** Marca la línea del 25 % de cuerda (75 mm desde el borde de ataque) y haz un canal
   de **12 mm**. Puedes empujar un tubo de latón de 12 mm **caliente** por esa línea sin girarlo, o usar una
   fresa. **Pruébalo con el tubo de carbono** antes de pegar: debe entrar sin holgura.
6. **Unir los bloques de cada semiala** con CA por el borde, apoyados sobre una **mesa plana**. Pon el tubo de
   12 mm en el canal de modo que **cruce la junta** (250 mm a cada lado) y pégalo con **epoxi**.
7. **Unión central con diedro de 2°.** Antes de pegar, **lija la cara de la raíz de cada semiala** apoyándola con
   la punta **52 mm por encima de la mesa** y la cara contra un tablero vertical. Une las dos semialas con el
   manguito de carbono de **20 mm (interior 18 mm, 150 mm de largo)** relleno de **epoxi espesado**, con las puntas
   calzadas 52 mm; **24 h de curado** sin tocar. Comprueba que cada punta queda 52 ± 5 mm sobre la raíz.
8. **Forrar.** Fija el borde de la película con cinta, calienta **a temperatura media** con el secador y alisa
   **del centro hacia fuera**. Si hay arrugas, vuelve a calentar; si se quema, bajaste demasiado el calor.
   Forra arriba y abajo.
9. **Pesa el ala:** objetivo **≤ 0,8 kg**.
10. **Prueba de carga:** apoya el ala por el centro y carga las semialas con ~21 kg (3 veces el peso del avión)
    repartidos; no debe romperse ni deformarse, ni moverse la unión central.

**Está bien cuando:** apoyada en una mesa plana el alabeo es **≤ 3 mm**, el perfil se parece al de la
plantilla en las dos puntas y el ala pesa ≤ 0,8 kg. **Errores típicos:** perfiles distintos a cada lado
(cortaste a distinta velocidad), canal torcido (el larguero queda inclinado), exceso de epoxi (peso), ala
**con alabeo** porque curó sobre una mesa que no era plana. Un ala alabeada **no se corrige con el mando**.

---

## Fase 3 · Fuselaje, cola, motor y tren (8–11 h)

**Qué haces:** montas la caja del fuselaje, el botalón con la cola, el soporte del motor y el tren.
**Necesitas:** planchas de foam de 10 mm y 5 mm, tubo de carbono 16/14 mm, piezas impresas, aluminio de 4 mm.

1. **Caja:** pega con CA los laterales (900 × 120 mm), la base y la tapa (900 × 150 mm); coloca **cuadernas**
   (150 × 120 mm) en el morro, bajo el ala y en la cola para que no se deforme. Comprueba escuadra con una
   escuadra real.
2. **Hueco de tolva:** 300 × 200 mm en la base, centrado bajo el ala.
3. **Botalón:** corta **500 mm** del tubo de 16 mm, mételo en la cola y fíjalo con dos abrazaderas impresas
   y epoxi.
4. **Cola:** pega el estabilizador horizontal (600 × 320 mm, foam de 5 mm) sobre el botalón, **horizontal**;
   el vertical (250 × 600 mm) encima, **perpendicular**. Corta los timones y únelos con **cinta de bisagra**
   (que gire libre y sin holgura). Añade una **pequeña aleta ventral** que proteja la hélice
   ([Decisiones de diseño](../decisiones-de-diseno.md)).
5. **Motor:** soporte impreso en PETG atornillado al extremo del botalón; el BR4114 con sus cuatro tornillos.
6. **Sentido de giro** (**sin hélice**): conecta motor y ESC; si empuja el avión hacia atrás, **intercambia
   dos cables** del motor.
7. **Tren** ([9.4b](../construccion/9.4b-tren-de-aterrizaje.md)): patas de 180 mm (principales) y 200 mm
   (morro) dobladas en L, soportes impresos, placa de contrachapado de 3 mm bajo el larguero, ruedas con
   arandelas de nailon. **Comprueba la holgura de la hélice con el avión inclinado ~5°.**

**Está bien cuando:** el botalón no tiene holgura al mover la cola; el motor está alineado con el eje
(error < 1°); el avión queda **nivelado sobre sus tres ruedas**; hay ≥ 70–100 mm entre hélice y suelo.
**Errores típicos:** cola ligeramente girada (el avión no vuela recto), bisagras flojas, hélice demasiado
baja, ruedas que no giran libres.

---

## Fase 4 · Tolva y tambor (6–8 h)

**Qué haces:** imprimes y montas el depósito de semillas y el tambor que suelta una bola por pulso.
**Mecanismo:** un servo estándar no da 360°, así que el tambor lleva un **trinquete** (rueda libre): el servo da una carrera y vuelve, y cada carrera avanza una celda ([S2](../discrepancias-y-pendientes.md)).

1. Dibuja tolva y tambor en Tinkercad ([03 §5](03-programas.md)) con el **mecanismo elegido**.
2. Imprime una **pieza de prueba**; ajusta tolerancias (un hueco de 0,3–0,5 mm entre piezas móviles).
3. Monta el eje en dos bujes; fija el servo con su brazo (**15 mm**, **60° por pulso**).
4. **Prueba en seco con 10 bolas:** cada pulso debe soltar **exactamente una**. Ajusta el ángulo del brazo.
5. Fija la tolva bajo el fuselaje, **centrada en el CG** (80 mm detrás del borde de ataque).

**Está bien cuando:** 10 pulsos = 10 bolas, 5 veces seguidas. **Errores típicos:** bolas que se atascan en el
embudo (aumenta el ángulo a ≥ 45°, o el diámetro de celda), servo que patina (más par o menos radio).

---

## Fase 5 · Electrónica de la fase 1 (8–10 h)

**Qué haces:** cableas batería → fusible → ESC → motor, los BEC, la ESP32 y el PCA9685 a los servos.
**Necesitas:** soldador, estaño, termorretráctil, multímetro, el cableado de la lista, `firmware/esp32_fase1`.

1. **Dibuja el esquema en papel** (diagrama de [04 §4.4](../04-electronica-y-vuelo-autonomo.md)) y marca
   **rojo = +, negro = −** en cada conexión.
2. **Soldadura de conectores:** estaña los dos extremos, junta, calienta y deja enfriar **sin mover**.
   Termorretráctil después. **Un conector con la polaridad invertida mata el ESC.**
3. **Mide con el multímetro antes de conectar nada:** continuidad entre positivos, **ninguna** entre + y −,
   y que el BEC entrega **6 V** y **5 V** (con la batería conectada, **sin servos ni ESP32**).
4. **Masa común:** une el GND de batería, BEC, PCA9685 y ESP32.
5. **I²C:** SDA con SDA y SCL con SCL (pines 21 y 22 en muchas ESP32; **confirma los de tu placa**).
6. Canales del PCA9685: 0 alerón izq., 1 alerón der., 2 profundidad, 3 timón, 4 tambor, 5 ESC.
7. **Carga el firmware** (`pio run -t upload`) y comprueba el **failsafe**: **apaga la emisora con el motor
   SIN hélice: el gas debe ir a cero.**
8. **Armado:** un interruptor; sin armado el motor **nunca** gira.

**Está bien cuando:** con la emisora apagada el motor no gira; cada servo se mueve en el sentido correcto
(invierte en la emisora si hace falta). **Errores típicos:** polaridad invertida, masa no común (servos que
tiemblan), alimentar los servos desde la ESP32 (se reinicia), olvidar proteger las soldaduras.

---

## Fase 6 · Pruebas de banco (incluidas en 8–10 h)

**Qué haces:** compruebas el motor y el empuje antes de montarlo en el avión.
**Necesitas:** vatímetro, báscula, abrazadera/soporte fijo, la hélice, la batería.

1. **Calibrar el ESC:** gas al máximo, conecta la batería, espera los pitidos, baja a mínimo.
2. **Servos:** muévelos uno a uno y comprueba sentido y recorrido.
3. **Motor sin hélice**, sujeto, al 30 % durante 10 s: temperatura **< 60 °C**.
4. **Con hélice**, el avión (o el motor en un soporte) **sujeto con báscula**: mide el empuje al 30, 50, 75 y
   100 % y compáralo con `python3 tools/perf_calc.py empuje` (≈ 1,4 / 2,8 / 4,4 / 5,8 kg). Más del 30 % de
   diferencia → revisa ESC, hélice y batería.
5. **Corriente** con el vatímetro: a gas pleno **no más de 60 A** (el cálculo da ~54 A).

**Está bien cuando:** tienes la curva empuje–gas medida y apuntada. **Errores típicos:** probar sin sujetar
bien (la hélice es peligrosa), sin gafas, o con batería poco cargada (los números salen bajos).

---

## Fase 7 · Ajustar el centro de gravedad (1–2 h)

1. Monta el avión **completo** sin hélice, con la batería y la tolva **llena**.
2. Marca en el ala la línea del **27 % de cuerda** (80 mm tras el borde de ataque) y apoya el avión sobre
   **dos dedos** (o dos cintas) justo en esa marca.
3. Morro cae → **mueve la batería hacia atrás** o añade lastre en cola; la cola cae → batería **hacia
   delante**. Ajusta de 5 en 5 mm.

**Está bien cuando** el avión queda **horizontal y estable** sobre la marca. **Error típico:** ajustar con
la tolva vacía (el CG cambia).

---

## Fase 8 · Primeros vuelos manuales (6–10 h)

Lee antes [06 Aprender a volar y normativa](06-aprender-a-volar-y-normativa.md): **no vueles solo la primera
vez.**

1. **Pista:** hierba o asfalto de 30 m o más, viento < 10 km/h. Lista de revisión
   ([9.11](../construccion/9.11-checklist-prevuelo.md)) **entera**.
2. **Despegue** con gas al 80 %, subida recta y suave (**sin tirar bruscamente**: la hélice está cerca del
   suelo).
3. **Planeo:** a ~30 m de altura corta el gas y comprueba que planea recto; ajusta los *trims*.
4. **Vuelos de 2–3 min** a 45–50 km/h; después pasa a la carga: **2 bolas, luego más**, hasta la carga
   completa.
5. **Aterrizaje:** aproximación con gas bajo, **gas a cero al tocar**.

**Pasas a la fase 2 cuando:** 10 minutos de vuelo estable con carga completa a 45–50 km/h.

---

## Fase 9 · ArduPilot y Raspberry Pi 5 (12–16 h)

**Primero se simula, después se vuela** ([03 §8](03-programas.md)).

1. Ejecuta el simulador y la misión de ejemplo; entiende qué hace cada mensaje (`SeedDrop: …`).
2. Instala el firmware **ArduPlane 4.7.2** (placa `MatekH743`), carga los `.parm` y **calibra** (acelerómetro,
   brújula, radio, ESC, servos) siguiendo [ArduPilot §6](../ardupilot.md#6-pasar-de-simulador-a-avión-real).
3. **Calibra el sensor de batería** con multímetro/vatímetro y copia los **datos de terreno SRTM** en la SD.
4. Prueba en tierra los **modos** (MANUAL/FBWA/AUTO/RTL) y el **failsafe**.
5. **Primeros vuelos en FBWA con piloto**; el despegue y el aterrizaje automáticos solo después de **10
   aterrizajes manuales limpios**.
6. Primera misión autónoma: 5 min, 3 waypoints a menos de 100 m, **sin carga**, con RTL preparado.

**Está bien cuando** una misión corta se completa sin incidencias. **Errores típicos:** no poder armar por
falta de datos de terreno, voltaje mal calibrado (el failsafe de batería no salta), olvidar `SEED_TEST = 0`.
