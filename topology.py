import napalm
import json
import textfsm

def send_command(device_info, command):
    driver_ios = napalm.get_network_driver("ios")
    ios_router = driver_ios(
        hostname=device_info["ip"],
        username=device_info["username"],
        password=device_info["password"]
    )
    
    try:
        print(f"Connecting to {device_info['ip']}...")
        ios_router.open()
        print(f"Checking {device_info['ip']} Connection Status:")
        result = ios_router.cli([command])
        with open('vecino.textfsm', 'r') as archivofsm:
            template = textfsm.TextFSM(archivofsm)
        
        parsed_data = template.ParseText(result["show cdp neighbors"])
        print(parsed_data)
        return parsed_data
    except Exception as e:
        return {}
        print(f"Error connecting to {device_info['ip']}: {str(e)}")
    finally:
        ios_router.close()

def get_topology():
    devices = {
        "R1": {"device_type": "cisco_ios","ip": "10.10.10.17","username": "admin", "password": "admin"},
        "R2": {"device_type": "cisco_ios","ip": "10.10.10.13","username": "admin", "password": "admin"},
        "TDR-1": {"device_type": "cisco_ios","ip": "192.168.0.1","username": "admin", "password": "admin"},
        "TDR-2": {"device_type": "cisco_ios","ip": "10.10.10.10","username": "admin", "password": "admin"},
        "Edge": {"device_type": "cisco_ios","ip": "10.10.10.1","username": "admin", "password": "admin"},
        "ISP": {"device_type": "cisco_ios","ip": "20.20.30.1","username": "admin", "password": "admin"}
    }

    command_to_send = "show cdp neighbors"
    
    result_dict = {}

    for device_name, device_info in devices.items():
        parsed_data = send_command(device_info, command_to_send)
        
        # Convert parsed data to a list of dictionaries with named fields
        entries = []
        for entry in parsed_data:
            entry_dict = {
                "Name": entry[0],
                "Local Interface": entry[1],
                "Tipo": entry[2],
                "Modelo": entry[3],
                "Interfaz Siguiente": entry[4],
                "Link":"http://localhost:5000/routes/"+ entry[0]
            }
            entries.append(entry_dict)
        
        result_dict[device_name] = entries

    # Convert the result dictionary to JSON
    json_result = json.dumps(result_dict, indent=4)
    return result_dict

