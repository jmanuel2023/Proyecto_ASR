from flask import Flask, jsonify, request, url_for
import json
from pysnmp.entity.rfc3413.oneliner import cmdgen
from netmiko import ConnectHandler
import textfsm


def obtener_info_router(host,community):
	cmdGen = cmdgen.CommandGenerator()
	
	router = {
		'device_type':'cisco_ios',
		'ip': host,
		'username':'admin',
		'password':'admin',
	}
		
	rol1 = "ROL DE ACCESO"
	rol2 = "ROL DE AGREGACION/DISTRIBUCION"
	rol3 = "NUCLEO"

# Hostname OID
	system_name = '1.3.6.1.2.1.1.5.0'
	empresa_system = '1.3.6.1.4.1.9.2.1.61.0'
	so_system = '1.3.6.1.2.1.1.1.0'
	
	def obtiene_interfaces():
		try:
			connection = ConnectHandler(**router)
			output = connection.send_command('show ip interface brief')
		
		
			with open('plantilla.textfsm', 'r') as archivofsm:
				template = textfsm.TextFSM(archivofsm)
		
			parsed_data = template.ParseText(output)
			connection.disconnect()
		
			interfaces_info = []
			for entry in parsed_data:
				interface_info = {
					"Nombre de Interfaz": entry[0],
					"Direccion IP": entry[1],
					"enlace": ""
				}
				interfaces_info.append(interface_info)
			
		
			return (interfaces_info)
		except Exception as e:
			return jsonify({'error': str(e)})

	def snmp_query(host, community, oid):
		errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(cmdgen.CommunityData(community),cmdgen.UdpTransportTarget((host, 161)),oid)
		if errorIndication:
			print(errorIndication)
		else:
			if errorStatus:
				print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex)-1] or '?'))
			else:
				for name, val in varBinds:
					return(str(val))

	def obtiene_rol(host,community,oid):
		errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(cmdgen.CommunityData(community), cmdgen.UdpTransportTarget((host,161)),oid)
		if errorIndication:
			print(errorIndication)
		else:
			if errorStatus:
				print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex)-1] or '?'))
			else:
				for name, val in varBinds:
					if str(val) == "TOR-1" or str(val) == "TOR-2":
						return(rol1)
					elif str(val) == "R1" or str(val) == "R2":
						return(rol2)
					else:
						return(rol3) 
						
	def obtiene_iploopback():
		return("N/A")
	
	def obtiene_ipadmin():
		try:
			connection = ConnectHandler(**router)
			output = connection.send_command('show ip interface brief')
		
		
			with open('plantilla.textfsm', 'r') as archivofsm:
				template = textfsm.TextFSM(archivofsm)
		
			parsed_data = template.ParseText(output)
			connection.disconnect()
		
			interfaces_info = []
			for entry in parsed_data:
				interface_info = {
					"Direccion IP":entry[1]
				}
				interfaces_info.append(interface_info)
				break
			
		
			return (interfaces_info)
		except Exception as e:
			return jsonify({'error': str(e)})

	def obtiene_empresa(host, community, oid):
		errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(cmdgen.CommunityData(community),cmdgen.UdpTransportTarget((host, 161)),oid)
		if errorIndication:
			print(errorIndication)
		else:
			if errorStatus:
				print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex)-1] or '?'))
			else:
				for name, val in varBinds:
					cadena = str(val)
					empresa = cadena[:19]
					return(empresa)

	def obtiene_so(host, community, oid):
		errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(cmdgen.CommunityData(community),cmdgen.UdpTransportTarget((host, 161)),oid)
		if errorIndication:
			print(errorIndication)
		else:
			if errorStatus:
				print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex)-1] or '?'))
			else:
				for name, val in varBinds:
					cadena2 = str(val)
					so = cadena2[:18]
					return(so)

	
	result = {}
	result["hostname"] = snmp_query(host, community, system_name)
	result["LoopBack_IP"] = obtiene_iploopback()
	result["IP_administrativa"] = obtiene_ipadmin()
	result["Empresa"] = obtiene_empresa(host, community, empresa_system)
	result["rol"] = obtiene_rol(host, community,  system_name)
	result["Sistema Operativo"] = obtiene_so(host, community, so_system) 
	result["Interfaces activas"] = obtiene_interfaces()
	
	return result

