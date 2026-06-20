class EventBus:
    def __init__(self):
        self.subscribers = {}
        
    def subscribe(self, event_type: str, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        
    def publish(self, event_type: str, data=None):
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error en subscriber de {event_type}: {e}")

# Instancia global (Singleton)
bus = EventBus()
