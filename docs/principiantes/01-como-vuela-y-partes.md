# 01 · Cómo vuela un avión y qué partes tiene

## Las cuatro fuerzas

| Fuerza | Qué es | En este avión |
|---|---|---|
| **Sustentación** | Lo que sostiene el avión; la genera el **ala** al avanzar | Ala de 3 m × 0,30 m (0,9 m²) con perfil Clark Y |
| **Peso** | Lo que lo tira hacia abajo | ~7,1 kg ≈ 70 N con las 250 bolas |
| **Empuje** | Lo que lo empuja hacia delante: motor + hélice | Hasta 5,8 kg (57 N) parado a gas pleno |
| **Resistencia** | Lo que lo frena: el aire | En crucero se vence con solo ~120–140 W |

El ala solo sustenta si hay **velocidad suficiente**. Por debajo de ~**36 km/h** (velocidad de *pérdida*) el
aire se despega del ala y el avión cae: eso se llama **entrar en pérdida**. Por eso se vuela a **45–50 km/h**
(con margen) y nunca se intenta "frenar en el aire".

## Los tres movimientos y sus mandos

Un avión gira en tres ejes. Cada uno se controla con una **superficie móvil** movida por un **servo**:

| Movimiento | Qué hace el avión | Superficie | Servos de este avión |
|---|---|---|---|
| **Alabeo** (roll) | Se inclina a izquierda/derecha | **Alerones** (en el borde de salida del ala) | 2 (uno por semiala) |
| **Cabeceo** (pitch) | Sube/baja el morro | **Timón de profundidad** (en la cola, horizontal) | 1 |
| **Guiñada** (yaw) | Gira el morro a los lados, en plano | **Timón de dirección** (en la cola, vertical) | 1 |

El quinto servo abre el **tambor de semillas**. Un sexto "mando" es el **gas**, que va al **ESC** (el
regulador del motor).

Para girar de verdad se usa alerón (inclinar) y un poco de profundidad (tirar), y el timón apenas ayuda a
coordinar. **ArduPilot lo hace solo** en la fase 2; en la fase 1 lo haces tú con la emisora.

## El centro de gravedad (lo más importante del montaje)

El **centro de gravedad (CG)** es el punto donde el avión se equilibraría sostenido con un dedo. Hay un punto
más atrás, el **punto neutro**, y **mientras el CG quede por delante del punto neutro el avión es estable**
(si algo lo desequilibra, se corrige solo). Si el CG queda **detrás**, el avión es **inestable y no se puede
pilotar**: suele acabar en accidente en el primer vuelo.

* Objetivo de este avión: CG al **25–30 % de la cuerda media** (la *MAC*), unos **80 mm detrás del borde de
  ataque del ala**.
* **Morro pesado = seguro pero vuela mal; cola pesada = peligroso.** Ante la duda, adelantar.
* Se ajusta **moviendo la batería** (por eso va en el morro y sobre carriles) y se comprueba **colgando el
  avión de dos dedos** en la marca ([9.8](../construccion/9.8-ajuste-del-cg.md)).
* Truco de diseño: la **tolva con las bolas** va justo en el CG, así que al soltarlas el CG no se mueve.

## Las partes del avión y por qué están donde están

| Parte | Qué es | Detalle de este proyecto |
|---|---|---|
| **Ala** | Dos **semialas** de foam XPS con un **larguero** (tubo de carbono de 12 mm) dentro, unidas en el centro por un **manguito** de carbono, y forradas con película termorretráctil | Perfil Clark Y 12 % (36 mm de grosor) |
| **Larguero** | El "hueso" del ala: aguanta la flexión | 12 mm al 25 % de la cuerda |
| **Fuselaje** | La caja central donde va la batería, la electrónica y la tolva | Caja de foam de 900 mm |
| **Botalón** | Tubo de carbono que sale hacia atrás y sostiene la cola y el motor | 500 mm, carbono 16/14 mm |
| **Empenaje (cola)** | Estabilizador horizontal + vertical con sus timones | 0,19 m² y 0,15 m² |
| **Motor + hélice** | **Pusher**: empuja desde detrás, al final del botalón | BR4114 400 KV + APC 18 × 5,5 |
| **Tren de aterrizaje** | **Triciclo fijo**: una rueda delante y dos detrás del CG | Ruedas de 80–90 mm |
| **Tolva y tambor** | Depósito de 250 bolas y un disco con 6 celdas que suelta una bola por pulso | Impreso en PETG |
| **Batería** | LiPo 6S 10 000 mAh (la pieza más pesada) | En el morro; 1,4–1,5 kg |

Por qué el motor va detrás y qué implica (hélice cerca del suelo, cola, despegue):
[Decisiones de diseño](../decisiones-de-diseno.md).

## Cómo se pilota, en una frase por fase

* **Fase 1 (manual):** la emisora manda a los servos **sin ayuda**. Si sueltas los mandos el avión no se
  endereza solo. Hay que saber volar o tener a alguien que sepa.
* **Fase 2 (ArduPilot):** hay modos. **MANUAL** = como la fase 1. **FBWA** = tú mandas inclinación y
  cabeceo y la controladora estabiliza (el modo de los primeros vuelos con ArduPilot). **AUTO** = sigue la
  misión (despega, vuela puntos, suelta semillas). **RTL** = vuelve al punto de inicio.
