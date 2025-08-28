# app/services/geoip_service.py
import geoip2.database
from app.core.config import settings
from app.core.logger import get_logger
from typing import Optional, Dict, Any
import ipaddress
import os

logger = get_logger(__name__)

class GeoIPService:
    """
    A service to provide geolocation information for IP addresses.
    """
    _reader = None

    @classmethod
    def _get_reader(cls):
        """Initializes and returns a singleton GeoIP2 database reader."""
        if cls._reader is None:
            db_path = settings.GEOIP_DATABASE_PATH
            if not os.path.exists(db_path):
                logger.error(f"GeoIP database not found at path: {db_path}")
                raise FileNotFoundError(f"GeoIP database not found at {db_path}")
            try:
                logger.info(f"Loading GeoIP database from: {db_path}")
                cls._reader = geoip2.database.Reader(db_path)
            except Exception as e:
                logger.error(f"Failed to load GeoIP database: {e}")
                raise
        return cls._reader

    def get_ip_location(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Get geolocation information for a given IP address.

        Args:
            ip_address (str): The IP address to look up.

        Returns:
            Optional[Dict[str, Any]]: A dictionary with location data or None if not found or invalid.
        """
        try:
            # Validate that the IP is public and not a private/reserved address
            ip_obj = ipaddress.ip_address(ip_address)
            if not ip_obj.is_global:
                logger.debug(f"Skipping geolocation for private/reserved IP: {ip_address}")
                return None

            reader = self._get_reader()
            response = reader.city(ip_address)
            
            location_data = {
                "ip_address": ip_address,
                "country": response.country.name,
                "city": response.city.name,
                "postal_code": response.postal.code,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
                "isp": response.traits.isp,
                "organization": response.traits.organization,
            }
            logger.debug(f"Successfully geolocated IP {ip_address}: {location_data['city']}, {location_data['country']}")
            return location_data

        except geoip2.errors.AddressNotFoundError:
            logger.warning(f"Geolocation for IP address not found: {ip_address}")
            return None
        except Exception as e:
            logger.error(f"An error occurred during GeoIP lookup for {ip_address}: {e}")
            return None

    def __del__(self):
        """Ensure the database reader is closed when the service is destroyed."""
        if self.__class__._reader:
            self.__class__._reader.close()
            self.__class__._reader = None
            logger.info("GeoIP database connection closed.")
