from microbit import *
import music
import random

# === IMÁGENES DE OJOS ===
ojos_neutros = Image("09090:"
                     "90909:"
                     "00000:"
                     "90009:"
                     "09990")

sonrisa = Image("09090:"
                "90909:"
                "00000:"
                "09990:"
                "90009")

ojos_tristes = Image("09090:"
                     "90909:"
                     "00000:"
                     "09090:"
                     "99999")

ojos_cerrados = Image("09090:"
                      "99999:"
                      "00000:"
                      "00000:"
                      "00000")

# === CONFIGURACIÓN DE MOTORES ===
# Pines para controlar el puente H (L298N)
IN1 = pin0   # Motor A adelante
IN2 = pin1   # Motor A atrás
IN3 = pin2   # Motor B adelante
IN4 = pin3   # Motor B atrás

# Configuración inicial de pines
IN1.write_digital(0)
IN2.write_digital(0)
IN3.write_digital(0)
IN4.write_digital(0)

def motor_adelante():
    motor_detener()
    IN1.write_digital(1)
    IN3.write_digital(1)
    sleep(50)

def motor_atras():
    motor_detener()
    IN2.write_digital(1)
    IN4.write_digital(1)
    sleep(50)

def motor_derecha():
    motor_detener()
    IN1.write_digital(1)
    IN4.write_digital(1)
    sleep(50)

def motor_izquierda():
    motor_detener()
    IN2.write_digital(1)
    IN3.write_digital(1)
    sleep(50)

def motor_detener():
    IN1.write_digital(0)
    IN2.write_digital(0)
    IN3.write_digital(0)
    IN4.write_digital(0)
    sleep(50)  # Pequeña pausa para evitar cortocircuitos

# === VARIABLES GLOBALES ===
ultimo_sonido = running_time()  # Inicializar con tiempo actual
modo_sueno = False             # Si está "dormido"
tiempo_sin_sonido_para_sueno = 10000  # 10 segundos sin sonido → modo sueño
tiempo_fondo = 0               # Para música de fondo
nivel_base_sonido = 0          # Nivel base de sonido ambiente

# === SONIDOS DE FONDO ===
sonidos_fondo = [
    soundExpression.happy,
    soundExpression.twinkle,
    soundExpression.spring,
    soundExpression.soaring
]

# Calibrar nivel de sonido ambiente
def calibrar_sonido():
    global nivel_base_sonido
    sleep(1000)  # Esperar a que se estabilice
    niveles = []
    for i in range(5):
        niveles.append(microphone.sound_level())
        sleep(100)
    nivel_base_sonido = sum(niveles) / len(niveles) + 30  # Margen de 30

# Mostrar ojos neutros al inicio
display.show(ojos_neutros)
music.play(music.PRELUDE)  # Saludo inicial
calibrar_sonido()

# === BUCLE PRINCIPAL ===
while True:
    # Leer nivel de sonido (0-255)
    nivel = microphone.sound_level()
    umbral_sonido = nivel_base_sonido + 50  # Umbral dinámico
    
    # Si hay sonido fuerte, reaccionar
    if nivel > umbral_sonido:
        ultimo_sonido = running_time()
        
        if modo_sueno:
            # Despertar
            modo_sueno = False
            display.show(sonrisa)
            music.play(soundExpression.jump_up)
            motor_adelante()
            sleep(800)
            motor_detener()
        else:
            # Mostrar sonrisa
            display.show(sonrisa)
            music.play(soundExpression.happy)
            
            # Mover robot un momento (más breve)
            motor_adelante()
            sleep(500)
            motor_detener()
        
        # Volver a ojos neutros después de breve pausa
        sleep(300)
        display.show(ojos_neutros)
    
    # Verificar si debe entrar en modo sueño
    tiempo_actual = running_time()
    tiempo_sin_sonido = tiempo_actual - ultimo_sonido
    
    if not modo_sueno and tiempo_sin_sonido > tiempo_sin_sonido_para_sueno:
        modo_sueno = True
        # Animación para dormir
        for i in range(3):
            display.show(ojos_cerrados)
            sleep(300)
            display.show(ojos_neutros)
            sleep(300)
        display.show(ojos_cerrados)
        music.play(soundExpression.yawn)
    
    # Modo sueño: parpadeo y ronquido de vez en cuando
    if modo_sueno:
        if (tiempo_actual // 1000) % 8 == 0:  # cada ~8 segundos
            display.show(Image.SURPRISED)
            music.play(soundExpression.mysterious)
            sleep(500)
            display.show(ojos_cerrados)
    
    # Música de fondo aleatoria cada 20-40 segundos (solo despierto)
    if not modo_sueno and (tiempo_actual - tiempo_fondo) > random.randint(20000, 40000):
        sonido_fondo = random.choice(sonidos_fondo)
        music.play(sonido_fondo)
        tiempo_fondo = tiempo_actual
    
    # Mostrar ojos tristes si hace rato que no hay sonido (pero no dormido)
    if not modo_sueno and tiempo_sin_sonido > 5000:  # 5 segundos
        display.show(ojos_tristes)
        if (tiempo_actual // 1000) % 6 == 0:  # cada 6 segundos
            music.play(soundExpression.sad, wait=False)
    elif not modo_sueno:
        display.show(ojos_neutros)
    
    # Recalibrar sonido ocasionalmente
    if (tiempo_actual // 1000) % 60 == 0:  # cada minuto
        calibrar_sonido()
    
    sleep(100)  # Pausa para evitar saturación