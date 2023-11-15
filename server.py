from flask import Flask, jsonify, request
import json
import CRUDgeneral as crud
import CRUDdispositivo as crud_router

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
			enlace = f"{request.url_root}routes/{router_hostname}/interfaces/{nombre_interfaz}"
			enlace = enlace.rstrip('/')
			interfaz['enlace'] = enlace



app =  Flask(__name__)


#Users endpoints TODO: Implement funtionalities 
@app.route("/usuarios")
def get_usuarios():
    usuarios = crud.get_users_all_routers()
    return json.dumps(usuarios)

@app.route("/usuarios", methods=["POST"])
def create_usuarios():
    user = request.form['user']
    privilege = request.form['privilege']
    password = request.form['password']
    usuarios = crud.create_user_all_routers(user, privilege, password)
    return json.dumps(usuarios)

@app.route("/usuarios", methods=["PUT"])
def update_usuarios():
    user = request.form['user']
    privilege = request.form['privilege']
    password = request.form['password']
    usuarios = crud.update_user_all_routers(user, privilege, password)
    return json.dumps(usuarios)

@app.route("/usuarios",methods=["DELETE"])
def delete_usuarios():
    user = request.form['user']
    usuarios = crud.delete_user_all_routers(user)
    return json.dumps(usuarios)


#Routes Endpoint TODO: Iplement get funtion
@app.route("/routes")
def get_routes():
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


#Routes Hostname Endpoint TODO: Iplement get funtion
@app.route("/routes/<hostname>")
def get_routes_hostname(hostname):
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

#Routes Hostname Interface Endpoint TODO: Iplement get funtion
@app.route("/routes/<hostname>/interfaces/<interfaz>")
def get_routes_hostname_interface(hostname,interfaz):
    return jsonify({"hostname": hostname, "interfaz": interfaz})

#Crud users per router TODO: implement funtions
@app.route("/routes/<hostname>/usuarios")
def get_usuarios_router(hostname):
    usuarios = crud_router.get_users(hostname)
    return json.dumps(usuarios)

@app.route("/routes/<hostname>/usuarios", methods=["POST"])
def create_usuario_router(hostname):
    user = request.form['user']
    privilege = request.form['privilege']
    password = request.form['password']
    usuarios = crud_router.create_user(hostname, user, privilege, password)
    return json.dumps(usuarios)

@app.route("/routes/<hostname>/usuarios", methods=["PUT"])
def update_usuario_router(hostname):
    user = request.form['user']
    privilege = request.form['privilege']
    password = request.form['password']
    usuarios = crud_router.update_user(hostname, user,privilege, password)
    return json.dumps(usuarios)

@app.route("/routes/<hostname>/usuarios",methods=["DELETE"])
def delete_usuario_router(hostname):
    user = request.form['user']
    usuarios = crud_router.delete_user(hostname, user)
    return json.dumps(usuarios)


#Detect topology TODO: implement funtions
@app.route("/topologia")
def get_topologia():
    return "Hola"

@app.route("/topologia", methods=["POST"])
def create_daemon():
    return "Hola"

@app.route("/topologia", methods=["PUT"])
def update_daemon():
    return "Hola"

@app.route("/topologia",methods=["DELETE"])
def delete_daemon():
    return "Hola"

#Graphic topology TODO: implement funtions
@app.route("/topologia/grafica")
def get_topologiagrafico():
    return "Hola"


if __name__ == '__main__':
    app.run(debug=True)