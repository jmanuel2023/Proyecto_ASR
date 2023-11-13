from flask import Flask, jsonify, request

app =  Flask(__name__)


#Users endpoints TODO: Implement funtionalities 
@app.route("/usuarios")
def get_usuarios():
    return "Hola"

@app.route("/usuarios", methods=["POST"])
def create_usuarios():
    return "Hola"

@app.route("/usuarios", methods=["PUT"])
def update_usuarios():
    return "Hola"

@app.route("/usuarios",methods=["DELETE"])
def delete_usuarios():
    return "Hola"


#Routes Endpoint TODO: Iplement get funtion
@app.route("/routes")
def get_routes():
    return "Hola"


#Routes Hostname Endpoint TODO: Iplement get funtion
@app.route("/routes/<hostname>")
def get_routes_hostname(hostname):
    return hostname

#Routes Hostname Interface Endpoint TODO: Iplement get funtion
@app.route("/routes/<hostname>/interfaces")
def get_routes_hostname_interface(hostname):
    return hostname+"interface"

#Crud users per router TODO: implement funtions
@app.route("/routes/<hostname>/usuarios")
def get_usuarios_router():
    return "Hola"

@app.route("/routes/<hostname>/usuarios", methods=["POST"])
def create_usuario_router():
    return "Hola"

@app.route("/routes/<hostname>/usuarios", methods=["PUT"])
def update_usuario_router():
    return "Hola"

@app.route("/routes/<hostname>/usuarios",methods=["DELETE"])
def delete_usuario_router():
    return "Hola"


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