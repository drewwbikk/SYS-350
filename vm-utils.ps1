# Storyline: view VM list and details of VMs, as well as modify specific VMs and their attributes

function menu() {

    # Print menu options
    Write-Host "[1] List VMs by name"
    Write-Host "[2] View VM details"
    Write-Host "[3] VM actions"
    Write-Host "[0] Quit the program"

}

function vm_actions_menu() {
    
    # Print vm action menu options
    Write-Host "[1] Power on"
    Write-Host "[2] Power off"
    Write-Host "[3] Take a snapshot (checkpoint)"
    Write-Host "[4] Restore latest snapshot (checkpoint)"
    Write-Host "[5] Change num CPU"
    Write-Host "[6] Change the network"
    Write-Host "[0] Go back"

}

cls
menu

# Prompt the user for the menu choice
$readStatus = Read-Host -Prompt "Enter option value"

while ($readStatus -ne 0) {

    if ($readStatus -match 1) {
        
        # List VMs by name
        $filter = Read-Host -Prompt "Enter a filter for your VM"
        $vms = Get-VM | where{ $_.Name -match $filter}
        Write-Host "`n"
        foreach ($vm  in $vms) {
        
            Write-Host "VM Name: `t" $vm.Name 
            if ($vm.State -eq "Running") {
                Write-Host "Power State: On"
            }
            else {
                Write-Host "Power State: Off"
            }
            if ($vm.NetworkAdapters.IPAddresses) {
                $ips = $vm.NetworkAdapters.IPAddresses.Split(" ")
                Write-Host "IP Address: " $ips[0]
            }
            Write-Host "`n"
        }

    } elseif ($readStatus -match 2) {

        # View VM details
        $filter = Read-Host -Prompt "Enter the VM name"
        $vm = Get-VM | where{ $_.Name -eq $filter}
        if ($vm) {

            Write-Host "`n"
            
            # Name
            Write-Host "Name: `t`t " $vm.Name

            # Num CPUs
            Write-Host "Num of CPUs: " $vm.ProcessorCount

            # Memory (GB)
            $vmMem = $vm.MemoryAssigned/1073741824
            Write-Host "Memory: `t " $vmMem "GB"

            # Storage (GB)
            $vmDisk = $vm.HardDrives | Get-VHD
            $vmStorage = $vmDisk.Size/1073741824
            Write-Host "Storage: `t " $vmStorage "GB"

            # Uptime
            Write-Host "Uptime: `t " $vm.Uptime

            # CPU Usage
            Write-Host "CPU Usage: `t " $vm.CPUUsage "%"

            Write-Host "`n"

        } else {

            Write-Host -ForegroundColor red "No VM exists with name" $filter
            sleep 1
        }

    } elseif ($readStatus -match 3) {

        # VM actions
        $filter = Read-Host -Prompt "Enter a filter for your VM"
        $vms = Get-VM | where{ $_.Name -match $filter}
        Write-Host "Selected VMs:"
        foreach ($vm  in $vms) {Write-Host $vm.Name}
        
        vm_actions_menu
        $option = Read-Host -Prompt "Enter option value"

        while ($option -ne 0) {

            if ($option -eq 1) {

                # Power on
                foreach ($vm in $vms) {

                    Start-VM -VM $vm

                }

            } elseif ($option -eq 2) {

                # Power off
                foreach ($vm in $vms) {

                    Stop-VM -VM $vm

                }

            } elseif ($option -eq 3) {

                # Take snapshot
                foreach ($vm in $vms) {

                    $snapshotName = Read-Host -Prompt "Snapshot name"
                    Checkpoint-VM -VM $vm -SnapshotName $snapshotName

                }
            
            } elseif ($option -eq 4) {

                # Restore snapshot
                foreach ($vm in $vms) {

                    Get-VMSnapshot -VM $vm | Sort CreationTime | Select -Last 1 | Restore-VMSnapshot

                }
            
            } elseif ($option -eq 5) {

                # Change num CPU
                foreach ($vm in $vms) {

                    $vmName = $vm.Name
                    if ($vm.State -eq "Off") {

                        Write-Host "Current num of CPUs for $vmName : " $vm.ProcessorCount

                        $newCPU = Read-Host -Prompt "Enter the new num CPU for $vmName"

                        Set-VMProcessor -VM $vm -Count $newCPU
                     
                    } else {

                        Write-Host -ForegroundColor yellow "$vmName is not powered off! Skipping..."

                    }

                }
            
            } elseif ($option -eq 6) {

                # Change network
                foreach ($vm in $vms) {

                    $vmName = $vm.Name
                    Write-Host "The following networks are available: "
                    $switches = Get-VMSwitch
                    $i = 1
                    foreach ($switch in $switches) {

                        Write-Host "[$i]" $switch.Name
                        $i += 1
                    }

                    $newSwitch = Read-Host -Prompt "Which network for $vmName"

                    Get-VMNetworkAdapter -VM $vm | Connect-VMNetworkAdapter -VMSwitch $switches[$newSwitch-1]

                }

            } else {

                # Warn user if invalid input is entered
                Write-Host -ForegroundColor red "Invalid option."
                sleep 1

            }

            vm_actions_menu

            # Prompt the user for the menu choice
            $option = Read-Host -Prompt "Enter option value"

        }

    } else {

        # Warn user if invalid input is entered
        Write-Host -ForegroundColor red "Invalid option."
        sleep 1

    }

    menu

    # Prompt the user for the menu choice
    $readStatus = Read-Host -Prompt "Enter option value"

}