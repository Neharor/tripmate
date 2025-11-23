"""
Flight Ranking Service - Determines "best" flights based on multiple criteria
"""
import re
from datetime import datetime, timedelta

class FlightRanker:
    """
    Ranks flights based on weighted scoring system:
    - Price (40%)
    - Duration (25%)
    - Departure time preference (15%)
    - Stops (10%)
    - Airline reputation (10%)
    """
    
    # Airline quality ratings (based on Skytrax, AirlineRatings.com)
    AIRLINE_RATINGS = {
        # 5-Star Airlines
        'Singapore Airlines': 5, 'Qatar Airways': 5, 'ANA': 5, 'Cathay Pacific': 5,
        'JAL': 5, 'Emirates': 5, 'Hainan Airlines': 5,
        
        # 4-Star Airlines  
        'Lufthansa': 4, 'Thai Airways': 4, 'Korean Air': 4, 'Asiana Airlines': 4,
        'British Airways': 4, 'Air France': 4, 'KLM': 4, 'Virgin Atlantic': 4,
        'Turkish Airlines': 4, 'EVA Air': 4,
        
        # 3-Star Airlines
        'United': 3, 'American Airlines': 3, 'Delta': 3, 'Air Canada': 3,
        'Air India': 3, 'Garuda Indonesia': 3, 'China Airlines': 3,
        
        # Budget Airlines (2-Star)
        'AirAsia': 2, 'Lion Air': 2, 'Jeju Air': 2, 'Scoot': 2, 
        'Jetstar': 2, 'Peach': 2, 'VietJet': 2
    }
    
    def __init__(self):
        self.weights = {
            'price': 0.40,
            'duration': 0.25,
            'time_preference': 0.15,
            'stops': 0.10,
            'airline_rating': 0.10
        }
    
    def rank_flights(self, flights, user_preferences=None):
        """
        Rank flights and return sorted list with scores and reasoning
        
        Args:
            flights: List of flight dicts
            user_preferences: Dict with 'budget_max', 'time_pref', 'priority' (price/comfort/speed)
        
        Returns:
            List of flights with added 'score', 'rank', 'pros', 'cons'
        """
        if not flights:
            return []
        
        preferences = user_preferences or {}
        
        # Adjust weights based on user priority
        if preferences.get('priority') == 'price':
            self.weights = {'price': 0.60, 'duration': 0.15, 'time_preference': 0.10, 'stops': 0.10, 'airline_rating': 0.05}
        elif preferences.get('priority') == 'comfort':
            self.weights = {'price': 0.20, 'duration': 0.20, 'time_preference': 0.15, 'stops': 0.15, 'airline_rating': 0.30}
        elif preferences.get('priority') == 'speed':
            self.weights = {'price': 0.25, 'duration': 0.50, 'time_preference': 0.10, 'stops': 0.15, 'airline_rating': 0.00}
        
        # Score each flight
        scored_flights = []
        for flight in flights:
            score_breakdown = self._calculate_score(flight, flights, preferences)
            flight['score'] = score_breakdown['total']
            flight['score_breakdown'] = score_breakdown
            flight['pros'], flight['cons'] = self._generate_pros_cons(flight, flights, preferences)
            scored_flights.append(flight)
        
        # Sort by score (highest first)
        scored_flights.sort(key=lambda x: x['score'], reverse=True)
        
        # Assign ranks
        for i, flight in enumerate(scored_flights):
            flight['rank'] = i + 1
            if i == 0:
                flight['badge'] = '🥇 Best Overall'
            elif flight.get('price_round_trip', 999999) == min(f.get('price_round_trip', 999999) for f in flights):
                flight['badge'] = '💰 Cheapest'
            elif self._parse_duration(flight.get('duration', '')) == min(self._parse_duration(f.get('duration', '')) for f in flights):
                flight['badge'] = '⚡ Fastest'
            elif self.AIRLINE_RATINGS.get(flight.get('airline', ''), 0) >= 5:
                flight['badge'] = '⭐ Premium'
        
        return scored_flights
    
    def _calculate_score(self, flight, all_flights, preferences):
        """Calculate weighted score for a flight"""
        scores = {}
        
        # 1. Price Score (lower is better)
        prices = [f.get('price_round_trip', 0) for f in all_flights if f.get('price_round_trip', 0) > 0]
        if prices and flight.get('price_round_trip'):
            min_price = min(prices)
            max_price = max(prices)
            if max_price > min_price:
                # Invert: cheaper = higher score
                scores['price'] = 100 * (1 - (flight['price_round_trip'] - min_price) / (max_price - min_price))
            else:
                scores['price'] = 100
        else:
            scores['price'] = 50
        
        # 2. Duration Score (shorter is better)
        durations = [self._parse_duration(f.get('duration', '')) for f in all_flights]
        durations = [d for d in durations if d > 0]
        flight_duration = self._parse_duration(flight.get('duration', ''))
        
        if durations and flight_duration > 0:
            min_duration = min(durations)
            max_duration = max(durations)
            if max_duration > min_duration:
                scores['duration'] = 100 * (1 - (flight_duration - min_duration) / (max_duration - min_duration))
            else:
                scores['duration'] = 100
        else:
            scores['duration'] = 50
        
        # 3. Time Preference Score
        time_pref = preferences.get('time_pref', 'anytime').lower()
        departure_time = flight.get('departure_time', '')
        scores['time_preference'] = self._score_departure_time(departure_time, time_pref)
        
        # 4. Stops Score (non-stop is best)
        stops = flight.get('stops', 0)
        if stops == 0:
            scores['stops'] = 100
        elif stops == 1:
            scores['stops'] = 60
        else:
            scores['stops'] = 30
        
        # 5. Airline Rating Score
        airline = flight.get('airline', '')
        rating = self.AIRLINE_RATINGS.get(airline, 3)
        scores['airline_rating'] = (rating / 5) * 100
        
        # Calculate weighted total
        total = sum(scores[key] * self.weights[key] for key in scores)
        
        return {
            'total': round(total, 1),
            'price': round(scores['price'], 1),
            'duration': round(scores['duration'], 1),
            'time_preference': round(scores['time_preference'], 1),
            'stops': round(scores['stops'], 1),
            'airline_rating': round(scores['airline_rating'], 1)
        }
    
    def _score_departure_time(self, departure_str, preference):
        """Score based on time preference"""
        if preference == 'anytime':
            return 100
        
        # Extract hour from "08:00 AM" format
        match = re.search(r'(\d{1,2}):(\d{2})\s*(AM|PM)', departure_str, re.IGNORECASE)
        if not match:
            return 50
        
        hour = int(match.group(1))
        meridiem = match.group(3).upper()
        
        # Convert to 24-hour
        if meridiem == 'PM' and hour != 12:
            hour += 12
        elif meridiem == 'AM' and hour == 12:
            hour = 0
        
        # Score based on preference
        if preference == 'morning':  # 6am-11am
            if 6 <= hour < 12:
                return 100
            elif 12 <= hour < 14:
                return 70  # Early afternoon ok
            else:
                return 40
        
        elif preference == 'afternoon':  # 12pm-5pm
            if 12 <= hour < 17:
                return 100
            elif 10 <= hour < 12 or 17 <= hour < 19:
                return 70
            else:
                return 40
        
        elif preference == 'evening':  # 6pm-11pm
            if 18 <= hour < 24:
                return 100
            elif 16 <= hour < 18:
                return 70
            else:
                return 40
        
        return 50
    
    def _parse_duration(self, duration_str):
        """Parse '10h 20m' into minutes"""
        if not duration_str:
            return 0
        
        hours = 0
        minutes = 0
        
        hour_match = re.search(r'(\d+)h', duration_str)
        if hour_match:
            hours = int(hour_match.group(1))
        
        min_match = re.search(r'(\d+)m', duration_str)
        if min_match:
            minutes = int(min_match.group(1))
        
        return hours * 60 + minutes
    
    def _generate_pros_cons(self, flight, all_flights, preferences):
        """Generate human-readable pros and cons"""
        pros = []
        cons = []
        
        price = flight.get('price_round_trip', 0)
        duration_min = self._parse_duration(flight.get('duration', ''))
        stops = flight.get('stops', 0)
        airline = flight.get('airline', '')
        rating = self.AIRLINE_RATINGS.get(airline, 3)
        
        # Price analysis
        prices = [f.get('price_round_trip', 0) for f in all_flights if f.get('price_round_trip', 0) > 0]
        if prices:
            min_price = min(prices)
            avg_price = sum(prices) / len(prices)
            
            if price == min_price:
                pros.append(f"Cheapest option (${price})")
            elif price <= avg_price * 1.1:
                pros.append(f"Competitive price (${price})")
            else:
                cons.append(f"${price - min_price} more than cheapest")
        
        # Duration analysis
        durations = [self._parse_duration(f.get('duration', '')) for f in all_flights]
        durations = [d for d in durations if d > 0]
        if durations:
            min_duration = min(durations)
            if duration_min == min_duration:
                pros.append(f"Fastest flight ({flight.get('duration', '')})")
            elif duration_min <= min_duration * 1.1:
                pros.append(f"Quick flight time ({flight.get('duration', '')})")
        
        # Stops
        if stops == 0:
            pros.append("Direct flight (no layovers)")
        elif stops == 1:
            cons.append("1 layover (adds 2-4 hours)")
        else:
            cons.append(f"{stops} layovers (significantly longer)")
        
        # Airline quality
        if rating >= 5:
            pros.append(f"{airline} - 5-star airline (premium service)")
        elif rating >= 4:
            pros.append(f"{airline} - 4-star airline (excellent service)")
        elif rating <= 2:
            cons.append(f"Budget airline (basic amenities)")
        
        # Cabin class
        cabin = flight.get('cabin_class', 'Economy')
        if cabin == 'Premium Economy':
            pros.append("Premium Economy (extra legroom, priority boarding)")
        elif cabin == 'Business':
            pros.append("Business Class (lie-flat seats, lounge access)")
        
        # Budget check
        budget_max = preferences.get('budget_max', 0)
        if budget_max > 0 and price > budget_max:
            cons.append(f"${price - budget_max} over budget")
        
        return pros, cons
    
    def get_best_value_explanation(self, flights):
        """Generate explanation of why top flight is 'best'"""
        if not flights:
            return ""
        
        ranked = self.rank_flights(flights)
        best = ranked[0]
        
        explanation = f"""
**Why {best['airline']} {best.get('flight_number', '')} is ranked #1:**

**Score Breakdown** ({best['score']}/100):
• Price: {best['score_breakdown']['price']}/100 (${best.get('price_round_trip', 0)} round-trip)
• Duration: {best['score_breakdown']['duration']}/100 ({best.get('duration', 'N/A')})
• Schedule: {best['score_breakdown']['time_preference']}/100 (Departs {best.get('departure_time', '')})
• Stops: {best['score_breakdown']['stops']}/100 ({'Direct' if best.get('stops') == 0 else f"{best.get('stops')} stop(s)"})
• Airline: {best['score_breakdown']['airline_rating']}/100 ({best['airline']} - {self.AIRLINE_RATINGS.get(best['airline'], 3)}-star rated)

**Pros:**
{chr(10).join(f'✅ {pro}' for pro in best.get('pros', []))}

**Cons:**
{chr(10).join(f'⚠️ {con}' for con in best.get('cons', ['None'])) if best.get('cons') else '✅ None'}

**Comparison:**
"""
        
        # Compare with other options
        for i, flight in enumerate(ranked[1:3], 2):
            diff = best['score'] - flight['score']
            explanation += f"\n#{i}. {flight['airline']} scores {flight['score']}/100 ({diff:.1f} points lower)\n"
        
        return explanation.strip()
