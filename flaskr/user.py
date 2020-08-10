import requests
import dataclasses as dc

    
@dc.dataclass
class User:
    user_id: int
    ip_address: str
    location: str = 'UNKNOWN'

    def lookup_location(self):
        """Use the set ip_address to set location."""
        # TODO
        self.location = 'UNKOWN'