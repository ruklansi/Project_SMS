import serial
import time
import psycopg2

try:
    puerto_serial = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
except Exception as e:
    print("Error al abrir el puerto serial:", e)
    pass


def enviar_respuesta(telefono, mensaje):
    # Función para enviar un mensaje de texto
    count = 0
    time.sleep(2)
    count += 1
    puerto_serial.write((telefono.replace(' ', '') + "\n").encode())
    puerto_serial.write((mensaje + "\n").encode())
    time.sleep(5)


def bienvenida(numero):
    try:
        # Elimina el signo de "+" y los espacios en blanco del número de teléfono
        numero_limpio = numero.replace('+54', '').replace(' ', '')
        if len(numero_limpio) != 10:
            numero_limpio = numero.replace('+549', '').replace(' ', '')
        # Configura la conexión a la base de datos PostgreSQL
        conn = psycopg2.connect(
            dbname="nombre_de_la_base_de_datos",
            user="usuario_de_la_base_de_datos",
            password="contraseña_de_la_base_de_datos",
            host="host_o_direccion_IP"  # Cambia esto según la ubicación de tu base de datos
        )
        cursor = conn.cursor()
        # Realiza una consulta para obtener el nombre y apellido
        cursor.execute('SELECT columna1, columna2, columna3 FROM tabla WHERE columna_phone = %s',
                       (numero_limpio,))
        columna1, columna2, columna3 = cursor.fetchone()
        mensaje_bienvenida = f"Bienvenido/a {columna1} {columna2} {columna3}"
        enviar_respuesta(numero, mensaje_bienvenida)
        cursor.close()
        conn.close()
    except Exception as E:
        print("Error al enviar la bienvenida:", E)
        pass


def guardar_novedad(telefono, novedad_sms, fecha_hora):
    try:
        conn = psycopg2.connect(
            dbname="nombre_de_la_base_de_datos",
            user="usuario_de_la_base_de_datos",
            password="contraseña_de_la_base_de_datos",
            host="host_o_direccion_IP"
        )
        cursor = conn.cursor()
        numero_limpio = telefono.replace('+54', '').replace(' ', '')
        if len(numero_limpio) != 10:
            numero_limpio = telefono.replace('+549', '').replace(' ', '')
        print(numero_limpio)
        cursor.execute('SELECT columna_id FROM tabla WHERE columna_phone = %s', (numero_limpio,))
        columna_id = cursor.fetchone()
        # Insertar la novedad en la base de datos
        print(fecha_hora)

        cursor.execute("INSERT INTO tabla (columna_id, columna2, columna3) VALUES (%s,%s,%s)",
                       (columna_id, novedad_sms, '20' + fecha_hora.replace('"', ''),))
        conn.commit()

        cursor.close()
        conn.close()
        return True
    except Exception as E:
        print("Error al guardar la novedad en la base de datos:", E)
        return False


def interaccion(mensaje, telefono, fecha):
    print(mensaje)
    asterisco = 'HOLA'

    if asterisco in mensaje:
        bienvenida(telefono)
        print('entro aca')
        enviar_respuesta(telefono, "Redacte la novedad de no mas de 140 caracteres. Al finalizar el texto" "coloque #.")
        time.sleep(2)

    enviar = "#"
    if enviar in mensaje.replace('\x00', ''):
        print('entre')
        if len(mensaje) <= 140:
            guardado = guardar_novedad(telefono=telefono, novedad_sms=mensaje.replace('#', ''), fecha_hora=fecha)
            if guardado:
                enviar_respuesta(telefono, "Su novedad fue registrada con exito.")
            else:
                enviar_respuesta(telefono, 'Su novedad no fue registrada')
        else:
            enviar_respuesta(telefono, "La novedad es demasiado larga. Por favor, redacte una novedad más corta.")


def verificar_numero(numero, texto):
    if '#' in texto or 'HOLA' in texto:
        try:
            # Elimina el signo de "+" y los espacios en blanco del número de teléfono
            numero_limpio = numero.replace('+54', '').replace(' ', '')
            if len(numero_limpio) != 10:
                numero_limpio = numero.replace('+549', '').replace(' ', '')
            # Configura la conexión a la base de datos PostgreSQL
            conn = psycopg2.connect(
                dbname="nombre_de_la_base_de_datos",
                user="usuario_de_la_base_de_datos",
                password="contraseña_de_la_base_de_datos",
                host="host_o_direccion_IP"
            )
            cursor = conn.cursor()
            # Realiza una consulta para verificar si el número existe en la tabla de usuarios
            cursor.execute('SELECT COUNT(*) FROM tabla WHERE columna_phone = %s', (numero_limpio,))
            count = cursor.fetchone()[0]
            # Si count es mayor que 0, significa que el número existe en la base de datos
            if count == 0:
                mensaje_no_existe = "USTED NO EXISTE EN LA BASE DE DATOS"
                enviar_respuesta(numero, mensaje_no_existe)
                # Cierra la conexión a la base de datos
            cursor.close()
            conn.close()
            print(count)
            return count > 0

        except Exception as E:
            print("Error al verificar el número en la base de datos:", E)
            return False


def hex_a_texto(hex_string):
    try:
        bytes_object = bytes.fromhex(hex_string)
        return bytes_object.decode('iso-8859-1')
    except ValueError:
        return "No se pudo decodificar el hexadecimal"


try:
    puerto_serial = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
except Exception as e:
    print("Error al abrir el puerto serial:", e)
    pass


def recibir_mensaje():
    tel = None
    while True:
        try:
            linea = puerto_serial.readline().decode('iso-8859-1').strip()
            if all(c in '0123456789ABCDEF' for c in linea):
                texto_decodificado = hex_a_texto(linea).replace('\x00', '')
            else:
                texto_decodificado = linea.replace('\x00', '')
            if '+CMT:' in linea:
                fecha_nueva = linea.split(',')
                tel = fecha_nueva[0].split('"')[1]
                fecha = fecha_nueva[2].replace('/', '-') + ' ' + fecha_nueva[3].replace(' ', '')[:-3] + '03'
                # print(linea)
            elif len(texto_decodificado) != 0:
                print(texto_decodificado)
                if verificar_numero(tel, texto_decodificado):
                    interaccion(texto_decodificado, tel, fecha)
                    tel = None
        except Exception as E:
            print("Error:", E)


try:
    recibir_mensaje()
except KeyboardInterrupt:
    pass
finally:
    puerto_serial.close()
