$services = @(
    @{ Name = 'avatar';        Url = 'http://localhost:8081/health' },
    @{ Name = 'configuration'; Url = 'http://localhost:8082/health' },
    @{ Name = 'essays';        Url = 'http://localhost:8083/health' },
    @{ Name = 'questions';     Url = 'http://localhost:8084/health' },
    @{ Name = 'upskilling';    Url = 'http://localhost:8085/health' },
    @{ Name = 'chat';          Url = 'http://localhost:8086/health' },
    @{ Name = 'evaluation';    Url = 'http://localhost:8087/health' },
    @{ Name = 'lms-gateway';   Url = 'http://localhost:8088/health' },
    @{ Name = 'insights';      Url = 'http://localhost:8089/health' }
)

$results = foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 3
        [pscustomobject]@{
            Service = $service.Name
            Url = $service.Url
            Status = $response.StatusCode
        }
    }
    catch {
        [pscustomobject]@{
            Service = $service.Name
            Url = $service.Url
            Status = 'Unavailable'
        }
    }
}

$results | Format-Table -AutoSize
