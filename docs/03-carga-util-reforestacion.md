# 3. Mecanismo de carga útil (reforestación)

> Convertido del [informe técnico v3](fuentes/informe_tecnico_dron_reforestador_v3.docx), sección 3. La numeración original se conserva (otras secciones la citan). Las notas `⚠` son del repositorio y no estaban en el informe.


## 3.1 Supuestos sobre las bolas de semillas

- Diámetro de 2 a 4 cm y masa de 10 g (estimación; el diseño aún no está cerrado).

- Con 2,5 kg hay 250 bolas. Una bola de 3 cm ocupa 14 cm3; con los huecos entre bolas el conjunto ocupa unos 6 L.

- La tolva mide unos 300 × 200 × 100 mm. Si necesitas menos volumen, baja la carga a 2 kg (200 bolas, unos 5 L).

## 3.2 Comparativa de opciones

| Opción                           | Descripción                                                           | Ventajas                                | Inconvenientes                         |
|----------------------------------|-----------------------------------------------------------------------|-----------------------------------------|----------------------------------------|
| A. Compuerta basculante          | Un servo abre una compuerta en la base de la tolva                    | Muy simple                              | Suelta todo de golpe; sin dosificación |
| B. Tambor indexado (recomendada) | Tambor de 6 celdas; el servo gira 60 grados por pulso y suelta 1 bola | Dosificación exacta; control por evento | Algo más de impresión 3D               |

> ⚠ **Nota del repositorio:** un servo de 20 kg gira ~180°, no los 360° que necesita un tambor de 6 celdas a 60° por pulso. Hay que decidir el mecanismo (servo de rotación continua, trinquete o reductor 2:1) antes de imprimir ([S2](discrepancias-y-pendientes.md)).

## 3.3 Esquema del tambor

```text
Tolva (250 bolas de 10 g)
+------------------------------+
| o o o o o o o o o o          |
+--------------+---------------+
               |
        .------+------.
        |   TAMBOR    |   <- 6 celdas de 50 mm
        | (c) (c) (c) |      Servo gira 60 grados por pulso
        '------+------'      (1 bola por pulso)
               |
               v  caída por gravedad (bajo el fuselaje)
```


## 3.4 Lógica de liberación

1.  Interlock de seguridad: soltar solo si el avión está armado, en modo misión, por encima de 15 m AGL y a velocidad de crucero estable.

2.  Punto de liberación anticipado: a 30 m AGL y 45 km/h las bolas caen unos 31 m por delante (t = raíz(2h/g) ≈ 2,5 s; 12,5 m/s × 2,5 s). El software desplaza el punto de suelta ese recorrido, y el viento lo modifica.

3.  Cadencia: un pulso cada 0,5–1 s para dispersar; un lote por pasada.

4.  Fallo seguro: si el servo se bloquea, la tolva no suelta nada. Con el avión en tierra nunca debe soltar.

5.  Accionamiento: en fase 1 el servo del tambor va al canal 4 del PCA9685; en fase 2 va a la salida S5 de la controladora.

> ⚠ **Nota del repositorio:** la lógica de este apartado está implementada en [`ardupilot/scripts/seed_dropper.lua`](../ardupilot/scripts/seed_dropper.lua) (fase 2, con interlock: armado, AUTO, ≥ 15 m, velocidad estable) y, simplificada, en [`root_safety.h`](../firmware/esp32_fase1/lib/root_safety/root_safety.h) (fase 1, solo armado). En la misión se usa `DO_AUX_FUNCTION` en lugar de `DO_SET_SERVO` para no saltarse el interlock. Detalle en [ArduPilot](ardupilot.md#5-el-dosificador-de-semillas).

---
[← 2. Diseño aerodinámico y estructural (inspiración MQ-9)](02-diseno-aerodinamico-estructural.md) · [Índice](README.md) · [4. Arquitectura electrónica y vuelo autónomo →](04-electronica-y-vuelo-autonomo.md)
