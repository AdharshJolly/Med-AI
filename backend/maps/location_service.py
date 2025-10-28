"""
Google Maps Integration for MedAI-Pro
Find nearby hospitals, clinics, and medical facilities
"""

import googlemaps
from typing import Dict, List, Optional
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()


class LocationService:
    """Google Maps integration for finding medical facilities"""
    
    def __init__(self):
        api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
        
        if not api_key:
            logger.warning("⚠️ Google Maps API key not found. Set GOOGLE_MAPS_API_KEY in .env")
            self.gmaps = None
        else:
            try:
                self.gmaps = googlemaps.Client(key=api_key)
                logger.info("✅ Google Maps client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Google Maps: {e}")
                self.gmaps = None
        
        self.facility_types = {
            'hospital': 'hospital',
            'clinic': 'doctor',
            'pharmacy': 'pharmacy',
            'diagnostic': 'health',
            'emergency': 'hospital'
        }
    
    def find_nearby_facilities(
        self,
        location: str,
        facility_type: str = 'hospital',
        radius: int = 5000,
        max_results: int = 20
    ) -> List[Dict]:
        """Find nearby medical facilities"""
        
        if not self.gmaps:
            return self._get_mock_facilities(location)
        
        try:
            # Geocode location
            geocode_result = self.gmaps.geocode(location)
            
            if not geocode_result:
                logger.warning(f"Could not geocode location: {location}")
                return []
            
            lat_lng = geocode_result[0]['geometry']['location']
            
            # Search for places
            places_type = self.facility_types.get(facility_type, 'hospital')
            
            places_result = self.gmaps.places_nearby(
                location=lat_lng,
                radius=radius,
                type=places_type
            )
            
            facilities = []
            
            for place in places_result.get('results', [])[:max_results]:
                facility = self._parse_place(place)
                facilities.append(facility)
            
            logger.info(f"Found {len(facilities)} facilities near {location}")
            
            return facilities
        
        except Exception as e:
            logger.error(f"Error finding facilities: {e}")
            return []
    
    def get_facility_details(self, place_id: str) -> Dict:
        """Get detailed information about a facility"""
        
        if not self.gmaps:
            return {}
        
        try:
            place_details = self.gmaps.place(place_id)
            
            if place_details['status'] == 'OK':
                return self._parse_place_details(place_details['result'])
            
            return {}
        
        except Exception as e:
            logger.error(f"Error getting facility details: {e}")
            return {}
    
    def get_directions(
        self,
        origin: str,
        destination: str,
        mode: str = 'driving'
    ) -> Dict:
        """Get directions to a facility"""
        
        if not self.gmaps:
            return {}
        
        try:
            directions = self.gmaps.directions(
                origin,
                destination,
                mode=mode
            )
            
            if directions:
                route = directions[0]
                leg = route['legs'][0]
                
                return {
                    'distance': leg['distance']['text'],
                    'duration': leg['duration']['text'],
                    'steps': [step['html_instructions'] for step in leg['steps']],
                    'polyline': route['overview_polyline']['points']
                }
            
            return {}
        
        except Exception as e:
            logger.error(f"Error getting directions: {e}")
            return {}
    
    def _parse_place(self, place: Dict) -> Dict:
        """Parse Google Places API result"""
        
        location = place.get('geometry', {}).get('location', {})
        
        return {
            'place_id': place.get('place_id'),
            'name': place.get('name'),
            'address': place.get('vicinity'),
            'latitude': location.get('lat'),
            'longitude': location.get('lng'),
            'rating': place.get('rating'),
            'total_ratings': place.get('user_ratings_total'),
            'is_open': place.get('opening_hours', {}).get('open_now'),
            'types': place.get('types', []),
            'icon': place.get('icon')
        }
    
    def _parse_place_details(self, place: Dict) -> Dict:
        """Parse detailed place information"""
        
        location = place.get('geometry', {}).get('location', {})
        
        return {
            'place_id': place.get('place_id'),
            'name': place.get('name'),
            'address': place.get('formatted_address'),
            'phone': place.get('formatted_phone_number'),
            'website': place.get('website'),
            'latitude': location.get('lat'),
            'longitude': location.get('lng'),
            'rating': place.get('rating'),
            'total_ratings': place.get('user_ratings_total'),
            'reviews': place.get('reviews', [])[:5],
            'opening_hours': place.get('opening_hours', {}).get('weekday_text', []),
            'types': place.get('types', [])
        }
    
    def _get_mock_facilities(self, location: str) -> List[Dict]:
        """Return mock facilities when API is not available"""
        
        logger.info("Using mock facility data")
        
        return [
            {
                'place_id': 'mock_1',
                'name': 'City General Hospital',
                'address': f'123 Main St, {location}',
                'latitude': 28.6139,
                'longitude': 77.2090,
                'rating': 4.2,
                'total_ratings': 1250,
                'is_open': True,
                'types': ['hospital', 'health'],
                'phone': '+91-11-12345678',
                'has_emergency': True
            },
            {
                'place_id': 'mock_2',
                'name': 'Apollo Clinic',
                'address': f'456 Park Ave, {location}',
                'latitude': 28.6149,
                'longitude': 77.2100,
                'rating': 4.5,
                'total_ratings': 890,
                'is_open': True,
                'types': ['doctor', 'health'],
                'phone': '+91-11-23456789'
            },
            {
                'place_id': 'mock_3',
                'name': 'MedPlus Pharmacy',
                'address': f'789 Health Rd, {location}',
                'latitude': 28.6159,
                'longitude': 77.2110,
                'rating': 4.0,
                'total_ratings': 450,
                'is_open': True,
                'types': ['pharmacy', 'store'],
                'phone': '+91-11-34567890'
            }
        ]
    
    def search_specialists(
        self,
        location: str,
        specialty: str,
        radius: int = 10000
    ) -> List[Dict]:
        """Search for specialist doctors"""
        
        search_query = f"{specialty} doctor near {location}"
        
        if not self.gmaps:
            return []
        
        try:
            places_result = self.gmaps.places(
                query=search_query,
                location=location,
                radius=radius
            )
            
            specialists = []
            
            for place in places_result.get('results', [])[:10]:
                specialist = self._parse_place(place)
                specialist['specialty'] = specialty
                specialists.append(specialist)
            
            return specialists
        
        except Exception as e:
            logger.error(f"Error searching specialists: {e}")
            return []


if __name__ == "__main__":
    service = LocationService()
    
    # Test finding facilities
    facilities = service.find_nearby_facilities("New Delhi, India", "hospital")
    
    print(f"\nFound {len(facilities)} facilities:")
    for facility in facilities[:3]:
        print(f"- {facility['name']}: {facility['address']}")
    
    logger.info("✅ Location Service test completed")

