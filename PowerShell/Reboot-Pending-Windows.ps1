# this script is to confirm if OS is pending for reboot

# Check registry
# RebootPending HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing
# RebootRequired HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update
# PendingFileRenameOperations HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager

$reboot = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending"
$required = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired"

if ($required) {
    $return = $true
    Write-Output "True required"
} else {
    if($reboot){
        $return = $true
        Write-Output "True reboot"
    } else {
        $return = $false
        Write-Output "False NoReboot"
    }
}

Write-Host "test" -NoNewline

# Return values
Write-Output "reboot:" $return