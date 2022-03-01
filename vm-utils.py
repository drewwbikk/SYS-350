import getpass
import json
from pyVim.connect import SmartConnect, Disconnect
import ssl
from pyVmomi import vim

# Read data from json file
with open('vm-utils.json', 'r') as f:
    vmutils=json.load(f)

# Initialize connection to vCenter
passw = getpass.getpass()
s=ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
s.verify_mode=ssl.CERT_NONE
si=SmartConnect(host=vmutils['vcenter_server'], user=vmutils['user'], pwd=passw, sslContext=s)

def menu():
    print("[1] - Login Info")
    print("[2] - List VMs by name")
    print("[0] - Quit the program")

menu()
option = int(input("Enter option value: "))

while option != 0:
    if option == 1:
        # Login Info
        # Inspired by https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/sessions_list.py
        print("You are logged into " + str(vmutils['vcenter_server']) \
            + " as " + str(si.content.sessionManager.currentSession.userName) \
            + " from " + str(si.content.sessionManager.currentSession.ipAddress))
    elif option == 2:
        # List VMs by name
        # Inspired by https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/getallvms.py 
        # Attributes found using https://vdc-repo.vmware.com/vmwb-repository/dcr-public/6b586ed2-655c-49d9-9029-bc416323cb22/fa0b429a-a695-4c11-b7d2-2cbc284049dc/doc/vim.vm.Summary.ConfigSummary.html 
        filter = input("Enter a filter for your vm: ")
        container = si.content.rootFolder
        view_type = [vim.VirtualMachine]
        recursive = True
        container_view = si.content.viewManager.CreateContainerView(container, view_type, recursive)

        children = container_view.view
        for child in children:
            if filter in child.summary.config.name: # filter by vm name
                if child.summary.config.template == False: # make sure its not a template
                    print("VM Name: " + child.summary.config.name) # Print the name
                    if child.summary.runtime.powerState == "poweredOn": # determine power state
                        print("Power State: On") # Print powered on
                    else:
                        print("Power State: Off") # Print powered off
                    print("Memory (GB): " + str((child.summary.config.memorySizeMB / 1024))) # Print memory
                    print("Num CPU: " + str(child.summary.config.numCpu)) # Print num CPU
                    print("IP Address: " + child.summary.guest.ipAddress) # Print IP address
                    print()

    else:
        print("Invalid option.")
    
    print()
    menu()
    option = int(input("Enter option value: "))

print("Exiting...")
Disconnect(si)