def actualizar_enlaces(routers):
	for router in routers:
		interfaces_activas = router.get('Interfaces activas', [])
		for interfaz in interfaces_activas:
			nombre_interfaz = interfaz.get('Nombre de Interfaz','')
			router_hostname = router.get('hostname','')
			nombre_interfaz = nombre_interfaz.replace("/","_")
			enlace = f"{request.url_root}routers/{router_hostname}/interfaces/{nombre_interfaz}"
			enlace = enlace.rstrip('/')
			interfaz['enlace'] = enlace
			

app = Flask(__name__)

@app.route('/')
def inicio():
    return 'Hola!!!, esta es la pagina principal'

@app.route('/usuarios')
def usuarios():
    return 'GET: Regresa un json con todos los usuarios existentes en los routers, incluyendo nombre, permisos y dispositivos donde existe (URL a routers donde exista cada usuario. POST: Agregar un nuevo usuario a todos los routers, regresar json con la misma informacion de GET pero del usuario agregado. PUT: Actualiza un usuario en todos los routers, regresa un json con la misma informacion de GET pero del usuario actualizado. DELETE: Elimina el usuario comun a todos los routers, recupera un json con la misma informacion de GET pero del usuario eliminado.'
    
@app.route('/routers/', methods=['GET'])
def enrutadorsimple():
	
	
	with open('routers.json','r') as file:
		datos = json.load(file)
	hosts=[device['ip'] for device in datos.values()]
	community = 'publica'
	
	all_results = []
	
	for host in hosts:
		result = obtener_info_router(host, community)
		all_results.append(result)
	
	with open('/home/hanz/Documentos/ProyectoP1/resultados.json', 'w') as f:
		json.dump(all_results,f, indent=2)
	
	try:
		with open('resultados.json', 'r') as json_file:
			routers = json.load(json_file)
		
		actualizar_enlaces(routers)
				
		
		return jsonify(resultados = routers)
	except FileNotFoundError:
		return jsonify({'error': 'El archivo JSON no se encuentra'})
		
@app.route('/routers/<hostname>/', methods=['GET'])
def enrutadorname(hostname):
	try:
		with open('resultados.json', 'r') as archivo:
			datos = json.load(archivo)	
		for router in datos:
			if router['hostname'] == hostname:
				actualizar_enlaces(datos)
				return jsonify(router)
				
		return jsonify({'error': 'Router no encontrado'}),404
	except FileNotFoundError:
		return jsonify({'error': 'El archivo JSON no se encuentra'}),404
    
@app.route('/routers/<hostname>/interfaces/<interfaz>', methods=['GET'])
def enrutadorinterfaz(hostname, interfaz):
	print(hostname)
	print(interfaz)
	return jsonify({"hostname": hostname, "interfaz": interfaz})
    
@app.route('/routers/<hostname>/usuarios')
def routerusuario(hostname):
    return 'GET: Regresa un json con los usuarios existentes en el router especifico, incluyendo nombre y permisos. POST: Agrega un nuevo usuarrio al router especifico, regresa un json con la misma informacion de GET pero del usuario agregado. PUT: Actualiza un nuevo usuario al router especifico, regresa un json con la misma informacion del GET pero del usuario actualizado. DELETE: Elimina el usuario comun a todos los routers, recupera en un json la misma informacion del GET pero del usuario eliminado: Router %s' % hostname
    
@app.route('/topologia')
def topologia():
    return 'GET: Regresa un json con los routers existentes en la topologia y ligas a sus routers vecinos. POST: Activa un demonio que cada 5 minutos explore la red para detectar cambios en la misma. PUT: Permite cambiar el intervalo de tiempo en el que el demonio explora la topologia. DELETE: Detiene el demonio que explora la topologia'

@app.route('/topologia/grafica')
def graficatopo():
    return 'GET: Regresa un archivo en algun formato grafico donde se pueda visualizar la topologia existente'
	
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
