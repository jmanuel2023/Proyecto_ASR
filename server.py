from flask import Flask, jsonify, request, url_for, send_file
from pysnmp.entity.rfc3413.oneliner import cmdgen
from netmiko import ConnectHandler
from netmiko import Netmiko
import textfsm
import json
import CRUDgeneral as crud
import CRUDdispositivo as crud_router
import topology as topology_scaner
import threading
import time
import graficar_topologia as topog


def obtener_info_router(host,community):
    cmdGen = cmdgen.CommandGenerator()

    router = {
    	'device_type':'cisco_ios',
    	'ip': host,
    	'username':'admin',
    	'password':'admin',
    }
    
    rol1 = "Proveedor de servicios"
    rol2 = "Router de frontera"
    rol3 = "Nucleo"
    rol4 = "Hojas"

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

    def snmp_query_1(host, community, oid):
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
                        return(rol4)
                    elif str(val) == "R1" or str(val) == "R2":
                        return(rol3)
                    elif str(val) == "Edge":
                        return(rol2)
                    else:
                        return(rol1) 
						
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
    result["hostname"] = snmp_query_1(host, community, system_name)
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
    return jsonify(usuarios)

@app.route("/usuarios", methods=["POST"])
def create_usuarios():
    user = request.form['user']
    privilege = request.form['privilege']
    password = request.form['password']
    usuarios = crud.create_user_all_routers(user, privilege, password)
    return jsonify(usuarios)

@app.route("/usuarios", methods=["PUT"])
def update_usuarios():
    user = request.form['user']
    privilege = request.form['privilege']
    password = request.form['password']
    usuarios = crud.update_user_all_routers(user, privilege, password)
    return jsonify(usuarios)

