"""
LangChain Tools for TripMate Agents
Wraps each specialized agent as a LangChain Tool for orchestration
"""

from langchain.tools import Tool, StructuredTool
from pydantic import BaseModel, Field
from typing import Optional, List
import json


class FlightSearchInput(BaseModel):
    """Input schema for flight search"""
    query: str = Field(description="User query containing origin, destination, dates, and preferences")


class HotelSearchInput(BaseModel):
    """Input schema for hotel search"""
    query: str = Field(description="User query containing destination, dates, budget, and interests")


class ActivitySearchInput(BaseModel):
    """Input schema for activity search"""
    query: str = Field(description="User query containing destination, interests, and budget")


class DestinationSuggestInput(BaseModel):
    """Input schema for destination suggestions"""
    query: str = Field(description="User query containing budget, duration, and interests")


class LocalEventsInput(BaseModel):
    """Input schema for local events search"""
    query: str = Field(description="User query containing destination and travel dates")


def create_flight_tool(flight_agent):
    """
    Creates a LangChain tool for flight search
    """
    def search_flights(query: str) -> str:
        """
        Search for flights based on user requirements.
        Returns 3 flight options: Cheapest, Fastest, and Best Overall.
        """
        try:
            result = flight_agent.handle_request(query)
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Flight search error: {str(e)}"
    
    return Tool(
        name="FlightPlanner",
        description="Plan flights using Amadeus API. Use this when user asks about flights, airfare, or how to get to destination. Returns 3 options: Cheapest, Fastest, Best Overall with real prices.",
        func=search_flights
    )


def create_hotel_tool(stays_agent):
    """
    Creates a LangChain tool for hotel search
    """
    def search_hotels(query: str) -> str:
        """
        Search for hotels based on destination, budget, and user interests.
        Returns 3-5 hotel recommendations at different price tiers.
        """
        try:
            result = stays_agent.handle_request(query)
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Hotel search error: {str(e)}"
    
    return Tool(
        name="HotelPlanner",
        description="Plan hotels and accommodations. Use this when user asks about where to stay, hotels, or accommodation. Returns budget-aware recommendations matching user interests.",
        func=search_hotels
    )


def create_activities_tool(activities_agent):
    """
    Creates a LangChain tool for activities search
    """
    def search_activities(query: str) -> str:
        """
        Search for activities, tours, and experiences based on destination and interests.
        Returns curated activity recommendations.
        """
        try:
            result = activities_agent.handle_request(query)
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Activities search error: {str(e)}"
    
    return Tool(
        name="ActivityRecommender",
        description="Recommend activities, tours, and experiences. Use this when user asks what to do, things to see, or experiences at destination. Returns interest-based activity recommendations.",
        func=search_activities
    )


def create_destination_tool(destination_agent):
    """
    Creates a LangChain tool for destination suggestions
    """
    def suggest_destinations(query: str) -> str:
        """
        Suggest travel destinations based on budget, duration, and interests.
        Returns 3 destination recommendations.
        """
        try:
            result = destination_agent.handle_request(query)
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Destination suggestion error: {str(e)}"
    
    return Tool(
        name="DestinationRecommender",
        description="Recommend travel destinations. Use this when user hasn't specified a destination or asks where to go. Returns personalized destination recommendations based on budget and interests.",
        func=suggest_destinations
    )


def create_local_events_tool(local_events_agent):
    """
    Creates a LangChain tool for local events discovery - UNIQUE FEATURE
    """
    def discover_events(query: str) -> str:
        """
        Discover local events, festivals, markets, and cultural happenings during travel dates.
        This is a UNIQUE feature not available in other travel AI tools.
        """
        try:
            result = local_events_agent.handle_request(query)
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Local events error: {str(e)}"
    
    return Tool(
        name="LocalEventsDiscoverer",
        description="Discover local events, festivals, concerts, and cultural happenings during travel dates. UNIQUE FEATURE. Use this to find what's happening at the destination during the trip dates. Returns real events, markets, festivals.",
        func=discover_events
    )


def create_all_tools(flight_agent, stays_agent, activities_agent, destination_agent, local_events_agent):
    """
    Creates all LangChain tools for the orchestrator
    """
    return [
        create_flight_tool(flight_agent),
        create_hotel_tool(stays_agent),
        create_activities_tool(activities_agent),
        create_destination_tool(destination_agent),
        create_local_events_tool(local_events_agent)
    ]
