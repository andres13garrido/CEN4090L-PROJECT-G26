from mcp.server.fastmcp import FastMCP
from tools import GetWeather
# Create MCP server
mcp = FastMCP("Weather-Demo")

# Register the tool
@mcp.tool()
async def weather(city: str):
    """Get weather for a city using the get_weather tool."""
    return await GetWeather.get_weather(city)

if __name__ == "__main__":
    mcp.run(transport="stdio")