@app.route("/usuarios",methods=["DELETE"])
def delete_usuarios():
    user = request.form['user']
    usuarios = crud.delete_user_all_routers(user)
    return jsonify(usuarios)


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

    with open('resultados.json', 'w') as f:
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
@app.route("/routes/<hostname>/interfaces/")
def interface(hostname):
    cmdGen = cmdgen.CommandGenerator()
    with open('routers.json','r') as f: #Aqui se abrirá el routers.json pero se necesita cambiar al directorio que tendŕa cada quien
        data = json.load(f)
    if hostname in data:
        host = data[hostname]['ip'] #Se debe cambiar a la estructura del json, para encontrar la ip del router
    else:
        resp_json = jsonify({"Error":"El router no se encuentra definido"})
        resp_json.status_code = 404
        return resp_json
    community = 'publica'
    my_device = {
        'host': host,
        'username':"admin",
        'password':"admin",
        'secret' : "admin",
        'device_type':"cisco_ios"
    }
    net_connect = Netmiko(**my_device)
    output = net_connect.send_command("show ip interface brief",use_textfsm=True)
    def snmp_query_oid_no(host, community, oid):
        errorIndication, errorStatus, errorIndex, varBinds =cmdGen.nextCmd(
            cmdgen.CommunityData(community),
            cmdgen.UdpTransportTarget((host, 161)),
            oid
        )

        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex)-1] or '?'
                    )
                )
            else:
                conter = 0
                for val in varBinds:
                    val_string = str(val[0])
                    conter = conter + 1
                return conter
    oi = '.1.3.6.1.2.1.2.2.1.2'
    index = snmp_query_oid_no(host,community,oi)
    def snmp_query(host, community, oid):
        errorIndication, errorStatus, errorIndex, varBinds =cmdGen.getCmd(
            cmdgen.CommunityData(community),
            cmdgen.UdpTransportTarget((host, 161)),
            oid
        )

        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex)-1] or '?'
                    )
                )
            else:
                for name, val in varBinds:
                    return(val.prettyPrint())
    i=1
    json_interface = {}
    for _ in range(index-1):
        name_interface = oi+'.'+str(i)
        n_int = str(snmp_query(host,community,name_interface))
        json_interface[n_int]={}

        tipo_int = '.1.3.6.1.2.1.2.2.1.3.'+str(i)
        no_int = '.1.3.6.1.2.1.2.2.1.1.'+str(i)
        state_int = '.1.3.6.1.2.1.2.2.1.8.'+str(i)

        json_interface[n_int]['Tipo']= snmp_query(host,community,tipo_int)
        if(json_interface[n_int]['Tipo']=='1'):
            json_interface[n_int]['Tipo']= 'other(1)'
        elif(json_interface[n_int]['Tipo']=='2'):
            json_interface[n_int]['Tipo']='regular1822(2)'
        elif(json_interface[n_int]['Tipo']=='3'):
            json_interface[n_int]['Tipo']='hdh1822(3)'
        elif(json_interface[n_int]['Tipo']=='4'):
            json_interface[n_int]['Tipo']='ddn-x25(4)'
        elif(json_interface[n_int]['Tipo']=='5'):
            json_interface[n_int]['Tipo']='rfc877-x25(5)'
        elif(json_interface[n_int]['Tipo']=='6'):
            json_interface[n_int]['Tipo']='ethernet-csmacd(6)'
        elif(json_interface[n_int]['Tipo']=='7'):
            json_interface[n_int]['Tipo']='iso88023-csmacd(7)'
        elif(json_interface[n_int]['Tipo']=='8'):
            json_interface[n_int]['Tipo']='iso88024-tokenBus(8)'
        elif(json_interface[n_int]['Tipo']=='9'):
            json_interface[n_int]['Tipo']='iso88025-tokenRIng(9)'
        elif(json_interface[n_int]['Tipo']=='10'):
            json_interface[n_int]['Tipo']='iso88026-man(10)'
        elif(json_interface[n_int]['Tipo']=='11'):
            json_interface[n_int]['Tipo']='starLan(11)'
        elif(json_interface[n_int]['Tipo']=='12'):
            json_interface[n_int]['Tipo']='proteon-10Mbit(12)'
        elif(json_interface[n_int]['Tipo']=='13'):
            json_interface[n_int]['Tipo']='proteon-80Mbit'
        elif(json_interface[n_int]['Tipo']=='14'):
            json_interface[n_int]['Tipo']='hyperchannel(14)'
        elif(json_interface[n_int]['Tipo']=='15'):
            json_interface[n_int]['Tipo']='fddi(15)'
        elif(json_interface[n_int]['Tipo']=='16'):
            json_interface[n_int]['Tipo']='lapb(16)'
        elif(json_interface[n_int]['Tipo']=='17'):
            json_interface[n_int]['Tipo']='sdlc(17)'
        elif(json_interface[n_int]['Tipo']=='18'):
            json_interface[n_int]['Tipo']='ds1(18)'
        elif(json_interface[n_int]['Tipo']=='19'):
            json_interface[n_int]['Tipo']='e1(19)'
        elif(json_interface[n_int]['Tipo']=='20'):
            json_interface[n_int]['Tipo']='basicISDN(20)'
        elif(json_interface[n_int]['Tipo']=='21'):
            json_interface[n_int]['Tipo']='primaryISDN(21)'
        elif(json_interface[n_int]['Tipo']=='22'):
            json_interface[n_int]['Tipo']='propPointToSerial(22)'
        elif(json_interface[n_int]['Tipo']=='23'):
            json_interface[n_int]['Tipo']='ppp(23)'
        elif(json_interface[n_int]['Tipo']=='24'):
            json_interface[n_int]['Tipo']='softwareLoopback(24)'
        elif(json_interface[n_int]['Tipo']=='25'):
            json_interface[n_int]['Tipo']='eon(25)'
        elif(json_interface[n_int]['Tipo']=='26'):
            json_interface[n_int]['Tipo']='ethernet-32Mbit(26)'
        elif(json_interface[n_int]['Tipo']=='27'):
            json_interface[n_int]['Tipo']='nsip(27)'
        elif(json_interface[n_int]['Tipo']=='28'):
            json_interface[n_int]['Tipo']='slip(28)'
        elif(json_interface[n_int]['Tipo']=='29'):
            json_interface[n_int]['Tipo']='ultra(29)'
        elif(json_interface[n_int]['Tipo']=='30'):
            json_interface[n_int]['Tipo']='ds3(30)'
        elif(json_interface[n_int]['Tipo']=='31'):
            json_interface[n_int]['Tipo']='sip(31)'
        else:
            json_interface[n_int]['Tipo']='frame-relay(32)'

        json_interface[n_int]['Numero de Interfaz']= snmp_query(host,community,no_int)
        json_interface[n_int]['Estado']= snmp_query(host,community,state_int)
        if(json_interface[n_int]['Estado']=='1'):
            json_interface[n_int]['Estado']='UP(1)'
        elif(json_interface[n_int]['Estado']=='2'):
            json_interface[n_int]['Estado']='DOWN(2)'
        else:
            json_interface[n_int]['Estado']='Testing(3)'
        liga = f"{request.url_root}routes/{hostname}"
        json_interface[n_int]['Liga al router']=liga
        if output[i-1].get('ip_address') != 'unassigned':
            ip_int = output[i-1]['ip_address']
            json_interface[n_int]['Direccion IP'] = ip_int
            netmask_int = '.1.3.6.1.2.1.4.20.1.3.'+ ip_int
            json_interface[n_int]['Submascara'] = snmp_query(host,community,netmask_int)
        else:
            json_interface[n_int]['Direccion IP'] = 'Sin Asignar'
            json_interface[n_int]['Submascara'] = 'Sin Asignar'

        i = i + 1

    with open('interfaz.json', 'w') as f: #cambiar para la dirección de cada computadora
        json.dump(json_interface,f)
    return jsonify(json_interface)
