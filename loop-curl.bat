## This script is used to continuously call the LLM API endpoints for generating traffic from all four endpoints.
while ($true) {
    try {
        $response1 = Invoke-WebRequest -Uri "http://localhost:8001/generate" -UseBasicParsing
        $response2 = Invoke-WebRequest -Uri "http://localhost:8002/generate" -UseBasicParsing
        $response3 = Invoke-WebRequest -Uri "http://localhost:8003/generate" -UseBasicParsing
        $response4 = Invoke-WebRequest -Uri "http://localhost:8004/generate" -UseBasicParsing

        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Output "$timestamp - Status Code: $($response.StatusCode), Response: $($response.Content)"
    } catch {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Output "$timestamp - Error: $_"
    }

    Start-Sleep -Seconds 2
}
