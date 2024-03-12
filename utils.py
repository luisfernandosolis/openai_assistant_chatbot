#gmail
from email.message import EmailMessage
import smtplib

##google sheets
import pandas as pd
import pygsheets


##whatsapp 
from heyoo import WhatsApp

#openai
from openai import OpenAI
from time import sleep
import json

##Obtener el api key
from dotenv import load_dotenv
import os
load_dotenv()

##credenciales
CONTRASENIA_EMAIL=os.getenv("APP_PASSWORD_GMAIL")
CORREO_REMITENTE=os.getenv("EMAIL_REMITENTE")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
WHATSAPP_API_TOKEN=os.getenv("WHATSAPP_API_TOKEN")
PHONE_NUMBER_ID=os.getenv("PHONE_NUMBER_ID")
DOCUMENT_URL=os.getenv("DOCUMENT_URL")
JSON_SERVICE_ACCOUNT=os.getenv("JSON_SERVICE_ACCOUNT")

client = OpenAI(api_key=OPENAI_API_KEY) 

def enviar_correo(nombre,correo, mensaje):
  try:
    remitente = CORREO_REMITENTE
    destinatario = correo
    mensaje = mensaje
    email = EmailMessage()
    email["From"] = remitente
    email["To"] = destinatario
    email["Subject"] = "Correo Informativo"
    email.set_content(mensaje)
    smtp = smtplib.SMTP_SSL("smtp.gmail.com")
    smtp.login(remitente, CONTRASENIA_EMAIL)
    smtp.sendmail(remitente, destinatario, email.as_string())
    smtp.quit()
    return True
  except:
    return False

## Google Sheets
def registrar_datos_gsheets(nombre, edad, correo,programa,telefono):

  ##obtener los datos de google sheets

  url=DOCUMENT_URL
  
  ##añadimos el nuevo registro al dataframe
  df=pd.read_csv(url)
  print(df)
  df.loc[len(df.index)] = ['123',nombre, edad, correo,programa,telefono]
  print(df)


  try:
    ##luego cargamos a google sheets
    service_account_path=JSON_SERVICE_ACCOUNT
    gc = pygsheets.authorize(service_file=service_account_path)

    #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
    sh = gc.open_by_url(DOCUMENT_URL)


    #select the first sheet 
    wks = sh[0]

    #update the first sheet with df, starting at cell B2. 
    wks.set_dataframe(df,(1,1))
    return True
  except Exception as e:
    return e
  

#enviar correo por whatsapp
def enviar_whatsapp_asesor(nombre: str, whatsapp: str, mensaje :str):
  try:
    messenger = WhatsApp(WHATSAPP_API_TOKEN,phone_number_id=PHONE_NUMBER_ID)
    # For sending a Text messages
    messenger.send_message(mensaje, whatsapp)
    return True
  except:
    return False
  

#ejecutar un run
def run_excecuter(run):
  while True:

    run_status=client.beta.threads.runs.retrieve(
        thread_id=run.thread_id,
        run_id=run.id
    )

    if run_status.status =="completed":
      print("accion terminada")
      break
    elif run_status.status=="requires_action":
      print("requiere accion")

      list_of_actions=run_status.required_action.submit_tool_outputs.tool_calls
      print("-----"*20)
      print(list_of_actions)
      print("-----"*20)

      tools_output=[]
      for accion in list_of_actions:
        if accion.function.name =="registrar_datos_gsheets":
          nombre=accion.function.name
          argumentos=json.loads(accion.function.arguments)

          
          print("Nombre de la funcion a ejecutar: ", nombre)
          print("Argumentos de la funcion: ", argumentos)

          interesado_agregado=registrar_datos_gsheets(argumentos["nombre"],argumentos["edad"],argumentos["correo"],argumentos["programa"],argumentos["telefono"])

          tools_output.append(
              {
                  "tool_call_id": accion.id,
                  "output": interesado_agregado
              }
          )
        elif accion.function.name =="enviar_correo":
          nombre=accion.function.name
          argumentos=json.loads(accion.function.arguments)

          
          print("Nombre de la funcion a ejecutar: ", nombre)
          print("Argumentos de la funcion: ", argumentos)

          correo_enviado=enviar_correo(argumentos["nombre"],argumentos["correo"],argumentos["mensaje"])

          tools_output.append(
              {
                  "tool_call_id": accion.id,
                  "output": correo_enviado
              }
          )
        elif accion.function.name =="enviar_whatsapp_asesor":
          nombre=accion.function.name
          argumentos=json.loads(accion.function.arguments)

          
          print("Nombre de la funcion a ejecutar: ", nombre)
          print("Argumentos de la funcion: ", argumentos)

          whatsapp_enviado=enviar_whatsapp_asesor(argumentos["nombre"],argumentos["whatsapp"],argumentos["mensaje"])

          tools_output.append(
              {
                  "tool_call_id": accion.id,
                  "output": whatsapp_enviado
              }
          )

        else:
          return "No se encontró la accion"
      print("ejecucion de acciones ha terminado")
      print(tools_output)
      client.beta.threads.runs.submit_tool_outputs(
          thread_id=run.thread_id,
          run_id=run.id,
          tool_outputs=tools_output
      )
    else:
      print("Esperando respuesta del rasistente")
      sleep(3)