from .base_agent import BaseAgent
import json
import os
import requests

class WeatherAgent(BaseAgent):
    """
    Specialized agent for weather insights and travel timing recommendations
    """
    def __init__(self):
        system_prompt = """You are a weather and travel timing expert AI agent. Your role is to:
1. Provide weather insights for destinations
2. Recommend best times to visit based on weather
3. Suggest what to pack based on climate
4. Warn about extreme weather conditions or seasons to avoid

Format your response as JSON with:
- best_months: array of recommended months to visit
- weather_considerations: key weather factors to consider
- packing_tips: what to pack for the climate
- current_conditions: brief current weather info if available

Be practical and seasonal-aware."""
        
        super().__init__("WeatherAgent", system_prompt)
        self.weather_api_key = os.getenv("WEATHER_API_KEY")

    def _get_weather_data(self, location):
        """
        Optional: Fetch real weather data if API key is available
        """
        if not self.weather_api_key or self.weather_api_key == "your-weather-api-key-here":
            return None
        
        try:
            # Example with OpenWeatherMap API
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.weather_api_key}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None

    def handle_request(self, input_data):
        """
        Process user query and return weather/timing recommendations
        """
        try:
            # Try to get real weather data
            weather_data = None
            # Simple location extraction (can be improved)
            words = str(input_data).split()
            for word in words:
                if len(word) > 3 and word[0].isupper():
                    weather_data = self._get_weather_data(word)
                    if weather_data:
                        break
            
            context = ""
            if weather_data:
                context = f"\nCurrent weather data available: {json.dumps(weather_data)}"
            
            user_prompt = f"""User Query: {input_data}{context}
            
Please provide weather insights and best time to visit recommendations."""

            llm_response = self._call_llm(user_prompt)
            
            try:
                weather_info = json.loads(llm_response)
                return {"weather_info": weather_info}
            except json.JSONDecodeError:
                pass
            
            return {
                "weather_info": llm_response
            }
            
        except Exception as e:
            print(f"WeatherAgent error: {str(e)}")
            return {
                "weather_info": f"Unable to generate weather insights. Error: {str(e)}"
            }
