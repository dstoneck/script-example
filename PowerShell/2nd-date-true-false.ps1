# this script is to determine if the date is true or false if past the targeted date

# Example 2nd-date-true=false.ps1 -find 2 -weekday Tuesday -date 10/20/2024

Param (
        [Parameter(Mandatory=$true)][ValidateSet("First","Second","Third","Fourth","Last","1","2","3","4","5")][string]$find,
        [Parameter(Mandatory=$true)][ValidateSet("Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday")][string]$weekday,
        [Parameter(Mandatory=$true)][datetime]$date
    )
switch($find) 
    { 
        "First" { $intFind = 1 }
        "Second" { $intFind = 2 }
        "Third" { $intFind = 3 }
        "Fourth" { $intFind = 4 }
        "Last" { $intFind = 5 }
        default { $intFind = [int]$Find }
    }
# Function to find target date
function find-datetarget ([int]$year, [int]$month, [string]$weekdate, [int]$intFind) {
    
    $allDays = @()
    0..31 | ForEach-Object -Process {            
        $evaldate = (Get-Date -Year $year -Month $month -Day 1).AddDays($_)        
        if ($evaldate.Month -eq $month)         
        {
            if ($evaldate.DayOfWeek -eq $weekdate) { 
                $allDays += $evaldate  
            }            
        }            
    }
    if ($allDays.Count -lt $intFind) {$intFind = $intFind-1}
    $allDays[$($intFind-1)]
    Return
}

$output = find-datetarget $date.Year $date.Month $weekday $intFind

switch ($intFind) {
    1 { $di = "1st" }
    2 { $di = "2nd" }
    3 { $di = "3rd" }
    4 { $di = "4th" }
    5 { $di = "5th" }
    Default { $di = "error"}
}

if ($date.day -ge $output.day) {
    Write-Host -ForegroundColor Green "The date ($date) is passed the $di $weekday of the month"
} else {
    Write-Host -ForegroundColor Red "The date ($date) is not passed the $di $weekday of the month"
}

