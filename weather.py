import requests
from rich.console import Console
from rich.panel import Panel

console = Console()

CITY_NAME = "Tallinn"
LATITUDE = 59.4370
LONGITUDE = 24.7536

WMO_CODES = {
    0:  ("Clear sky", "☀️"), 1: ("Mainly clear", "🌤️"), 2: ("Partly cloudy", "⛅"),
    3:  ("Overcast", "☁️"), 45: ("Foggy", "🌫️"), 48: ("Icy fog", "🌫️"),
    51: ("Light drizzle", "🌦️"), 53: ("Moderate drizzle", "🌦️"), 55: ("Dense drizzle", "🌧️"),
    61: ("Slight rain", "🌧️"), 63: ("Moderate rain", "🌧️"), 65: ("Heavy rain", "🌧️"),
    71: ("Slight snow", "🌨️"), 73: ("Moderate snow", "❄️"), 75: ("Heavy snow", "❄️"),
    80: ("Rain showers", "🌦️"), 95: ("Thunderstorm", "⛈️"),
}

def fetch_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": latitude, "longitude": longitude, "current": ["temperature_2m","apparent_temperature","relative_humidity_2m","wind_speed_10m","wind_direction_10m","weathercode"], "wind_speed_unit": "ms"}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def wind_direction_label(degrees):
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return directions[round(degrees / 45) % 8]

def build_display(data):
    current = data["current"]
    temperature = current["temperature_2m"]
    feels_like = current["apparent_temperature"]
    humidity = current["relative_humidity_2m"]
    wind_speed = current["wind_speed_10m"]
    wind_deg = current["wind_direction_10m"]
    weather_code = current["weathercode"]
    description, icon = WMO_CODES.get(weather_code, ("Unknown", "❓"))
    wind_dir = wind_direction_label(wind_deg)
    temp_color = "bold blue" if temperature < 0 else "bold cyan" if temperature < 15 else "bold green" if temperature < 25 else "bold red"
    lines = [f"{icon}  [bold white]{description}[/bold white]", "", f"[{temp_color}]Temperature:   {temperature:.1f} °C[/{temp_color}]", f"[dim]Feels like:    {feels_like:.1f} °C[/dim]", f"[cyan]Humidity:      {humidity} %[/cyan]", f"[yellow]Wind:          {wind_speed:.1f} m/s  {wind_dir}[/yellow]"]
    return Panel("\n".join(lines), title=f"[bold cyan]Weather in {CITY_NAME}[/bold cyan]", border_style="cyan", padding=(1, 2))

def main():
    console.print(f"\n[dim]Fetching weather for {CITY_NAME}...[/dim]\n")
    try:
        data = fetch_weather(LATITUDE, LONGITUDE)
        console.print(build_display(data))
        console.print()
    except requests.exceptions.ConnectionError:
        console.print("[red]Error: No internet connection.[/red]")
    except requests.exceptions.Timeout:
        console.print("[red]Error: The request timed out.[/red]")
    except requests.exceptions.HTTPError as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()
