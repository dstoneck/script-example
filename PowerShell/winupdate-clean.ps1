# Script to clean up the Windows Update Folders
$servicesstop = "wuauserv","cryptSvc","bits","msiserver"

function stopservice ($serv){
    try {
        $state = Get-Service -Name $serv
        if ($state.status -ne "Stopped") {
            Stop-Service -Name $serv
        }
    }
    catch {
        Write-Output "Failed to stop $serv"
        Exit 1
    }
}

# remove all in C:\Windows\SoftwareDistribution

$dirclear = "C:\Windows\SoftwareDistribution"

function clearfolder($dirclear){
    try {
        $files = Get-ChildItem -Path $dirclear -Recurse
        foreach ($i in $files){
            $i.Delete()
        }
        Write-Output "Cleared Windows Update Directory"
    }
    catch {
        Write-Output "Failed to clear Windows Update Folder"
    }
}


# Restart Services

function startservice ($serv){
    try {
        $state = Get-Service -Name $serv
        if ($state.status -eq "Stopped") {
            Stop-Service -Name $serv
        }
    }
    catch {
        Write-Output "Failed to start $serv"
        Exit 1
    }
}

# Reset Cache ren C:\Windows\SoftwareDistribution SoftwareDistribution.old
# ren C:\Windows\System32\catroot2 Catroot2.old