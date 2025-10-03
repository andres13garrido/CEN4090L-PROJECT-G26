from mcp.server.fastmcp import FastMCP
from tools import GetWeather
# Create MCP server
mcp = FastMCP("Personal-Assistant")

# Register the tool
@mcp.tool()
async def weather(city: str):
    """Get weather for a city using the get_weather tool."""
    return await GetWeather.get_weather(city)

# Entry point to run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")