@app.route("/routes/<hostname>/interfaces/<interfaz>")
def get_routes_hostname_interface(hostname,interfaz):
    cmdGen = cmdgen.CommandGenerator()
    n_int = interfaz
    n_int = n_int.replace('_','/')
    with open('routers.json','r') as f: #Aqui se abrirá el routers.json pero se necesita cambiar al directorio que tendŕa cada quien
        data = json.load(f)
    if hostname in data:
        host = data[hostname]['ip'] #Se debe cambiar a la estructura del json, para encontrar la ip del router
    else:
        resp_json = jsonify({"Error":"El router no se encuentra definido"})
        resp_json.status_code = 404
        return resp_json
    community = 'publica'
    my_device = {
        'host': host,
        'username':"admin",
        'password':"admin",
        'secret' : "admin",
        'device_type':"cisco_ios"
    }

    net_connect = Netmiko(**my_device)
    output = net_connect.send_command("show ip interface brief",use_textfsm=True)
    i=0
    indice = 0
    for salida in output:
        print(salida['interface'])
        if(salida['interface']==n_int):
            indice = i
        else:
            i = i + 1


    if output[indice].get('ip_address') != 'unassigned':
        ip_int = output[indice]['ip_address']
    else:
        resp_json = jsonify({"Error":"La interfaz no tiene ip definida"})
        resp_json.status_code = 404
        return resp_json

    def snmp_query_oid_no(host, community, oid):
        errorIndication, errorStatus, errorIndex, varBinds =cmdGen.nextCmd(
            cmdgen.CommunityData(community),
            cmdgen.UdpTransportTarget((host, 161)),
            oid
        )

        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex)-1] or '?'
                    )
                )
            else:
                conter = 1
                indice = 0
                for val in varBinds:
                    val_string = str(val[0])
                    bandera_1=val_string.count(n_int)
                    if bandera_1 == 1:
                        indice = conter
                    else:
                        conter = conter + 1
                return indice
    oi = '.1.3.6.1.2.1.2.2.1.2'
    index = snmp_query_oid_no(host,community,oi)
    if index == 0:
        resp_json = jsonify({"Error":"La interfaz no se encuentra definida"})
        resp_json.status_code = 404
        return resp_json
    tipo_int = '.1.3.6.1.2.1.2.2.1.3.'+str(index)
    no_int = '.1.3.6.1.2.1.2.2.1.1.'+str(index)
    netmask_int = '.1.3.6.1.2.1.4.20.1.3.'
    state_int = '.1.3.6.1.2.1.2.2.1.8.'+str(index)
    def snmp_query(host, community, oid):
        errorIndication, errorStatus, errorIndex, varBinds =cmdGen.getCmd(
            cmdgen.CommunityData(community),
            cmdgen.UdpTransportTarget((host, 161)),
            oid
        )

        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex)-1] or '?'
                    )
                )
            else:
                for name, val in varBinds:
                    return(val.prettyPrint())

    json_interface = {}
    json_interface['Tipo']= snmp_query(host,community,tipo_int)
    if(json_interface['Tipo']=='1'):
        json_interface['Tipo']= 'other(1)'
    elif(json_interface['Tipo']=='2'):
        json_interface['Tipo']='regular1822(2)'
    elif(json_interface['Tipo']=='3'):
        json_interface['Tipo']='hdh1822(3)'
    elif(json_interface['Tipo']=='4'):
        json_interface['Tipo']='ddn-x25(4)'
    elif(json_interface['Tipo']=='5'):
        json_interface['Tipo']='rfc877-x25(5)'
    elif(json_interface['Tipo']=='6'):
        json_interface['Tipo']='ethernet-csmacd(6)'
    elif(json_interface['Tipo']=='7'):
        json_interface['Tipo']='iso88023-csmacd(7)'
    elif(json_interface['Tipo']=='8'):
        json_interface['Tipo']='iso88024-tokenBus(8)'
    elif(json_interface['Tipo']=='9'):
        json_interface['Tipo']='iso88025-tokenRIng(9)'
    elif(json_interface['Tipo']=='10'):
        json_interface['Tipo']='iso88026-man(10)'
    elif(json_interface['Tipo']=='11'):
        json_interface['Tipo']='starLan(11)'
    elif(json_interface['Tipo']=='12'):
        json_interface['Tipo']='proteon-10Mbit(12)'
    elif(json_interface['Tipo']=='13'):
        json_interface['Tipo']='proteon-80Mbit'
    elif(json_interface['Tipo']=='14'):
        json_interface['Tipo']='hyperchannel(14)'
    elif(json_interface['Tipo']=='15'):
        json_interface['Tipo']='fddi(15)'
    elif(json_interface['Tipo']=='16'):
        json_interface['Tipo']='lapb(16)'
    elif(json_interface['Tipo']=='17'):
        json_interface['Tipo']='sdlc(17)'
    elif(json_interface['Tipo']=='18'):
        json_interface['Tipo']='ds1(18)'
    elif(json_interface['Tipo']=='19'):
        json_interface['Tipo']='e1(19)'
    elif(json_interface['Tipo']=='20'):
        json_interface['Tipo']='basicISDN(20)'
    elif(json_interface['Tipo']=='21'):
        json_interface['Tipo']='primaryISDN(21)'
    elif(json_interface['Tipo']=='22'):
        json_interface['Tipo']='propPointToSerial(22)'
    elif(json_interface['Tipo']=='23'):
        json_interface['Tipo']='ppp(23)'
    elif(json_interface['Tipo']=='24'):
        json_interface['Tipo']='softwareLoopback(24)'
    elif(json_interface['Tipo']=='25'):
        json_interface['Tipo']='eon(25)'
    elif(json_interface['Tipo']=='26'):
        json_interface['Tipo']='ethernet-32Mbit(26)'
    elif(json_interface['Tipo']=='27'):
        json_interface['Tipo']='nsip(27)'
    elif(json_interface['Tipo']=='28'):
        json_interface['Tipo']='slip(28)'
    elif(json_interface['Tipo']=='29'):
        json_interface['Tipo']='ultra(29)'
    elif(json_interface['Tipo']=='30'):
        json_interface['Tipo']='ds3(30)'
    elif(json_interface['Tipo']=='31'):
        json_interface['Tipo']='sip(31)'
    else:
        json_interface['Tipo']='frame-relay(32)'

    json_interface['Numero de Interfaz']= snmp_query(host,community,no_int)
    json_interface['Direccion IP']=ip_int
    netmask_int=netmask_int+ip_int
    json_interface['Submascara']= snmp_query(host,community,netmask_int)
    json_interface['Estado']= snmp_query(host,community,state_int)
    if(json_interface['Estado']=='1'):
        json_interface['Estado']='UP(1)'
    elif(json_interface['Estado']=='2'):
        json_interface['Estado']='DOWN(2)'
    else:
        json_interface['Estado']='Testing(3)'
    liga = f"{request.url_root}routes/{hostname}"
    json_interface['Liga al router']=liga

    with open('interfaz.json', 'w') as f: #cambiar para la dirección de cada computadora
        json.dump(json_interface,f)
    return jsonify(json_interface)

