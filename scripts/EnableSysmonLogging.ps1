# Set Variables
$url = "https://download.sysinternals.com/files/Sysmon.zip"
$outputPath = "C:\Program Files (X86)\ossec-agent\active-response\Sysmon\Sysmon.zip"
$extractPath = "C:\Program Files (X86)\ossec-agent\active-response\Sysmon"
$configUrl = "https://staging.coldwatercorp.co.za/cdn0/sys_mon__config___.x_m_l"
$configPath = "$extractPath\sysmonconfig.xml"

# Install Sysmon
New-Item -ItemType Directory -Path $extractPath
Invoke-WebRequest -Uri $url -OutFile $outputPath
Expand-Archive -Path $outputPath -DestinationPath $extractPath
Remove-Item -Path $outputPath -Force
wget -Uri $configUrl -OutFile $configPath
& "$extractPath\Sysmon64.exe" -accepteula -i $configPath
cd $extractPath
& "Sysmom64.exe" -accepteula -i sysmonconfig.xml