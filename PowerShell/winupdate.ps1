# This script was built to update the OS that are having issues reaching the Update Servers
# Script will pull from awsconfigrepo for kb files
# Built by CloudOps
# Chris Kallinen

# Get the OS Version
$osv = Get-CimInstance Win32_OperatingSystem

# Determining Version of OS
switch -wildcard ($osv) {
    "*10*" { 
        Write-Host "Win10"
        $vers = '10/'
    }
    "*2012*" {
        Write-Host "WinServ2012R2"
        $vers = '20112R2/'
    }
    "*2016*" {
        Write-Host "WinServ2016"
        $vers = '2016/'
    }
    "*2019*" {
        Write-Host "WinServ2019"
        $vers = '2019/'
    }
    Default { Write-Host "OS Not Valid" break}
}

# Source for KB Files
$url = 'http://url/windows/patch/' + $vers
# Location to save too
$dir = 'c:\updates\'

# Getting file list from server
$cache = Invoke-WebRequest $url -UseBasicParsing
$filetype = 'msu', 'cab'
$KBArrayList = New-Object -TypeName System.Collections.ArrayList 

# Download Command
$wc = New-Object System.Net.WebClient

# Check for Directory
if (-not (Test-Path $dir)) {
    New-Item -Path $dir -ItemType Directory
}

# Get the List of KB from files at awsconfigrepo
foreach($type in $filetype){
    $file = ($cache.Links |Where-Object{$_.href -match $type}).href
    foreach($kbfind in $file){
        Write-Host $kbfind
        $write = $kbfind | Select-String -Pattern 'kb\d{7}' -Allmatches | ForEach-Object {$_.matches.value}
        # Write-Host $write
        $KBArrayList += $write
    }
}

Write-Host "Checking for the following KB and installing the missing:"
Write-Host $KBArrayList

foreach($kb in $KBArrayList) {
    if (-not(Get-HotFix -Id $kb)){
        # Find match kb to download link
        $filename = ($cache.Links | Where-Object{$_.href -match $kb}).href
        Write-Host "Installating $kb"
        # Write-host $filename
        $wc.DownloadFile($url + $filename, $dir + $filename)
        try {
            Start-Process -FilePath "wusa.exe" -ArgumentList "$dir$filename /quiet /norestart" -Wait
        }
        catch {
            Write-Host -ForegroundColor Red -BackgroundColor Black "Installation Failed"
            Write-Host -ForegroundColor Red -BackgroundColor Black "Please note $kb either try to re-run this script or contact CloudOps Team"
            Write-Host -ForegroundColor Red -BackgroundColor Black "Location: $url"
        }
        
    } else {
        Write-Host -ForegroundColor Green -BackgroundColor Black "Update found and Installed: $kb"
    }
}

