from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
import logging

class SharedData:
    def __init__(self):
        self.interfaces_state = {}

snmpEngine = engine.SnmpEngine()
TrapAgentAddress='192.168.0.10';
Port=162;
shared = SharedData()

logging.basicConfig(filename='traps_recibidas.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

def init_traps():
    print("El gestor esta escuchando SNMP Traps en "+TrapAgentAddress+" , Puerto : " +str(Port));
    config.addTransport(
        snmpEngine,
        udp.domainName + (1,),
        udp.UdpTransport().openServerMode((TrapAgentAddress, Port))
    )
    config.addV1System(snmpEngine, 'publica', 'publica')

def cbFun(snmpEngine, stateReference, contextEngineId, contextName,
          varBinds, cbCtx):
    print("Mensaje nuevo de traps recibido");
    logging.info("Mensaje nuevo de traps recibido")
    global shared
    trap_info = {}
    interfaz = None
    for name, val in varBinds:
        print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
        logging.info('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
        if name != "1.3.6.1.2.1.2.2.1.2.1":
            trap_info[name] = val
        else:
            interfaz = val
    shared.interfaces_state[interfaz] = trap_info
    logging.info("Fin del mensaje de la trampa")

def trap_lisener():
    ntfrcv.NotificationReceiver(snmpEngine, cbFun)
    snmpEngine.transportDispatcher.jobStarted(1)
    try:
        a = snmpEngine.transportDispatcher.runDispatcher()
        print(a)
    except:
        snmpEngine.transportDispatcher.closeDispatcher()
        raise

def start_trap():
    init_traps()
    trap_lisener()