#Crud users per router TODO: implement funtions
@app.route("/routes/<hostname>/usuarios")
def get_usuarios_router(hostname):
    usuarios = crud_router.get_users(hostname)
    return jsonify(usuarios)

@app.route("/routes/<hostname>/usuarios", methods=["POST"])
def create_usuario_router(hostname):
    user = request.form['user']
    privilege = request.form['privilege']
    password = request.form['password']
    usuarios = crud_router.create_user(hostname, user, privilege, password)
    return jsonify(usuarios)

@app.route("/routes/<hostname>/usuarios", methods=["PUT"])
def update_usuario_router(hostname):
    user = request.form['user']
    privilege = request.form['privilege']
    password = request.form['password']
    usuarios = crud_router.update_user(hostname, user,privilege, password)
    return jsonify(usuarios)

@app.route("/routes/<hostname>/usuarios",methods=["DELETE"])
def delete_usuario_router(hostname):
    user = request.form['user']
    usuarios = crud_router.delete_user(hostname, user)
    return jsonify(usuarios)


#Detect topology TODO: implement funtions

# Variables globales para almacenar el estado del demonio y el tiempo de espera
daemon_running = False
update_interval = 0
current_topology = {"mensaje": "Topología no actualizada"}

def update_topology():
    global daemon_running
    global update_interval
    global current_topology

    while daemon_running:
        time.sleep(update_interval)
        # Lógica para actualizar la topología aquí
        current_topology = topology_scaner.get_topology()
        print("Actualizando topología...")

