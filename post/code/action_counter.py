class ActionCounter:
    def __init__(self, threshold=10):
        self.count = 0
        self.threshold = threshold
        
    def increment(self):
        self.count += 1
        
    def reset(self):
        self.count = 0
        
    def get_count(self):
        return self.count
    
    def check_completion(self):
        if self.count >= self.threshold:
            self.count = self.threshold
            
    def get_completion(self):
        return self.count / self.threshold if self.count >= self.threshold else self.count / self.threshold * 100
    
    def is_completed(self):
        return self.count >= self.threshold
