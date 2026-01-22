$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$exePath    = Join-Path $toolsDir 'boosty-dl.exe'

Install-BinFile -Name 'boosty-dl' -Path $exePath