@app.route("/topologia", methods=["GET"])
def get_topologia():
    global current_topology
    # Devolver la topología actualizada o no actualizada, según el estado del demonio
    return jsonify(current_topology)

@app.route("/topologia", methods=["POST"])
def create_daemon():
    global daemon_running
    global update_interval

    if not daemon_running:
        # Obtener el tiempo de espera del cuerpo de la solicitud
        data = request.get_json()
        update_interval = data.get("update_interval", 60)  # 60 segundos por defecto

        # Iniciar el demonio en un hilo
        daemon_running = True
        daemon_thread = threading.Thread(target=update_topology)
        daemon_thread.start()

        return jsonify({"mensaje": "Demonio creado correctamente"})

    return jsonify({"mensaje": "El demonio ya está en ejecución"})

@app.route("/topologia", methods=["PUT"])
def update_daemon():
    global update_interval

    # Obtener el nuevo tiempo de espera del cuerpo de la solicitud
    data = request.get_json()
    update_interval = data.get("update_interval", 60)  # 60 segundos por defecto

    return jsonify({"mensaje": "Tiempo de actualización del demonio actualizado correctamente"})

@app.route("/topologia", methods=["DELETE"])
def delete_daemon():
    global daemon_running

    if daemon_running:
        # Detener el demonio
        daemon_running = False

        return jsonify({"mensaje": "Demonio eliminado correctamente"})

    return jsonify({"mensaje": "El demonio no está en ejecución"})

#Graphic topology TODO: implement funtions
@app.route("/topologia/grafica")
def get_topologiagrafico():
    if len(current_topology) == 0:
        imagen = topog.generar_grafico(current_topology)
        return send_file(imagen, mimetype='image/png')
    else:
        return jsonify("No hay datos")


if __name__ == '__main__':
    app.run(debug=True)