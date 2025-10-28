"""
Maps Routes for MedAI-Pro
Google Maps integration for finding nearby hospitals and medical facilities
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Optional
from pydantic import BaseModel

from ..utils.auth import require_clerk_auth
from ..maps.location_service import LocationService

router = APIRouter(prefix="/api/maps", tags=["maps"])
location_service = LocationService()


class NearbyFacilitiesRequest(BaseModel):
    location: Dict[str, float]  # {"lat": 12.9716, "lng": 77.5946}
    facility_type: str = "hospital"
    radius: int = 5000


class SearchFacilitiesRequest(BaseModel):
    query: str
    location: Dict[str, float]


@router.post("/nearby")
async def get_nearby_facilities(
    request: NearbyFacilitiesRequest,
    user_id: str = Depends(require_clerk_auth)
):
    """
    Find nearby medical facilities
    Uses Google Maps API to locate hospitals, clinics, pharmacies, etc.
    """
    try:
        # Convert location dict to string format
        location_str = f"{request.location['lat']},{request.location['lng']}"
        
        # Find facilities
        facilities = location_service.find_nearby_facilities(
            location=location_str,
            facility_type=request.facility_type,
            radius=request.radius
        )
        
        return {
            "facilities": facilities,
            "count": len(facilities),
            "location": request.location,
            "radius": request.radius
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_facilities(
    request: SearchFacilitiesRequest,
    user_id: str = Depends(require_clerk_auth)
):
    """
    Search for specific medical facilities
    """
    try:
        location_str = f"{request.location['lat']},{request.location['lng']}"
        
        facilities = location_service.search_facilities(
            query=request.query,
            location=location_str
        )
        
        return {
            "facilities": facilities,
            "count": len(facilities),
            "query": request.query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/facility/{place_id}")
async def get_facility_details(
    place_id: str,
    user_id: str = Depends(require_clerk_auth)
):
    """
    Get detailed information about a specific facility
    """
    try:
        details = location_service.get_facility_details(place_id)
        
        return details
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

