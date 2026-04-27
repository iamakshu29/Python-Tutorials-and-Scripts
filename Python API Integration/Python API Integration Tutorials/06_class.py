# 6_class.py — OOP Concepts: Classes, Instances, Inheritance

# =============================================
# BASIC CLASS
# =============================================
# __init__ is the constructor — runs automatically when an instance is created.
# self refers to the specific instance being created.
class ServiceMonitor:
    def __init__(self,service_name, port):
        print(f"Monitoring {service_name} on port {port}")
        self.service = service_name  # instance attribute — unique per object
        self.port = port
        self.is_alive = False        # default state before any check is run

# nginx_monitor = ServiceMonitor("nginx",80)

# print(type(nginx_monitor))                       # <class '__main__.ServiceMonitor'>
# print(isinstance(nginx_monitor,ServiceMonitor))  # True
# print(nginx_monitor.service)
# print(nginx_monitor.port)


# =============================================
# CLASS WITH METHODS
# =============================================
# Methods are functions defined inside a class — they always receive self as the first arg.
class ServiceMonitor:
    def __init__(self,service_name, port):
        print(f"Initializing Monitoring for {service_name} on port {port}")
        self.service = service_name
        self.port = port
        self.is_alive = False

    def check(self):
        print(f"Method: checking {self.service} on port {self.port}")
        self.is_alive = True  # mutates instance state

        print(f"Method: {self.service} service staus: {"Alive" if self.service else "DOWN"}")

        return self.is_alive  # caller can use the return value to act on status
    
# redis_monitor = ServiceMonitor("redis",6379)
# status = redis_monitor.check()
# print(f"Received Status: {status}")

# =============================================
# INHERITANCE — Subclass
# =============================================
# HttpServiceMonitor extends ServiceMonitor — it gets all parent methods for free.
# super().__init__() delegates attribute setup to the parent constructor.
class HttpServiceMonitor(ServiceMonitor):
    def __init__(self, service_name, port,url):
        super().__init__(service_name,port)
        self.url = url  # extra attribute specific to HTTP services

    def ping(self):
        print(f"Method: ping url {self.url}")
    
    def check(self):
        alive = super().check()  # reuse parent logic, then extend it
        print(alive)
        print("This is different than method in superclass")  # method overriding

# http_monitor = HttpServiceMonitor("web",8080,"http://localhost")
# http_monitor.ping()
# http_monitor.check()