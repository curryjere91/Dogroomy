# Utility Methods (shared across tabs)
def get_clients(self):
    """Fetch all client names."""
    self.cursor.execute("SELECT name FROM Clients")
    return [row[0] for row in self.cursor.fetchall()]

def get_dogs_by_client(self, client_name):
    """Fetch all dogs owned by a specific client."""
    client_id = self.get_client_id(client_name)
    self.cursor.execute("SELECT name FROM Dogs WHERE client_id = ?", (client_id,))
    return [row[0] for row in self.cursor.fetchall()]

def get_services(self):
    """Fetch all services."""
    self.cursor.execute("SELECT service_name FROM Services")
    return [row[0] for row in self.cursor.fetchall()]

def get_price_by_service(self, service_name):
    """Fetch the price of a service."""
    self.cursor.execute("""
        SELECT price FROM Prices WHERE service_id = 
        (SELECT service_id FROM Services WHERE service_name = ?)
    """, (service_name,))
    result = self.cursor.fetchone()
    return result[0] if result else None

def get_client_id(self, client_name):
    """Fetch the client ID for a given client name."""
    self.cursor.execute("SELECT client_id FROM Clients WHERE name = ?", (client_name,))
    result = self.cursor.fetchone()
    return result[0] if result else None

def get_dog_id(self, dog_name):
    """Fetch the dog ID for a given dog name."""
    self.cursor.execute("SELECT dog_id FROM Dogs WHERE name = ?", (dog_name,))
    result = self.cursor.fetchone()
    return result[0] if result else None

def get_service_id_by_name(self, service_name):
    """Fetch the service ID for a given service name."""
    self.cursor.execute("SELECT service_id FROM Services WHERE service_name = ?", (service_name,))
    result = self.cursor.fetchone()
    return result[0] if result else None

def get_price_id_by_service_id(self, service_id):
    """Fetch the price ID for a given service ID."""
    self.cursor.execute("SELECT price_id FROM Prices WHERE service_id = ?", (service_id,))
    result = self.cursor.fetchone()
    return result[0] if result else None
