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
    print("[3] - VM Actions")
    print("[0] - Quit the program")

def vm_actions_menu():
    print("[1] - Power On")
    print("[2] - Power Off")
    print("[3] - Take a Snapshot")
    print("[4] - Revert to Latest Snapshot")
    print("[5] - Change VM Specs")
    print("[6] - Change the Network")
    print("[0] - Main Menu")

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
                    print("VM Name: " + str(child.summary.config.name)) # Print the name
                    if child.summary.runtime.powerState == "poweredOn": # determine power state
                        print("Power State: On") # Print powered on
                    else:
                        print("Power State: Off") # Print powered off
                    print("Memory (GB): " + str((child.summary.config.memorySizeMB / 1024))) # Print memory
                    print("Num CPU: " + str(child.summary.config.numCpu)) # Print num CPU
                    print("IP Address: " + str(child.summary.guest.ipAddress)) # Print IP address
                    print()

    elif option == 3:
        # VM Actions
        action_filter = input("Enter a filter for your vm: ")

        # Get VMs
        action_container = si.content.rootFolder
        action_view_type = [vim.VirtualMachine]
        action_recursive = True
        obj_view = si.content.viewManager.CreateContainerView(action_container, action_view_type, action_recursive)
        vm_list = obj_view.view
        obj_view.Destroy()

        # Get networks
        action_view_type = [vim.Network]
        obj_view = si.content.viewManager.CreateContainerView(action_container, action_view_type, action_recursive)
        network_list = obj_view.view
        obj_view.Destroy()

        print("Selected VMs: ")
        for vm in vm_list:
            if action_filter in vm.summary.config.name: # filter by vm name
                print(vm.summary.config.name)
        print()

        vm_actions_menu()
        action_option = int(input("Enter option value: "))

        while action_option != 0:
            if action_option == 1:
                # Power on
                # Found PowerOn() and try/except from https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/vm_power_on.py 
                for vm in vm_list:
                    name = str(vm.summary.config.name)
                    if action_filter in name:
                        if vm.summary.config.template == False:
                            if vm.summary.runtime.powerState == "poweredOff":
                                try:
                                    vm.PowerOn()
                                    print(name + " is powering on.")
                                except Exception as error:
                                    print("Caught Exception : " + str(error))
                            else: 
                                print(name + " is already on.")
                        else:
                            print(name + " is a template - skipping.")

            elif action_option == 2:
                # Power off
                for vm in vm_list:
                    name = str(vm.summary.config.name)
                    if action_filter in name:
                        if vm.summary.config.template == False:
                            if vm.summary.runtime.powerState == "poweredOn":
                                try:
                                    vm.PowerOff()
                                    print(name + " is powering off.")
                                except Exception as error:
                                    print("Caught Exception : " + str(error))
                            else: 
                                print(name + " is already off.")
                        else:
                            print(name + " is a template - skipping.")

            elif action_option == 3:
                # Take snapshot
                # Inspired by https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/snapshot_operations.py 
                for vm in vm_list:
                    name = str(vm.summary.config.name)
                    if action_filter in name:
                        if vm.summary.config.template == False:
                            snapshot_name = input("Snapshot name: ")
                            snapshot_desc = input("Snapshot description: ")
                            dump_memory = False
                            quiesce = False
                            print("Creating snapshot " + snapshot_name + " on " + name)
                            vm.CreateSnapshot(snapshot_name, snapshot_desc, dump_memory, quiesce)
                        else:
                            print(name + " is a template - skipping.")

            elif action_option == 4:
                # Revert to latest snapshot
                # Inspired by https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/snapshot_operations.py 
                # Attributes from https://vdc-repo.vmware.com/vmwb-repository/dcr-public/9fd87c06-14a3-41e5-b28d-277864a80f29/d6112c2a-b124-4fa5-96d7-9fb4b6f1bb50/doc/vim.vm.SnapshotTree.html#field_detail 
                for vm in vm_list:
                    name = str(vm.summary.config.name)
                    if action_filter in name:
                        if vm.summary.config.template == False:
                            if vm.snapshot.rootSnapshotList[0]:
                                snapshot_name = str(vm.snapshot.rootSnapshotList[0].name)
                                snapshot = vm.snapshot.rootSnapshotList[0].snapshot
                                print("Reverting to snapshot " + snapshot_name + " on " + name)
                                snapshot.RevertToSnapshot_Task()
                            else: 
                                print("No snapshots exist for " + name)
                        else:
                            print(name + " is a template - skipping.")

            elif action_option == 5:
                # Change VM specs
                # Inspired by https://github.com/vmware/pyvmomi-community-samples/issues/265 
                for vm in vm_list:
                    name = str(vm.summary.config.name)
                    if action_filter in name:
                        if vm.summary.config.template == False:
                            if vm.summary.runtime.powerState == "poweredOff":
                                print("Current VM Specs: ")
                                print("Num CPU: " + str(vm.summary.config.numCpu)) # Print num CPU
                                print("Memory (GB): " + str((vm.summary.config.memorySizeMB / 1024))) # Print memory
                                spec = vim.vm.ConfigSpec()
                                spec.numCPUs = int(input("Enter the new num CPU: "))
                                spec.memoryMB = int(input("Enter the new memory (GB): ")) * 1024
                                print("Reconfiguring " + name)
                                vm.Reconfigure(spec)
                            else:
                                print(name + " is powered on - skipping.")
                        else:
                            print(name + " is a template - skipping.")

            elif action_option == 6:
                # Change network
                # Inspired by https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/change_vm_vif.py 
                for vm in vm_list:
                    name = str(vm.summary.config.name)
                    if action_filter in name:
                        if vm.summary.config.template == False:
                            device_change = []
                            for device in vm.config.hardware.device:
                                if isinstance(device, vim.vm.device.VirtualEthernetCard):
                                    nic_spec = vim.vm.device.VirtualDeviceSpec()
                                    nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
                                    nic_spec.device = device
                                    nic_spec.device.wakeOnLanEnabled = True
                                    nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
                                    network_select = True
                                    while network_select:
                                        print("The following networks are available: ")
                                        i = 1
                                        for network in network_list:
                                            print("[" + str(i) + "] " + str(network.name))
                                            i += 1
                                        try: 
                                            network_option = int(input("Which network for " + name + "?: "))
                                            nic_spec.device.backing.network = network_list[network_option-1]
                                            nic_spec.device.backing.deviceName = network_list[network_option-1].name
                                            network_select = False
                                        except Exception:
                                            print("Invalid option.")
                                    nic_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
                                    nic_spec.device.connectable.startConnected = True
                                    nic_spec.device.connectable.allowGuestControl = True
                                    device_change.append(nic_spec)
                                    break
                            
                            config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
                            vm.ReconfigVM_Task(config_spec)
                            print("Successfully changed network")

                        else:
                            print(name + " is a template - skipping.")

            else:
                print("Invalid option.")
            
            print()
            vm_actions_menu()
            action_option = int(input("Enter option value: "))

    else:
        print("Invalid option.")
    
    print()
    menu()
    option = int(input("Enter option value: "))

print("Exiting...")
Disconnect(si)