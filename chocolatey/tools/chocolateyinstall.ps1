$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$exePath    = Join-Path $toolsDir 'boosty-milker.exe'

Install-BinFile -Name 'boosty-milker' -Path $exePath
